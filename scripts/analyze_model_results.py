from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "analysis_set",
    "group_by",
    "group",
    "planned_cells",
    "covered_cells_any",
    "covered_cells_noninfra",
    "rows_total",
    "rows_noninfra",
    "successes",
    "mean_pass_at_k",
    "wilson_low",
    "wilson_high",
    "infra_fail_rows",
    "timeout_rows",
    "notes",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n <= 0:
        return 0.0, 0.0
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def as_int(value: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def row(
    analysis_set: str,
    group_by: str,
    group: str,
    planned_cells: int | str,
    covered_cells_any: int | str,
    covered_cells_noninfra: int | str,
    rows: list[dict[str, str]],
    notes: str,
    successes_override: int | None = None,
) -> dict[str, object]:
    noninfra = [item for item in rows if as_int(item.get("infra_fail_count", "0")) == 0]
    successes = successes_override if successes_override is not None else sum(1 for item in noninfra if as_float(item.get("pass_at_k", "0")) > 0)
    low, high = wilson_interval(successes, len(noninfra))
    mean = successes / len(noninfra) if noninfra else 0.0
    return {
        "analysis_set": analysis_set,
        "group_by": group_by,
        "group": group,
        "planned_cells": planned_cells,
        "covered_cells_any": covered_cells_any,
        "covered_cells_noninfra": covered_cells_noninfra,
        "rows_total": len(rows),
        "rows_noninfra": len(noninfra),
        "successes": successes,
        "mean_pass_at_k": f"{mean:.4f}",
        "wilson_low": f"{low:.4f}",
        "wilson_high": f"{high:.4f}",
        "infra_fail_rows": sum(as_int(item.get("infra_fail_count", "0")) > 0 for item in rows),
        "timeout_rows": sum(as_int(item.get("timeout_count", "0")) for item in rows),
        "notes": notes,
    }


def task_status_map(metadata: list[dict[str, str]]) -> dict[str, str]:
    return {item["task_id"]: item.get("acceptance_status", "") for item in metadata}


def cells(rows: list[dict[str, str]]) -> set[tuple[str, str]]:
    return {(item.get("task_id", ""), item.get("scaffold", "")) for item in rows}


def successful_cells(rows: list[dict[str, str]]) -> set[tuple[str, str]]:
    return {(item.get("task_id", ""), item.get("scaffold", "")) for item in rows if as_float(item.get("pass_at_k", "0")) > 0}


def grouped(rows: list[dict[str, str]], key: str) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = defaultdict(list)
    for item in rows:
        out[item.get(key, "unknown")].append(item)
    return dict(out)


def build_summary() -> list[dict[str, object]]:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    run_results = read_csv(ROOT / "data" / "run_results.csv")
    plan = read_csv(ROOT / "data" / "model_sweep_plan.csv")
    status_by_id = task_status_map(metadata)
    model_rows = [item for item in run_results if item.get("qa_stage") != "local_qa"]
    accepted_rows = [item for item in model_rows if status_by_id.get(item.get("task_id", "")) == "accepted_v0"]
    calibration_rows = [item for item in model_rows if status_by_id.get(item.get("task_id", "")) == "calibration_only"]
    plan_cells = cells(plan)
    accepted_cells = cells(accepted_rows)
    accepted_noninfra_cells = cells([item for item in accepted_rows if as_int(item.get("infra_fail_count", "0")) == 0])
    accepted_success_cells = successful_cells([item for item in accepted_rows if as_int(item.get("infra_fail_count", "0")) == 0])

    rows: list[dict[str, object]] = [
        row(
            "all_provider_smoke_rows",
            "all",
            "all",
            "",
            "",
            "",
            model_rows,
            "All committed non-local rows, including calibration rows and infra failures. Not a primary benchmark estimate.",
        ),
        row(
            "accepted_core_results",
            "all",
            "all",
            len(plan_cells),
            len(accepted_cells & plan_cells),
            len(accepted_noninfra_cells & plan_cells),
            accepted_rows,
            "Committed accepted-core provider rows only. This is far below the planned sweep.",
        ),
        row(
            "calibration_smoke_rows",
            "all",
            "all",
            "",
            "",
            "",
            calibration_rows,
            "Committed calibration-only provider rows. Excluded from accepted-core capability claims.",
        ),
        row(
            "primary_plan_coverage",
            "all",
            "all",
            len(plan_cells),
            len(accepted_cells & plan_cells),
            len(accepted_noninfra_cells & plan_cells),
            accepted_rows,
            "Coverage of the planned accepted_v0 x scaffold sweep by committed provider rows.",
            successes_override=len(accepted_success_cells & plan_cells),
        ),
    ]

    for scaffold, planned_group in grouped(plan, "scaffold").items():
        planned = cells(planned_group)
        scaffold_rows = [item for item in accepted_rows if item.get("scaffold") == scaffold]
        scaffold_noninfra = [item for item in scaffold_rows if as_int(item.get("infra_fail_count", "0")) == 0]
        rows.append(
            row(
                "primary_plan_coverage",
                "scaffold",
                scaffold,
                len(planned),
                len(cells(scaffold_rows) & planned),
                len(cells(scaffold_noninfra) & planned),
                scaffold_rows,
                "Per-scaffold planned-sweep coverage for accepted-core provider rows.",
                successes_override=len(successful_cells(scaffold_noninfra) & planned),
            )
        )

    for scaffold, scaffold_rows in grouped(accepted_rows, "scaffold").items():
        rows.append(
            row(
                "accepted_core_results",
                "scaffold",
                scaffold,
                "",
                "",
                "",
                scaffold_rows,
                "Accepted-core provider rows by scaffold.",
            )
        )

    failure_counts = Counter(item.get("failure_label", "unknown") for item in model_rows if item.get("failure_label") != "none")
    for label, count in sorted(failure_counts.items()):
        label_rows = [item for item in model_rows if item.get("failure_label") == label]
        rows.append(
            row(
                "failure_label_counts",
                "failure_label",
                label,
                "",
                "",
                "",
                label_rows,
                f"{count} committed provider row(s) with this primary failure label.",
            )
        )

    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, object]]) -> None:
    by_id = {(item["analysis_set"], item["group_by"], item["group"]): item for item in rows}
    primary = by_id.get(("primary_plan_coverage", "all", "all"), {})
    accepted = by_id.get(("accepted_core_results", "all", "all"), {})
    smoke = by_id.get(("all_provider_smoke_rows", "all", "all"), {})
    failure_rows = [item for item in rows if item["analysis_set"] == "failure_label_counts"]
    coverage_rows = [item for item in rows if item["analysis_set"] == "primary_plan_coverage" and item["group_by"] == "scaffold"]
    result_rows = [item for item in rows if item["analysis_set"] == "accepted_core_results" and item["group_by"] == "scaffold"]

    lines = [
        "# Model Run Analysis",
        "",
        "This generated analysis reads `data/run_results.csv` and `data/model_sweep_plan.csv`. It separates local QA from provider rows, accepted-core rows from calibration rows, and planned-sweep coverage from smoke evidence.",
        "",
        "## Current Evidence Status",
        "",
        f"- planned accepted-core task/scaffold cells: `{primary.get('planned_cells', 0)}`",
        f"- planned cells with any committed accepted-core provider row: `{primary.get('covered_cells_any', 0)}`",
        f"- planned cells with a non-infra accepted-core provider row: `{primary.get('covered_cells_noninfra', 0)}`",
        f"- accepted-core provider rows: `{accepted.get('rows_total', 0)}` total, `{accepted.get('rows_noninfra', 0)}` non-infra",
        f"- accepted-core successes among non-infra provider rows: `{accepted.get('successes', 0)}`",
        f"- all committed provider smoke rows: `{smoke.get('rows_total', 0)}` total, `{smoke.get('rows_noninfra', 0)}` non-infra",
        "",
        "The committed provider rows are useful smoke evidence, but they are not a benchmark performance run. The planned primary sweep remains mostly uncovered.",
        "",
        "## Planned-Sweep Coverage By Scaffold",
        "",
        "| scaffold | planned cells | covered any | covered non-infra | successful cells |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for item in coverage_rows:
        lines.append(
            f"| `{item['group']}` | {item['planned_cells']} | {item['covered_cells_any']} | "
            f"{item['covered_cells_noninfra']} | {item['successes']} |"
        )
    lines.extend([
        "",
        "## Accepted-Core Provider Rows By Scaffold",
        "",
        "| scaffold | rows | non-infra rows | successes | mean pass@k | Wilson 95% CI | infra rows |",
        "| --- | ---: | ---: | ---: | ---: | --- | ---: |",
    ])
    for item in result_rows:
        lines.append(
            f"| `{item['group']}` | {item['rows_total']} | {item['rows_noninfra']} | {item['successes']} | "
            f"{item['mean_pass_at_k']} | {item['wilson_low']}-{item['wilson_high']} | {item['infra_fail_rows']} |"
        )
    lines.extend([
        "",
        "## Failure Labels In Provider Rows",
        "",
        "| label | rows | notes |",
        "| --- | ---: | --- |",
    ])
    for item in failure_rows:
        lines.append(f"| `{item['group']}` | {item['rows_total']} | {item['notes']} |")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- Do not use these rows for frontier-model capability claims.",
        "- Use the analysis to verify that future sweeps cover all planned accepted-core task/scaffold cells.",
        "- Keep calibration-only rows separate from accepted-core estimates.",
        "- Retain infra failures in `data/run_results.csv`, but exclude them from capability means while reporting reliability separately.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = build_summary()
    write_csv(ROOT / "data" / "model_result_summary.csv", rows)
    write_markdown(ROOT / "reports" / "model_run_analysis.md", rows)
    print(f"wrote data/model_result_summary.csv and reports/model_run_analysis.md with {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
