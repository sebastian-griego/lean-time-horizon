from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "gate_id",
    "decision_scope",
    "decision",
    "status",
    "evidence_basis",
    "blocking_or_caution_items",
    "required_next_action",
]


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


def status(reqs: dict[str, dict[str, str]], requirement_id: str) -> str:
    return reqs.get(requirement_id, {}).get("status", "missing")


def evidence(reqs: dict[str, dict[str, str]], requirement_id: str) -> str:
    row = reqs.get(requirement_id, {})
    if not row:
        return f"`{requirement_id}` missing from requirement coverage"
    return f"`{requirement_id}`={row.get('status', '')}: {row.get('evidence', '')}"


def row(
    gate_id: str,
    decision_scope: str,
    decision: str,
    status_value: str,
    evidence_basis: str,
    blocking_or_caution_items: str,
    required_next_action: str,
) -> dict[str, str]:
    return {
        "gate_id": gate_id,
        "decision_scope": decision_scope,
        "decision": decision,
        "status": status_value,
        "evidence_basis": evidence_basis,
        "blocking_or_caution_items": blocking_or_caution_items,
        "required_next_action": required_next_action,
    }


def build_rows() -> list[dict[str, str]]:
    requirements = read_csv(ROOT / "data" / "requirement_coverage.csv")
    claims = read_csv(ROOT / "data" / "claim_evidence_audit.csv")
    task_quality = read_csv(ROOT / "data" / "task_quality_matrix.csv")
    pin_coverage = read_csv(ROOT / "data" / "pin_coverage_audit.csv")
    run_integrity = read_csv(ROOT / "data" / "run_integrity_audit.csv")
    model_summary = read_csv(ROOT / "data" / "model_result_summary.csv")

    reqs = {row_data["requirement_id"]: row_data for row_data in requirements}
    claims_by_id = {row_data["claim_id"]: row_data for row_data in claims}
    accepted_quality = [row_data for row_data in task_quality if row_data.get("release_role") == "accepted_core"]
    accepted_pin = [row_data for row_data in pin_coverage if row_data.get("acceptance_status") == "accepted_v0"]
    integrity_failures = [row_data for row_data in run_integrity if row_data.get("integrity_status") == "fail"]
    caveat_count = sum(1 for row_data in accepted_quality if row_data.get("benchmark_grade_status") == "accepted_core_with_caveat")
    automation_count = sum(1 for row_data in accepted_quality if row_data.get("automation_dominated") == "true")
    hidden_pin_tasks = sum(
        1 for row_data in accepted_pin
        if int(row_data.get("wrongs_failing_hidden_pin_stage", "0") or "0") > 0
    )
    requirement_status_counts = Counter(row_data.get("status", "unknown") for row_data in requirements)
    claim_status_counts = Counter(row_data.get("support_status", "unknown") for row_data in claims)
    locked_gaps = [
        row_data for row_data in requirements
        if row_data.get("freeze_relevance") == "required_for_locked_benchmark"
        and row_data.get("status") != "supported"
    ]
    research_gaps = [
        row_data for row_data in requirements
        if row_data.get("freeze_relevance") == "required_for_research_report"
        and row_data.get("status") != "supported"
    ]
    release_gaps = [
        row_data for row_data in requirements
        if row_data.get("freeze_relevance") == "required_for_release_artifact"
        and row_data.get("status") != "supported"
    ]
    unsupported_claims = [row_data for row_data in claims if row_data.get("support_status") == "unsupported"]
    partial_claims = [row_data for row_data in claims if row_data.get("support_status") == "partial"]
    primary_coverage = next(
        (
            row_data for row_data in model_summary
            if row_data.get("analysis_set") == "primary_plan_coverage"
            and row_data.get("group_by") == "all"
            and row_data.get("group") == "all"
        ),
        {},
    )

    rows: list[dict[str, str]] = []
    rows.append(row(
        "local_release_artifact",
        "artifact_release",
        "OK to treat v0.1 as a locally validated research artifact, not as a locked benchmark.",
        "pass" if not release_gaps and not integrity_failures else "block",
        (
            f"release-artifact gaps={len(release_gaps)}; integrity failures={len(integrity_failures)}; "
            f"requirement statuses={compact_json(dict(sorted(requirement_status_counts.items())))}; "
            f"{evidence(reqs, 'public_export_no_hidden_leak')}; {evidence(reqs, 'run_integrity_audit')}"
        ),
        "Scope is local validation only; hosted QA and independent timing are outside this decision.",
        "Keep artifact claims scoped to local reproducibility and local grading evidence.",
    ))
    rows.append(row(
        "research_report_readiness",
        "reporting",
        "OK to use the report as a research review memo if caveats and unsupported claims stay visible.",
        "pass" if not research_gaps and len(unsupported_claims) >= 2 else "caution",
        (
            f"research-report gaps={len(research_gaps)}; claim statuses={compact_json(dict(sorted(claim_status_counts.items())))}; "
            f"unsupported claims={compact_json([row_data.get('claim_id') for row_data in unsupported_claims])}; "
            f"{evidence(reqs, 'hosted_qa_readiness_audit')}"
        ),
        "The report is evidence-rich but not backed by broad model sweeps or independent timing.",
        "Update the decision log whenever a requirement, claim audit, or provider sweep changes.",
    ))
    rows.append(row(
        "accepted_core_stats_scope",
        "task_set",
        "Use accepted_v0 rows for artifact-level task-quality summaries only; do not use them for population-level frontier claims.",
        "caution",
        (
            f"accepted-core rows={len(accepted_quality)}; caveat rows={caveat_count}; automation-dominated rows={automation_count}; "
            f"{evidence(reqs, 'portfolio_accepted_count')}; {evidence(reqs, 'task_quality_matrix')}; "
            f"{evidence(reqs, 'diagnostic_coverage_audit')}"
        ),
        "The core is intentionally small and several rows retain caveats.",
        "Add independently reviewed T2/T3/T4 rows before treating accepted-core aggregates as benchmark estimates.",
    ))
    rows.append(row(
        "hidden_pin_confidence",
        "grading",
        "Treat hidden pins as meaningful anti-gaming probes but not exhaustive semantic equivalence checks.",
        "caution" if hidden_pin_tasks < len(accepted_quality) else "pass",
        (
            f"accepted tasks with wrong submissions reaching hidden pins={hidden_pin_tasks}/{len(accepted_quality)}; "
            f"{evidence(reqs, 'pin_coverage_audit')}; claim={claims_by_id.get('hidden_pin_strength', {}).get('support_status', 'missing')}"
        ),
        "Some fixed-statement rows fail wrong submissions before hidden pins run; finite pins cannot cover every weakening.",
        "Add same-signature hidden-pin failures where realistic and expand negative examples for retained caveat rows.",
    ))
    rows.append(row(
        "time_horizon_claim",
        "construct_validity",
        "Do not claim strong time-horizon measurement yet.",
        "block",
        f"{evidence(reqs, 'time_horizon_spread')}; claim={claims_by_id.get('time_horizon_measurement', {}).get('support_status', 'missing')}",
        "Accepted core has no T4 task and only one T3 task; human times are not independently measured.",
        "Add independently timed T3/T4 tasks, including at least one T4 row, before claiming robust time-horizon coverage.",
    ))
    rows.append(row(
        "scaffold_effect_claim",
        "performance",
        "Do not report scaffold-effect conclusions from committed data.",
        "block",
        (
            f"{evidence(reqs, 'scaffold_result_comparison')}; primary plan coverage={compact_json(primary_coverage)}; "
            f"{evidence(reqs, 'provider_readiness_audit')}; "
            f"claim={claims_by_id.get('scaffold_effects', {}).get('support_status', 'missing')}"
        ),
        "The scaffold ladder exists, but accepted-core provider data cover only one non-infra one-shot cell.",
        "Run the planned accepted_v0 x scaffold sweep with fixed k before comparing scaffold effects.",
    ))
    rows.append(row(
        "frontier_performance_claim",
        "performance",
        "Do not use committed provider rows to characterize frontier-model capability.",
        "block",
        f"{evidence(reqs, 'frontier_model_evidence')}; {evidence(reqs, 'provider_readiness_audit')}; claim={claims_by_id.get('frontier_performance', {}).get('support_status', 'missing')}",
        "Provider rows are smoke evidence only and include an infra failure.",
        "Run documented provider sweeps after local and hosted QA are stable.",
    ))
    rows.append(row(
        "locked_benchmark_freeze",
        "benchmark_status",
        "Do not call v0.1 a locked benchmark.",
        "block",
        (
            f"locked-benchmark gaps={len(locked_gaps)}: {compact_json([row_data.get('requirement_id') for row_data in locked_gaps])}; "
            f"claim={claims_by_id.get('locked_benchmark', {}).get('support_status', 'missing')}; "
            f"{evidence(reqs, 'hosted_qa_readiness_audit')}"
        ),
        "The accepted count, time-horizon spread, scaffold data, frontier data, independent timing, and hosted QA are not complete.",
        "Reach the 20-50 accepted-task target, complete hosted QA, independent timing, and scaffold sweeps, then freeze exact task versions.",
    ))
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row_data["status"] for row_data in rows)
    lines = [
        "# Release Decision Log",
        "",
        "This generated log translates the requirement and claim audits into explicit gate decisions. It is intentionally conservative: a `pass` gate is a narrow local-artifact decision, while `caution` and `block` gates identify claims that should not be made from the current evidence.",
        "",
        "## Summary",
        "",
        f"- gates: `{len(rows)}`",
        f"- gate statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        "",
        "## Gate Table",
        "",
        "| gate | scope | status | decision | evidence | blockers or cautions | next action |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row_data in rows:
        lines.append(
            f"| `{row_data['gate_id']}` | {row_data['decision_scope']} | {row_data['status']} | "
            f"{escaped(row_data['decision'])} | {escaped(row_data['evidence_basis'])} | "
            f"{escaped(row_data['blocking_or_caution_items'])} | {escaped(row_data['required_next_action'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`pass` means the current local evidence supports the narrow decision in that row. `caution` means the artifact can be used for review with the stated caveat. `block` means the report must not make the corresponding stronger claim.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "release_decision_log.csv", rows)
    write_markdown(ROOT / "reports" / "release_decision_log.md", rows)
    print(f"wrote data/release_decision_log.csv and reports/release_decision_log.md with {len(rows)} gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
