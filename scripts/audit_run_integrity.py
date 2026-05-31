from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "row_index",
    "task_id",
    "qa_stage",
    "model",
    "model_version",
    "scaffold",
    "job_id",
    "transcript_link",
    "transcript_exists",
    "transcript_parse_ok",
    "transcript_records",
    "matching_transcript_records",
    "attempts_total",
    "attempts_completed",
    "k",
    "successes_out_of_k",
    "pass_at_k",
    "score_values_count",
    "score_values_successes",
    "metadata_match_ok",
    "arithmetic_ok",
    "failure_label_known",
    "transcript_consistency_ok",
    "integrity_status",
    "issues",
]

KNOWN_QA_STAGES = {"local_qa", "model_sweep"}
KNOWN_QA_STATUSES = {"passed", "expected_failure", "unreviewed"}


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


def as_int(value: str) -> int | None:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def as_float(value: str) -> float | None:
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def score_values(value: str) -> list[int] | None:
    if value is None:
        return None
    parts = [part.strip() for part in str(value).split(",") if part.strip()]
    scores: list[int] = []
    for part in parts:
        numeric = as_float(part)
        if numeric is None or numeric not in {0.0, 1.0}:
            return None
        scores.append(1 if numeric == 1.0 else 0)
    return scores


def known_failure_labels() -> set[str]:
    labels = {"none"}
    for row in read_csv(ROOT / "data" / "failure_labels.csv"):
        label = row.get("label", "").strip()
        if label:
            labels.add(label)
    return labels


def metadata_by_task() -> dict[str, dict[str, str]]:
    return {row["task_id"]: row for row in read_csv(ROOT / "data" / "task_metadata.csv")}


def read_transcript(path: Path) -> tuple[bool, list[dict[str, object]], str]:
    if not path.exists():
        return False, [], "missing transcript file"
    records: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            return False, records, f"line {line_number} JSON parse error: {exc}"
        if not isinstance(item, dict):
            return False, records, f"line {line_number} is not a JSON object"
        records.append(item)
    return True, records, ""


def transcript_path(row: dict[str, str]) -> Path:
    link = row.get("transcript_link", "")
    return (ROOT / link).resolve()


def matching_records(row: dict[str, str], records: list[dict[str, object]]) -> list[dict[str, object]]:
    task_id = row.get("task_id", "")
    scaffold = row.get("scaffold", "")
    row_model = row.get("model", "")
    model_version = row.get("model_version", "")
    allowed_models = {row_model, model_version}
    return [
        item for item in records
        if str(item.get("task_id", "")) == task_id
        and str(item.get("scaffold", "")) == scaffold
        and str(item.get("model", "")) in allowed_models
    ]


def validate_row(index: int, row: dict[str, str], task_metadata: dict[str, dict[str, str]], known_labels: set[str]) -> dict[str, str]:
    issues: list[str] = []
    warnings: list[str] = []
    task_id = row.get("task_id", "")
    metadata = task_metadata.get(task_id)
    if metadata is None:
        issues.append("task_id not found in task_metadata")
        metadata_ok = False
    else:
        metadata_ok = (
            row.get("split") == metadata.get("split")
            and row.get("family") == metadata.get("family")
        )
        if not metadata_ok:
            issues.append("split/family mismatch with task_metadata")

    attempts_total = as_int(row.get("attempts_total", ""))
    attempts_completed = as_int(row.get("attempts_completed", ""))
    k = as_int(row.get("k", ""))
    successes = as_int(row.get("successes_out_of_k", ""))
    pass_at_k = as_float(row.get("pass_at_k", ""))
    timeouts = as_int(row.get("timeout_count", ""))
    infra_fails = as_int(row.get("infra_fail_count", ""))
    scores = score_values(row.get("score_values", ""))
    numeric_values = [attempts_total, attempts_completed, k, successes, pass_at_k, timeouts, infra_fails]
    if any(value is None for value in numeric_values):
        issues.append("nonnumeric run-result field")
    if scores is None:
        issues.append("score_values is not a comma-separated 0/1 list")
        score_count = 0
        score_successes = 0
    else:
        score_count = len(scores)
        score_successes = sum(scores)

    arithmetic_ok = True
    if attempts_total is not None and attempts_completed is not None and attempts_completed > attempts_total:
        arithmetic_ok = False
        issues.append("attempts_completed exceeds attempts_total")
    if k is not None and successes is not None and successes > k:
        arithmetic_ok = False
        issues.append("successes_out_of_k exceeds k")
    if attempts_completed is not None and score_count != attempts_completed:
        arithmetic_ok = False
        issues.append("score_values count does not match attempts_completed")
    if successes is not None and score_successes != successes:
        arithmetic_ok = False
        issues.append("score_values successes do not match successes_out_of_k")
    if successes is not None and pass_at_k is not None:
        expected_pass = 1.0 if successes > 0 else 0.0
        if pass_at_k != expected_pass:
            arithmetic_ok = False
            issues.append("pass_at_k does not equal binary successes_out_of_k")

    label = row.get("failure_label", "")
    label_known = label in known_labels
    if not label_known:
        issues.append(f"unknown failure_label: {label}")
    if pass_at_k == 1.0 and label != "none":
        issues.append("successful row has non-none failure_label")
    if pass_at_k == 0.0 and label == "none":
        issues.append("failed row has none failure_label")
    if infra_fails is not None and infra_fails > 0 and label != "infra_failure":
        issues.append("infra_fail_count is positive but failure_label is not infra_failure")

    if row.get("qa_stage") not in KNOWN_QA_STAGES:
        issues.append("unknown qa_stage")
    if row.get("qa_findings_status") not in KNOWN_QA_STATUSES:
        warnings.append("unknown qa_findings_status")

    transcript = transcript_path(row)
    exists = transcript.exists()
    parse_ok, records, parse_issue = read_transcript(transcript)
    if not exists:
        issues.append("transcript file missing")
    elif not parse_ok:
        issues.append(parse_issue)
    matches = matching_records(row, records) if parse_ok else []
    transcript_ok = bool(matches)
    if not matches:
        issues.append("no matching transcript record for task/scaffold/model")
    else:
        transcript_scores = [as_int(str(item.get("score", ""))) for item in matches]
        transcript_successes = sum(1 for score in transcript_scores if score == 1)
        transcript_labels = {str(item.get("primary_failure_label", "")) for item in matches}
        if score_successes != transcript_successes:
            transcript_ok = False
            issues.append("transcript scores do not match score_values successes")
        if label not in transcript_labels and label != "none":
            transcript_ok = False
            issues.append("failure_label not present in matching transcript labels")
        if label == "none" and "none" not in transcript_labels:
            transcript_ok = False
            issues.append("successful row missing none transcript label")
        if len(matches) != (attempts_completed or 0):
            transcript_ok = False
            issues.append("matching transcript record count does not match attempts_completed")

    status = "pass"
    if issues:
        status = "fail"
    elif warnings:
        status = "warn"

    return {
        "row_index": str(index),
        "task_id": task_id,
        "qa_stage": row.get("qa_stage", ""),
        "model": row.get("model", ""),
        "model_version": row.get("model_version", ""),
        "scaffold": row.get("scaffold", ""),
        "job_id": row.get("job_id", ""),
        "transcript_link": row.get("transcript_link", ""),
        "transcript_exists": str(exists).lower(),
        "transcript_parse_ok": str(parse_ok).lower(),
        "transcript_records": str(len(records)),
        "matching_transcript_records": str(len(matches)),
        "attempts_total": row.get("attempts_total", ""),
        "attempts_completed": row.get("attempts_completed", ""),
        "k": row.get("k", ""),
        "successes_out_of_k": row.get("successes_out_of_k", ""),
        "pass_at_k": row.get("pass_at_k", ""),
        "score_values_count": str(score_count),
        "score_values_successes": str(score_successes),
        "metadata_match_ok": str(metadata_ok).lower(),
        "arithmetic_ok": str(arithmetic_ok).lower(),
        "failure_label_known": str(label_known).lower(),
        "transcript_consistency_ok": str(transcript_ok).lower(),
        "integrity_status": status,
        "issues": "; ".join(issues + warnings),
    }


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row["integrity_status"] for row in rows)
    qa_counts = Counter(row["qa_stage"] for row in rows)
    model_counts = Counter(row["model"] for row in rows)
    transcript_missing = sum(row["transcript_exists"] != "true" for row in rows)
    parse_failures = sum(row["transcript_parse_ok"] != "true" for row in rows)
    arithmetic_failures = sum(row["arithmetic_ok"] != "true" for row in rows)
    transcript_failures = sum(row["transcript_consistency_ok"] != "true" for row in rows)
    failure_rows = [row for row in rows if row["integrity_status"] == "fail"]
    warn_rows = [row for row in rows if row["integrity_status"] == "warn"]
    lines = [
        "# Run Result Integrity Audit",
        "",
        "This generated audit checks `data/run_results.csv` against task metadata, known failure labels, pass@k arithmetic, score vectors, and JSONL transcript files. It is evidence for data hygiene only; it does not add model-performance evidence.",
        "",
        "## Summary",
        "",
        f"- rows checked: `{len(rows)}`",
        f"- integrity statuses: `{json.dumps(dict(sorted(status_counts.items())), sort_keys=True)}`",
        f"- qa stages: `{json.dumps(dict(sorted(qa_counts.items())), sort_keys=True)}`",
        f"- model/source rows: `{json.dumps(dict(sorted(model_counts.items())), sort_keys=True)}`",
        f"- missing transcript files: `{transcript_missing}`",
        f"- transcript parse failures: `{parse_failures}`",
        f"- pass@k arithmetic failures: `{arithmetic_failures}`",
        f"- transcript consistency failures: `{transcript_failures}`",
        "",
        "## Failed Rows",
        "",
    ]
    if failure_rows:
        lines.extend([
            "| row | task | model | qa stage | issue |",
            "| ---: | --- | --- | --- | --- |",
        ])
        for row in failure_rows:
            lines.append(f"| {row['row_index']} | `{row['task_id']}` | {row['model']} | {row['qa_stage']} | {escaped(row['issues'])} |")
    else:
        lines.append("_None._")
    lines.extend([
        "",
        "## Warning Rows",
        "",
    ])
    if warn_rows:
        lines.extend([
            "| row | task | model | qa stage | warning |",
            "| ---: | --- | --- | --- | --- |",
        ])
        for row in warn_rows:
            lines.append(f"| {row['row_index']} | `{row['task_id']}` | {row['model']} | {row['qa_stage']} | {escaped(row['issues'])} |")
    else:
        lines.append("_None._")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "A passing row means the committed run-result row is internally consistent with its transcript and metadata. Provider rows remain smoke evidence unless the planned accepted-core scaffold sweep is actually covered.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    run_rows = read_csv(ROOT / "data" / "run_results.csv")
    task_metadata = metadata_by_task()
    labels = known_failure_labels()
    rows = [validate_row(index, row, task_metadata, labels) for index, row in enumerate(run_rows, start=1)]
    write_csv(ROOT / "data" / "run_integrity_audit.csv", rows)
    write_markdown(ROOT / "reports" / "run_integrity_audit.md", rows)
    failures = sum(1 for row in rows if row["integrity_status"] == "fail")
    print(f"wrote data/run_integrity_audit.csv and reports/run_integrity_audit.md with {len(rows)} rows; failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
