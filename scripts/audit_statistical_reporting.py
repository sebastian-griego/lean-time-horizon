from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "check_id",
    "area",
    "status",
    "evidence",
    "current_sample",
    "minimum_for_claim",
    "supported_output",
    "limitation",
    "next_action",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def as_int(value: object) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def as_float(value: object) -> float:
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return 0.0


def accepted_task_ids(metadata: list[dict[str, str]]) -> set[str]:
    return {row["task_id"] for row in metadata if row.get("acceptance_status") == "accepted_v0"}


def nonlocal_rows(run_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in run_rows if row.get("qa_stage") != "local_qa"]


def noninfra(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if as_int(row.get("infra_fail_count", "0")) == 0]


def row(
    check_id: str,
    area: str,
    status: str,
    evidence: str,
    current_sample: str,
    minimum_for_claim: str,
    supported_output: str,
    limitation: str,
    next_action: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "status": status,
        "evidence": evidence,
        "current_sample": current_sample,
        "minimum_for_claim": minimum_for_claim,
        "supported_output": supported_output,
        "limitation": limitation,
        "next_action": next_action,
    }


def build_rows() -> list[dict[str, str]]:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    run_rows = read_csv(ROOT / "data" / "run_results.csv")
    plan = read_csv(ROOT / "data" / "model_sweep_plan.csv")
    model_summary = read_csv(ROOT / "data" / "model_result_summary.csv")
    report_text = read_text(ROOT / "reports" / "metr_style_report.md")
    generate_report = read_text(ROOT / "scripts" / "generate_report.py")
    accepted_ids = accepted_task_ids(metadata)
    accepted_meta = {row["task_id"]: row for row in metadata if row["task_id"] in accepted_ids}
    provider_rows = nonlocal_rows(run_rows)
    accepted_provider = [row for row in provider_rows if row.get("task_id") in accepted_ids]
    accepted_noninfra = noninfra(accepted_provider)
    planned_cells = {(row.get("task_id", ""), row.get("scaffold", "")) for row in plan}
    covered_cells = {(row.get("task_id", ""), row.get("scaffold", "")) for row in accepted_noninfra}
    scaffolds_planned = {row.get("scaffold", "") for row in plan}
    scaffolds_observed = {row.get("scaffold", "") for row in accepted_noninfra}
    buckets_observed = {
        accepted_meta[row.get("task_id", "")].get("human_time_bucket", "")
        for row in accepted_noninfra
        if row.get("task_id", "") in accepted_meta
    }
    families_observed = {
        accepted_meta[row.get("task_id", "")].get("family", "")
        for row in accepted_noninfra
        if row.get("task_id", "") in accepted_meta
    }
    all_accepted_families = {row.get("family", "") for row in accepted_meta.values()}
    failure_rows = [row for row in provider_rows if row.get("failure_label") not in {"", "none"}]
    noninfra_failure_rows = noninfra(failure_rows)
    known_model_summary_fields = set(model_summary[0]) if model_summary else set()
    rows: list[dict[str, str]] = []

    rows.append(row(
        "primary_sweep_coverage",
        "planned_sweep",
        "pass" if planned_cells and covered_cells >= planned_cells else "block",
        f"planned_cells={len(planned_cells)}; covered_noninfra_cells={len(covered_cells)}; missing={len(planned_cells - covered_cells)}",
        f"{len(covered_cells)}/{len(planned_cells)} accepted task/scaffold cells covered by non-infra provider rows",
        "All planned accepted_v0 x scaffold cells covered with non-infra rows.",
        "Coverage table only.",
        "The committed provider rows cannot support accepted-core performance estimates.",
        "Run the planned accepted_v0 x scaffold sweep before reporting benchmark performance.",
    ))
    performance_terms = ["pass@k mean", "Wilson 95% CI"]
    undercovered = not (planned_cells and covered_cells >= planned_cells)
    forbidden_performance_terms = [
        term for term in performance_terms
        if term.lower() in report_text.lower()
    ]
    suppression_phrase_present = "no benchmark pass-rate or interval is reported" in report_text.lower()
    rows.append(row(
        "main_report_performance_estimate_suppression",
        "report_text",
        "pass" if not undercovered or (not forbidden_performance_terms and suppression_phrase_present) else "fail",
        (
            f"undercovered={undercovered}; forbidden_terms={compact_json(forbidden_performance_terms)}; "
            f"suppression_phrase_present={suppression_phrase_present}"
        ),
        f"{len(covered_cells)}/{len(planned_cells)} accepted task/scaffold cells covered by non-infra provider rows",
        "All planned accepted_v0 x scaffold cells covered with non-infra rows before reporting means or intervals.",
        "Smoke row provenance only.",
        "The main report should not display performance-style estimates when primary sweep coverage is blocked.",
        "Suppress mean/interval wording in the main report until the planned accepted-core sweep is covered.",
    ))
    rows.append(row(
        "scaffold_pass_at_k_plot",
        "recommended_plot",
        "pass" if scaffolds_observed >= scaffolds_planned and len(accepted_noninfra) >= len(planned_cells) else "block",
        f"observed_scaffolds={compact_json(sorted(scaffolds_observed))}; planned_scaffolds={compact_json(sorted(scaffolds_planned))}; accepted_noninfra_rows={len(accepted_noninfra)}",
        f"{len(scaffolds_observed)}/{len(scaffolds_planned)} scaffolds observed; {len(accepted_noninfra)} non-infra accepted-core rows",
        "Non-infra accepted-core rows for every planned scaffold, preferably pass@10 rows for every planned cell.",
        "Scaffold coverage audit and planned sweep table.",
        "A mean pass@10-by-scaffold plot would imply comparisons the data do not support.",
        "Populate all one-shot, lookup, and lookup_unlimited cells before generating scaffold-effect plots.",
    ))
    rows.append(row(
        "bucket_success_plot",
        "recommended_plot",
        "pass" if len(buckets_observed) >= 2 and len(accepted_noninfra) >= len(accepted_ids) else "block",
        f"observed_buckets={compact_json(sorted(buckets_observed))}; accepted_noninfra_rows={len(accepted_noninfra)}; accepted_tasks={len(accepted_ids)}",
        f"{len(buckets_observed)} human-time buckets observed in non-infra accepted-core provider rows",
        "Rows covering at least the accepted-core bucket spread, with enough tasks per bucket to show uncertainty.",
        "Human-time distribution and planned sweep table.",
        "Current rows cannot estimate success by human-time bucket.",
        "Run the planned sweep and add T3/T4 accepted tasks before plotting time-horizon success curves.",
    ))
    rows.append(row(
        "family_success_plot",
        "recommended_plot",
        "pass" if families_observed >= all_accepted_families and len(accepted_noninfra) >= len(accepted_ids) else "block",
        f"observed_families={compact_json(sorted(families_observed))}; accepted_families={compact_json(sorted(all_accepted_families))}",
        f"{len(families_observed)}/{len(all_accepted_families)} accepted families observed in non-infra provider rows",
        "At least one non-infra provider row for every accepted family, with enough rows to report uncertainty.",
        "Accepted family composition only.",
        "Current rows cannot estimate success by task family.",
        "Run provider rows across the accepted core before family-level summaries.",
    ))
    rows.append(row(
        "failure_taxonomy_plot",
        "recommended_plot",
        "pass" if len(noninfra_failure_rows) >= 10 and len(scaffolds_observed) >= 2 else "block",
        f"noninfra_failure_rows={len(noninfra_failure_rows)}; labels={compact_json(dict(sorted(Counter(row.get('failure_label', 'unknown') for row in noninfra_failure_rows).items())))}",
        f"{len(noninfra_failure_rows)} non-infra provider failure rows",
        "Enough non-infra failed provider rows across scaffolds to make a stacked failure-label plot meaningful.",
        "Failure-label counts table only.",
        "The current failure taxonomy is useful for transcript QA but too small for distributional claims.",
        "Collect provider failures across the planned scaffold sweep and review labels before plotting.",
    ))
    rows.append(row(
        "wilson_interval_reporting",
        "statistical_method",
        "pass" if {"wilson_low", "wilson_high", "rows_noninfra", "successes"}.issubset(known_model_summary_fields) and "wilson_interval" in generate_report else "fail",
        f"model_result_summary_fields={compact_json(sorted(known_model_summary_fields))}; generate_report_has_wilson={'wilson_interval' in generate_report}",
        f"model_result_summary rows={len(model_summary)}",
        "Performance summaries include numerator, denominator, and Wilson interval fields.",
        "Wilson interval fields are generated even when sample sizes are too small for claims.",
        "Intervals are not a substitute for adequate coverage or independent timing.",
        "Keep Wilson intervals in future performance summaries and report raw n.",
    ))
    local_qa_excluded = (
        "Local QA rows for reference solutions and wrong submissions are validation evidence, not model performance" in report_text
        and "These rows are not model performance and are excluded from benchmark pass-rate summaries" in report_text
    )
    rows.append(row(
        "local_qa_exclusion",
        "data_hygiene",
        "pass" if local_qa_excluded and provider_rows else "fail",
        f"provider_rows={len(provider_rows)}; local_qa_rows={len(run_rows) - len(provider_rows)}; report_excludes_local={local_qa_excluded}",
        f"{len(provider_rows)} provider rows; {len(run_rows) - len(provider_rows)} local QA rows",
        "Report text and analysis exclude local QA rows from capability means.",
        "Local QA is retained as validation evidence.",
        "No benchmark performance claim should use local reference/wrong rows.",
        "Keep local QA and provider rows separated in future analyses.",
    ))
    rows.append(row(
        "infra_failure_policy",
        "data_hygiene",
        "pass" if "infra_fail_rows" in known_model_summary_fields and "excluded from pass-rate summaries" in report_text else "fail",
        f"infra_model_rows={sum(as_int(row.get('infra_fail_count', '0')) > 0 for row in provider_rows)}; report_mentions_exclusion={'excluded from pass-rate summaries' in report_text}",
        "Infra failures retained in run_results and counted separately.",
        "Infra failures excluded from capability means but reported for reliability.",
        "Infra-failure accounting is implemented.",
        "Provider reliability claims still need more rows.",
        "Keep infra rows in raw data and exclude them from model-capability means.",
    ))
    return rows


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row["status"] for row in rows)
    area_counts = Counter(row["area"] for row in rows)
    table_lines = [
        "| check | area | status | current sample | supported output | limitation | next action |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        table_lines.append(
            f"| `{row['check_id']}` | {row['area']} | {row['status']} | "
            f"{row['current_sample']} | {row['supported_output']} | "
            f"{row['limitation']} | {row['next_action']} |"
        )
    lines = [
        "# Statistical Reporting Audit",
        "",
        "This generated audit checks whether the committed run data can support the METR-style performance plots and claims recommended by the playbook. `block` rows are not script failures; they are explicit evidence that the current data should not be used for that claim.",
        "",
        "## Summary",
        "",
        f"- checks: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- areas: `{compact_json(dict(sorted(area_counts.items())))}`",
        "",
        "## Check Table",
        "",
        "\n".join(table_lines),
        "",
        "## Interpretation",
        "",
        "The current artifact supports local validation, smoke-run analysis, and planned-sweep readiness checks. It does not support scaffold-effect, human-time-bucket, family-level, or failure-distribution performance claims until broader non-infra provider sweeps are committed.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "statistical_reporting_audit.csv", rows)
    write_markdown(ROOT / "reports" / "statistical_reporting_audit.md", rows)
    print(f"wrote data/statistical_reporting_audit.csv and reports/statistical_reporting_audit.md with {len(rows)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
