from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "decision_id",
    "analysis_area",
    "decision_type",
    "preregistered_decision",
    "current_evidence_status",
    "evidence",
    "permitted_current_output",
    "blocked_output",
    "upgrade_condition",
    "source_artifacts",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_json(path: Path) -> object:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def row(
    decision_id: str,
    analysis_area: str,
    decision_type: str,
    preregistered_decision: str,
    current_evidence_status: str,
    evidence: str,
    permitted_current_output: str,
    blocked_output: str,
    upgrade_condition: str,
    source_artifacts: list[str],
) -> dict[str, str]:
    return {
        "decision_id": decision_id,
        "analysis_area": analysis_area,
        "decision_type": decision_type,
        "preregistered_decision": preregistered_decision,
        "current_evidence_status": current_evidence_status,
        "evidence": evidence,
        "permitted_current_output": permitted_current_output,
        "blocked_output": blocked_output,
        "upgrade_condition": upgrade_condition,
        "source_artifacts": ";".join(source_artifacts),
    }


def schema_fields(schema: object) -> set[str]:
    if not isinstance(schema, dict):
        return set()
    properties = schema.get("properties", {})
    if isinstance(properties, dict):
        return set(properties)
    return set()


def build_rows() -> list[dict[str, str]]:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    sweep_plan = read_csv(ROOT / "data" / "model_sweep_plan.csv")
    sweep_coverage = read_csv(ROOT / "data" / "model_sweep_coverage_audit.csv")
    model_summary = read_csv(ROOT / "data" / "model_result_summary.csv")
    statistical = read_csv(ROOT / "data" / "statistical_design_thresholds.csv")
    run_results = read_csv(ROOT / "data" / "run_results.csv")
    failure_codebook = read_csv(ROOT / "data" / "failure_labels.csv")
    failure_reviews = read_csv(ROOT / "data" / "failure_label_reviews.csv")
    human_observations = read_csv(ROOT / "data" / "human_time_observations.csv")
    hosted = read_csv(ROOT / "data" / "hosted_qa_readiness_audit.csv")
    run_schema = read_json(ROOT / "data" / "run_results_schema.json")
    failure_schema = read_json(ROOT / "data" / "failure_label_schema.json")

    accepted = [task for task in metadata if task.get("acceptance_status") == "accepted_v0"]
    calibration = [task for task in metadata if task.get("acceptance_status") == "calibration_only"]
    rejected = [task for task in metadata if task.get("acceptance_status", "").startswith("rejected_")]
    accepted_ids = {task.get("task_id", "") for task in accepted}
    plan_task_ids = {item.get("task_id", "") for item in sweep_plan}
    plan_scaffolds = Counter(item.get("scaffold", "") for item in sweep_plan)
    plan_k_values = sorted({item.get("planned_k", "") for item in sweep_plan})
    plan_cells = len(sweep_plan)
    passk_ready = sum(
        1 for item in sweep_coverage
        if item.get("coverage_status") in {"covered_pass", "covered_fail"}
    )
    smoke_only = sum(1 for item in sweep_coverage if item.get("coverage_status") == "smoke_only")
    coverage_counts = Counter(item.get("coverage_status", "unknown") for item in sweep_coverage)
    primary_summary = next(
        (
            item for item in model_summary
            if item.get("analysis_set") == "primary_plan_coverage"
            and item.get("group_by") == "all"
            and item.get("group") == "all"
        ),
        {},
    )
    accepted_summary = next(
        (
            item for item in model_summary
            if item.get("analysis_set") == "accepted_core_results"
            and item.get("group_by") == "all"
            and item.get("group") == "all"
        ),
        {},
    )
    current_tiers = {item.get("tier_id", ""): item for item in statistical}
    supported_tiers = [item.get("tier_id", "") for item in statistical if item.get("current_status") == "supported"]
    blocked_tiers = [item.get("tier_id", "") for item in statistical if item.get("current_status") == "blocked"]
    run_fields = schema_fields(run_schema)
    failure_fields = schema_fields(failure_schema)
    codebook_labels = [item.get("label", "") for item in failure_codebook if item.get("label")]
    nonlocal_rows = [item for item in run_results if item.get("qa_stage") != "local_qa"]
    nonlocal_failures = [
        item for item in nonlocal_rows
        if item.get("failure_label") not in {"", "none"} and item.get("infra_fail_count") in {"", "0", 0}
    ]
    hosted_blocks = [item for item in hosted if item.get("status") == "block"]
    bucket_counts = Counter(task.get("human_time_bucket", "unknown") for task in accepted)
    family_counts = Counter(task.get("family", "unknown") for task in accepted)

    return [
        row(
            "analysis_unit",
            "endpoint",
            "unit_of_analysis",
            "Use one `(task_id, model, model_version, scaffold, k)` row as the task-level analysis unit; local QA rows are validation evidence only.",
            "ready_for_future_rows",
            (
                f"run_schema_fields_present={compact_json(sorted(run_fields & {'task_id', 'model', 'model_version', 'scaffold', 'k', 'qa_stage'}))}; "
                f"run_rows={len(run_results)}; nonlocal_rows={len(nonlocal_rows)}"
            ),
            "State the analysis unit and exclude local QA from model-performance summaries.",
            "Do not aggregate reference/wrong local QA rows into model capability estimates.",
            "Keep run_results schema and integrity audits synchronized with any analysis-unit change.",
            ["data/run_results_schema.json", "data/run_results.csv", "reports/evaluation_protocol.md"],
        ),
        row(
            "primary_endpoint",
            "endpoint",
            "primary_endpoint",
            "`successes_out_of_k` is a count; `pass_at_k` is binary and equals 1 only when at least one completed attempt succeeds.",
            "ready_for_future_rows",
            (
                f"required_fields_present={compact_json(sorted(run_fields & {'successes_out_of_k', 'pass_at_k', 'attempts_completed', 'k'}))}; "
                f"primary_summary={compact_json(primary_summary)}"
            ),
            "Report pass@k arithmetic and keep smoke rows separated from exact-k evidence.",
            "Do not treat successes_out_of_k as pass@k or report k=1 smoke rows as pass@10 evidence.",
            "Maintain pass@k boundary and run-integrity audits after every provider sweep.",
            ["data/run_results_schema.json", "reports/evaluation_protocol.md", "reports/passk_claim_boundary_audit.md"],
        ),
        row(
            "primary_task_set",
            "analysis_set",
            "inclusion_rule",
            "Headline task-performance analyses use `accepted_v0` tasks only; calibration rows are separate and rejected rows are excluded.",
            "ready_with_small_n_caveat",
            (
                f"accepted={len(accepted)}; calibration={len(calibration)}; rejected={len(rejected)}; "
                f"plan_task_ids_match_accepted={plan_task_ids == accepted_ids}"
            ),
            "Use accepted-core rows for local task-quality summaries and report calibration rows separately.",
            "Do not mix calibration or rejected rows into accepted-core pass-rate claims.",
            "Recompute plan rows after any accepted/calibration/rejected metadata status change.",
            ["data/task_metadata.csv", "data/model_sweep_plan.csv", "reports/evaluation_protocol.md"],
        ),
        row(
            "scaffold_ladder",
            "scaffolds",
            "planned_comparison",
            "The primary scaffold ladder is `one-shot`, `lookup`, and `lookup_unlimited`, crossed with every accepted task at fixed k.",
            "planned_not_empirical",
            f"plan_cells={plan_cells}; scaffold_counts={compact_json(dict(sorted(plan_scaffolds.items())))}; plan_k_values={compact_json(plan_k_values)}",
            "Describe the planned scaffold ladder and current coverage status.",
            "Do not claim lookup or iterative-debug effects until every reported scaffold cell is covered for the same task/model set.",
            "Run all accepted_v0 x scaffold cells for each reported model version.",
            ["data/scaffold_variants.csv", "data/model_sweep_plan.csv", "reports/evaluation_protocol.md"],
        ),
        row(
            "exact_k_coverage",
            "coverage",
            "coverage_rule",
            "A primary pass@k cell is reportable only when non-infra rows cover the planned task/scaffold/model at the planned k.",
            "blocked_by_undercoverage",
            (
                f"planned_cells={plan_cells}; passk_ready={passk_ready}; smoke_only={smoke_only}; "
                f"coverage={compact_json(dict(sorted(coverage_counts.items())))}"
            ),
            "Report coverage and blocked-performance status only.",
            "Do not report aggregate accepted-core pass@k estimates or intervals from incomplete planned cells.",
            "Cover all planned accepted-core cells with non-infra rows at the planned k.",
            ["data/model_sweep_coverage_audit.csv", "reports/model_sweep_coverage_audit.md", "reports/passk_claim_boundary_audit.md"],
        ),
        row(
            "infra_timeout_handling",
            "run_accounting",
            "exclusion_and_retention_rule",
            "Retain infra failures and timeouts in raw run data and reliability summaries; exclude infra failures from capability means.",
            "ready_for_future_rows",
            f"accepted_summary={compact_json(accepted_summary)}",
            "Report infra rows as provenance/reliability evidence only.",
            "Do not silently drop infra failures from raw data or count them as solved capability rows.",
            "Keep infra/timeout fields required in run_results and rerun integrity audits after sweeps.",
            ["data/run_results.csv", "data/run_results_schema.json", "reports/model_run_analysis.md"],
        ),
        row(
            "wilson_interval_rule",
            "statistics",
            "interval_rule",
            "For binary task-row means, report Wilson 95% intervals only after the planned cells for the stated analysis set are covered.",
            "blocked_by_undercoverage",
            (
                f"supported_tiers={compact_json(supported_tiers)}; blocked_tiers={compact_json(blocked_tiers)}; "
                f"primary_tier_status={current_tiers.get('v0_1_primary_descriptive_performance', {}).get('current_status', 'missing')}"
            ),
            "Show precision planning and blocked claim tiers.",
            "Do not display performance intervals for the accepted core while planned coverage is missing.",
            "Meet the minimum evidence row for the relevant statistical claim tier.",
            ["data/statistical_design_thresholds.csv", "reports/statistical_analysis_plan.md", "reports/statistical_reporting_audit.md"],
        ),
        row(
            "subgroup_threshold_rule",
            "statistics",
            "subgroup_rule",
            "Family, bucket, and skill summaries with fewer than five accepted tasks per reported group are coverage tables, not stable estimates.",
            "blocked_by_small_groups",
            f"accepted_bucket_counts={compact_json(dict(sorted(bucket_counts.items())))}; accepted_family_counts={compact_json(dict(sorted(family_counts.items())))}",
            "Report family and bucket composition with singleton caveats.",
            "Do not interpret singleton family, skill, or T3 rows as stable subgroup performance estimates.",
            "Reach at least five accepted tasks in every reported subgroup before interpreting subgroup means.",
            ["data/task_metadata.csv", "data/statistical_design_thresholds.csv", "reports/construct_validity_matrix.md"],
        ),
        row(
            "scaffold_delta_rule",
            "scaffolds",
            "paired_comparison_rule",
            "Scaffold deltas must compare the same accepted task set, model version, planned k, and non-infra rows across scaffolds.",
            "blocked_by_undercoverage",
            f"coverage={compact_json(dict(sorted(coverage_counts.items())))}; observed_scaffold_rows={compact_json(dict(sorted(plan_scaffolds.items())))}",
            "State scaffold deltas as planned analyses only.",
            "Do not infer lookup or iterative-debug gains from one-shot-only smoke rows.",
            "Collect complete paired rows for every accepted task under each reported scaffold.",
            ["data/model_sweep_plan.csv", "data/model_sweep_coverage_audit.csv", "reports/evaluation_protocol.md"],
        ),
        row(
            "failure_label_rule",
            "failure_analysis",
            "failure_label_rule",
            "Failure distributions require transcript-reviewed non-infra failures and use the committed failure-label codebook.",
            "workflow_ready_data_blocked",
            (
                f"failure_schema_fields_present={compact_json(sorted(failure_fields & {'primary_label', 'rationale', 'transcript_link'}))}; "
                f"codebook_label_count={len(codebook_labels)}; "
                f"noninfra_failure_rows={len(nonlocal_failures)}; failure_review_rows={len(failure_reviews)}"
            ),
            "Report the transcript-review workflow and smoke labels as provenance only.",
            "Do not claim dominant failure modes from single-review smoke rows or unreviewed transcripts.",
            "Collect enough non-infra failed provider rows and independent review labels before reporting distributions.",
            ["data/failure_label_schema.json", "data/failure_labels.csv", "data/failure_label_reviews.csv", "reports/failure_label_review_audit.md"],
        ),
        row(
            "human_time_rule",
            "calibration",
            "calibration_rule",
            "Human-time trends require independent Lean-human timing; never infer human time from model pass rates.",
            "blocked_by_missing_timing",
            f"human_time_observation_rows={len(human_observations)}; accepted_tasks={len(accepted)}",
            "Report author/reviewer p50/p90 estimates and missing independent timing as a limitation.",
            "Do not claim calibrated time-horizon scaling from metadata estimates alone.",
            "Collect independent timing observations for every accepted task before freeze.",
            ["data/human_time_observations.csv", "reports/human_time_calibration_audit.md", "reports/human_timing_collection_packet.md"],
        ),
        row(
            "hosted_freeze_rule",
            "operational_validity",
            "freeze_rule",
            "Locked-benchmark claims require hosted QA, Env Linter disposition, exact problem-version mapping, and final source/export hashes.",
            "blocked_by_hosted_qa",
            f"hosted_block_rows={len(hosted_blocks)}",
            "State local readiness and hosted-QA blockers.",
            "Do not call the artifact hosted-QA-cleared, frozen, or locked.",
            "Run hosted Full Env QA/Env Linter and commit exact version evidence before freeze.",
            ["data/hosted_qa_readiness_audit.csv", "reports/hosted_qa_readiness_audit.md", "reports/freeze_readiness_roadmap.md"],
        ),
    ]


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    status_counts = Counter(item["current_evidence_status"] for item in rows)
    area_counts = Counter(item["analysis_area"] for item in rows)
    lines = [
        "# Analysis Decision Register",
        "",
        "This generated register makes the v0.1 analysis plan auditable before broad provider sweeps. It fixes inclusion rules, endpoints, coverage thresholds, subgroup rules, failure-label requirements, human-time requirements, and freeze boundaries from committed artifacts. It does not create model results.",
        "",
        "## Summary",
        "",
        f"- decisions: `{len(rows)}`",
        f"- evidence statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- analysis areas: `{compact_json(dict(sorted(area_counts.items())))}`",
        "",
        "## Decision Table",
        "",
        "| decision | area | type | evidence status | preregistered decision | permitted now | blocked output | upgrade condition |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in rows:
        lines.append(
            f"| `{item['decision_id']}` | {item['analysis_area']} | {item['decision_type']} | {item['current_evidence_status']} | "
            f"{escaped(item['preregistered_decision'])} | {escaped(item['permitted_current_output'])} | "
            f"{escaped(item['blocked_output'])} | {escaped(item['upgrade_condition'])} |"
        )
    lines.extend([
        "",
        "## Evidence Detail",
        "",
        "| decision | evidence | sources |",
        "| --- | --- | --- |",
    ])
    for item in rows:
        lines.append(
            f"| `{item['decision_id']}` | {escaped(item['evidence'])} | {escaped(item['source_artifacts'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`ready_for_future_rows` and `ready_with_small_n_caveat` rows define analysis rules that can be applied once data arrive. `blocked_*` rows are explicit evidence limits: they prevent the report from turning smoke rows, singleton groups, missing timing, or missing hosted QA into stronger claims.",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "analysis_decision_register.csv", rows)
    write_markdown(ROOT / "reports" / "analysis_decision_register.md", rows)
    print(
        "wrote data/analysis_decision_register.csv and reports/analysis_decision_register.md "
        f"with {len(rows)} decisions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
