from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "plot_id",
    "category",
    "current_status",
    "figure_path",
    "figure_exists",
    "source_artifacts",
    "sources_exist",
    "allowed_interpretation",
    "blocked_overclaim",
    "evidence",
    "next_action",
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


def exists_rel(path: str) -> bool:
    return (ROOT / path).exists()


def sources_exist(sources: list[str]) -> bool:
    return all(exists_rel(source) for source in sources)


def row(
    plot_id: str,
    category: str,
    expected_status: str,
    figure_path: str,
    source_artifacts: list[str],
    allowed_interpretation: str,
    blocked_overclaim: str,
    evidence: str,
    next_action: str,
    should_exist: bool,
) -> dict[str, str]:
    figure_exists = exists_rel(figure_path)
    source_ok = sources_exist(source_artifacts)
    if should_exist and not figure_exists:
        current_status = "missing_generated_artifact"
    elif not should_exist and figure_exists:
        current_status = "unexpected_performance_plot"
    elif not source_ok:
        current_status = "missing_source_artifact"
    else:
        current_status = expected_status
    return {
        "plot_id": plot_id,
        "category": category,
        "current_status": current_status,
        "figure_path": figure_path,
        "figure_exists": str(figure_exists).lower(),
        "source_artifacts": ";".join(source_artifacts),
        "sources_exist": str(source_ok).lower(),
        "allowed_interpretation": allowed_interpretation,
        "blocked_overclaim": blocked_overclaim,
        "evidence": evidence,
        "next_action": next_action,
    }


def build_rows() -> list[dict[str, str]]:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    run_rows = read_csv(ROOT / "data" / "run_results.csv")
    statistical = read_csv(ROOT / "data" / "statistical_reporting_audit.csv")
    model_summary = read_csv(ROOT / "data" / "model_result_summary.csv")
    model_sweep_coverage = read_csv(ROOT / "data" / "model_sweep_coverage_audit.csv")
    human_time = read_csv(ROOT / "data" / "human_time_calibration_audit.csv")

    accepted = [item for item in metadata if item.get("acceptance_status") == "accepted_v0"]
    release = [
        item for item in metadata
        if item.get("acceptance_status") in {"accepted_v0", "calibration_only"}
    ]
    stat_by_id = {item.get("check_id", ""): item for item in statistical}
    stat_statuses = Counter(item.get("status", "unknown") for item in statistical)
    provider_rows = [item for item in run_rows if item.get("qa_stage") != "local_qa"]

    rows = [
        row(
            "task_counts_by_family",
            "generated_descriptive",
            "generated_descriptive",
            "reports/figures/task_counts_by_family.svg",
            ["data/task_metadata.csv", "reports/metr_style_report.md"],
            "Accepted-core family composition only.",
            "Do not infer model performance, family difficulty, or representativeness from task-count bars.",
            f"accepted_tasks={len(accepted)}; accepted_families={compact_json(dict(sorted(Counter(item.get('family', '') for item in accepted).items())))}",
            "Regenerate with python scripts/generate_report.py after metadata changes.",
            should_exist=True,
        ),
        row(
            "task_counts_by_bucket",
            "generated_descriptive",
            "generated_descriptive",
            "reports/figures/task_counts_by_bucket.svg",
            ["data/task_metadata.csv", "reports/metr_style_report.md"],
            "Release task-count composition by human-time bucket.",
            "Do not treat author-estimated bucket counts as measured time-horizon performance.",
            f"release_tasks={len(release)}; release_buckets={compact_json(dict(sorted(Counter(item.get('human_time_bucket', '') for item in release).items())))}",
            "Regenerate after task-status or human-time metadata changes.",
            should_exist=True,
        ),
        row(
            "top_skills",
            "generated_descriptive",
            "generated_descriptive",
            "reports/figures/top_skills.svg",
            ["data/task_metadata.csv", "reports/metr_style_report.md"],
            "Most frequent declared skills in the release set.",
            "Do not read skill-frequency bars as validated capability coverage or model failure frequencies.",
            f"release_tasks={len(release)}",
            "Use diagnostic and construct-validity audits for capability claims.",
            should_exist=True,
        ),
        row(
            "run_rows_by_model",
            "generated_provenance",
            "generated_provenance",
            "reports/figures/run_rows_by_model.svg",
            ["data/run_results.csv", "reports/model_run_analysis.md"],
            "Committed run-row provenance by model/source, including local QA rows.",
            "Do not read row-count bars as pass-rate evidence or model ranking.",
            f"run_rows={len(run_rows)}; provider_rows={len(provider_rows)}",
            "Use model-result summaries only after coverage thresholds are met.",
            should_exist=bool(run_rows),
        ),
        row(
            "task_minutes_by_bucket",
            "generated_descriptive",
            "generated_descriptive",
            "reports/figures/task_minutes_by_bucket.svg",
            ["data/task_metadata.csv", "data/human_time_calibration_audit.csv"],
            "Reviewer-estimated p50 minutes by task bucket.",
            "Do not claim calibrated human-time scaling from this figure without independent timing observations.",
            f"human_time_rows={len(human_time)}; accepted_tasks={len(accepted)}",
            "Replace or supplement reviewer estimates after independent timing collection.",
            should_exist=True,
        ),
    ]

    blocked_plots = [
        (
            "scaffold_pass_at_k_plot",
            "reports/figures/pass_at_k_by_scaffold.svg",
            "No scaffold performance plot is generated from the undercovered smoke rows.",
        ),
        (
            "bucket_success_plot",
            "reports/figures/success_by_human_time_bucket.svg",
            "No success-by-time-bucket plot is generated from the undercovered smoke rows.",
        ),
        (
            "family_success_plot",
            "reports/figures/success_by_family.svg",
            "No family success plot is generated from the undercovered smoke rows.",
        ),
        (
            "failure_taxonomy_plot",
            "reports/figures/failure_labels_by_scaffold.svg",
            "No failure-taxonomy distribution plot is generated from the undercovered smoke rows.",
        ),
    ]
    for check_id, figure_path, allowed in blocked_plots:
        stat = stat_by_id.get(check_id, {})
        rows.append(row(
            check_id,
            "blocked_performance",
            "blocked_by_evidence" if stat.get("status") == "block" else "needs_audit_review",
            figure_path,
            ["data/statistical_reporting_audit.csv", "reports/statistical_reporting_audit.md", "data/model_result_summary.csv"],
            allowed,
            stat.get("limitation", "Do not publish unsupported performance plots."),
            stat.get("evidence", f"statistical_statuses={compact_json(dict(sorted(stat_statuses.items())))}"),
            stat.get("next_action", "Regenerate statistical reporting and inspect plot-support rows."),
            should_exist=False,
        ))

    primary = next(
        (
            item for item in model_summary
            if item.get("analysis_set") == "primary_plan_coverage"
            and item.get("group_by") == "all"
            and item.get("group") == "all"
        ),
        {},
    )
    pass_at_k_ready_cells = sum(
        1 for item in model_sweep_coverage
        if item.get("coverage_status") in {"covered_pass", "covered_fail"}
    )
    coverage_statuses = Counter(item.get("coverage_status", "unknown") for item in model_sweep_coverage)
    rows.append(row(
        "problem_pass_vs_time",
        "blocked_performance",
        "blocked_by_evidence",
        "reports/figures/problem_pass_vs_human_minutes.svg",
        [
            "data/model_result_summary.csv",
            "data/model_sweep_coverage_audit.csv",
            "data/human_time_calibration_audit.csv",
            "data/statistical_design_thresholds.csv",
        ],
        "No problem-level pass-rate versus human-time plot is generated yet.",
        "Do not imply a time-horizon trend from zero pass@k-ready accepted-core cells and author-estimated times.",
        (
            f"planned_cells={primary.get('planned_cells', '0')}; "
            f"pass_at_k_ready_cells={pass_at_k_ready_cells}/{len(model_sweep_coverage)}; "
            f"aggregate_noninfra_smoke_cells={primary.get('covered_cells_noninfra', '0')}; "
            f"coverage_statuses={compact_json(dict(sorted(coverage_statuses.items())))}; "
            f"human_time_rows={len(human_time)}"
        ),
        "Run covered scaffold sweeps and collect independent timing before generating this plot.",
        should_exist=False,
    ))

    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    status_counts = Counter(item["current_status"] for item in rows)
    category_counts = Counter(item["category"] for item in rows)
    lines = [
        "# Figure Manifest And Plot Boundary Audit",
        "",
        "This generated audit maps each committed SVG figure to its source data and allowed interpretation, and records the recommended performance plots that are intentionally absent because the current evidence cannot support them.",
        "",
        "## Summary",
        "",
        f"- plot rows: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- categories: `{compact_json(dict(sorted(category_counts.items())))}`",
        "",
        "## Plot Ledger",
        "",
        "| plot | status | figure | sources | allowed interpretation | blocked overclaim | evidence | next action |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in rows:
        lines.append(
            f"| `{item['plot_id']}` | {item['current_status']} | `{item['figure_path']}` "
            f"(exists={item['figure_exists']}) | {escaped(item['source_artifacts'])} | "
            f"{escaped(item['allowed_interpretation'])} | {escaped(item['blocked_overclaim'])} | "
            f"{escaped(item['evidence'])} | {escaped(item['next_action'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`generated_descriptive` and `generated_provenance` rows are allowed as composition or provenance figures only. `blocked_by_evidence` rows are not missing artifacts; they are performance plots that should remain absent until the statistical and sweep-coverage gates are supported.",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "figure_manifest.csv", rows)
    write_markdown(ROOT / "reports" / "figure_manifest.md", rows)
    problem_rows = [
        item for item in rows
        if item["current_status"] in {
            "missing_generated_artifact",
            "unexpected_performance_plot",
            "missing_source_artifact",
            "needs_audit_review",
        }
    ]
    print(
        "wrote data/figure_manifest.csv and reports/figure_manifest.md "
        f"with {len(rows)} plot rows; problem_rows={len(problem_rows)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
