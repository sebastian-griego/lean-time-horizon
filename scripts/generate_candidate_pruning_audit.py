from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "task_id",
    "title",
    "split",
    "family",
    "domain",
    "acceptance_status",
    "pruning_decision",
    "counts_toward_accepted_core",
    "public_export_role",
    "human_time_bucket",
    "human_minutes_p50",
    "human_minutes_p90",
    "proof_lines",
    "tactic_profile",
    "automation_dominated",
    "hidden_pin_strength",
    "wrong_submission_count",
    "frontier_one_shot_likelihood",
    "diagnostic_value",
    "decision_flags",
    "decision_basis",
    "core_exclusion_reason",
    "retained_role",
    "next_action",
]

RELEASE_STATUSES = {"accepted_v0", "calibration_only", "candidate_review_pending"}


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


def as_bool(value: str) -> bool:
    return str(value).strip().lower() == "true"


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def pruning_decision(status: str) -> str:
    if status == "accepted_v0":
        return "accepted_core"
    if status == "calibration_only":
        return "retained_calibration_only"
    if status == "candidate_review_pending":
        return "pending_review"
    if status.startswith("rejected_"):
        return "rejected_archive"
    return "unclassified"


def public_export_role(status: str) -> str:
    if status in RELEASE_STATUSES:
        return "included_in_public_release_export"
    if status.startswith("rejected_"):
        return "retained_in_repo_not_exported"
    return "unclassified"


def decision_flags(status: str, audit: dict[str, str], quality: dict[str, str]) -> list[str]:
    flags: list[str] = []
    bucket = audit.get("manual_time_bucket", quality.get("human_time_bucket", ""))
    if bucket in {"T0", "T1"} and status != "accepted_v0":
        flags.append("lower_time_bucket")
    if as_bool(audit.get("mechanical_automation_dominated", quality.get("automation_dominated", ""))):
        flags.append("automation_dominated")
    if audit.get("manual_frontier_model_one_shot_likelihood") in {"likely", "very_likely"}:
        flags.append("likely_frontier_one_shot")
    if status == "calibration_only":
        flags.append("calibration_role")
    if status == "rejected_duplicate":
        flags.append("duplicate_role")
    if status == "rejected_too_easy":
        flags.append("too_easy_role")
    if status == "accepted_v0" and "caveat" in quality.get("benchmark_grade_status", ""):
        flags.append("accepted_with_caveat")
    if status == "accepted_v0":
        flags.append("accepted_core")
    if not flags:
        flags.append("manual_review_required")
    return flags


def core_exclusion_reason(status: str, metadata: dict[str, str], audit: dict[str, str]) -> str:
    note = metadata.get("difficulty_review_notes") or audit.get("manual_final_reason", "")
    if status == "accepted_v0":
        return "Counts toward accepted-core v0.1 task set, with any caveat recorded in the review note."
    if status == "calibration_only":
        return "Excluded from accepted-core performance claims and retained only for lower-bound calibration, harness regression, or simple semantic-pin checks."
    if status == "rejected_duplicate":
        return "Excluded from release/core claims because it duplicates an already retained calibration or capability role."
    if status == "rejected_too_easy":
        return "Excluded from release/core claims because the proof surface is too short, too local, automation dominated, or likely one-shot solvable."
    if status.startswith("rejected_"):
        return "Excluded from release/core claims by manual review."
    if status == "candidate_review_pending":
        return "Not accepted until reference, wrong submissions, hidden pins, metadata, and manual review pass."
    return note or "No core-exclusion reason recorded."


def retained_role(status: str) -> str:
    if status == "accepted_v0":
        return "accepted-core local task/grader validity evidence"
    if status == "calibration_only":
        return "release calibration and harness regression evidence"
    if status.startswith("rejected_"):
        return "pruning evidence retained in repo archive only"
    if status == "candidate_review_pending":
        return "candidate not eligible for benchmark claims"
    return "unclassified"


def next_action(status: str, quality: dict[str, str]) -> str:
    quality_action = quality.get("next_review_action", "").strip()
    if quality_action:
        return quality_action
    if status == "accepted_v0":
        return "Collect independent timing, model/scaffold evidence, and hosted QA before any locked benchmark claim."
    if status == "calibration_only":
        return "Keep excluded from accepted-core statistics unless revised into a larger diagnostic task and re-reviewed."
    if status.startswith("rejected_"):
        return "Keep archived for pruning transparency; do not export or count in benchmark statistics."
    if status == "candidate_review_pending":
        return "Run the full acceptance checklist before assigning a release role."
    return "Review manually before use."


def unique_join(parts: list[str]) -> str:
    seen: set[str] = set()
    out: list[str] = []
    for raw in parts:
        value = raw.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return " ".join(out)


def build_rows() -> list[dict[str, str]]:
    metadata_rows = read_csv(ROOT / "data" / "task_metadata.csv")
    difficulty = {row["task_id"]: row for row in read_csv(ROOT / "data" / "difficulty_audit.csv")}
    quality = {row["task_id"]: row for row in read_csv(ROOT / "data" / "task_quality_matrix.csv")}
    rows: list[dict[str, str]] = []
    for metadata in metadata_rows:
        task_id = metadata["task_id"]
        audit = difficulty.get(task_id, {})
        quality_row = quality.get(task_id, {})
        status = metadata.get("acceptance_status", "")
        flags = decision_flags(status, audit, quality_row)
        basis_parts = [metadata.get("difficulty_review_notes", ""), audit.get("manual_final_reason", "")]
        rows.append({
            "task_id": task_id,
            "title": metadata.get("title", ""),
            "split": metadata.get("split", ""),
            "family": metadata.get("family", ""),
            "domain": metadata.get("domain", ""),
            "acceptance_status": status,
            "pruning_decision": pruning_decision(status),
            "counts_toward_accepted_core": "true" if status == "accepted_v0" else "false",
            "public_export_role": public_export_role(status),
            "human_time_bucket": metadata.get("human_time_bucket", ""),
            "human_minutes_p50": metadata.get("human_minutes_p50", ""),
            "human_minutes_p90": metadata.get("human_minutes_p90", ""),
            "proof_lines": audit.get("mechanical_reference_proof_lines", quality_row.get("proof_lines", "")),
            "tactic_profile": audit.get("mechanical_tactic_profile", quality_row.get("tactic_profile", "")),
            "automation_dominated": audit.get("mechanical_automation_dominated", quality_row.get("automation_dominated", "")),
            "hidden_pin_strength": audit.get("mechanical_hidden_pin_strength", quality_row.get("hidden_pin_strength", "")),
            "wrong_submission_count": audit.get("mechanical_wrong_submission_count", quality_row.get("wrong_submission_count", "")),
            "frontier_one_shot_likelihood": audit.get("manual_frontier_model_one_shot_likelihood", quality_row.get("frontier_one_shot_likelihood", "")),
            "diagnostic_value": audit.get("manual_diagnostic_value", quality_row.get("diagnostic_value", "")),
            "decision_flags": ";".join(flags),
            "decision_basis": unique_join(basis_parts),
            "core_exclusion_reason": core_exclusion_reason(status, metadata, audit),
            "retained_role": retained_role(status),
            "next_action": next_action(status, quality_row),
        })
    return rows


def status_table(rows: list[dict[str, str]]) -> str:
    counts = Counter(row["acceptance_status"] for row in rows)
    decision_counts = Counter(row["pruning_decision"] for row in rows)
    lines = [
        f"- acceptance statuses: `{compact_json(dict(sorted(counts.items())))}`",
        f"- pruning decisions: `{compact_json(dict(sorted(decision_counts.items())))}`",
        f"- accepted-core rate: `{sum(1 for row in rows if row['acceptance_status'] == 'accepted_v0')}/{len(rows)}`",
    ]
    return "\n".join(lines)


def family_table(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "_None._"
    families = sorted({row["family"] for row in rows})
    statuses = ["accepted_v0", "calibration_only", "rejected_duplicate", "rejected_too_easy"]
    lines = [
        "| family | " + " | ".join(statuses) + " |",
        "| --- | " + " | ".join("---:" for _ in statuses) + " |",
    ]
    for family in families:
        counts = Counter(row["acceptance_status"] for row in rows if row["family"] == family)
        lines.append(
            f"| `{family}` | " + " | ".join(str(counts.get(status, 0)) for status in statuses) + " |"
        )
    return "\n".join(lines)


def decision_table(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "_None._"
    lines = [
        "| task | status | bucket | proof lines | automation | one-shot | pins | wrongs | core decision basis |",
        "| --- | --- | --- | ---: | --- | --- | --- | ---: | --- |",
    ]
    for row in rows:
        basis = escaped(row["core_exclusion_reason"])
        lines.append(
            f"| `{row['task_id']}` | {row['acceptance_status']} | {row['human_time_bucket']} | "
            f"{row['proof_lines']} | {row['automation_dominated']} | "
            f"{row['frontier_one_shot_likelihood']} | {row['hidden_pin_strength']} | "
            f"{row['wrong_submission_count']} | {basis} |"
        )
    return "\n".join(lines)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    accepted = [row for row in rows if row["acceptance_status"] == "accepted_v0"]
    calibration = [row for row in rows if row["acceptance_status"] == "calibration_only"]
    rejected = [row for row in rows if row["acceptance_status"].startswith("rejected_")]
    automation_rejected = [
        row for row in rejected
        if as_bool(row["automation_dominated"]) or "too_easy_role" in row["decision_flags"]
    ]
    lines = [
        "# Candidate Pruning Audit",
        "",
        "This generated audit makes the v0.1 pruning decision visible for every tracked task. It joins metadata, difficulty-audit signals, and the task-quality matrix so the small accepted core is explained by task-quality review rather than by directory placement or model performance.",
        "",
        "The audit is not a new acceptance decision. `metadata.json`, `reports/accepted_task_review.md`, and the validation scripts remain authoritative.",
        "",
        "## Summary",
        "",
        status_table(rows),
        f"- calibration-only rows: `{len(calibration)}`",
        f"- rejected archive rows: `{len(rejected)}`",
        f"- rejected rows flagged too easy or automation dominated: `{len(automation_rejected)}/{len(rejected)}`",
        "",
        "## Family By Status",
        "",
        family_table(rows),
        "",
        "## Decision Ledger",
        "",
        decision_table(rows),
        "",
        "## Interpretation",
        "",
        "Accepted rows are the only rows eligible for accepted-core task-quality summaries. Calibration rows may be exported for lower-bound and harness checks but stay out of accepted-core performance claims. Rejected rows are retained in the repository only as pruning evidence and are not exported as public release tasks. The current accepted core remains below the target benchmark size because many candidates were too short, duplicated another role, or were likely to be solved one-shot.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    csv_out = ROOT / "data" / "candidate_pruning_audit.csv"
    md_out = ROOT / "reports" / "candidate_pruning_audit.md"
    write_csv(csv_out, rows)
    write_markdown(md_out, rows)
    print(f"wrote {csv_out.relative_to(ROOT)} and {md_out.relative_to(ROOT)} with {len(rows)} task rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
