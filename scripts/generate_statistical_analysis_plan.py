from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

THRESHOLD_FIELDS = [
    "tier_id",
    "claim_type",
    "current_status",
    "minimum_accepted_tasks",
    "minimum_noninfra_primary_cells",
    "minimum_k",
    "minimum_scaffold_count",
    "minimum_group_n",
    "minimum_independent_timing",
    "minimum_failure_reviews",
    "hosted_qa_required",
    "current_evidence",
    "allowed_output_now",
    "blocked_overclaim",
    "stronger_claim_requires",
]

PRECISION_FIELDS = [
    "n",
    "assumed_p",
    "successes",
    "wilson_low",
    "wilson_high",
    "interval_width",
    "interpretation",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def as_int(value: object) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n <= 0:
        return 0.0, 0.0
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def precision_label(width: float) -> str:
    if width >= 0.60:
        return "very_wide"
    if width >= 0.40:
        return "wide"
    if width >= 0.25:
        return "moderate"
    return "tighter_descriptive"


def current_counts() -> dict[str, object]:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    run_rows = read_csv(ROOT / "data" / "run_results.csv")
    plan_rows = read_csv(ROOT / "data" / "model_sweep_plan.csv")
    coverage_rows = read_csv(ROOT / "data" / "model_sweep_coverage_audit.csv")
    human_time = read_csv(ROOT / "data" / "human_time_calibration_audit.csv")
    failure_reviews = read_csv(ROOT / "data" / "failure_label_reviews.csv")
    failure_review_audit = read_csv(ROOT / "data" / "failure_label_review_audit.csv")
    hosted = read_csv(ROOT / "data" / "hosted_qa_readiness_audit.csv")

    accepted = [row for row in metadata if row.get("acceptance_status") == "accepted_v0"]
    accepted_ids = {row.get("task_id", "") for row in accepted}
    provider_rows = [row for row in run_rows if row.get("qa_stage") != "local_qa"]
    accepted_provider_rows = [row for row in provider_rows if row.get("task_id") in accepted_ids]
    accepted_noninfra = [
        row for row in accepted_provider_rows
        if as_int(row.get("infra_fail_count", "0")) == 0
    ]
    planned_cells = {(row.get("task_id", ""), row.get("scaffold", "")) for row in plan_rows}
    covered_noninfra_cells = {(row.get("task_id", ""), row.get("scaffold", "")) for row in accepted_noninfra}
    pass_at_k_ready_rows = [
        row for row in coverage_rows
        if row.get("coverage_status") in {"covered_pass", "covered_fail"}
    ]
    pass_at_k_ready_cells = {(row.get("task_id", ""), row.get("scaffold", "")) for row in pass_at_k_ready_rows}
    strict_coverage_status_counts = Counter(row.get("coverage_status", "unknown") for row in coverage_rows)
    observed_scaffolds = {row.get("scaffold", "") for row in accepted_noninfra}
    accepted_bucket_counts = Counter(row.get("human_time_bucket", "") for row in accepted)
    accepted_family_counts = Counter(row.get("family", "") for row in accepted)
    independent_timing_count = sum(
        1 for row in human_time
        if row.get("acceptance_status") == "accepted_v0"
        and as_int(row.get("successful_independent_observation_count", "0")) > 0
    )
    noninfra_failures = [
        row for row in provider_rows
        if as_int(row.get("infra_fail_count", "0")) == 0
        and row.get("failure_label") not in {"", "none"}
    ]
    failure_review_failures = sum(1 for row in failure_review_audit if row.get("status") == "fail")
    hosted_blocks = sum(1 for row in hosted if row.get("status") == "block")
    k_values = sorted({row.get("planned_k", "") for row in plan_rows if row.get("planned_k")})

    return {
        "accepted_count": len(accepted),
        "accepted_bucket_counts": dict(sorted(accepted_bucket_counts.items())),
        "accepted_family_counts": dict(sorted(accepted_family_counts.items())),
        "provider_rows": len(provider_rows),
        "accepted_provider_rows": len(accepted_provider_rows),
        "accepted_noninfra_rows": len(accepted_noninfra),
        "planned_cells": len(planned_cells),
        "covered_noninfra_cells": len(covered_noninfra_cells),
        "pass_at_k_ready_cells": len(pass_at_k_ready_cells),
        "strict_coverage_status_counts": dict(sorted(strict_coverage_status_counts.items())),
        "observed_scaffolds": len(observed_scaffolds),
        "observed_scaffold_names": sorted(observed_scaffolds),
        "planned_k_values": k_values,
        "independent_timing_count": independent_timing_count,
        "noninfra_failure_rows": len(noninfra_failures),
        "failure_review_rows": len(failure_reviews),
        "failure_review_failures": failure_review_failures,
        "hosted_blocks": hosted_blocks,
    }


def threshold_row(
    tier_id: str,
    claim_type: str,
    current_status: str,
    minimum_accepted_tasks: str,
    minimum_noninfra_primary_cells: str,
    minimum_k: str,
    minimum_scaffold_count: str,
    minimum_group_n: str,
    minimum_independent_timing: str,
    minimum_failure_reviews: str,
    hosted_qa_required: str,
    current_evidence: str,
    allowed_output_now: str,
    blocked_overclaim: str,
    stronger_claim_requires: str,
) -> dict[str, object]:
    return {
        "tier_id": tier_id,
        "claim_type": claim_type,
        "current_status": current_status,
        "minimum_accepted_tasks": minimum_accepted_tasks,
        "minimum_noninfra_primary_cells": minimum_noninfra_primary_cells,
        "minimum_k": minimum_k,
        "minimum_scaffold_count": minimum_scaffold_count,
        "minimum_group_n": minimum_group_n,
        "minimum_independent_timing": minimum_independent_timing,
        "minimum_failure_reviews": minimum_failure_reviews,
        "hosted_qa_required": hosted_qa_required,
        "current_evidence": current_evidence,
        "allowed_output_now": allowed_output_now,
        "blocked_overclaim": blocked_overclaim,
        "stronger_claim_requires": stronger_claim_requires,
    }


def build_threshold_rows(counts: dict[str, object]) -> list[dict[str, object]]:
    accepted_count = as_int(counts["accepted_count"])
    planned_cells = as_int(counts["planned_cells"])
    covered_cells = as_int(counts["pass_at_k_ready_cells"])
    noninfra_failures = as_int(counts["noninfra_failure_rows"])
    failure_review_rows = as_int(counts["failure_review_rows"])
    failure_review_failures = as_int(counts["failure_review_failures"])
    observed_scaffolds = as_int(counts["observed_scaffolds"])
    independent_timing_count = as_int(counts["independent_timing_count"])
    hosted_blocks = as_int(counts["hosted_blocks"])
    evidence = (
        f"accepted={accepted_count}; planned_cells={planned_cells}; pass_at_k_ready_cells={covered_cells}; "
        f"aggregate_covered_noninfra_cells={counts['covered_noninfra_cells']}; "
        f"coverage_statuses={counts['strict_coverage_status_counts']}; "
        f"observed_scaffolds={counts['observed_scaffold_names']}; independent_timing={independent_timing_count}; "
        f"noninfra_failures={noninfra_failures}; failure_review_rows={failure_review_rows}; "
        f"failure_review_audit_failures={failure_review_failures}; hosted_blocks={hosted_blocks}"
    )
    return [
        threshold_row(
            "smoke_run_provenance",
            "run_provenance",
            "supported" if as_int(counts["provider_rows"]) > 0 and failure_review_failures == 0 else "blocked",
            "0",
            "1",
            "1",
            "1",
            "not_applicable",
            "0",
            "all committed smoke rows reviewed or explicitly queued",
            "false",
            evidence,
            "Adapter, transcript, and run-result provenance only.",
            "Do not treat smoke rows as benchmark performance.",
            "A covered accepted-core scaffold sweep with documented model versions and zero integrity failures.",
        ),
        threshold_row(
            "v0_1_primary_descriptive_performance",
            "descriptive_performance",
            "supported" if planned_cells > 0 and covered_cells >= planned_cells else "blocked",
            str(accepted_count),
            str(planned_cells),
            "10",
            "3",
            "not_applicable",
            "0",
            "all non-success transcripts reviewed",
            "false",
            evidence,
            "Coverage table and blocked performance statement.",
            "Do not report aggregate pass@k estimates or intervals for accepted-core performance until every planned cell is covered.",
            "Non-infra k=10 rows for every accepted_v0 task x scaffold cell for the reported model.",
        ),
        threshold_row(
            "scaffold_effect_comparison",
            "performance_comparison",
            "supported" if accepted_count >= 20 and covered_cells >= max(60, planned_cells) and observed_scaffolds >= 3 else "blocked",
            "20",
            "accepted_tasks * 3 scaffold cells",
            "10",
            "3",
            "not_applicable",
            "0",
            "all non-success transcripts reviewed",
            "false",
            evidence,
            "Planned scaffold comparison only.",
            "Do not claim lookup or iterative compile/debug effects from the current smoke rows.",
            "At least 20 accepted tasks, all scaffold cells covered for each reported model, raw n, and Wilson intervals.",
        ),
        threshold_row(
            "time_horizon_bucket_trend",
            "time_horizon_performance",
            "supported" if independent_timing_count >= accepted_count and accepted_count >= 20 else "blocked",
            "20",
            "all accepted task x scaffold cells for reported model",
            "10",
            "3",
            "5 per reported bucket",
            "all accepted tasks",
            "all non-success transcripts reviewed",
            "false",
            evidence + f"; bucket_counts={compact_json(counts['accepted_bucket_counts'])}",
            "Task-set time-bucket composition only.",
            "Do not claim calibrated time-horizon scaling from author estimates or singleton T3 coverage.",
            "Independent timing for all accepted tasks plus at least five accepted tasks in each reported bucket.",
        ),
        threshold_row(
            "family_or_skill_summary",
            "subgroup_performance",
            "supported" if accepted_count >= 30 else "blocked",
            "30",
            "all accepted task x scaffold cells for reported model",
            "10",
            "3",
            "5 per reported family or skill group",
            "all accepted tasks",
            "all non-success transcripts reviewed",
            "false",
            evidence + f"; family_counts={compact_json(counts['accepted_family_counts'])}",
            "Family/skill coverage table only.",
            "Do not interpret singleton family or skill rows as stable estimates.",
            "Enough accepted tasks that every reported family or skill group has at least five rows.",
        ),
        threshold_row(
            "failure_taxonomy_distribution",
            "failure_analysis",
            "supported" if noninfra_failures >= 10 and failure_review_rows >= noninfra_failures and failure_review_failures == 0 else "blocked",
            "20",
            "enough covered cells to produce at least 10 non-infra failures",
            "10",
            "2",
            "not_applicable",
            "0",
            "at least 10 independently reviewed non-infra failures",
            "false",
            evidence,
            "Failure-label workflow and smoke transcript review only.",
            "Do not claim dominant failure modes or failure distributions.",
            "At least 10 non-infra failed provider rows with independent review or adjudication.",
        ),
        threshold_row(
            "locked_benchmark_population_claims",
            "benchmark_status",
            "supported" if accepted_count >= 20 and covered_cells >= 60 and independent_timing_count >= accepted_count and hosted_blocks == 0 else "blocked",
            "20-50",
            "all accepted task x scaffold cells for reported model",
            "10",
            "3",
            "5 per reported subgroup",
            "all accepted tasks",
            "all non-success transcripts independently reviewed",
            "true",
            evidence,
            "Local v0.1 research artifact only.",
            "Do not call v0.1 locked, final, population-valid, or frontier-performance-characterizing.",
            "Accepted scale, T3/T4 depth, independent timing, complete scaffold sweeps, hosted QA, and freeze evidence.",
        ),
    ]


def build_precision_rows(counts: dict[str, object]) -> list[dict[str, object]]:
    n_values = [
        1,
        as_int(counts["accepted_count"]),
        as_int(counts["planned_cells"]),
        20,
        30,
        50,
    ]
    unique_n = sorted({n for n in n_values if n > 0})
    rows: list[dict[str, object]] = []
    for n in unique_n:
        for assumed_p in [0.1, 0.5, 0.9]:
            successes = round(n * assumed_p)
            low, high = wilson_interval(successes, n)
            width = high - low
            rows.append({
                "n": n,
                "assumed_p": f"{assumed_p:.1f}",
                "successes": successes,
                "wilson_low": f"{low:.4f}",
                "wilson_high": f"{high:.4f}",
                "interval_width": f"{width:.4f}",
                "interpretation": precision_label(width),
            })
    return rows


def escaped(value: object) -> str:
    return str(value).replace("|", "/").replace("\n", " ")


def write_report(path: Path, threshold_rows: list[dict[str, object]], precision_rows: list[dict[str, object]], counts: dict[str, object]) -> None:
    status_counts = Counter(str(row["current_status"]) for row in threshold_rows)
    threshold_lines = [
        "| tier | status | minimum evidence | allowed output now | blocked overclaim |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in threshold_rows:
        minimum = (
            f"accepted={row['minimum_accepted_tasks']}; cells={row['minimum_noninfra_primary_cells']}; "
            f"k={row['minimum_k']}; scaffolds={row['minimum_scaffold_count']}; group_n={row['minimum_group_n']}; "
            f"timing={row['minimum_independent_timing']}; failure_reviews={row['minimum_failure_reviews']}; "
            f"hosted={row['hosted_qa_required']}"
        )
        threshold_lines.append(
            f"| `{row['tier_id']}` | {row['current_status']} | {escaped(minimum)} | "
            f"{escaped(row['allowed_output_now'])} | {escaped(row['blocked_overclaim'])} |"
        )
    precision_half = [row for row in precision_rows if row["assumed_p"] == "0.5"]
    precision_lines = [
        "| n | successes at p=0.5 | Wilson low | Wilson high | width | interpretation |",
        "| ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in precision_half:
        precision_lines.append(
            f"| {row['n']} | {row['successes']} | {row['wilson_low']} | {row['wilson_high']} | "
            f"{row['interval_width']} | {row['interpretation']} |"
        )
    lines = [
        "# Statistical Analysis Plan",
        "",
        "This generated plan fixes the minimum evidence thresholds for interpreting future model runs. It complements `reports/evaluation_protocol.md`: the protocol defines what to run, while this plan defines what claims the resulting sample can and cannot support.",
        "",
        "## Current Evidence Snapshot",
        "",
        f"- accepted tasks: `{counts['accepted_count']}`",
        f"- planned accepted task/scaffold cells: `{counts['planned_cells']}`",
        f"- pass@k-ready accepted task/scaffold cells: `{counts['pass_at_k_ready_cells']}`",
        f"- aggregate non-infra smoke-covered cells: `{counts['covered_noninfra_cells']}`",
        f"- strict coverage statuses: `{compact_json(counts['strict_coverage_status_counts'])}`",
        f"- observed scaffolds: `{compact_json(counts['observed_scaffold_names'])}`",
        f"- independent timing observations on accepted tasks: `{counts['independent_timing_count']}`",
        f"- non-infra provider failure rows: `{counts['noninfra_failure_rows']}`",
        f"- failure-label review rows: `{counts['failure_review_rows']}`",
        f"- hosted-QA block rows: `{counts['hosted_blocks']}`",
        "",
        "## Claim Tiers",
        "",
        f"- tier statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        "",
        "\n".join(threshold_lines),
        "",
        "## Precision Ledger",
        "",
        "The table below shows Wilson 95% intervals for a binary task-row endpoint under a worst-case midrange success rate. It is a precision guide, not a power guarantee. It makes visible why the current accepted-core size and smoke rows cannot support stable population-level estimates.",
        "",
        "\n".join(precision_lines),
        "",
        "## Reporting Rules",
        "",
        "1. Report raw numerators and denominators before percentages.",
        "2. Report Wilson intervals for binary task-row means only when the planned cells for the stated analysis set are covered.",
        "3. Treat subgroup summaries with fewer than five accepted tasks as coverage tables, not estimates.",
        "4. Keep infra failures in raw data and reliability summaries, but exclude them from model-capability means.",
        "5. Do not strengthen blocked claim tiers until the threshold row for that tier is supported by committed evidence.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    counts = current_counts()
    threshold_rows = build_threshold_rows(counts)
    precision_rows = build_precision_rows(counts)
    write_csv(ROOT / "data" / "statistical_design_thresholds.csv", threshold_rows, THRESHOLD_FIELDS)
    write_csv(ROOT / "data" / "wilson_precision_table.csv", precision_rows, PRECISION_FIELDS)
    write_report(ROOT / "reports" / "statistical_analysis_plan.md", threshold_rows, precision_rows, counts)
    print(
        "wrote data/statistical_design_thresholds.csv, data/wilson_precision_table.csv, "
        f"and reports/statistical_analysis_plan.md with {len(threshold_rows)} claim tiers"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
