from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "threat_id",
    "category",
    "severity",
    "current_status",
    "evidence",
    "mitigation_in_repo",
    "stronger_evidence_needed",
    "claims_limited",
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


def int_value(row: dict[str, str], key: str, default: int = 0) -> int:
    try:
        return int(row.get(key, "") or default)
    except ValueError:
        return default


def row(
    threat_id: str,
    category: str,
    severity: str,
    current_status: str,
    evidence: str,
    mitigation_in_repo: str,
    stronger_evidence_needed: str,
    claims_limited: list[str],
    source_artifacts: list[str],
) -> dict[str, str]:
    return {
        "threat_id": threat_id,
        "category": category,
        "severity": severity,
        "current_status": current_status,
        "evidence": evidence,
        "mitigation_in_repo": mitigation_in_repo,
        "stronger_evidence_needed": stronger_evidence_needed,
        "claims_limited": ";".join(claims_limited),
        "source_artifacts": ";".join(source_artifacts),
    }


def primary_model_coverage(model_summary: list[dict[str, str]]) -> dict[str, str]:
    return next(
        (
            row_data
            for row_data in model_summary
            if row_data.get("analysis_set") == "primary_plan_coverage"
            and row_data.get("group_by") == "all"
            and row_data.get("group") == "all"
        ),
        {},
    )


def build_rows() -> list[dict[str, str]]:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    difficulty = read_csv(ROOT / "data" / "difficulty_audit.csv")
    diagnostic = read_csv(ROOT / "data" / "diagnostic_coverage_audit.csv")
    human_time = read_csv(ROOT / "data" / "human_time_calibration_audit.csv")
    human_observations = read_csv(ROOT / "data" / "human_time_observations.csv")
    transcript_review_queue = read_csv(ROOT / "data" / "transcript_review_queue.csv")
    failure_label_reviews = read_csv(ROOT / "data" / "failure_label_reviews.csv")
    failure_label_review_audit = read_csv(ROOT / "data" / "failure_label_review_audit.csv")
    pin_coverage = read_csv(ROOT / "data" / "pin_coverage_audit.csv")
    model_summary = read_csv(ROOT / "data" / "model_result_summary.csv")
    statistical = read_csv(ROOT / "data" / "statistical_reporting_audit.csv")
    provider = read_csv(ROOT / "data" / "provider_readiness_audit.csv")
    hosted = read_csv(ROOT / "data" / "hosted_qa_readiness_audit.csv")
    command_rows = read_csv(ROOT / "data" / "model_sweep_execution_commands.csv")

    accepted = [task for task in metadata if task.get("acceptance_status") == "accepted_v0"]
    calibration = [task for task in metadata if task.get("acceptance_status") == "calibration_only"]
    rejected = [task for task in metadata if task.get("acceptance_status", "").startswith("rejected_")]
    accepted_ids = {task.get("task_id", "") for task in accepted}
    accepted_buckets = Counter(task.get("human_time_bucket", "unknown") for task in accepted)
    accepted_families = Counter(task.get("family", "unknown") for task in accepted)
    accepted_difficulty = [row_data for row_data in difficulty if row_data.get("acceptance_status") == "accepted_v0"]
    automation_dominated = [
        row_data for row_data in accepted_difficulty
        if row_data.get("mechanical_automation_dominated") == "true"
    ]
    accepted_pin = [row_data for row_data in pin_coverage if row_data.get("acceptance_status") == "accepted_v0"]
    hidden_pin_reach = [
        row_data for row_data in accepted_pin
        if int_value(row_data, "wrongs_failing_hidden_pin_stage") > 0
    ]
    proof_only_pin = [
        row_data for row_data in accepted_pin
        if row_data.get("same_signature_hidden_wrong_feasibility")
        == "structurally_infeasible_for_same_signature_proof_wrongs"
    ]
    independent_timed = {
        row_data.get("task_id")
        for row_data in human_time
        if row_data.get("acceptance_status") == "accepted_v0"
        and int_value(row_data, "successful_independent_observation_count") > 0
    }
    diagnostic_blocks = [row_data for row_data in diagnostic if row_data.get("status") == "block"]
    diagnostic_cautions = [row_data for row_data in diagnostic if row_data.get("status") == "caution"]
    primary = primary_model_coverage(model_summary)
    planned_cells = int_value(primary, "planned_cells")
    covered_noninfra = int_value(primary, "covered_cells_noninfra")
    accepted_provider = next(
        (
            row_data
            for row_data in model_summary
            if row_data.get("analysis_set") == "accepted_core_results"
            and row_data.get("group_by") == "all"
            and row_data.get("group") == "all"
        ),
        {},
    )
    accepted_provider_rows = int_value(accepted_provider, "rows_noninfra")
    transcript_high_priority = [
        row_data for row_data in transcript_review_queue
        if row_data.get("review_priority") in {"critical", "high"}
    ]
    failure_review_failures = [
        row_data for row_data in failure_label_review_audit
        if row_data.get("status") == "fail"
    ]
    statistical_blocks = [row_data for row_data in statistical if row_data.get("status") == "block"]
    hosted_blocks = [row_data for row_data in hosted if row_data.get("status") == "block"]
    provider_failures = [row_data for row_data in provider if row_data.get("status") == "fail"]
    command_key_leaks = [
        row_data for row_data in command_rows
        if "API_KEY=" in row_data.get("full_sweep_command", "")
        or "API_KEY=" in row_data.get("smoke_command", "")
    ]
    public_export_hidden_paths = [
        path for path in (ROOT / "public_tasks").rglob("*")
        if path.is_file() and ("hidden" in path.parts or "wrong" in path.parts)
    ] if (ROOT / "public_tasks").exists() else []

    rows = [
        row(
            "construct_time_horizon_depth",
            "construct_validity",
            "high",
            "block" if accepted_buckets.get("T4", 0) == 0 or accepted_buckets.get("T3", 0) < 2 else "caution",
            (
                f"accepted={len(accepted)}; accepted buckets={compact_json(dict(sorted(accepted_buckets.items())))}; "
                f"diagnostic blocks={len(diagnostic_blocks)}; diagnostic cautions={len(diagnostic_cautions)}"
            ),
            "The report and freeze roadmap explicitly block strong time-horizon claims.",
            "Add independently reviewed and timed T3/T4 tasks, including at least one T4 stretch row.",
            ["time_horizon_measurement", "locked_benchmark"],
            ["data/task_metadata.csv", "data/diagnostic_coverage_audit.csv", "reports/freeze_readiness_roadmap.md"],
        ),
        row(
            "portfolio_scale_and_balance",
            "external_validity",
            "high",
            "block" if len(accepted) < 20 else "caution",
            (
                f"accepted={len(accepted)}; calibration_only={len(calibration)}; rejected={len(rejected)}; "
                f"accepted families={compact_json(dict(sorted(accepted_families.items())))}"
            ),
            "Accepted, calibration, and rejected rows are separated so small-core claims are visible.",
            "Reach the 20-50 accepted-task target while preserving family and capability diversity.",
            ["frontier_performance", "locked_benchmark", "family_level_performance"],
            ["data/task_metadata.csv", "reports/task_quality_matrix.md", "reports/accepted_task_review.md"],
        ),
        row(
            "author_estimated_human_time",
            "internal_validity",
            "high",
            "block" if len(independent_timed) < len(accepted_ids) else "controlled",
            (
                f"accepted timed solves={len(independent_timed)}/{len(accepted_ids)}; "
                f"human_time_observation_rows={len(human_observations)}"
            ),
            "Human-time calibration audit and timing collection packet make missing observations explicit.",
            "Collect independent Lean-human timed solves or second-review timing notes for every accepted task.",
            ["time_horizon_measurement", "locked_benchmark"],
            ["data/human_time_calibration_audit.csv", "data/human_timing_collection_plan.csv"],
        ),
        row(
            "automation_dominated_retained_tasks",
            "construct_validity",
            "medium",
            "caution" if automation_dominated else "controlled",
            f"automation-dominated accepted tasks={len(automation_dominated)}: {compact_json([r.get('task_id') for r in automation_dominated])}",
            "Automation-dominated accepted rows are marked with caveats and excluded from claims of standalone proof-depth difficulty.",
            "Replace or independently validate retained caveat rows before locked benchmark status.",
            ["accepted_core_reviewed", "time_horizon_measurement"],
            ["data/difficulty_audit.csv", "reports/accepted_task_review.md"],
        ),
        row(
            "semantic_pin_finiteness",
            "internal_validity",
            "medium",
            "caution",
            (
                f"accepted tasks with hidden-pin wrong failures={len(hidden_pin_reach)}/{len(accepted_pin)}; "
                f"proof-only fixed-statement rows={len(proof_only_pin)}"
            ),
            "Pin coverage audit distinguishes semantic hidden-pin failures from public-stage and fixed-statement proof checks.",
            "Have an independent reviewer inspect hidden pins and add richer same-signature hidden wrongs for future mutable tasks.",
            ["hidden_pin_strength", "grading_validity"],
            ["data/pin_coverage_audit.csv", "reports/pin_coverage_audit.md"],
        ),
        row(
            "scaffold_sweep_undercoverage",
            "statistical_validity",
            "high",
            "block" if planned_cells == 0 or covered_noninfra < planned_cells else "controlled",
            f"planned accepted-core cells={planned_cells}; covered non-infra cells={covered_noninfra}",
            "Evaluation protocol and model-sweep execution packet define the missing sweep before broad model runs.",
            "Run accepted_v0 x one-shot/lookup/lookup_unlimited rows with fixed k and committed transcripts.",
            ["scaffold_effects", "frontier_performance"],
            ["data/model_sweep_plan.csv", "data/model_sweep_execution_commands.csv", "data/model_result_summary.csv"],
        ),
        row(
            "frontier_performance_undercoverage",
            "external_validity",
            "high",
            "block" if accepted_provider_rows < max(1, len(accepted)) else "caution",
            f"accepted-core non-infra provider rows={accepted_provider_rows}; accepted tasks={len(accepted)}",
            "Committed smoke rows are separated from local QA and kept out of population-level performance claims.",
            "Run documented frontier/open-model sweeps across the accepted scaffold plan with model versions and transcripts.",
            ["frontier_performance", "locked_benchmark"],
            ["data/run_results.csv", "data/model_result_summary.csv", "reports/model_run_analysis.md"],
        ),
        row(
            "statistical_power_and_plots",
            "statistical_validity",
            "high",
            "block" if statistical_blocks else "controlled",
            f"statistical audit rows={len(statistical)}; blocked outputs={len(statistical_blocks)}",
            "Statistical reporting audit blocks unsupported pass-rate plots and requires raw n plus Wilson intervals.",
            "Populate the planned sweep and accepted task count before generating scaffold, family, and bucket performance plots.",
            ["scaffold_effects", "frontier_performance", "family_level_performance"],
            ["data/statistical_reporting_audit.csv", "reports/statistical_reporting_audit.md"],
        ),
        row(
            "failure_taxonomy_forecast",
            "internal_validity",
            "medium",
            "caution" if accepted_provider_rows < len(accepted) else "controlled",
            (
                f"accepted-core non-infra provider rows={accepted_provider_rows}; "
                f"transcript review queue rows={len(transcript_review_queue)}; "
                f"single-review rows={len(failure_label_reviews)}; "
                f"review-audit failures={len(failure_review_failures)}; "
                f"high/critical queue rows={len(transcript_high_priority)}"
            ),
            "Failure labels, transcript workflow, a blank review template, and single-review smoke adjudications exist, but distributions are not interpreted until broad provider rows are independently reviewed.",
            "Label real model transcripts after the scaffold sweep, use independent adjudication for disagreements, and compare observed failures to intended diagnostic modes.",
            ["diagnostic_failure_distribution", "scaffold_effects"],
            [
                "data/failure_labels.csv",
                "data/run_results.csv",
                "data/transcript_review_queue.csv",
                "data/failure_label_reviews.csv",
                "reports/transcript_review_packet.md",
                "reports/failure_label_review_audit.md",
            ],
        ),
        row(
            "hosted_environment_gap",
            "operational_validity",
            "high",
            "block" if hosted_blocks else "controlled",
            f"hosted readiness rows={len(hosted)}; blocked hosted-QA steps={len(hosted_blocks)}",
            "Hosted QA readiness audit separates local readiness from missing Taiga packaging and Env Linter evidence.",
            "Create hosted packaging, run Full Env QA/Env Linter on exact problem versions, and commit findings/dispositions.",
            ["locked_benchmark", "deployment_reliability"],
            ["data/hosted_qa_readiness_audit.csv", "reports/hosted_qa_readiness_audit.md"],
        ),
        row(
            "secret_and_runner_boundary",
            "operational_security",
            "medium",
            "controlled" if not provider_failures and not command_key_leaks else "caution",
            f"provider readiness failures={len(provider_failures)}; model-sweep command key-assignment leaks={len(command_key_leaks)}",
            "Provider commands require external runner env vars and keep provider keys out of committed commands.",
            "Repeat secret scans before every commit that touches runner or transcript files.",
            ["artifact_security", "provider_run_reproducibility"],
            ["data/provider_readiness_audit.csv", "data/model_sweep_execution_commands.csv"],
        ),
        row(
            "public_export_hidden_leakage",
            "operational_security",
            "high",
            "controlled" if (ROOT / "public_tasks").exists() and not public_export_hidden_paths else "caution",
            f"public_tasks exists={(ROOT / 'public_tasks').exists()}; hidden/wrong paths in export={len(public_export_hidden_paths)}",
            "Public-export validation checks that hidden references and wrong submissions are absent.",
            "Validate the public export after every task-asset or export-script change.",
            ["public_release_safety", "locked_benchmark"],
            ["public_tasks", "reports/task_asset_manifest.md", "reports/validation_manifest.json"],
        ),
    ]
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row_data["current_status"] for row_data in rows)
    category_counts = Counter(row_data["category"] for row_data in rows)
    severity_counts = Counter(row_data["severity"] for row_data in rows)
    lines = [
        "# Threats To Validity Register",
        "",
        "This generated register turns the report limitations into reviewable evidence rows. `block` and `caution` statuses are research limitations, not script failures; they identify claims that must remain scoped until stronger evidence is committed.",
        "",
        "## Summary",
        "",
        f"- threats: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- categories: `{compact_json(dict(sorted(category_counts.items())))}`",
        f"- severities: `{compact_json(dict(sorted(severity_counts.items())))}`",
        "",
        "## Register",
        "",
        "| threat | category | severity | status | evidence | mitigation in repo | stronger evidence needed | claims limited |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row_data in rows:
        lines.append(
            f"| `{row_data['threat_id']}` | {row_data['category']} | {row_data['severity']} | "
            f"{row_data['current_status']} | {escaped(row_data['evidence'])} | "
            f"{escaped(row_data['mitigation_in_repo'])} | {escaped(row_data['stronger_evidence_needed'])} | "
            f"{escaped(row_data['claims_limited'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`controlled` means the threat is currently mitigated for local v0.1 claims. `caution` means the report may discuss the artifact but must keep the limitation visible. `block` means the stronger claims in `claims_limited` should not be made from the current evidence.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "threats_to_validity.csv", rows)
    write_markdown(ROOT / "reports" / "threats_to_validity.md", rows)
    print(
        "wrote data/threats_to_validity.csv and reports/threats_to_validity.md "
        f"with {len(rows)} threat rows"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
