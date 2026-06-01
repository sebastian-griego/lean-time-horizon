from __future__ import annotations

import csv
import json
import math
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BUCKET_RANGES: dict[str, tuple[int, float]] = {
    "T0": (5, 15),
    "T1": (15, 45),
    "T2": (45, 120),
    "T3": (120, 360),
    "T4": (360, math.inf),
}

FIELDS = [
    "task_id",
    "split",
    "acceptance_status",
    "family",
    "human_time_bucket",
    "human_minutes_p50",
    "human_minutes_p90",
    "bucket_range_minutes",
    "p50_bucket_consistent",
    "p90_at_or_above_p50",
    "estimate_confidence_level",
    "manual_review_complete",
    "independent_observation_count",
    "successful_independent_observation_count",
    "observed_minutes_summary",
    "calibration_status",
    "issues",
    "notes",
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


def confidence_level(note: str) -> str:
    lower = note.lower()
    if "high" in lower:
        return "high"
    if "medium" in lower:
        return "medium"
    if "low" in lower:
        return "low"
    return "unspecified"


def parse_minutes(value: str) -> int | None:
    try:
        minutes = int(value)
    except (TypeError, ValueError):
        return None
    return minutes if minutes > 0 else None


def range_label(bucket: str) -> str:
    low, high = BUCKET_RANGES.get(bucket, (0, 0))
    if high == math.inf:
        return f"{low}+"
    return f"{low}-{int(high)}"


def in_bucket(minutes: int | None, bucket: str) -> bool:
    if minutes is None or bucket not in BUCKET_RANGES:
        return False
    low, high = BUCKET_RANGES[bucket]
    return low <= minutes <= high


def observations_by_task(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        task_id = row.get("task_id", "")
        if task_id:
            grouped.setdefault(task_id, []).append(row)
    return grouped


def successful_minutes(rows: list[dict[str, str]]) -> list[int]:
    out: list[int] = []
    for row in rows:
        if row.get("outcome") not in {"solved", "completed", "pass"}:
            continue
        minutes = parse_minutes(row.get("observed_minutes", ""))
        if minutes is not None:
            out.append(minutes)
    return out


def minutes_summary(minutes: list[int]) -> str:
    if not minutes:
        return ""
    if len(minutes) == 1:
        return f"n=1; median={minutes[0]}; min={minutes[0]}; max={minutes[0]}"
    return (
        f"n={len(minutes)}; median={statistics.median(minutes):g}; "
        f"min={min(minutes)}; max={max(minutes)}"
    )


def audit_row(task: dict[str, str], task_observations: list[dict[str, str]]) -> dict[str, str]:
    bucket = task.get("human_time_bucket", "")
    p50 = parse_minutes(task.get("human_minutes_p50", ""))
    p90 = parse_minutes(task.get("human_minutes_p90", ""))
    issues: list[str] = []

    if bucket not in BUCKET_RANGES:
        issues.append("unknown_bucket")
    if p50 is None:
        issues.append("missing_or_invalid_p50")
    if p90 is None:
        issues.append("missing_or_invalid_p90")
    if p50 is not None and p90 is not None and p90 < p50:
        issues.append("p90_below_p50")
    p50_consistent = in_bucket(p50, bucket)
    if p50 is not None and bucket in BUCKET_RANGES and not p50_consistent:
        issues.append("p50_outside_bucket")

    manual_review = task.get("difficulty_review_status") == "manual_review_complete"
    if task.get("acceptance_status") == "accepted_v0" and not manual_review:
        issues.append("accepted_without_manual_review")

    minutes = successful_minutes(task_observations)
    if task.get("acceptance_status") == "accepted_v0" and not minutes:
        issues.append("accepted_without_independent_timing")

    if any(issue in issues for issue in ["unknown_bucket", "missing_or_invalid_p50", "missing_or_invalid_p90", "p90_below_p50", "p50_outside_bucket", "accepted_without_manual_review"]):
        status = "fail"
    elif "accepted_without_independent_timing" in issues:
        status = "caution"
    else:
        status = "pass"

    note = (
        "p50 is checked against the bucket range; p90 is allowed to exceed the bucket "
        "because it represents tail effort. Independent timing is required before freeze."
    )
    return {
        "task_id": task.get("task_id", ""),
        "split": task.get("split", ""),
        "acceptance_status": task.get("acceptance_status", ""),
        "family": task.get("family", ""),
        "human_time_bucket": bucket,
        "human_minutes_p50": task.get("human_minutes_p50", ""),
        "human_minutes_p90": task.get("human_minutes_p90", ""),
        "bucket_range_minutes": range_label(bucket),
        "p50_bucket_consistent": str(p50_consistent).lower(),
        "p90_at_or_above_p50": str(bool(p50 is not None and p90 is not None and p90 >= p50)).lower(),
        "estimate_confidence_level": confidence_level(task.get("human_estimate_confidence", "")),
        "manual_review_complete": str(manual_review).lower(),
        "independent_observation_count": str(len(task_observations)),
        "successful_independent_observation_count": str(len(minutes)),
        "observed_minutes_summary": minutes_summary(minutes),
        "calibration_status": status,
        "issues": json.dumps(issues),
        "notes": note,
    }


def write_markdown(path: Path, rows: list[dict[str, str]], observations: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row["calibration_status"] for row in rows)
    bucket_counts = Counter(row["human_time_bucket"] for row in rows)
    accepted = [row for row in rows if row["acceptance_status"] == "accepted_v0"]
    accepted_without_timing = [
        row for row in accepted
        if int(row["successful_independent_observation_count"]) == 0
    ]
    issue_counts: Counter[str] = Counter()
    for row in rows:
        issue_counts.update(json.loads(row["issues"]))

    accepted_lines = [
        "| task | bucket | p50/p90 | range | status | successful timings | issues |",
        "| --- | --- | ---: | --- | --- | ---: | --- |",
    ]
    for row in accepted:
        accepted_lines.append(
            f"| `{row['task_id']}` | {row['human_time_bucket']} | "
            f"{row['human_minutes_p50']}/{row['human_minutes_p90']} | "
            f"{row['bucket_range_minutes']} | {row['calibration_status']} | "
            f"{row['successful_independent_observation_count']} | `{row['issues']}` |"
        )

    lines = [
        "# Human-Time Calibration Audit",
        "",
        "This generated audit checks whether metadata human-time estimates are internally consistent and whether independent timing evidence exists. It does not convert author estimates into measured human times.",
        "",
        "## Summary",
        "",
        f"- tasks audited: `{len(rows)}`",
        f"- observation rows: `{len(observations)}`",
        f"- calibration statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- task buckets: `{compact_json(dict(sorted(bucket_counts.items())))}`",
        f"- issue counts: `{compact_json(dict(sorted(issue_counts.items())))}`",
        f"- accepted tasks without successful independent timing: `{len(accepted_without_timing)}/{len(accepted)}`",
        "",
        "## Accepted-Core Timing Rows",
        "",
        "\n".join(accepted_lines),
        "",
        "## Interpretation",
        "",
        "`pass` means the metadata estimate is internally consistent and any required timing evidence exists. `caution` means metadata is internally consistent but an accepted task lacks independent timing evidence. `fail` means a metadata inconsistency needs correction before the row should be used.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    observations = read_csv(ROOT / "data" / "human_time_observations.csv")
    grouped = observations_by_task(observations)
    rows = [audit_row(task, grouped.get(task.get("task_id", ""), [])) for task in metadata]
    write_csv(ROOT / "data" / "human_time_calibration_audit.csv", rows)
    write_markdown(ROOT / "reports" / "human_time_calibration_audit.md", rows, observations)
    print(
        "wrote data/human_time_calibration_audit.csv and "
        f"reports/human_time_calibration_audit.md with {len(rows)} task rows"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
