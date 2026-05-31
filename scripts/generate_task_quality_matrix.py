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
    "acceptance_status",
    "release_role",
    "benchmark_grade_status",
    "family",
    "domain",
    "human_time_bucket",
    "human_minutes_p50",
    "human_minutes_p90",
    "proof_lines",
    "declaration_count",
    "public_file_count",
    "public_lemma_count",
    "automation_dominated",
    "tactic_profile",
    "mathlib_use",
    "multi_file_context",
    "hidden_pin_strength",
    "hidden_check_count",
    "hidden_example_count",
    "wrong_submission_count",
    "frontier_one_shot_likelihood",
    "diagnostic_value",
    "scaffold_sensitivity",
    "requires_library_search",
    "requires_decomposition",
    "requires_semantic_formalization",
    "requires_proof_debugging",
    "requires_codebase_navigation",
    "requires_invariant_design",
    "requires_long_horizon_construction",
    "manual_review_note",
    "next_review_action",
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


def as_bool(value: str) -> bool:
    return str(value).strip().lower() == "true"


def release_role(status: str) -> str:
    if status == "accepted_v0":
        return "accepted_core"
    if status == "calibration_only":
        return "calibration_release"
    if status == "candidate_review_pending":
        return "pending_candidate"
    if status.startswith("rejected_"):
        return "rejected_archive"
    return "unclassified"


def benchmark_grade_status(metadata: dict[str, str], audit: dict[str, str]) -> str:
    status = metadata.get("acceptance_status", "")
    notes = metadata.get("difficulty_review_notes", "").lower()
    automation = as_bool(audit.get("mechanical_automation_dominated", "false"))
    if status == "accepted_v0":
        if "caveat" in notes or automation:
            return "accepted_core_with_caveat"
        return "accepted_core_retained"
    if status == "calibration_only":
        return "calibration_only"
    if status == "candidate_review_pending":
        return "pending_review"
    if status.startswith("rejected_"):
        return "rejected_archive"
    return status or "unknown"


def next_review_action(status: str, grade: str, audit: dict[str, str], metadata: dict[str, str]) -> str:
    if grade == "accepted_core_with_caveat":
        return (
            "Retain in v0.1 only with the recorded caveat; collect independent human timing, "
            "full scaffold sweep evidence, and external QA before freeze."
        )
    if grade == "accepted_core_retained":
        if metadata.get("human_time_bucket") in {"T3", "T4"}:
            return (
                "Independently time at least one human solve and run the planned scaffold sweep "
                "before using this as long-horizon evidence."
            )
        return (
            "Collect independent timing, hosted QA, and accepted-core scaffold/model evidence "
            "before benchmark freeze."
        )
    if status == "calibration_only":
        return "Exclude from core performance claims; use only for lower-bound calibration and harness regression checks."
    if status == "candidate_review_pending":
        return "Do not export as benchmark-grade until reference, wrong submissions, hidden pins, and manual review all pass."
    if status == "rejected_too_easy":
        return "Keep archived as pruning evidence; exclude because the proof surface is too automation-dominated or local."
    if status == "rejected_duplicate":
        return "Keep archived as pruning evidence; exclude because it duplicates a retained calibration or core capability."
    if status == "rejected_grader_weak":
        return "Keep archived until grading can reject weakened or off-target solutions."
    if status.startswith("rejected_"):
        return "Keep archived for auditability; exclude from release and model-performance claims."
    return "Review status is unclassified; do not use in benchmark claims."


def matrix_rows(metadata_rows: list[dict[str, str]], audit_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    audit_by_id = {row["task_id"]: row for row in audit_rows}
    rows: list[dict[str, str]] = []
    for metadata in metadata_rows:
        task_id = metadata["task_id"]
        audit = audit_by_id.get(task_id, {})
        status = metadata.get("acceptance_status", "")
        grade = benchmark_grade_status(metadata, audit)
        rows.append({
            "task_id": task_id,
            "title": metadata.get("title", ""),
            "split": metadata.get("split", ""),
            "acceptance_status": status,
            "release_role": release_role(status),
            "benchmark_grade_status": grade,
            "family": metadata.get("family", ""),
            "domain": metadata.get("domain", ""),
            "human_time_bucket": metadata.get("human_time_bucket", ""),
            "human_minutes_p50": metadata.get("human_minutes_p50", ""),
            "human_minutes_p90": metadata.get("human_minutes_p90", ""),
            "proof_lines": audit.get("mechanical_reference_proof_lines", ""),
            "declaration_count": audit.get("mechanical_declaration_count", ""),
            "public_file_count": audit.get("mechanical_file_count", ""),
            "public_lemma_count": audit.get("mechanical_public_lemma_count", ""),
            "automation_dominated": audit.get("mechanical_automation_dominated", ""),
            "tactic_profile": audit.get("mechanical_tactic_profile", ""),
            "mathlib_use": audit.get("mechanical_mathlib_required", ""),
            "multi_file_context": audit.get("mechanical_multifile_context", ""),
            "hidden_pin_strength": audit.get("mechanical_hidden_pin_strength", ""),
            "hidden_check_count": audit.get("mechanical_hidden_check_count", ""),
            "hidden_example_count": audit.get("mechanical_hidden_example_count", ""),
            "wrong_submission_count": audit.get("mechanical_wrong_submission_count", ""),
            "frontier_one_shot_likelihood": audit.get("manual_frontier_model_one_shot_likelihood", ""),
            "diagnostic_value": audit.get("manual_diagnostic_value", ""),
            "scaffold_sensitivity": audit.get("manual_scaffold_sensitivity", metadata.get("scaffold_sensitivity", "")),
            "requires_library_search": audit.get("requires_library_search", ""),
            "requires_decomposition": audit.get("requires_decomposition", ""),
            "requires_semantic_formalization": audit.get("requires_semantic_formalization", ""),
            "requires_proof_debugging": audit.get("requires_proof_debugging", ""),
            "requires_codebase_navigation": audit.get("requires_codebase_navigation", ""),
            "requires_invariant_design": audit.get("requires_invariant_design", ""),
            "requires_long_horizon_construction": audit.get("requires_long_horizon_construction", ""),
            "manual_review_note": metadata.get("difficulty_review_notes", ""),
            "next_review_action": next_review_action(status, grade, audit, metadata),
        })
    return rows


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def md_bool(value: str) -> str:
    return "yes" if as_bool(value) else "no"


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def accepted_table(rows: list[dict[str, str]]) -> str:
    accepted = [row for row in rows if row["release_role"] == "accepted_core"]
    if not accepted:
        return "_None._"
    lines = [
        "| task | grade | family | bucket | proof lines | automation | pins | wrongs | one-shot | diagnostic | next review action |",
        "| --- | --- | --- | --- | ---: | --- | --- | ---: | --- | --- | --- |",
    ]
    for row in accepted:
        lines.append(
            f"| `{row['task_id']}` | {row['benchmark_grade_status']} | {row['family']} | "
            f"{row['human_time_bucket']} | {row['proof_lines']} | {md_bool(row['automation_dominated'])} | "
            f"{row['hidden_pin_strength']} | {row['wrong_submission_count']} | "
            f"{row['frontier_one_shot_likelihood']} | {row['diagnostic_value']} | "
            f"{escaped(row['next_review_action'])} |"
        )
    return "\n".join(lines)


def calibration_table(rows: list[dict[str, str]]) -> str:
    calibration = [row for row in rows if row["release_role"] == "calibration_release"]
    if not calibration:
        return "_None._"
    lines = [
        "| task | family | bucket | proof lines | automation | pins | wrongs | one-shot | diagnostic role |",
        "| --- | --- | --- | ---: | --- | --- | ---: | --- | --- |",
    ]
    for row in calibration:
        note = escaped(row["manual_review_note"])
        lines.append(
            f"| `{row['task_id']}` | {row['family']} | {row['human_time_bucket']} | {row['proof_lines']} | "
            f"{md_bool(row['automation_dominated'])} | {row['hidden_pin_strength']} | "
            f"{row['wrong_submission_count']} | {row['frontier_one_shot_likelihood']} | {note} |"
        )
    return "\n".join(lines)


def rejected_summary(rows: list[dict[str, str]]) -> str:
    rejected = [row for row in rows if row["release_role"] == "rejected_archive"]
    if not rejected:
        return "_None._"
    status_counts = Counter(row["acceptance_status"] for row in rejected)
    family_counts = Counter(row["family"] for row in rejected)
    automation_count = sum(1 for row in rejected if as_bool(row["automation_dominated"]))
    return "\n".join([
        f"- rejected rows: `{len(rejected)}`",
        f"- rejection statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- rejected families: `{compact_json(dict(sorted(family_counts.items())))}`",
        f"- automation-dominated rejected rows: `{automation_count}`",
    ])


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    grade_counts = Counter(row["benchmark_grade_status"] for row in rows)
    role_counts = Counter(row["release_role"] for row in rows)
    accepted = [row for row in rows if row["release_role"] == "accepted_core"]
    accepted_caveats = [row for row in accepted if row["benchmark_grade_status"] == "accepted_core_with_caveat"]
    accepted_automation = [row for row in accepted if as_bool(row["automation_dominated"])]
    accepted_likely = [row for row in accepted if row["frontier_one_shot_likelihood"] in {"likely", "very_likely"}]
    lines = [
        "# Task Quality Matrix",
        "",
        "This generated matrix joins task metadata with the difficulty audit so reviewers can inspect one row per task without treating directory placement as acceptance. It is not an acceptance decision by itself; `metadata.json`, `reports/accepted_task_review.md`, and the validation scripts remain authoritative.",
        "",
        "## Status Counts",
        "",
        f"- release roles: `{compact_json(dict(sorted(role_counts.items())))}`",
        f"- benchmark-grade statuses: `{compact_json(dict(sorted(grade_counts.items())))}`",
        f"- accepted-core caveat rows: `{len(accepted_caveats)}/{len(accepted)}`",
        f"- accepted-core automation-dominated rows: `{len(accepted_automation)}/{len(accepted)}`",
        f"- accepted-core likely/very-likely one-shot rows: `{len(accepted_likely)}/{len(accepted)}`",
        "",
        "## Accepted Core Matrix",
        "",
        accepted_table(rows),
        "",
        "## Calibration Matrix",
        "",
        calibration_table(rows),
        "",
        "## Rejected Archive Summary",
        "",
        rejected_summary(rows),
        "",
        "## Interpretation",
        "",
        "Rows marked `accepted_core_with_caveat` are retained in v0.1 only because their task context still gives diagnostic signal despite automation or finite-pin limitations. Calibration rows should not enter benchmark performance claims. Rejected rows are kept to make pruning decisions auditable.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    difficulty = read_csv(ROOT / "data" / "difficulty_audit.csv")
    rows = matrix_rows(metadata, difficulty)
    csv_out = ROOT / "data" / "task_quality_matrix.csv"
    md_out = ROOT / "reports" / "task_quality_matrix.md"
    write_csv(csv_out, rows)
    write_markdown(md_out, rows)
    print(f"wrote {csv_out.relative_to(ROOT)} and {md_out.relative_to(ROOT)} with {len(rows)} task rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
