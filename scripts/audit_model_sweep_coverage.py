from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "cell_id",
    "task_id",
    "split",
    "family",
    "human_time_bucket",
    "scaffold",
    "analysis_set",
    "planned_k",
    "provider_rows",
    "noninfra_rows",
    "exact_k_noninfra_rows",
    "max_noninfra_k",
    "max_attempts_completed",
    "successes_out_of_k_total",
    "pass_at_k_values",
    "model_versions",
    "job_ids",
    "transcript_links",
    "coverage_status",
    "evidence",
    "limitation",
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


def as_int(value: str | int | None) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def as_float(value: str | float | None) -> float:
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return 0.0


def clean_join(values: set[str] | list[str]) -> str:
    return ";".join(sorted(value for value in values if value))


def row_for_cell(plan_row: dict[str, str], matching_rows: list[dict[str, str]]) -> dict[str, str]:
    task_id = plan_row.get("task_id", "")
    scaffold = plan_row.get("scaffold", "")
    planned_k = as_int(plan_row.get("planned_k", "0"))
    provider_rows = [row for row in matching_rows if row.get("qa_stage") != "local_qa"]
    noninfra = [row for row in provider_rows if as_int(row.get("infra_fail_count", "0")) == 0]
    exact_k_noninfra = [
        row
        for row in noninfra
        if as_int(row.get("k", "0")) >= planned_k
        and as_int(row.get("attempts_completed", "0")) >= planned_k
    ]
    max_k = max([as_int(row.get("k", "0")) for row in noninfra] or [0])
    max_attempts = max([as_int(row.get("attempts_completed", "0")) for row in noninfra] or [0])
    successes_total = sum(as_int(row.get("successes_out_of_k", "0")) for row in exact_k_noninfra)
    pass_values = [as_float(row.get("pass_at_k", "0")) for row in exact_k_noninfra]

    if exact_k_noninfra:
        coverage_status = "covered_pass" if any(value > 0 for value in pass_values) else "covered_fail"
        evidence = (
            f"{len(exact_k_noninfra)} non-infra row(s) meet planned_k={planned_k}; "
            f"pass_at_k_values={compact_json(pass_values)}"
        )
        limitation = "This cell has enough committed row shape for pass@k accounting; claim strength still depends on model/provider coverage and hosted QA."
        next_action = "Include this cell in future aggregate analysis after the full scaffold/provider plan is covered."
    elif noninfra:
        coverage_status = "smoke_only"
        evidence = f"{len(noninfra)} non-infra row(s), but max_k={max_k} and max_attempts_completed={max_attempts} are below planned_k={planned_k}."
        limitation = "Current rows are smoke evidence, not a planned pass@k result."
        next_action = "Run this task/scaffold with the planned k and commit the full score vector and transcript."
    elif provider_rows:
        coverage_status = "infra_only"
        evidence = f"{len(provider_rows)} provider row(s), all with infra_fail_count > 0."
        limitation = "Infra-only rows cannot support capability or scaffold-effect estimates."
        next_action = "Resolve infrastructure failure and rerun this planned cell."
    else:
        coverage_status = "missing"
        evidence = "No committed non-local row matches this planned task/scaffold cell."
        limitation = "The planned pass@k cell is unobserved."
        next_action = "Run the planned sweep command for this task/scaffold and commit transcripts/results."

    return {
        "cell_id": f"{task_id}:{scaffold}",
        "task_id": task_id,
        "split": plan_row.get("split", ""),
        "family": plan_row.get("family", ""),
        "human_time_bucket": plan_row.get("human_time_bucket", ""),
        "scaffold": scaffold,
        "analysis_set": plan_row.get("analysis_set", ""),
        "planned_k": str(planned_k),
        "provider_rows": str(len(provider_rows)),
        "noninfra_rows": str(len(noninfra)),
        "exact_k_noninfra_rows": str(len(exact_k_noninfra)),
        "max_noninfra_k": str(max_k),
        "max_attempts_completed": str(max_attempts),
        "successes_out_of_k_total": str(successes_total),
        "pass_at_k_values": compact_json(pass_values),
        "model_versions": clean_join({f"{row.get('model', '')}:{row.get('model_version', '')}" for row in provider_rows}),
        "job_ids": clean_join({row.get("job_id", "") for row in provider_rows}),
        "transcript_links": clean_join({row.get("transcript_link", "") for row in provider_rows}),
        "coverage_status": coverage_status,
        "evidence": evidence,
        "limitation": limitation,
        "next_action": next_action,
    }


def build_rows() -> list[dict[str, str]]:
    plan = read_csv(ROOT / "data" / "model_sweep_plan.csv")
    run_results = read_csv(ROOT / "data" / "run_results.csv")
    by_cell: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in run_results:
        by_cell[(row.get("task_id", ""), row.get("scaffold", ""))].append(row)
    return [row_for_cell(plan_row, by_cell[(plan_row.get("task_id", ""), plan_row.get("scaffold", ""))]) for plan_row in plan]


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    status_counts = Counter(row["coverage_status"] for row in rows)
    scaffold_counts = Counter()
    for row in rows:
        scaffold_counts[(row["scaffold"], row["coverage_status"])] += 1
    blocked = [row for row in rows if row["coverage_status"] not in {"covered_pass", "covered_fail"}]
    lines = [
        "# Model Sweep Coverage Audit",
        "",
        "This generated audit maps each planned accepted-core `(task, scaffold, k)` cell in `data/model_sweep_plan.csv` to committed non-local rows in `data/run_results.csv`. It is deliberately stricter than the smoke-run summary: a cell is covered only when a non-infra provider row reaches the planned `k` and has at least `k` completed attempts.",
        "",
        "## Summary",
        "",
        f"- planned cells: `{len(rows)}`",
        f"- coverage statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- cells not ready for pass@k analysis: `{len(blocked)}`",
        "",
        "## Coverage By Scaffold",
        "",
        "| scaffold | status | cells |",
        "| --- | --- | ---: |",
    ]
    for (scaffold, status), count in sorted(scaffold_counts.items()):
        lines.append(f"| `{scaffold}` | {status} | {count} |")
    lines.extend([
        "",
        "## Planned Cell Ledger",
        "",
        "| cell | planned k | provider rows | non-infra rows | exact-k rows | status | evidence | next action |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ])
    for row in rows:
        lines.append(
            f"| `{row['cell_id']}` | {row['planned_k']} | {row['provider_rows']} | "
            f"{row['noninfra_rows']} | {row['exact_k_noninfra_rows']} | {row['coverage_status']} | "
            f"{escaped(row['evidence'])} | {escaped(row['next_action'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`covered_pass` and `covered_fail` are row-shape readiness states, not standalone benchmark validity: hosted QA, model/provider coverage, and claim-tier sample-size gates still apply. `smoke_only`, `infra_only`, and `missing` cells must stay out of scaffold-effect or frontier-performance estimates.",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "model_sweep_coverage_audit.csv", rows)
    write_markdown(ROOT / "reports" / "model_sweep_coverage_audit.md", rows)
    status_counts = Counter(row["coverage_status"] for row in rows)
    print(
        "wrote data/model_sweep_coverage_audit.csv and reports/model_sweep_coverage_audit.md "
        f"with {len(rows)} rows; statuses={compact_json(dict(sorted(status_counts.items())))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
