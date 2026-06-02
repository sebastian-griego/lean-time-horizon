from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMMAND_FIELDS = [
    "scaffold",
    "planned_task_count",
    "planned_k",
    "primary_endpoint",
    "provider_route",
    "runner_env_var",
    "credential_policy",
    "full_sweep_command",
    "smoke_command",
    "post_run_commands",
    "required_evidence",
]

CHECKLIST_FIELDS = [
    "check_id",
    "phase",
    "required_before_claim",
    "current_status",
    "evidence",
    "next_action",
]

PROVIDER_ROUTES = {
    "command": {
        "runner_env_var": "LEAN_MODEL_RUNNER",
        "credential_policy": "External runner owns credentials; keep any provider keys in environment variables only.",
    },
    "anthropic": {
        "runner_env_var": "ANTHROPIC_LEAN_RUNNER",
        "credential_policy": "Use ANTHROPIC_API_KEY only from the environment; do not commit keys or transcripts containing keys.",
    },
    "openai": {
        "runner_env_var": "OPENAI_LEAN_RUNNER",
        "credential_policy": "Use OPENAI_API_KEY only from the environment; OpenAI route currently expects an external runner command.",
    },
    "gemini": {
        "runner_env_var": "GEMINI_LEAN_RUNNER",
        "credential_policy": "Use GEMINI_API_KEY only from the environment; Gemini route currently expects an external runner command.",
    },
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def accepted_task_count() -> int:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    return sum(1 for row in metadata if row.get("acceptance_status") == "accepted_v0")


def grouped_plan() -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(ROOT / "data" / "model_sweep_plan.csv"):
        grouped[row.get("scaffold", "")].append(row)
    return dict(grouped)


def post_run_commands() -> str:
    commands = [
        "python scripts/audit_run_integrity.py",
        "python scripts/generate_transcript_review_packet.py",
        "python scripts/analyze_model_results.py",
        "python scripts/audit_model_sweep_coverage.py",
        "python scripts/audit_model_evidence_provenance.py",
        "python scripts/audit_statistical_reporting.py",
        "python scripts/audit_provider_readiness.py",
        "python scripts/audit_scaffold_support.py",
        "python scripts/audit_requirement_coverage.py --public-export public_tasks",
        "python scripts/audit_claim_evidence.py",
        "python scripts/generate_claim_authorization_matrix.py",
        "python scripts/generate_research_claim_gap_matrix.py",
        "python scripts/generate_concise_report.py",
        "python scripts/audit_report_claim_conformance.py",
        "python scripts/audit_report_shape.py",
        "python scripts/generate_release_decision_log.py",
        "python scripts/generate_freeze_readiness_roadmap.py",
        "python scripts/generate_report.py",
    ]
    return " && ".join(commands)


def full_command(provider: str, scaffold: str, k: str) -> str:
    return (
        "python scripts/run_model_sweep.py "
        f"--provider {provider} --model MODEL --scaffold {scaffold} --attempts {k} "
        "--acceptance-status accepted_v0"
    )


def smoke_command(provider: str, scaffold: str) -> str:
    return (
        "python scripts/run_model_sweep.py "
        f"--provider {provider} --model MODEL --scaffold {scaffold} --attempts 1 "
        "--task-id lt-201"
    )


def build_command_rows() -> list[dict[str, str]]:
    grouped = grouped_plan()
    rows: list[dict[str, str]] = []
    for scaffold, plan_rows in sorted(grouped.items()):
        k_values = sorted({row.get("planned_k", "") for row in plan_rows})
        k = k_values[0] if len(k_values) == 1 else "10"
        endpoint_values = sorted({row.get("primary_endpoint", "") for row in plan_rows})
        endpoint = endpoint_values[0] if len(endpoint_values) == 1 else "pass_at_k"
        for provider, provider_data in PROVIDER_ROUTES.items():
            rows.append({
                "scaffold": scaffold,
                "planned_task_count": str(len({row.get("task_id", "") for row in plan_rows})),
                "planned_k": k,
                "primary_endpoint": endpoint,
                "provider_route": provider,
                "runner_env_var": provider_data["runner_env_var"],
                "credential_policy": provider_data["credential_policy"],
                "full_sweep_command": full_command(provider, scaffold, k),
                "smoke_command": smoke_command(provider, scaffold),
                "post_run_commands": post_run_commands(),
                "required_evidence": "new run_results rows; transcripts/<job_id>/*.jsonl; zero run_integrity failures; updated transcript review queue; completed failure_label_reviews plus zero failure_label_review_audit failures before failure analysis; updated model_result_summary; updated statistical/provider/scaffold audits",
            })
    return rows


def status_from_requirement(requirement_id: str) -> tuple[str, str]:
    for row in read_csv(ROOT / "data" / "requirement_coverage.csv"):
        if row.get("requirement_id") == requirement_id:
            return row.get("status", "missing"), row.get("evidence", "")
    return "missing", "requirement row missing"


def status_from_audit(path: Path, status_field: str, blocked_statuses: set[str]) -> tuple[str, str]:
    rows = read_csv(path)
    if not rows:
        return "missing", f"{path.relative_to(ROOT).as_posix()} missing or empty"
    counts = Counter(row.get(status_field, "unknown") for row in rows)
    blockers = sum(count for status, count in counts.items() if status in blocked_statuses)
    return ("blocked" if blockers else "ready"), f"rows={len(rows)}; statuses={compact_json(dict(sorted(counts.items())))}"


def build_checklist_rows(command_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    scaffold_status, scaffold_evidence = status_from_requirement("scaffold_support_audit")
    provider_status, provider_evidence = status_from_requirement("provider_readiness_audit")
    run_status, run_evidence = status_from_requirement("run_integrity_audit")
    statistical_status, statistical_evidence = status_from_audit(
        ROOT / "data" / "statistical_reporting_audit.csv",
        "status",
        {"fail", "block"},
    )
    scaffold_result_status, scaffold_result_evidence = status_from_requirement("scaffold_result_comparison")
    frontier_status, frontier_evidence = status_from_requirement("frontier_model_evidence")
    plan_rows = read_csv(ROOT / "data" / "model_sweep_plan.csv")
    planned_scaffolds = sorted({row.get("scaffold", "") for row in plan_rows})
    planned_k = sorted({row.get("planned_k", "") for row in plan_rows})
    rows = [
        {
            "check_id": "local_validation_before_sweep",
            "phase": "pre_run",
            "required_before_claim": "true",
            "current_status": "ready" if run_status == "supported" else "blocked",
            "evidence": run_evidence,
            "next_action": "Run lake build, validate_all, public export validation, and run_integrity immediately before provider sweeps.",
        },
        {
            "check_id": "provider_runner_contract",
            "phase": "pre_run",
            "required_before_claim": "true",
            "current_status": "ready" if provider_status == "supported" else "blocked",
            "evidence": provider_evidence,
            "next_action": "Set the relevant runner env var and provider API key in the shell only; run a one-task smoke command first.",
        },
        {
            "check_id": "scaffold_ladder_contract",
            "phase": "pre_run",
            "required_before_claim": "true",
            "current_status": "ready" if scaffold_status == "supported" else "blocked",
            "evidence": scaffold_evidence,
            "next_action": "Keep one-shot, lookup, and lookup_unlimited prompt semantics fixed across provider runs.",
        },
        {
            "check_id": "planned_primary_cells",
            "phase": "run",
            "required_before_claim": "true",
            "current_status": "planned",
            "evidence": (
                f"accepted_tasks={accepted_task_count()}; planned_rows={len(plan_rows)}; "
                f"scaffolds={compact_json(planned_scaffolds)}; planned_k={compact_json(planned_k)}; "
                f"command_rows={len(command_rows)}"
            ),
            "next_action": "Run exactly the accepted_v0 x scaffold commands for each provider/model being reported.",
        },
        {
            "check_id": "transcript_and_run_result_evidence",
            "phase": "post_run",
            "required_before_claim": "true",
            "current_status": "blocked" if scaffold_result_status != "supported" else "ready",
            "evidence": scaffold_result_evidence,
            "next_action": "Commit run_results rows and transcript JSONL files, regenerate the transcript queue, complete failure-label review rows, then rerun integrity, model-result analysis, and model-sweep coverage audit.",
        },
        {
            "check_id": "frontier_claim_boundary",
            "phase": "post_run",
            "required_before_claim": "true",
            "current_status": "blocked" if frontier_status != "supported" else "ready",
            "evidence": frontier_evidence,
            "next_action": "Keep frontier and scaffold-effect claims unsupported until non-infra accepted-core coverage is broad enough.",
        },
        {
            "check_id": "statistical_report_refresh",
            "phase": "post_run",
            "required_before_claim": "true",
            "current_status": statistical_status,
            "evidence": statistical_evidence,
            "next_action": "Rerun statistical reporting after provider rows are committed; report raw n and Wilson intervals.",
        },
    ]
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, command_rows: list[dict[str, str]], checklist_rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    scaffold_counts = Counter(row["scaffold"] for row in command_rows)
    provider_counts = Counter(row["provider_route"] for row in command_rows)
    checklist_statuses = Counter(row["current_status"] for row in checklist_rows)
    lines = [
        "# Model Sweep Execution Packet",
        "",
        "This generated packet turns the planned accepted-core scaffold sweep into concrete provider-run commands and post-run evidence checks. It does not call provider APIs and does not create model results.",
        "",
        "## Summary",
        "",
        f"- command rows: `{len(command_rows)}`",
        f"- scaffold command counts: `{compact_json(dict(sorted(scaffold_counts.items())))}`",
        f"- provider routes: `{compact_json(dict(sorted(provider_counts.items())))}`",
        f"- checklist statuses: `{compact_json(dict(sorted(checklist_statuses.items())))}`",
        "- credentials policy: `all provider keys stay in environment variables; no secrets are committed`",
        "",
        "## Pre-Run Setup",
        "",
        "1. Run the local validation gate from `README.md` before starting a provider sweep.",
        "2. Set exactly one runner command environment variable for the provider route under test.",
        "3. Keep provider API keys in the shell environment only.",
        "4. Run a one-task smoke command and inspect transcript output before a full accepted-core sweep.",
        "5. Do not edit task prompts, public scaffolds, hidden checks, or accepted status between scaffold conditions for a reported model.",
        "",
        "## Command Table",
        "",
        "| provider | scaffold | runner env | k | full sweep command | smoke command |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for row in command_rows:
        lines.append(
            f"| `{row['provider_route']}` | `{row['scaffold']}` | `{row['runner_env_var']}` | "
            f"{row['planned_k']} | `{escaped(row['full_sweep_command'])}` | `{escaped(row['smoke_command'])}` |"
        )
    lines.extend([
        "",
        "## Evidence Checklist",
        "",
        "| check | phase | status | evidence | next action |",
        "| --- | --- | --- | --- | --- |",
    ])
    for row in checklist_rows:
        lines.append(
            f"| `{row['check_id']}` | {row['phase']} | {row['current_status']} | "
            f"{escaped(row['evidence'])} | {escaped(row['next_action'])} |"
        )
    lines.extend([
        "",
        "## Post-Run Refresh",
        "",
        "`post_run_commands` in `data/model_sweep_execution_commands.csv` records the regeneration chain to run after provider rows are appended. The report must keep scaffold-effect and frontier-performance claims blocked until run-result coverage, transcript integrity, and statistical reporting audits support them.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    command_rows = build_command_rows()
    checklist_rows = build_checklist_rows(command_rows)
    write_csv(ROOT / "data" / "model_sweep_execution_commands.csv", command_rows, COMMAND_FIELDS)
    write_csv(ROOT / "data" / "model_sweep_execution_checklist.csv", checklist_rows, CHECKLIST_FIELDS)
    write_markdown(ROOT / "reports" / "model_sweep_execution_packet.md", command_rows, checklist_rows)
    print(
        "wrote data/model_sweep_execution_commands.csv, "
        "data/model_sweep_execution_checklist.csv, and "
        f"reports/model_sweep_execution_packet.md with {len(command_rows)} command rows"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
