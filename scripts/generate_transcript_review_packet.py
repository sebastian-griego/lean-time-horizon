from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

QUEUE_FIELDS = [
    "run_id",
    "task_id",
    "split",
    "family",
    "scaffold",
    "model",
    "model_version",
    "job_id",
    "k",
    "pass_at_k",
    "failure_label_current",
    "qa_findings_status",
    "transcript_link",
    "transcript_exists",
    "transcript_record_count",
    "transcript_labels",
    "review_priority",
    "review_action",
]

TEMPLATE_FIELDS = [
    "run_id",
    "task_id",
    "reviewer_id",
    "review_timestamp_utc",
    "primary_label",
    "secondary_labels",
    "confidence",
    "rationale",
    "evidence_excerpt",
    "adjudication_needed",
    "adjudication_notes",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def load_transcript(path_text: str) -> tuple[bool, int, list[str]]:
    if not path_text:
        return False, 0, []
    path = ROOT / path_text
    if not path.exists():
        return False, 0, []
    labels: list[str] = []
    count = 0
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.strip():
                continue
            count += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                labels.append("<json_error>")
                continue
            label = str(record.get("primary_failure_label", ""))
            if label:
                labels.append(label)
    return True, count, sorted(set(labels))


def run_id(row: dict[str, str]) -> str:
    return f"{row.get('job_id', '')}:{row.get('task_id', '')}"


def review_priority(row: dict[str, str], transcript_exists: bool, transcript_labels: list[str]) -> tuple[str, str]:
    if row.get("qa_stage") == "local_qa":
        return "exclude_local_qa", "Local QA rows validate grader behavior; do not use them for model-failure distributions."
    if not transcript_exists:
        return "critical", "Find or regenerate the missing transcript before using this row."
    if row.get("infra_fail_count") not in {"", "0", 0}:
        return "medium", "Confirm this is an infrastructure failure and record whether the row should be rerun."
    if row.get("pass_at_k") in {"1", "1.0"}:
        return "low", "Confirm success transcript and keep primary label `none`."
    if row.get("failure_label") == "none":
        return "high", "Failed model row has `none`; assign a primary failure label before analysis."
    if row.get("failure_label") not in transcript_labels:
        return "high", "Run-result label and transcript label disagree; inspect and adjudicate."
    if row.get("qa_findings_status") == "unreviewed":
        return "high", "Review failed non-infra model row and record rationale."
    return "medium", "Review label rationale before using this row in failure-taxonomy analysis."


def build_queue() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in read_csv(ROOT / "data" / "run_results.csv"):
        transcript_exists, record_count, transcript_labels = load_transcript(row.get("transcript_link", ""))
        priority, action = review_priority(row, transcript_exists, transcript_labels)
        if priority == "exclude_local_qa":
            continue
        rows.append({
            "run_id": run_id(row),
            "task_id": row.get("task_id", ""),
            "split": row.get("split", ""),
            "family": row.get("family", ""),
            "scaffold": row.get("scaffold", ""),
            "model": row.get("model", ""),
            "model_version": row.get("model_version", ""),
            "job_id": row.get("job_id", ""),
            "k": row.get("k", ""),
            "pass_at_k": row.get("pass_at_k", ""),
            "failure_label_current": row.get("failure_label", ""),
            "qa_findings_status": row.get("qa_findings_status", ""),
            "transcript_link": row.get("transcript_link", ""),
            "transcript_exists": str(transcript_exists).lower(),
            "transcript_record_count": str(record_count),
            "transcript_labels": compact_json(transcript_labels),
            "review_priority": priority,
            "review_action": action,
        })
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    rows.sort(key=lambda item: (priority_order.get(item["review_priority"], 9), item["task_id"], item["run_id"]))
    return rows


def build_template(queue_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    template_rows: list[dict[str, str]] = []
    for row in queue_rows:
        template_rows.append({
            "run_id": row["run_id"],
            "task_id": row["task_id"],
            "reviewer_id": "",
            "review_timestamp_utc": "",
            "primary_label": "",
            "secondary_labels": "",
            "confidence": "",
            "rationale": "",
            "evidence_excerpt": "",
            "adjudication_needed": "",
            "adjudication_notes": "",
        })
    return template_rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, queue_rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    labels = read_csv(ROOT / "data" / "failure_labels.csv")
    if not any(row.get("label") == "none" for row in labels):
        labels = [{"label": "none", "description": "attempt succeeded; no failure label applies"}] + labels
    review_rows = read_csv(ROOT / "data" / "failure_label_reviews.csv")
    review_run_ids = {row.get("run_id", "") for row in review_rows}
    queue_run_ids = {row.get("run_id", "") for row in queue_rows}
    reviewed_queue_rows = queue_run_ids & review_run_ids
    reviews_needing_adjudication = [
        row for row in review_rows
        if row.get("adjudication_needed") == "true"
    ]
    priority_counts = Counter(row["review_priority"] for row in queue_rows)
    label_counts = Counter(row["failure_label_current"] for row in queue_rows)
    status_counts = Counter(row["qa_findings_status"] for row in queue_rows)
    lines = [
        "# Transcript Review Packet",
        "",
        "This generated packet turns committed non-local transcripts into a review queue for failure-label adjudication. It does not create new model results and does not change `data/run_results.csv`; reviewers should fill `data/failure_label_review_template.csv` after inspecting transcripts. A separate `data/failure_label_reviews.csv` file may record completed single-review adjudications, but the current smoke queue does not support distributional failure-mode claims.",
        "",
        "## Summary",
        "",
        f"- queued non-local rows: `{len(queue_rows)}`",
        f"- queue rows with committed single-review adjudication: `{len(reviewed_queue_rows)}/{len(queue_rows)}`",
        f"- review rows needing adjudication: `{len(reviews_needing_adjudication)}`",
        f"- review priorities: `{compact_json(dict(sorted(priority_counts.items())))}`",
        f"- current failure labels: `{compact_json(dict(sorted(label_counts.items())))}`",
        f"- QA finding statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        "",
        "## Label Codebook",
        "",
        "| label | description |",
        "| --- | --- |",
    ]
    for row in labels:
        lines.append(f"| `{row.get('label', '')}` | {escaped(row.get('description', ''))} |")
    lines.extend([
        "",
        "## Review Rules",
        "",
        "1. Review failed non-infra model rows before using failure-label distributions.",
        "2. Mark `infra_failure`, `timeout`, or `reward_hack_attempt` before cognitive labels when applicable.",
        "3. Use one primary label for the dominant failure and secondary labels only when the transcript has separable causes.",
        "4. Record a short evidence excerpt and rationale; do not infer a label from task metadata alone.",
        "5. If two reviewers disagree, set `adjudication_needed=true` in the template and resolve before reporting distributions.",
        "",
        "## Review Queue",
        "",
        "| priority | run id | task | scaffold | pass@k | current label | transcript | action |",
        "| --- | --- | --- | --- | ---: | --- | --- | --- |",
    ])
    for row in queue_rows:
        lines.append(
            f"| {row['review_priority']} | `{escaped(row['run_id'])}` | `{row['task_id']}` | "
            f"{row['scaffold']} | {row['pass_at_k']} | `{row['failure_label_current']}` | "
            f"`{escaped(row['transcript_link'])}` | {escaped(row['review_action'])} |"
        )
    lines.extend([
        "",
        "## Output Template",
        "",
        "`data/failure_label_review_template.csv` contains one blank review row for each queued non-local run. It is intentionally blank so that committed review labels are not fabricated from existing run metadata.",
        "",
        "## Completed Single-Review Rows",
        "",
        "`data/failure_label_reviews.csv` records any completed single-review adjudication rows. These rows can be audited for transcript-evidence consistency, but they are not independent adjudication and should not be summarized as failure-mode prevalence.",
        "",
        "| run id | primary label | confidence | adjudication needed |",
        "| --- | --- | --- | --- |",
    ])
    for row in review_rows:
        lines.append(
            f"| `{escaped(row.get('run_id', ''))}` | `{row.get('primary_label', '')}` | "
            f"{row.get('confidence', '')} | {row.get('adjudication_needed', '')} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    queue_rows = build_queue()
    template_rows = build_template(queue_rows)
    write_csv(ROOT / "data" / "transcript_review_queue.csv", queue_rows, QUEUE_FIELDS)
    write_csv(ROOT / "data" / "failure_label_review_template.csv", template_rows, TEMPLATE_FIELDS)
    write_markdown(ROOT / "reports" / "transcript_review_packet.md", queue_rows)
    print(
        "wrote data/transcript_review_queue.csv, data/failure_label_review_template.csv, "
        f"and reports/transcript_review_packet.md with {len(queue_rows)} queued rows"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
