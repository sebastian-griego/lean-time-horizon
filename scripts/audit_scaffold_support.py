from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_model_sweep import build_prompt  # noqa: E402
from lean_lookup import search_roots  # noqa: E402

FIELDS = [
    "check_id",
    "area",
    "status",
    "evidence",
    "risk_or_limit",
    "required_next_action",
]

EXPECTED_SCAFFOLDS = {
    "one-shot": {"lookup": "false", "iterative_compile_feedback": "false", "submission_limit": "1"},
    "lookup": {"lookup": "true", "iterative_compile_feedback": "false", "submission_limit": "1"},
    "lookup_unlimited": {"lookup": "true", "iterative_compile_feedback": "true", "submission_limit": "unlimited"},
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def row(
    check_id: str,
    area: str,
    status: str,
    evidence: str,
    risk_or_limit: str,
    required_next_action: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "status": status,
        "evidence": evidence,
        "risk_or_limit": risk_or_limit,
        "required_next_action": required_next_action,
    }


def task_dirs() -> dict[str, Path]:
    dirs: dict[str, Path] = {}
    for split in ["dev", "test", "candidates"]:
        base = ROOT / "tasks" / split
        if not base.exists():
            continue
        for task_dir in sorted(path for path in base.iterdir() if path.is_dir()):
            metadata_path = task_dir / "metadata.json"
            if not metadata_path.exists():
                continue
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            dirs[str(metadata["task_id"])] = task_dir
    return dirs


def run_lookup(query: str, limit: int = 50) -> dict[str, object]:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "lean_lookup.py"), query, "--limit", str(limit)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    lines = (proc.stdout or "").splitlines()
    hidden_lines = [
        line for line in lines
        if "\\hidden\\" in line or "/hidden/" in line or "\\wrong\\" in line or "/wrong/" in line
    ]
    return {
        "query": query,
        "returncode": proc.returncode,
        "line_count": len(lines),
        "hidden_or_wrong_line_count": len(hidden_lines),
        "sample": lines[:3],
    }


def build_rows() -> list[dict[str, str]]:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    scaffolds = read_csv(ROOT / "data" / "scaffold_variants.csv")
    plan = read_csv(ROOT / "data" / "model_sweep_plan.csv")
    run_results = read_csv(ROOT / "data" / "run_results.csv")
    claim_evidence = read_csv(ROOT / "data" / "claim_evidence_audit.csv")
    release_decision = read_csv(ROOT / "data" / "release_decision_log.csv")
    runner_source = (ROOT / "scripts" / "run_model_sweep.py").read_text(encoding="utf-8")
    dirs = task_dirs()
    accepted = [task for task in metadata if task.get("acceptance_status") == "accepted_v0"]

    rows: list[dict[str, str]] = []

    scaffold_by_name = {row_data.get("scaffold", ""): row_data for row_data in scaffolds}
    catalog_mismatches: list[str] = []
    for scaffold, expected in EXPECTED_SCAFFOLDS.items():
        actual = scaffold_by_name.get(scaffold)
        if not actual:
            catalog_mismatches.append(f"{scaffold}:missing")
            continue
        for field, expected_value in expected.items():
            if actual.get(field) != expected_value:
                catalog_mismatches.append(f"{scaffold}:{field}={actual.get(field)} expected {expected_value}")
    extra_scaffolds = sorted(set(scaffold_by_name) - set(EXPECTED_SCAFFOLDS))
    rows.append(row(
        "scaffold_catalog_complete",
        "scaffold_contract",
        "pass" if not catalog_mismatches and not extra_scaffolds else "fail",
        f"scaffold rows={len(scaffolds)}; names={compact_json(sorted(scaffold_by_name))}; mismatches={compact_json(catalog_mismatches)}; extras={compact_json(extra_scaffolds)}.",
        "Catalog correctness does not by itself prove provider behavior.",
        "Keep data/scaffold_variants.csv aligned with runner and protocol semantics.",
    ))

    sample_task_id = next((task["task_id"] for task in accepted if task["task_id"] in dirs), accepted[0]["task_id"] if accepted else "")
    sample_task = dirs.get(sample_task_id)
    prompt_evidence: dict[str, object] = {}
    prompt_ok = False
    if sample_task:
        one_shot = build_prompt(sample_task, "one-shot")
        lookup = build_prompt(sample_task, "lookup")
        lookup_unlimited = build_prompt(sample_task, "lookup_unlimited")
        prompt_evidence = {
            "sample_task": sample_task_id,
            "one_shot_no_lookup": "No lookup tools are available" in one_shot,
            "lookup_mentions_lookup_command": "lean_lookup.py QUERY" in lookup,
            "lookup_no_feedback_section": "Previous grader feedback" not in lookup,
            "unlimited_mentions_feedback": "iterative compile/debug attempts" in lookup_unlimited,
            "unlimited_mentions_lookup": "lean_lookup.py QUERY" in lookup_unlimited,
        }
        prompt_ok = all(bool(value) for key, value in prompt_evidence.items() if key != "sample_task")
    rows.append(row(
        "prompt_affordance_contract",
        "scaffold_contract",
        "pass" if prompt_ok else "fail",
        compact_json(prompt_evidence),
        "This checks prompt construction, not whether a particular external model obeys the affordance.",
        "Keep scaffold-specific prompt text explicit whenever runner semantics change.",
    ))

    required_env = [
        "PROMPT_PATH",
        "MODEL",
        "TASK_ID",
        "ATTEMPT_INDEX",
        "SCAFFOLD",
        "LEAN_LOOKUP_COMMAND",
        "TASK_PUBLIC_DIR",
        "TASK_PUBLIC_FILES",
    ]
    missing_env = [name for name in required_env if name not in runner_source]
    provider_env_present = all(name in runner_source for name in ["OPENAI_LEAN_RUNNER", "ANTHROPIC_LEAN_RUNNER", "GEMINI_LEAN_RUNNER", "LEAN_MODEL_RUNNER"])
    rows.append(row(
        "runner_env_contract",
        "runner_contract",
        "pass" if not missing_env and provider_env_present else "fail",
        f"missing env keys={compact_json(missing_env)}; provider env map complete={provider_env_present}.",
        "External adapters still need provider-specific QA; this only verifies the runner contract.",
        "Keep runner environment variables stable for provider adapters and transcripts.",
    ))

    iterative_gate_ok = 'feedback if args.scaffold == "lookup_unlimited" else ""' in runner_source
    rows.append(row(
        "iterative_feedback_gate",
        "runner_contract",
        "pass" if iterative_gate_ok else "fail",
        f"lookup_unlimited-only feedback gate present={iterative_gate_ok}.",
        "Static check; it should be backed by provider smoke tests before performance claims.",
        "Preserve feedback only for lookup_unlimited so lookup remains one-submission.",
    ))

    attempt_semantics_ok = (
        "attempts_allowed = args.attempts" in runner_source
        and "for attempt in range(1, attempts_allowed + 1)" in runner_source
        and '"k": attempts_allowed' in runner_source
        and '"successes_out_of_k": successes' in runner_source
    )
    rows.append(row(
        "attempt_count_semantics",
        "runner_contract",
        "pass" if attempt_semantics_ok else "fail",
        f"attempt loop and k/success fields present={attempt_semantics_ok}.",
        "This verifies runner bookkeeping structure; run_integrity_audit checks committed rows.",
        "Keep k, attempts_completed, successes_out_of_k, and pass_at_k tied to the same attempt budget.",
    ))

    roots = search_roots()
    root_parts = [part.lower() for root in roots for part in root.parts]
    hidden_root_count = sum(1 for root in roots if "hidden" in [part.lower() for part in root.parts] or "wrong" in [part.lower() for part in root.parts])
    public_task_file_count = sum(1 for root in roots if ROOT / "tasks" in root.parents and root.suffix == ".lean")
    mathlib_roots = [root for root in roots if ".lake" in root.parts]
    rows.append(row(
        "lookup_roots_public_only",
        "lookup_integrity",
        "pass" if hidden_root_count == 0 and "hidden" not in root_parts and "wrong" not in root_parts else "fail",
        f"lookup roots={len(roots)}; public task lean files={public_task_file_count}; mathlib/std roots={len(mathlib_roots)}; hidden_or_wrong_roots={hidden_root_count}.",
        "Lookup still exposes public task scaffolds and installed library sources by design.",
        "Never add tasks/ as a whole-tree root; include only metadata-listed public Lean files.",
    ))

    lookup_smoke = run_lookup("Set.image", limit=25)
    rows.append(row(
        "lookup_command_smoke",
        "lookup_integrity",
        "pass" if lookup_smoke["returncode"] == 0 and int(lookup_smoke["line_count"]) > 0 else "fail",
        compact_json(lookup_smoke),
        "A single query only proves the command is usable in this checkout.",
        "Keep lookup command read-only and runnable without provider credentials.",
    ))

    leak_queries = [run_lookup("Set.image", limit=100), run_lookup("PinCheck", limit=100)]
    leak_count = sum(int(result["hidden_or_wrong_line_count"]) for result in leak_queries)
    rows.append(row(
        "lookup_hidden_leak_scan",
        "lookup_integrity",
        "pass" if leak_count == 0 and all(result["returncode"] == 0 for result in leak_queries) else "fail",
        compact_json([{key: result[key] for key in ["query", "returncode", "line_count", "hidden_or_wrong_line_count"]} for result in leak_queries]),
        "This is a path-based leak scan over representative queries, not a proof over every possible query.",
        "Keep hidden and wrong directories out of lookup roots and public exports.",
    ))

    scaffold_names = {row_data.get("scaffold") for row_data in scaffolds}
    expected_pairs = {(task["task_id"], scaffold) for task in accepted for scaffold in scaffold_names}
    planned_pairs = {(row_data.get("task_id"), row_data.get("scaffold")) for row_data in plan if row_data.get("analysis_set") == "primary_accepted_v0"}
    planned_k_values = {row_data.get("planned_k") for row_data in plan if row_data.get("analysis_set") == "primary_accepted_v0"}
    rows.append(row(
        "planned_sweep_coverage",
        "evaluation_protocol",
        "pass" if expected_pairs and expected_pairs.issubset(planned_pairs) and planned_k_values == {"10"} else "fail",
        f"expected pairs={len(expected_pairs)}; planned pairs={len(planned_pairs)}; missing={compact_json(sorted(expected_pairs - planned_pairs))}; planned_k_values={compact_json(sorted(planned_k_values))}.",
        "A plan is not performance evidence.",
        "Regenerate the evaluation protocol whenever accepted tasks or scaffold variants change.",
    ))

    accepted_ids = {task["task_id"] for task in accepted}
    provider_rows = [
        row_data for row_data in run_results
        if row_data.get("qa_stage") != "local_qa" and row_data.get("task_id") in accepted_ids
    ]
    noninfra_provider_rows = [row_data for row_data in provider_rows if row_data.get("infra_fail_count") in {"", "0", 0}]
    observed_pairs = {(row_data.get("task_id"), row_data.get("scaffold")) for row_data in noninfra_provider_rows}
    observed_scaffolds = {row_data.get("scaffold") for row_data in noninfra_provider_rows}
    coverage_status = "pass" if expected_pairs and expected_pairs.issubset(observed_pairs) else ("caution" if observed_pairs else "fail")
    rows.append(row(
        "observed_scaffold_data_coverage",
        "evaluation_protocol",
        coverage_status,
        f"non-infra accepted-provider rows={len(noninfra_provider_rows)}; observed pairs={len(observed_pairs)}/{len(expected_pairs)}; observed scaffolds={compact_json(sorted(observed_scaffolds))}.",
        "This is intentionally expected to remain caution until real scaffold sweeps are committed.",
        "Run accepted-core provider rows across one-shot, lookup, and lookup_unlimited before scaffold-effect claims.",
    ))

    claims = {row_data.get("claim_id"): row_data.get("support_status") for row_data in claim_evidence}
    decisions = {row_data.get("gate_id"): row_data.get("status") for row_data in release_decision}
    boundary_ok = claims.get("scaffold_effects") == "unsupported" and decisions.get("scaffold_effect_claim") == "block"
    rows.append(row(
        "scaffold_claim_boundary",
        "reporting",
        "pass" if boundary_ok else "fail",
        f"claim scaffold_effects={claims.get('scaffold_effects')}; decision scaffold_effect_claim={decisions.get('scaffold_effect_claim')}.",
        "The implementation can be audited without treating scaffold effects as measured.",
        "Keep scaffold-effect claims blocked until observed scaffold coverage reaches the planned sweep.",
    ))

    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row_data["status"] for row_data in rows)
    area_counts = Counter(row_data["area"] for row_data in rows)
    lines = [
        "# Scaffold Support Audit",
        "",
        "This generated audit checks whether the scaffold ladder is implemented and reported safely. It verifies prompt/runner contracts, lookup command behavior, hidden-path exclusion, planned sweep coverage, observed provider coverage, and the report's scaffold-claim boundary.",
        "",
        "## Summary",
        "",
        f"- checks: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- areas: `{compact_json(dict(sorted(area_counts.items())))}`",
        "",
        "## Check Table",
        "",
        "| check | area | status | evidence | risk or limit | next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row_data in rows:
        lines.append(
            f"| `{row_data['check_id']}` | {row_data['area']} | {row_data['status']} | "
            f"{escaped(row_data['evidence'])} | {escaped(row_data['risk_or_limit'])} | {escaped(row_data['required_next_action'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`pass` means the local implementation or report boundary passes the audit. `caution` means the infrastructure exists but model-result coverage is incomplete. `fail` means scaffold or lookup behavior must be fixed before relying on the artifact.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "scaffold_support_audit.csv", rows)
    write_markdown(ROOT / "reports" / "scaffold_support_audit.md", rows)
    print(f"wrote data/scaffold_support_audit.csv and reports/scaffold_support_audit.md with {len(rows)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
