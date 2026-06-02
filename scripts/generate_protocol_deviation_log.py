from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "deviation_id",
    "protocol_area",
    "planned_standard",
    "current_state",
    "deviation_status",
    "rationale",
    "claim_impact",
    "current_disposition",
    "required_resolution",
    "source_artifacts",
]

VALID_STATUSES = {
    "open_blocker",
    "intentional_scope_limit",
    "resolved_by_quality_control",
    "resolved_by_claim_control",
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
    deviation_id: str,
    protocol_area: str,
    planned_standard: str,
    current_state: str,
    deviation_status: str,
    rationale: str,
    claim_impact: str,
    current_disposition: str,
    required_resolution: str,
    source_artifacts: list[str],
) -> dict[str, str]:
    if deviation_status not in VALID_STATUSES:
        raise ValueError(f"invalid deviation status for {deviation_id}: {deviation_status}")
    return {
        "deviation_id": deviation_id,
        "protocol_area": protocol_area,
        "planned_standard": planned_standard,
        "current_state": current_state,
        "deviation_status": deviation_status,
        "rationale": rationale,
        "claim_impact": claim_impact,
        "current_disposition": current_disposition,
        "required_resolution": required_resolution,
        "source_artifacts": ";".join(source_artifacts),
    }


def build_rows() -> list[dict[str, str]]:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    model_coverage = read_csv(ROOT / "data" / "model_sweep_coverage_audit.csv")
    run_results = read_csv(ROOT / "data" / "run_results.csv")
    human_observations = read_csv(ROOT / "data" / "human_time_observations.csv")
    independent_reviews = read_csv(ROOT / "data" / "independent_task_reviews.csv")
    hosted = read_csv(ROOT / "data" / "hosted_qa_readiness_audit.csv")
    statistical = read_csv(ROOT / "data" / "statistical_reporting_audit.csv")
    figure_manifest = read_csv(ROOT / "data" / "figure_manifest.csv")
    claim_auth = read_csv(ROOT / "data" / "claim_authorization_matrix.csv")
    evidence_strength = read_csv(ROOT / "data" / "evidence_strength_matrix.csv")
    failure_reviews = read_csv(ROOT / "data" / "failure_label_reviews.csv")
    transcript_queue = read_csv(ROOT / "data" / "transcript_review_queue.csv")

    accepted = [item for item in metadata if item.get("acceptance_status") == "accepted_v0"]
    calibration = [item for item in metadata if item.get("acceptance_status") == "calibration_only"]
    rejected = [item for item in metadata if item.get("acceptance_status", "").startswith("rejected_")]
    pending = [item for item in metadata if item.get("acceptance_status") == "candidate_review_pending"]
    accepted_buckets = Counter(item.get("human_time_bucket", "unknown") for item in accepted)
    accepted_families = Counter(item.get("family", "unknown") for item in accepted)
    coverage_counts = Counter(item.get("coverage_status", "unknown") for item in model_coverage)
    passk_ready = sum(
        1 for item in model_coverage
        if item.get("coverage_status") in {"covered_pass", "covered_fail"}
    )
    nonlocal_rows = [item for item in run_results if item.get("qa_stage") != "local_qa"]
    noninfra = [item for item in nonlocal_rows if item.get("infra_fail_count") in {"", "0", 0}]
    hosted_blocks = [item for item in hosted if item.get("status") == "block"]
    statistical_blocks = [item for item in statistical if item.get("status") == "block"]
    blocked_figures = [item for item in figure_manifest if item.get("current_status") == "blocked_by_evidence"]
    blocked_claims = [item for item in claim_auth if item.get("authorization_status") == "blocked"]
    evidence_grades = Counter(item.get("current_evidence_grade", "unknown") for item in evidence_strength)

    rows = [
        row(
            "accepted_count_shortfall",
            "task_portfolio",
            "The playbook target is 20-50 accepted tasks after QA and filtering.",
            f"accepted={len(accepted)}; calibration={len(calibration)}; rejected={len(rejected)}; pending={len(pending)}",
            "open_blocker",
            "The original pool was treated as candidates and pruned aggressively because many rows were automation-dominated or diagnostically weak.",
            "Blocks locked-benchmark, population-level, and stable subgroup-performance claims.",
            "Report keeps v0.1 as a local research artifact with accepted-count caveats.",
            "Author and hard-review additional T2/T3/T4 candidates until 20-50 accepted rows survive QA.",
            [
                "data/task_metadata.csv",
                "reports/candidate_pruning_audit.md",
                "reports/freeze_readiness_roadmap.md",
            ],
        ),
        row(
            "time_horizon_depth_shortfall",
            "task_portfolio",
            "Accepted tasks should span a meaningful T2/T3/T4 time-horizon ladder.",
            f"accepted_bucket_counts={compact_json(dict(sorted(accepted_buckets.items())))}",
            "open_blocker",
            "The accepted core currently has mostly T2 rows and one T3 row; no T4 stretch row is accepted.",
            "Blocks robust time-horizon scaling claims and weakens bucket-level comparisons.",
            "Report states the current accepted core is a limited T2/T3 slice.",
            "Add independently reviewed T3/T4 tasks, including at least one T4 stretch row, before freeze.",
            [
                "data/task_metadata.csv",
                "reports/human_time_calibration_audit.md",
                "reports/freeze_readiness_roadmap.md",
            ],
        ),
        row(
            "family_singleton_groups",
            "task_portfolio",
            "Family and capability summaries should not rely on singleton accepted groups.",
            f"accepted_family_counts={compact_json(dict(sorted(accepted_families.items())))}",
            "intentional_scope_limit",
            "The six accepted tasks intentionally preserve family diversity, but every family is a singleton.",
            "Blocks stable family-level performance means and capability-level generalization.",
            "Report presents family coverage as composition evidence only.",
            "Expand each reported family or avoid family-level estimates until groups have enough accepted tasks.",
            [
                "data/task_metadata.csv",
                "reports/diagnostic_coverage_audit.md",
                "reports/construct_validity_matrix.md",
            ],
        ),
        row(
            "independent_timing_absent",
            "calibration",
            "Human-time estimates should be independently timed or reviewed separately from model runs.",
            f"human_time_observation_rows={len(human_observations)}",
            "open_blocker",
            "Author/reviewer p50/p90 estimates exist, but no independent timed solves are committed.",
            "Blocks calibrated time-horizon and time-bucket trend claims.",
            "Report marks human-time values as estimates and provides a timing collection packet.",
            "Collect independent Lean-human timing rows for every accepted task.",
            [
                "data/human_time_observations.csv",
                "reports/human_time_calibration_audit.md",
                "reports/human_timing_collection_packet.md",
            ],
        ),
        row(
            "independent_task_review_absent",
            "task_review",
            "Accepted tasks should have non-author task-quality review before benchmark-grade claims.",
            f"independent_task_review_rows={len(independent_reviews)}",
            "open_blocker",
            "The independent review schema and packet are ready, but no real non-author review rows are committed.",
            "Blocks independent task-quality and benchmark-grade accepted-core claims.",
            "Report keeps accepted-core quality as internal review evidence only.",
            "Collect non-author review rows for every accepted_v0 task and rerun review-status audits.",
            [
                "data/independent_task_reviews.csv",
                "reports/independent_task_review_packet.md",
                "reports/independent_review_status_audit.md",
            ],
        ),
        row(
            "scaffold_passk_sweeps_missing",
            "model_sweeps",
            "The planned accepted_v0 x scaffold ladder should have exact-k non-infra rows before scaffold-effect claims.",
            f"planned_cells={len(model_coverage)}; passk_ready={passk_ready}; coverage_statuses={compact_json(dict(sorted(coverage_counts.items())))}",
            "open_blocker",
            "Only a one-shot smoke cell has non-infra provider evidence; lookup and lookup_unlimited cells are unobserved.",
            "Blocks empirical scaffold-effect, lookup-benefit, and iterative-debug claims.",
            "Report includes only the prospective scaffold plan and strict coverage ledger.",
            "Run exact-k provider sweeps across accepted_v0 x one-shot/lookup/lookup_unlimited cells.",
            [
                "data/model_sweep_coverage_audit.csv",
                "reports/evaluation_protocol.md",
                "reports/model_sweep_coverage_audit.md",
            ],
        ),
        row(
            "provider_evidence_smoke_only",
            "model_sweeps",
            "Frontier/open-model claims require documented provider rows across the planned accepted-core sweep.",
            f"nonlocal_rows={len(nonlocal_rows)}; noninfra_rows={len(noninfra)}; evidence_grades={compact_json(dict(sorted(evidence_grades.items())))}",
            "open_blocker",
            "Committed non-local rows are smoke provenance only and include too little coverage for model estimates.",
            "Blocks frontier-performance, model-ranking, and benchmark pass-rate claims.",
            "Report uses provider rows as provenance only and keeps performance claims blocked.",
            "Run documented provider sweeps after local and hosted QA stabilize, preserving transcripts and model versions.",
            [
                "data/run_results.csv",
                "reports/model_run_analysis.md",
                "reports/evidence_strength_matrix.md",
            ],
        ),
        row(
            "failure_distribution_unavailable",
            "failure_analysis",
            "Failure-mode distributions should be based on broad failed provider runs with transcript review.",
            f"transcript_queue_rows={len(transcript_queue)}; failure_review_rows={len(failure_reviews)}",
            "open_blocker",
            "The codebook, queue, and smoke review workflow exist, but broad failed provider rows are absent.",
            "Blocks dominant-failure-mode and distributional taxonomy claims.",
            "Report presents the workflow and smoke adjudications only.",
            "After broad sweeps, complete independent transcript review before reporting failure distributions.",
            [
                "reports/transcript_review_packet.md",
                "reports/failure_label_review_audit.md",
                "data/failure_label_reviews.csv",
            ],
        ),
        row(
            "performance_plots_omitted",
            "statistical_reporting",
            "Recommended performance plots should report raw n and uncertainty only after adequate coverage.",
            f"statistical_block_rows={len(statistical_blocks)}; blocked_figure_rows={len(blocked_figures)}",
            "resolved_by_claim_control",
            "Performance plots are intentionally omitted because planned provider/scaffold coverage is missing.",
            "Prevents accidental publication of unsupported pass@10, scaffold, family, or bucket performance plots.",
            "Figure manifest and statistical-reporting audit block performance plots while allowing descriptive task-count figures.",
            "Regenerate performance plots only after exact-k provider coverage and accepted-task scale meet the statistical thresholds.",
            [
                "reports/statistical_reporting_audit.md",
                "reports/figure_manifest.md",
                "reports/statistical_analysis_plan.md",
            ],
        ),
        row(
            "hosted_qa_not_run",
            "hosted_qa",
            "Final benchmark delivery requires hosted QA, Env Linter, finding dispositions, and exact problem-version mappings.",
            f"hosted_block_rows={len(hosted_blocks)}",
            "open_blocker",
            "Taiga packaging scaffolds and local wrapper-isolation checks exist, but no hosted result rows are committed.",
            "Blocks hosted-QA, locked-benchmark, and final problem-version claims.",
            "Report labels hosted readiness as local preparation only.",
            "Run hosted preflight, Full Env QA, Env Linter, disposition findings, and commit immutable version mappings.",
            [
                "reports/hosted_qa_readiness_audit.md",
                "reports/taiga_wrapper_isolation_audit.md",
                "taiga/problems_metadata.template.json",
            ],
        ),
        row(
            "non_core_rows_retained_but_excluded",
            "task_portfolio",
            "Rejected and calibration rows should not enter accepted-core benchmark statistics.",
            f"calibration={len(calibration)}; rejected={len(rejected)}; blocked_claims={len(blocked_claims)}",
            "resolved_by_quality_control",
            "The repo retains non-core rows for auditability and lower-bound calibration but excludes them from accepted-core claims.",
            "Prevents easy or duplicate tasks from inflating accepted-core quality or performance statistics.",
            "Metadata, candidate-pruning, and report-count audits separate accepted, calibration, and rejected rows.",
            "Maintain status separation whenever tasks are added or downgraded.",
            [
                "data/task_metadata.csv",
                "reports/candidate_pruning_audit.md",
                "reports/report_count_consistency_audit.md",
            ],
        ),
    ]
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    status_counts = Counter(row["deviation_status"] for row in rows)
    area_counts = Counter(row["protocol_area"] for row in rows)
    open_rows = [row for row in rows if row["deviation_status"] == "open_blocker"]
    lines = [
        "# Protocol Deviation Log",
        "",
        "This generated log records where the v0.1 artifact diverges from the intended full benchmark protocol in the playbook and project target. It separates open blockers from intentional scope or claim-control decisions. It is transparency evidence, not evidence that the deviations are resolved.",
        "",
        "## Summary",
        "",
        f"- deviations tracked: `{len(rows)}`",
        f"- deviation statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- protocol areas: `{compact_json(dict(sorted(area_counts.items())))}`",
        f"- open blockers: `{len(open_rows)}`",
        "",
        "## Deviation Table",
        "",
        "| deviation | area | status | planned standard | current state | claim impact | disposition | required resolution |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in rows:
        lines.append(
            f"| `{item['deviation_id']}` | {item['protocol_area']} | {item['deviation_status']} | "
            f"{escaped(item['planned_standard'])} | {escaped(item['current_state'])} | "
            f"{escaped(item['claim_impact'])} | {escaped(item['current_disposition'])} | "
            f"{escaped(item['required_resolution'])} |"
        )
    lines.extend([
        "",
        "## Rationale And Sources",
        "",
        "| deviation | rationale | sources |",
        "| --- | --- | --- |",
    ])
    for item in rows:
        lines.append(
            f"| `{item['deviation_id']}` | {escaped(item['rationale'])} | {escaped(item['source_artifacts'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`open_blocker` rows are unresolved evidence gaps that must stay attached to any report summary. `resolved_by_quality_control` and `resolved_by_claim_control` rows are acceptable v0.1 scope controls: they explain why a deviation from the larger target is reported honestly rather than hidden or counted as a stronger result.",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "protocol_deviation_log.csv", rows)
    write_markdown(ROOT / "reports" / "protocol_deviation_log.md", rows)
    print(
        "wrote data/protocol_deviation_log.csv and reports/protocol_deviation_log.md "
        f"with {len(rows)} deviations"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
