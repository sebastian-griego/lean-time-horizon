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
    "limitation",
    "next_action",
]

REQUIRED_REVIEW_FIELDS = {
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
}


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


def run_id(row: dict[str, str]) -> str:
    return f"{row.get('job_id', '')}:{row.get('task_id', '')}"


def label_set() -> set[str]:
    labels = {row.get("label", "") for row in read_csv(ROOT / "data" / "failure_labels.csv")}
    labels.add("none")
    return labels


def parse_secondary(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def transcript_text(queue_row: dict[str, str]) -> str:
    link = queue_row.get("transcript_link", "")
    if not link:
        return ""
    path = ROOT / link
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def row(
    check_id: str,
    area: str,
    status: str,
    evidence: str,
    limitation: str,
    next_action: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "status": status,
        "evidence": evidence,
        "limitation": limitation,
        "next_action": next_action,
    }


def build_rows() -> list[dict[str, str]]:
    queue = read_csv(ROOT / "data" / "transcript_review_queue.csv")
    reviews = read_csv(ROOT / "data" / "failure_label_reviews.csv")
    run_results = read_csv(ROOT / "data" / "run_results.csv")
    packet = (ROOT / "reports" / "transcript_review_packet.md").read_text(encoding="utf-8", errors="replace") if (ROOT / "reports" / "transcript_review_packet.md").exists() else ""

    review_fields = set(reviews[0].keys()) if reviews else set()
    review_ids = [review.get("run_id", "") for review in reviews]
    duplicate_review_ids = sorted(
        run_id_value for run_id_value, count in Counter(review_ids).items() if run_id_value and count > 1
    )
    queue_ids = {queue_row.get("run_id", "") for queue_row in queue}
    review_id_set = set(review_ids)
    model_run_ids = {
        run_id(run_row)
        for run_row in run_results
        if run_row.get("qa_stage") != "local_qa"
    }
    queue_by_id = {queue_row.get("run_id", ""): queue_row for queue_row in queue}
    run_by_id = {
        run_id(run_row): run_row
        for run_row in run_results
        if run_row.get("qa_stage") != "local_qa"
    }

    rows: list[dict[str, str]] = []

    schema_ok = (
        bool(reviews)
        and REQUIRED_REVIEW_FIELDS.issubset(review_fields)
        and not duplicate_review_ids
        and (ROOT / "data" / "failure_label_review_schema.json").exists()
    )
    rows.append(row(
        "review_schema",
        "schema",
        "pass" if schema_ok else "fail",
        (
            f"review rows={len(reviews)}; required_fields_covered={len(REQUIRED_REVIEW_FIELDS & review_fields)}/{len(REQUIRED_REVIEW_FIELDS)}; "
            f"duplicates={compact_json(duplicate_review_ids)}; schema_exists={(ROOT / 'data' / 'failure_label_review_schema.json').exists()}"
        ),
        "The schema records review metadata; it does not imply independent adjudication.",
        "Keep review rows keyed by run_id and update the schema before adding new review fields.",
    ))

    missing_reviews = sorted(queue_ids - review_id_set)
    extra_reviews = sorted(review_id_set - queue_ids)
    model_missing_queue = sorted(model_run_ids - queue_ids)
    coverage_ok = bool(queue) and not missing_reviews and not extra_reviews and not model_missing_queue
    rows.append(row(
        "queue_coverage",
        "coverage",
        "pass" if coverage_ok else "fail",
        (
            f"queue_rows={len(queue)}; review_rows={len(reviews)}; missing_reviews={compact_json(missing_reviews)}; "
            f"extra_reviews={compact_json(extra_reviews)}; model_rows_missing_queue={compact_json(model_missing_queue)}"
        ),
        "Coverage is over the tiny committed smoke queue only.",
        "After any provider sweep, regenerate the queue and add review rows before failure-taxonomy summaries.",
    ))

    labels = label_set()
    invalid_labels: list[str] = []
    none_on_failure: list[str] = []
    label_mismatches: list[str] = []
    for review in reviews:
        primary = review.get("primary_label", "")
        if primary not in labels:
            invalid_labels.append(f"{review.get('run_id', '')}:primary={primary}")
        for secondary in parse_secondary(review.get("secondary_labels", "")):
            if secondary not in labels or secondary == "none":
                invalid_labels.append(f"{review.get('run_id', '')}:secondary={secondary}")
        run = run_by_id.get(review.get("run_id", ""), {})
        if run and primary != run.get("failure_label", ""):
            label_mismatches.append(
                f"{review.get('run_id', '')}:review={primary}:run={run.get('failure_label', '')}"
            )
        if run and run.get("pass_at_k") not in {"1", "1.0"} and primary == "none":
            none_on_failure.append(review.get("run_id", ""))
    label_ok = not invalid_labels and not none_on_failure and not label_mismatches
    rows.append(row(
        "label_validity",
        "labels",
        "pass" if label_ok else "fail",
        (
            f"valid_labels={len(labels)}; invalid_labels={compact_json(invalid_labels)}; "
            f"none_on_failure={compact_json(none_on_failure)}; run_result_label_mismatches={compact_json(label_mismatches)}"
        ),
        "The review currently agrees with the run-record label; it has not been independently double-coded.",
        "Use a second reviewer for broader sweeps and adjudicate disagreements before reporting distributions.",
    ))

    missing_evidence: list[str] = []
    missing_rationale: list[str] = []
    for review in reviews:
        run_id_value = review.get("run_id", "")
        evidence = review.get("evidence_excerpt", "")
        rationale = review.get("rationale", "")
        text = transcript_text(queue_by_id.get(run_id_value, {}))
        if not evidence or evidence not in text:
            missing_evidence.append(run_id_value)
        if len(rationale.strip()) < 40:
            missing_rationale.append(run_id_value)
    evidence_ok = not missing_evidence and not missing_rationale
    rows.append(row(
        "transcript_evidence",
        "evidence",
        "pass" if evidence_ok else "fail",
        (
            f"evidence_excerpt_missing_or_not_in_transcript={compact_json(missing_evidence)}; "
            f"short_rationales={compact_json(missing_rationale)}"
        ),
        "Evidence excerpts are short anchors, not a substitute for full transcript inspection.",
        "Keep transcript files committed and cite concrete transcript text in every review row.",
    ))

    bad_confidence = [
        review.get("run_id", "")
        for review in reviews
        if review.get("confidence") not in {"low", "medium", "high"}
    ]
    bad_adjudication = [
        review.get("run_id", "")
        for review in reviews
        if review.get("adjudication_needed") not in {"true", "false"}
    ]
    adjudication_needed = [
        review.get("run_id", "")
        for review in reviews
        if review.get("adjudication_needed") == "true"
    ]
    reviewer_counts = Counter(review.get("reviewer_id", "") for review in reviews)
    review_meta_ok = not bad_confidence and not bad_adjudication
    rows.append(row(
        "review_metadata",
        "review_process",
        "pass" if review_meta_ok else "fail",
        (
            f"reviewers={compact_json(dict(sorted(reviewer_counts.items())))}; "
            f"bad_confidence={compact_json(bad_confidence)}; bad_adjudication_flags={compact_json(bad_adjudication)}; "
            f"adjudication_needed={compact_json(adjudication_needed)}"
        ),
        "All current rows are single internal reviews; this is weaker than independent adjudication.",
        "For research claims about failure distributions, require at least two reviewers or an explicit adjudication log.",
    ))

    boundary_phrase = "does not support distributional failure-mode claims"
    boundary_ok = boundary_phrase in packet
    rows.append(row(
        "claim_boundary",
        "claim_boundary",
        "pass" if boundary_ok else "fail",
        f"transcript_packet_mentions_distribution_boundary={boundary_ok}",
        "A reviewed smoke queue can support transcript-provenance claims only, not model-failure prevalence claims.",
        "Keep failure-taxonomy wording caveated until broad, independently adjudicated transcripts are available.",
    ))

    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row_data["status"] for row_data in rows)
    area_counts = Counter(row_data["area"] for row_data in rows)
    lines = [
        "# Failure Label Review Audit",
        "",
        "This generated audit checks the committed transcript-review adjudication file against the non-local transcript queue. It verifies queue coverage, label validity, transcript evidence excerpts, and claim-boundary wording. It does not create model results and does not make the smoke rows representative.",
        "",
        "## Summary",
        "",
        f"- checks: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- areas: `{compact_json(dict(sorted(area_counts.items())))}`",
        "",
        "## Check Table",
        "",
        "| check | area | status | evidence | limitation | next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row_data in rows:
        lines.append(
            f"| `{row_data['check_id']}` | {row_data['area']} | {row_data['status']} | "
            f"{escaped(row_data['evidence'])} | {escaped(row_data['limitation'])} | "
            f"{escaped(row_data['next_action'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`pass` means the committed review rows are internally consistent with the transcript queue and evidence excerpts. It does not mean the labels are independently adjudicated or sufficient for failure-mode distribution claims.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "failure_label_review_audit.csv", rows)
    write_markdown(ROOT / "reports" / "failure_label_review_audit.md", rows)
    failures = sum(1 for row_data in rows if row_data["status"] == "fail")
    print(
        "wrote data/failure_label_review_audit.csv and "
        f"reports/failure_label_review_audit.md with {len(rows)} checks; failures={failures}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
