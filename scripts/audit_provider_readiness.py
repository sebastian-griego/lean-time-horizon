from __future__ import annotations

import ast
import csv
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "check_id",
    "area",
    "status",
    "evidence",
    "current_state",
    "limitation",
    "next_action",
]

EXPECTED_PROVIDER_ENV = {
    "openai": "OPENAI_LEAN_RUNNER",
    "anthropic": "ANTHROPIC_LEAN_RUNNER",
    "gemini": "GEMINI_LEAN_RUNNER",
    "command": "LEAN_MODEL_RUNNER",
}

EXPECTED_RUNNER_ENV = [
    "PROMPT_PATH",
    "MODEL",
    "TASK_ID",
    "ATTEMPT_INDEX",
    "SCAFFOLD",
    "LEAN_LOOKUP_COMMAND",
    "TASK_PUBLIC_DIR",
    "TASK_PUBLIC_FILES",
]

SECRET_PATTERNS = {
    "openai_key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "anthropic_key": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"),
    "gemini_key": re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"),
    "api_key_assignment": re.compile(
        r"\b(?:OPENAI_API_KEY|ANTHROPIC_API_KEY|GEMINI_API_KEY|ARISTOTLE_API_KEY)\s*[:=]\s*[\"']?[A-Za-z0-9_-]{16,}",
        flags=re.IGNORECASE,
    ),
}

SCAN_EXCLUDE_PREFIXES = (
    ".git/",
    ".lake/",
    "public_tasks/",
    "tmp/",
    "harness/__pycache__/",
    "scripts/__pycache__/",
)


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def row(
    check_id: str,
    area: str,
    status: str,
    evidence: str,
    current_state: str,
    limitation: str,
    next_action: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "status": status,
        "evidence": evidence,
        "current_state": current_state,
        "limitation": limitation,
        "next_action": next_action,
    }


def parse_provider_env_map(source: str) -> dict[str, str]:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "PROVIDER_COMMAND_ENV":
                    value = ast.literal_eval(node.value)
                    return {str(k): str(v) for k, v in value.items()}
    return {}


def parse_provider_choices(source: str) -> list[str]:
    tree = ast.parse(source)
    choices: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            is_add_argument = isinstance(func, ast.Attribute) and func.attr == "add_argument"
            if not is_add_argument:
                continue
            first_arg = node.args[0].value if node.args and isinstance(node.args[0], ast.Constant) else None
            if first_arg != "--provider":
                continue
            for keyword in node.keywords:
                if keyword.arg == "choices":
                    choices.update(str(item) for item in ast.literal_eval(keyword.value))
    return sorted(choices)


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    files: list[Path] = []
    for line in result.stdout.splitlines():
        if not line or line == "scripts/audit_provider_readiness.py":
            continue
        if any(line.startswith(prefix) for prefix in SCAN_EXCLUDE_PREFIXES):
            continue
        files.append(ROOT / line)
    return files


def secret_scan() -> dict[str, object]:
    matches: list[dict[str, str]] = []
    for path in tracked_files():
        if not path.exists() or path.is_dir():
            continue
        text = read_text(path)
        for name, pattern in SECRET_PATTERNS.items():
            for match in pattern.finditer(text):
                matches.append({
                    "pattern": name,
                    "path": path.relative_to(ROOT).as_posix(),
                    "line": str(text[: match.start()].count("\n") + 1),
                })
                if len(matches) >= 12:
                    return {"match_count": len(matches), "sample": matches}
    return {"match_count": len(matches), "sample": matches}


def transcript_parse_summary(rows: list[dict[str, str]]) -> dict[str, object]:
    missing = 0
    parse_failures = 0
    total_jsonl_lines = 0
    for result_row in rows:
        transcript = ROOT / result_row.get("transcript_link", "")
        if not transcript.exists():
            missing += 1
            continue
        try:
            lines = [line for line in transcript.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
            for line in lines:
                json.loads(line)
            total_jsonl_lines += len(lines)
        except json.JSONDecodeError:
            parse_failures += 1
    return {
        "rows": len(rows),
        "missing_transcripts": missing,
        "parse_failures": parse_failures,
        "total_jsonl_lines": total_jsonl_lines,
    }


def build_rows() -> list[dict[str, str]]:
    run_model_source = read_text(ROOT / "scripts" / "run_model_sweep.py")
    anthropic_source = read_text(ROOT / "scripts" / "anthropic_runner.py")
    readme_text = read_text(ROOT / "README.md")
    report_text = read_text(ROOT / "reports" / "metr_style_report.md")
    model_analysis_text = read_text(ROOT / "reports" / "model_run_analysis.md")
    run_results = read_csv(ROOT / "data" / "run_results.csv")
    plan = read_csv(ROOT / "data" / "model_sweep_plan.csv")
    model_summary = read_csv(ROOT / "data" / "model_result_summary.csv")

    provider_env = parse_provider_env_map(run_model_source)
    provider_choices = parse_provider_choices(run_model_source)
    provider_env_ok = provider_env == EXPECTED_PROVIDER_ENV
    provider_choices_ok = set(provider_choices) == {"local_reference", "command", "openai", "anthropic", "gemini"}

    provider_rows = [result_row for result_row in run_results if result_row.get("qa_stage") != "local_qa"]
    accepted_provider_rows = [
        result_row for result_row in provider_rows
        if result_row.get("task_id") in {plan_row.get("task_id") for plan_row in plan}
    ]
    accepted_noninfra = [
        result_row for result_row in accepted_provider_rows
        if result_row.get("infra_fail_count") in {"", "0", 0}
    ]
    planned_cells = {(plan_row.get("task_id"), plan_row.get("scaffold")) for plan_row in plan}
    covered_cells = {(result_row.get("task_id"), result_row.get("scaffold")) for result_row in accepted_noninfra}
    provider_models = Counter(result_row.get("model", "unknown") for result_row in provider_rows)
    provider_scaffolds = Counter(result_row.get("scaffold", "unknown") for result_row in accepted_noninfra)
    summary_fields = set(model_summary[0]) if model_summary else set()

    rows: list[dict[str, str]] = []
    rows.append(row(
        "provider_catalog_contract",
        "runner_contract",
        "pass" if provider_env_ok and provider_choices_ok else "fail",
        f"provider_choices={compact_json(provider_choices)}; provider_env={compact_json(provider_env)}",
        "Runner exposes local_reference plus command/openai/anthropic/gemini provider routes.",
        "OpenAI and Gemini currently rely on the generic environment-command adapter contract.",
        "Keep provider choices and PROVIDER_COMMAND_ENV synchronized with README and sweep plans.",
    ))

    missing_runner_env = [name for name in EXPECTED_RUNNER_ENV if name not in run_model_source]
    rows.append(row(
        "external_runner_env_contract",
        "runner_contract",
        "pass" if not missing_runner_env else "fail",
        f"expected_env={compact_json(EXPECTED_RUNNER_ENV)}; missing_env={compact_json(missing_runner_env)}",
        "External runner commands receive prompt path, task identity, scaffold, lookup command, and public-file metadata.",
        "Static source checks do not prove a third-party adapter honors those variables.",
        "Keep this contract stable and update adapter docs when adding runner-supplied fields.",
    ))

    adapter_files = {
        "anthropic": (ROOT / "scripts" / "anthropic_runner.py").exists(),
        "openai": (ROOT / "scripts" / "openai_runner.py").exists(),
        "gemini": (ROOT / "scripts" / "gemini_runner.py").exists(),
    }
    rows.append(row(
        "bundled_provider_adapters",
        "provider_adapter_surface",
        "caution" if adapter_files.get("anthropic") and not all(adapter_files.values()) else "pass",
        f"adapter_files={compact_json(adapter_files)}; generic_command_adapter={'command' in provider_env}",
        "Anthropic has a minimal bundled adapter; OpenAI and Gemini are supported through external command env vars, not dedicated committed adapters.",
        "Missing dedicated adapters are acceptable for local report readiness but limit turnkey provider comparability.",
        "Add dedicated OpenAI and Gemini adapters or document external runner commands before a broad frontier sweep.",
    ))

    anthropic_reads_key = 'os.environ.get("ANTHROPIC_API_KEY")' in anthropic_source
    anthropic_sends_header = '"x-api-key": key' in anthropic_source
    anthropic_prints_key = "print(key" in anthropic_source
    anthropic_extracts_lean = "extract_lean" in anthropic_source
    anthropic_static_ok = (
        anthropic_reads_key
        and anthropic_sends_header
        and not anthropic_prints_key
        and anthropic_extracts_lean
    )
    rows.append(row(
        "anthropic_adapter_static_safety",
        "provider_adapter_surface",
        "pass" if anthropic_static_ok else "fail",
        f"reads_key_from_env={anthropic_reads_key}; sends_header={anthropic_sends_header}; prints_key={anthropic_prints_key}; extracts_lean={anthropic_extracts_lean}",
        "The bundled Anthropic adapter reads credentials from the environment and emits Lean text.",
        "This is a static audit; it does not call the provider API or validate current model availability.",
        "Run a fresh smoke job with explicit cost/version notes before claiming provider performance.",
    ))

    secret_result = secret_scan()
    rows.append(row(
        "tracked_secret_scan",
        "credential_policy",
        "pass" if int(secret_result["match_count"]) == 0 else "fail",
        compact_json(secret_result),
        "Tracked files contain no high-confidence API key patterns or direct API-key assignments.",
        "Pattern scanning can miss unknown key formats and should not replace careful review.",
        "Keep credentials in environment variables only and rerun this audit before publishing.",
    ))

    env_policy_ok = (
        "Do not fake results" in readme_text
        and "API keys stay in environment variables" in readme_text
        and "No provider API credentials or runner commands are committed" in report_text
    )
    rows.append(row(
        "credential_and_no_fake_policy_text",
        "credential_policy",
        "pass" if env_policy_ok else "fail",
        f"readme_no_fake={'Do not fake results' in readme_text}; readme_env_keys={'API keys stay in environment variables' in readme_text}; report_no_credentials={'No provider API credentials or runner commands are committed' in report_text}",
        "The public documentation states the no-fake-results and env-var credential policy.",
        "Policy text is not evidence that future provider rows are externally reproduced.",
        "Require transcripts, run-result integrity, and provider-version notes for every future model run.",
    ))

    planned_commands = [plan_row.get("sweep_command", "") for plan_row in plan]
    command_plan_ok = (
        bool(plan)
        and all("--provider command" in command for command in planned_commands)
        and all("--attempts 10" in command for command in planned_commands)
        and all("--acceptance-status accepted_v0" in command for command in planned_commands)
    )
    planned_k_values = sorted({plan_row.get("planned_k", "") for plan_row in plan})
    rows.append(row(
        "primary_sweep_command_plan",
        "planned_sweep",
        "pass" if command_plan_ok and planned_k_values == ["10"] else "fail",
        f"planned_rows={len(plan)}; planned_k_values={compact_json(planned_k_values)}; command_plan_ok={command_plan_ok}",
        "The committed model-sweep plan encodes accepted_v0 x scaffold pass@10 command templates.",
        "The plan is prospective and does not mean the rows have been run.",
        "Instantiate MODEL and runner env vars only when running real provider sweeps.",
    ))

    transcript_summary = transcript_parse_summary(provider_rows)
    rows.append(row(
        "provider_transcript_evidence",
        "run_data",
        "pass" if transcript_summary["rows"] > 0 and transcript_summary["missing_transcripts"] == 0 and transcript_summary["parse_failures"] == 0 else "fail",
        compact_json(transcript_summary),
        "Committed provider smoke rows have parseable transcript files.",
        "Transcript presence does not make the tiny smoke set representative.",
        "Keep transcript links mandatory and parse-check future provider sweeps.",
    ))

    qa_stage_counts = Counter(result_row.get("qa_stage", "unknown") for result_row in run_results)
    local_rows = [result_row for result_row in run_results if result_row.get("qa_stage") == "local_qa"]
    reference_solution_rows = sum(1 for result_row in local_rows if result_row.get("model") == "reference_solution")
    plausible_wrong_rows = sum(1 for result_row in local_rows if result_row.get("model", "").startswith("plausible_wrong:"))
    qa_stage_ok = (
        set(qa_stage_counts).issubset({"model_sweep", "local_qa"})
        and reference_solution_rows > 0
        and plausible_wrong_rows > 0
    )
    rows.append(row(
        "local_qa_provider_separation",
        "run_data",
        "pass" if qa_stage_ok else "fail",
        f"qa_stage_counts={compact_json(dict(sorted(qa_stage_counts.items())))}; reference_solution_rows={reference_solution_rows}; plausible_wrong_rows={plausible_wrong_rows}",
        "Local reference/wrong rows are separated from provider model_sweep rows.",
        "This is hygiene evidence only; it does not validate provider capability.",
        "Keep local QA rows excluded from model-performance summaries.",
    ))

    provider_coverage_status = "pass" if planned_cells and covered_cells >= planned_cells else ("block" if provider_rows else "fail")
    rows.append(row(
        "provider_sweep_coverage",
        "run_data",
        provider_coverage_status,
        f"provider_models={compact_json(dict(sorted(provider_models.items())))}; accepted_noninfra_rows={len(accepted_noninfra)}; covered_cells={len(covered_cells)}/{len(planned_cells)}; accepted_scaffolds={compact_json(dict(sorted(provider_scaffolds.items())))}",
        "Provider evidence is smoke-only and covers one accepted non-infra cell.",
        "This blocks frontier/scaffold-effect claims but does not block local report readiness.",
        "Run the full accepted_v0 x scaffold sweep after hosted QA and runner readiness checks are stable.",
    ))

    analysis_boundary_ok = (
        "not a benchmark performance run" in model_analysis_text
        and {"wilson_low", "wilson_high", "infra_fail_rows", "rows_noninfra"}.issubset(summary_fields)
    )
    rows.append(row(
        "provider_claim_boundary",
        "reporting",
        "pass" if analysis_boundary_ok else "fail",
        f"model_summary_fields={compact_json(sorted(summary_fields))}; model_analysis_has_smoke_boundary={'not a benchmark performance run' in model_analysis_text}",
        "Model analysis separates smoke evidence from benchmark performance claims.",
        "Future reports still need broader provider data before performance conclusions.",
        "Keep unsupported frontier and scaffold claims blocked until planned coverage is real.",
    ))

    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row_data["status"] for row_data in rows)
    area_counts = Counter(row_data["area"] for row_data in rows)
    lines = [
        "# Provider Readiness Audit",
        "",
        "This generated audit checks model-runner readiness without using provider credentials or creating new model results. It separates runner/adaptor implementation, credential policy, transcript evidence, planned sweep commands, and the current smoke-only provider coverage.",
        "",
        "## Summary",
        "",
        f"- checks: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- areas: `{compact_json(dict(sorted(area_counts.items())))}`",
        "",
        "## Check Table",
        "",
        "| check | area | status | evidence | current state | limitation | next action |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row_data in rows:
        lines.append(
            f"| `{row_data['check_id']}` | {row_data['area']} | {row_data['status']} | "
            f"{escaped(row_data['evidence'])} | {escaped(row_data['current_state'])} | "
            f"{escaped(row_data['limitation'])} | {escaped(row_data['next_action'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`pass` rows establish local readiness or hygiene. `caution` rows are missing convenience/provider-specific adapter coverage. `block` rows show that real provider evidence is still smoke-only and should not be used for frontier-model or scaffold-effect claims.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "provider_readiness_audit.csv", rows)
    write_markdown(ROOT / "reports" / "provider_readiness_audit.md", rows)
    print(f"wrote data/provider_readiness_audit.csv and reports/provider_readiness_audit.md with {len(rows)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
