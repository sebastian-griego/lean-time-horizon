from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "gate_id",
    "category",
    "roadmap_status",
    "current_state",
    "evidence",
    "exit_criteria",
    "concrete_next_action",
    "blocks_claims",
    "source_artifacts",
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


def row(
    gate_id: str,
    category: str,
    roadmap_status: str,
    current_state: str,
    evidence: str,
    exit_criteria: str,
    concrete_next_action: str,
    blocks_claims: list[str],
    source_artifacts: list[str],
) -> dict[str, str]:
    return {
        "gate_id": gate_id,
        "category": category,
        "roadmap_status": roadmap_status,
        "current_state": current_state,
        "evidence": evidence,
        "exit_criteria": exit_criteria,
        "concrete_next_action": concrete_next_action,
        "blocks_claims": ";".join(blocks_claims),
        "source_artifacts": ";".join(source_artifacts),
    }


def requirement(reqs: dict[str, dict[str, str]], requirement_id: str) -> str:
    data = reqs.get(requirement_id, {})
    if not data:
        return f"`{requirement_id}` missing from requirement coverage."
    return f"`{requirement_id}`={data.get('status', 'unknown')}: {data.get('evidence', '')}"


def claim(claims: dict[str, dict[str, str]], claim_id: str) -> str:
    data = claims.get(claim_id, {})
    if not data:
        return f"`{claim_id}` missing from claim evidence."
    return f"`{claim_id}`={data.get('support_status', 'unknown')}: {data.get('counterevidence_or_limits', '')}"


def build_rows() -> list[dict[str, str]]:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    requirements = {
        row_data["requirement_id"]: row_data
        for row_data in read_csv(ROOT / "data" / "requirement_coverage.csv")
    }
    claims = {
        row_data["claim_id"]: row_data
        for row_data in read_csv(ROOT / "data" / "claim_evidence_audit.csv")
    }
    claim_authorization = read_csv(ROOT / "data" / "claim_authorization_matrix.csv")
    research_claim_gap = read_csv(ROOT / "data" / "research_claim_gap_matrix.csv")
    report_claim_conformance = read_csv(ROOT / "data" / "report_claim_conformance_audit.csv")
    report_shape = read_csv(ROOT / "data" / "report_shape_audit.csv")
    run_results = read_csv(ROOT / "data" / "run_results.csv")
    model_summary = read_csv(ROOT / "data" / "model_result_summary.csv")
    model_sweep_plan = read_csv(ROOT / "data" / "model_sweep_plan.csv")
    human_observations = read_csv(ROOT / "data" / "human_time_observations.csv")
    hosted = read_csv(ROOT / "data" / "hosted_qa_readiness_audit.csv")
    statistical_design = read_csv(ROOT / "data" / "statistical_design_thresholds.csv")
    statistical = read_csv(ROOT / "data" / "statistical_reporting_audit.csv")
    figure_manifest = read_csv(ROOT / "data" / "figure_manifest.csv")
    release_decisions = read_csv(ROOT / "data" / "release_decision_log.csv")

    accepted = [row_data for row_data in metadata if row_data.get("acceptance_status") == "accepted_v0"]
    calibration = [row_data for row_data in metadata if row_data.get("acceptance_status") == "calibration_only"]
    rejected = [row_data for row_data in metadata if row_data.get("acceptance_status", "").startswith("rejected_")]
    accepted_buckets = Counter(row_data.get("human_time_bucket", "unknown") for row_data in accepted)
    release_buckets = Counter(row_data.get("human_time_bucket", "unknown") for row_data in accepted + calibration)
    accepted_families = Counter(row_data.get("family", "unknown") for row_data in accepted)
    provider_rows = [row_data for row_data in run_results if row_data.get("qa_stage") != "local_qa"]
    noninfra_provider_rows = [
        row_data for row_data in provider_rows
        if row_data.get("infra_fail_count") in {"", "0", 0}
    ]
    primary_coverage = next(
        (
            row_data for row_data in model_summary
            if row_data.get("analysis_set") == "primary_plan_coverage"
            and row_data.get("group_by") == "all"
            and row_data.get("group") == "all"
        ),
        {},
    )
    hosted_blocks = [row_data for row_data in hosted if row_data.get("status") == "block"]
    statistical_plan_blocks = [
        row_data for row_data in statistical_design
        if row_data.get("current_status") == "blocked"
    ]
    statistical_blocks = [row_data for row_data in statistical if row_data.get("status") == "block"]
    figure_blocks = [
        row_data for row_data in figure_manifest
        if row_data.get("category") == "blocked_performance"
    ]
    release_blocks = [row_data for row_data in release_decisions if row_data.get("status") == "block"]
    blocked_authorizations = [
        row_data for row_data in claim_authorization
        if row_data.get("authorization_status") == "blocked"
    ]
    authorization_status_counts = Counter(
        row_data.get("authorization_status", "unknown")
        for row_data in claim_authorization
    )
    conformance_failures = [
        row_data for row_data in report_claim_conformance
        if row_data.get("status") == "fail"
    ]
    conformance_cautions = [
        row_data for row_data in report_claim_conformance
        if row_data.get("status") == "caution"
    ]
    shape_needs_attention = [
        row_data for row_data in report_shape
        if row_data.get("answer_status") == "needs_attention"
    ]
    shape_blocked_by_evidence = [
        row_data for row_data in report_shape
        if row_data.get("answer_status") == "blocked_by_evidence"
    ]
    high_gap_rows = [
        row_data for row_data in research_claim_gap
        if row_data.get("upgrade_priority") in {"high", "highest"}
        or row_data.get("authorization_status") == "blocked"
    ]
    unsupported_claims = [
        row_data.get("claim_id", "")
        for row_data in claims.values()
        if row_data.get("support_status") == "unsupported"
    ]

    rows: list[dict[str, str]] = []
    rows.append(row(
        "local_artifact_validation",
        "local_release",
        "ready",
        "Local validation, public export, run-integrity, grader-hardening, and claim-evidence artifacts are present.",
        "; ".join([
            requirement(requirements, "public_export_no_hidden_leak"),
            requirement(requirements, "run_integrity_audit"),
            requirement(requirements, "grader_hardening_audit"),
        ]),
        "Keep zero failing local validation, public-export, run-integrity, and grader-hardening rows immediately before any release tag.",
        "Rerun the README validation gate after every task, grader, or report change.",
        ["local_release_artifact"],
        [
            "reports/validation_manifest.json",
            "reports/run_integrity_audit.md",
            "reports/grader_hardening_audit.md",
        ],
    ))
    rows.append(row(
        "accepted_portfolio_scale",
        "task_portfolio",
        "block",
        f"{len(accepted)} accepted_v0 tasks, {len(calibration)} calibration-only tasks, {len(rejected)} rejected archive tasks.",
        requirement(requirements, "portfolio_accepted_count"),
        "Reach 20-50 accepted_v0 tasks after hard review, with candidate/rejected rows retained for pruning evidence.",
        "Author a small batch of high-quality T2/T3/T4 candidates, then apply the existing hard review before accepting any row.",
        ["locked_benchmark", "frontier_performance"],
        ["data/task_metadata.csv", "reports/accepted_task_review.md", "reports/task_quality_matrix.md"],
    ))
    rows.append(row(
        "time_horizon_depth",
        "task_portfolio",
        "block",
        f"accepted buckets={compact_json(dict(sorted(accepted_buckets.items())))}; release buckets={compact_json(dict(sorted(release_buckets.items())))}.",
        requirement(requirements, "time_horizon_spread"),
        "Accepted core should include a meaningful T2/T3/T4 spread, including at least one independently reviewed T4 stretch task.",
        "Design one T4 candidate and several T3 candidates only after the current v0.1 core remains stable under review.",
        ["time_horizon_measurement", "locked_benchmark"],
        ["data/task_metadata.csv", "reports/human_time_calibration_audit.md"],
    ))
    rows.append(row(
        "family_balance_and_diagnostics",
        "task_portfolio",
        "caution",
        f"accepted families={compact_json(dict(sorted(accepted_families.items())))}.",
        requirement(requirements, "diagnostic_coverage_audit"),
        "Maintain family coverage while expanding; do not let direct theorem proving or simple list tasks dominate accepted rows.",
        "For each new accepted task, record the intended diagnostic failure mode and reject rows that are automation-dominated.",
        ["accepted_core_reviewed", "locked_benchmark"],
        ["reports/diagnostic_coverage_audit.md", "reports/difficulty_audit.md"],
    ))
    rows.append(row(
        "independent_human_timing",
        "calibration",
        "block",
        f"human observation rows={len(human_observations)}; accepted tasks={len(accepted)}.",
        f"{requirement(requirements, 'independent_human_time_review')}; {requirement(requirements, 'human_timing_collection_packet')}",
        "Every accepted task should have at least one independent Lean-human solve or second-review timing note; T3/T4 rows should get extra scrutiny.",
        "Run timed solves with non-authors and append rows to data/human_time_observations.csv before freeze.",
        ["time_horizon_measurement", "locked_benchmark"],
        [
            "data/human_time_observations.csv",
            "data/human_timing_collection_plan.csv",
            "reports/human_time_calibration_audit.md",
            "reports/human_timing_collection_packet.md",
        ],
    ))
    rows.append(row(
        "scaffold_sweep_coverage",
        "model_sweeps",
        "block",
        (
            f"planned cells={len(model_sweep_plan)}; covered_noninfra="
            f"{primary_coverage.get('covered_cells_noninfra', '0')}; observed non-infra provider rows={len(noninfra_provider_rows)}."
        ),
        f"{requirement(requirements, 'scaffold_result_comparison')}; {requirement(requirements, 'model_sweep_execution_packet')}",
        "Accepted_v0 x {one-shot, lookup, lookup_unlimited} cells should have non-infra pass@k rows for each reported model.",
        "Run the planned sweep commands from reports/evaluation_protocol.md with fixed k and committed transcripts.",
        ["scaffold_effects", "frontier_performance", "locked_benchmark"],
        [
            "data/model_sweep_plan.csv",
            "data/model_sweep_execution_commands.csv",
            "data/run_results.csv",
            "reports/model_run_analysis.md",
            "reports/model_sweep_execution_packet.md",
        ],
    ))
    rows.append(row(
        "frontier_and_open_model_evidence",
        "model_sweeps",
        "block",
        f"provider rows={len(provider_rows)}; non-infra provider rows={len(noninfra_provider_rows)}; unsupported claims={compact_json(unsupported_claims)}.",
        f"{requirement(requirements, 'frontier_model_evidence')}; {requirement(requirements, 'model_sweep_execution_packet')}; {requirement(requirements, 'model_evidence_provenance_audit')}; {requirement(requirements, 'transcript_review_packet')}; {requirement(requirements, 'failure_label_review_audit')}",
        "Commit documented provider/model-version rows across the accepted scaffold plan before any frontier or open-model capability claim.",
        "After hosted/local QA are stable, run provider adapters for the selected frontier/open models and retain transcripts plus infra notes.",
        ["frontier_performance", "scaffold_effects", "locked_benchmark"],
        [
            "data/run_results.csv",
            "data/model_sweep_execution_commands.csv",
            "reports/provider_readiness_audit.md",
            "reports/model_evidence_provenance_audit.md",
            "reports/model_run_analysis.md",
            "reports/model_sweep_execution_packet.md",
            "reports/transcript_review_packet.md",
            "reports/failure_label_review_audit.md",
        ],
    ))
    rows.append(row(
        "hosted_qa_and_env_linter",
        "hosted_qa",
        "block",
        f"hosted readiness blocks={len(hosted_blocks)}.",
        requirement(requirements, "hosted_qa_env_linter"),
        "Taiga/hosted package, problem metadata, Full Env QA, Env Linter, and finding dispositions must be committed for exact problem versions.",
        "Create hosted packaging artifacts, upload exact public versions, run hosted QA, and commit finding dispositions.",
        ["locked_benchmark"],
        ["reports/hosted_qa_readiness_audit.md"],
    ))
    rows.append(row(
        "statistical_reporting_readiness",
        "analysis",
        "block",
        f"statistical plan blocked tiers={len(statistical_plan_blocks)}; statistical audit blocks={len(statistical_blocks)}; figure-manifest blocked performance plots={len(figure_blocks)}.",
        f"{requirement(requirements, 'statistical_analysis_plan')}; {requirement(requirements, 'statistical_reporting_audit')}; {requirement(requirements, 'figure_manifest_audit')}; {requirement(requirements, 'transcript_review_packet')}; {requirement(requirements, 'failure_label_review_audit')}",
        "Recommended performance plots should have adequate task/scaffold coverage and report raw n plus Wilson intervals.",
        "Keep performance plots blocked until the planned accepted-core sweep and larger accepted set exist.",
        ["scaffold_effects", "frontier_performance", "locked_benchmark"],
        [
            "reports/statistical_analysis_plan.md",
            "reports/statistical_reporting_audit.md",
            "reports/figure_manifest.md",
            "reports/model_run_analysis.md",
            "reports/transcript_review_packet.md",
            "reports/failure_label_review_audit.md",
        ],
    ))
    rows.append(row(
        "freeze_versioning",
        "release_management",
        "block",
        f"release-decision block gates={len(release_blocks)}; report-shape needs_attention rows={len(shape_needs_attention)}; high-or-blocked claim gaps={len(high_gap_rows)}.",
        "; ".join([
            requirement(requirements, "hosted_qa_env_linter"),
            requirement(requirements, "threats_to_validity_register"),
            requirement(requirements, "claim_authorization_matrix"),
            requirement(requirements, "research_claim_gap_matrix"),
            requirement(requirements, "model_evidence_provenance_audit"),
            requirement(requirements, "report_claim_conformance_audit"),
            requirement(requirements, "report_source_traceability"),
            requirement(requirements, "report_shape_audit"),
            claim(claims, "locked_benchmark"),
        ]),
        "Freeze only after local validation, hosted QA, independent timing, accepted-count, scaffold-sweep, and provider-evidence gates are satisfied.",
        (
            "Tag the exact commit/export hash and hosted problem-version mapping only after all block gates are cleared. "
            f"Current authorization statuses={compact_json(dict(sorted(authorization_status_counts.items())))}; "
            f"claim-conformance failures={len(conformance_failures)}; claim-conformance cautions={len(conformance_cautions)}; "
            f"report-shape blocked_by_evidence={len(shape_blocked_by_evidence)}; "
            f"blocked authorizations={compact_json([row_data.get('claim_id') for row_data in blocked_authorizations])}."
        ),
        ["locked_benchmark"],
        [
            "reports/release_decision_log.md",
            "reports/threats_to_validity.md",
            "reports/claim_authorization_matrix.md",
            "reports/research_claim_gap_matrix.md",
            "reports/report_claim_conformance_audit.md",
            "reports/report_source_traceability.md",
            "reports/report_shape_audit.md",
            "reports/validation_manifest.json",
        ],
    ))
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row_data["roadmap_status"] for row_data in rows)
    category_counts = Counter(row_data["category"] for row_data in rows)
    blockers = [row_data for row_data in rows if row_data["roadmap_status"] == "block"]
    cautions = [row_data for row_data in rows if row_data["roadmap_status"] == "caution"]
    lines = [
        "# Freeze Readiness Roadmap",
        "",
        "This generated roadmap converts the requirement, claim, release-decision, hosted-QA, statistical, model-run, and metadata audits into concrete gates for turning the local v0.1 artifact into a locked benchmark. It is a planning artifact, not evidence that the blocked gates have been completed.",
        "",
        "## Summary",
        "",
        f"- gates: `{len(rows)}`",
        f"- roadmap statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- categories: `{compact_json(dict(sorted(category_counts.items())))}`",
        f"- blocking gates before locked benchmark: `{len(blockers)}`",
        f"- caution gates: `{len(cautions)}`",
        "",
        "## Gate Table",
        "",
        "| gate | category | status | current state | exit criteria | next action | blocks claims |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row_data in rows:
        lines.append(
            f"| `{row_data['gate_id']}` | {row_data['category']} | {row_data['roadmap_status']} | "
            f"{escaped(row_data['current_state'])} | {escaped(row_data['exit_criteria'])} | "
            f"{escaped(row_data['concrete_next_action'])} | `{row_data['blocks_claims']}` |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`ready` means the current local artifact supports the gate if it is regenerated immediately before release. `caution` means the gate is acceptable for v0.1 review but should be monitored during expansion. `block` means the stronger claim listed in `blocks_claims` must not be made until the exit criteria are satisfied with committed evidence.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "freeze_readiness_roadmap.csv", rows)
    write_markdown(ROOT / "reports" / "freeze_readiness_roadmap.md", rows)
    print(f"wrote data/freeze_readiness_roadmap.csv and reports/freeze_readiness_roadmap.md with {len(rows)} gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
