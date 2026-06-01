from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PLAN_FIELDS = [
    "task_id",
    "title",
    "split",
    "family",
    "domain",
    "human_time_bucket",
    "human_minutes_p50",
    "human_minutes_p90",
    "benchmark_grade_status",
    "automation_dominated",
    "hidden_pin_strength",
    "wrong_submission_count",
    "frontier_one_shot_likelihood",
    "diagnostic_value",
    "required_reviewer_profile",
    "review_scope",
    "review_questions",
    "validation_command",
]

TEMPLATE_FIELDS = [
    "task_id",
    "reviewer_id_hash",
    "reviewer_role",
    "review_date_utc",
    "reviewed_public_assets_only",
    "hidden_grader_files_inspected",
    "validation_command_run",
    "prompt_clarity",
    "time_bucket_assessment",
    "diagnostic_value_assessment",
    "hidden_pin_assessment",
    "wrong_submission_assessment",
    "automation_caveat_acknowledged",
    "benchmark_grade_recommendation",
    "notes",
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


def task_dir_for_id(task_id: str) -> Path | None:
    for split in ["dev", "test", "candidates"]:
        base = ROOT / "tasks" / split
        if not base.exists():
            continue
        for task_dir in base.iterdir():
            metadata_path = task_dir / "metadata.json"
            if not metadata_path.exists():
                continue
            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if metadata.get("task_id") == task_id:
                return task_dir
    return None


def validation_command(task_id: str) -> str:
    task_dir = task_dir_for_id(task_id)
    if task_dir is None:
        return f"python scripts/validate_task.py <task-dir-for-{task_id}> --submission <reviewer-solution.lean> --expect pass"
    relative = task_dir.relative_to(ROOT).as_posix()
    return f"python scripts/validate_task.py {relative} --submission <reviewer-solution.lean> --expect pass"


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def build_plan_rows() -> list[dict[str, str]]:
    metadata = [
        row for row in read_csv(ROOT / "data" / "task_metadata.csv")
        if row.get("acceptance_status") == "accepted_v0"
    ]
    difficulty = {row["task_id"]: row for row in read_csv(ROOT / "data" / "difficulty_audit.csv")}
    quality = {row["task_id"]: row for row in read_csv(ROOT / "data" / "task_quality_matrix.csv")}
    rows: list[dict[str, str]] = []
    for task in metadata:
        task_id = task["task_id"]
        audit = difficulty.get(task_id, {})
        quality_row = quality.get(task_id, {})
        questions = [
            "Does the public prompt state the intended deliverable and edit scope clearly?",
            "Does the stated human-time bucket look plausible for a competent Lean reviewer?",
            "Do the hidden-pin and wrong-submission summaries make reward hacking or weakening unlikely?",
            "Would likely model failures be diagnostically interpretable?",
            "Should this row stay accepted, stay accepted with caveat, be revised, or be downgraded?",
        ]
        rows.append({
            "task_id": task_id,
            "title": task.get("title", ""),
            "split": task.get("split", ""),
            "family": task.get("family", ""),
            "domain": task.get("domain", ""),
            "human_time_bucket": task.get("human_time_bucket", ""),
            "human_minutes_p50": task.get("human_minutes_p50", ""),
            "human_minutes_p90": task.get("human_minutes_p90", ""),
            "benchmark_grade_status": quality_row.get("benchmark_grade_status", ""),
            "automation_dominated": audit.get("mechanical_automation_dominated", ""),
            "hidden_pin_strength": audit.get("mechanical_hidden_pin_strength", ""),
            "wrong_submission_count": audit.get("mechanical_wrong_submission_count", ""),
            "frontier_one_shot_likelihood": audit.get("manual_frontier_model_one_shot_likelihood", ""),
            "diagnostic_value": audit.get("manual_diagnostic_value", ""),
            "required_reviewer_profile": "Lean user who did not author, repair, or manually tune this task; reviewer should record relevant Mathlib or verification background in notes.",
            "review_scope": "Review public prompt/scaffold, metadata, accepted task card, hidden-pin summary, wrong-submission summary, and local validation command. Do not copy hidden proof contents into review notes.",
            "review_questions": " ".join(questions),
            "validation_command": validation_command(task_id),
        })
    return rows


def build_template_rows(plan_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "task_id": row["task_id"],
            "reviewer_id_hash": "",
            "reviewer_role": "",
            "review_date_utc": "",
            "reviewed_public_assets_only": "",
            "hidden_grader_files_inspected": "",
            "validation_command_run": "",
            "prompt_clarity": "",
            "time_bucket_assessment": "",
            "diagnostic_value_assessment": "",
            "hidden_pin_assessment": "",
            "wrong_submission_assessment": "",
            "automation_caveat_acknowledged": "",
            "benchmark_grade_recommendation": "",
            "notes": "",
        }
        for row in plan_rows
    ]


def write_markdown(path: Path, plan_rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    family_counts = Counter(row["family"] for row in plan_rows)
    bucket_counts = Counter(row["human_time_bucket"] for row in plan_rows)
    caveat_count = sum(1 for row in plan_rows if "caveat" in row["benchmark_grade_status"])
    automation_count = sum(1 for row in plan_rows if row["automation_dominated"] == "true")
    lines = [
        "# Independent Task Review Packet",
        "",
        "This generated packet gives non-author Lean reviewers a structured way to review accepted_v0 task quality. It does not contain completed independent reviews and must not be cited as independent validation evidence.",
        "",
        "## Summary",
        "",
        f"- accepted tasks requiring independent review: `{len(plan_rows)}`",
        f"- family counts: `{compact_json(dict(sorted(family_counts.items())))}`",
        f"- bucket counts: `{compact_json(dict(sorted(bucket_counts.items())))}`",
        f"- accepted rows already carrying caveats: `{caveat_count}/{len(plan_rows)}`",
        f"- automation-dominated accepted rows: `{automation_count}/{len(plan_rows)}`",
        "- observation data file: `data/independent_task_reviews.csv`",
        "- blank reviewer template: `data/independent_task_review_template.csv`",
        "- review schema: `data/independent_task_review_schema.json`",
        "",
        "## Review Rules",
        "",
        "1. Use a reviewer who did not author, repair, or manually tune the task.",
        "2. Review only public task assets, metadata, generated review cards, and generated summaries unless the reviewer is explicitly doing a hidden-grader audit.",
        "3. Do not paste hidden reference proofs or hidden PinCheck contents into review notes.",
        "4. Record whether hidden grader files were inspected. A public-only review and a hidden-grader audit support different claims.",
        "5. Record whether the validation command was run and whether the reviewer actually solved the task.",
        "6. Treat `keep_with_caveat`, `revise`, `downgrade`, and `reject` as useful outcomes, not failures of the review process.",
        "",
        "Allowed template values:",
        "",
        "- `prompt_clarity`: `clear`, `minor_ambiguity`, `major_ambiguity`, `uncertain`",
        "- `time_bucket_assessment`: `too_low`, `plausible`, `too_high`, `uncertain`",
        "- `diagnostic_value_assessment`: `high`, `medium`, `low`, `uncertain`",
        "- `hidden_pin_assessment`: `adequate`, `needs_strengthening`, `not_applicable`, `uncertain`",
        "- `wrong_submission_assessment`: `meaningful`, `too_signature_based`, `insufficient`, `uncertain`",
        "- `benchmark_grade_recommendation`: `keep`, `keep_with_caveat`, `revise`, `downgrade`, `reject`",
        "",
        "## Review Plan",
        "",
        "| task | family | bucket | caveat | automation | pins | wrongs | one-shot | validation command |",
        "| --- | --- | --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for row in plan_rows:
        lines.append(
            f"| `{row['task_id']}` | {row['family']} | {row['human_time_bucket']} | "
            f"{row['benchmark_grade_status']} | {row['automation_dominated']} | "
            f"{row['hidden_pin_strength']} | {row['wrong_submission_count']} | "
            f"{row['frontier_one_shot_likelihood']} | `{escaped(row['validation_command'])}` |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "This packet makes independent review collection operational, but the committed observation file is the authority for whether independent review has actually happened. Until real rows are committed and audited, accepted-task quality remains an internal-review claim with caveats.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    plan_rows = build_plan_rows()
    template_rows = build_template_rows(plan_rows)
    write_csv(ROOT / "data" / "independent_task_review_plan.csv", plan_rows, PLAN_FIELDS)
    write_csv(ROOT / "data" / "independent_task_review_template.csv", template_rows, TEMPLATE_FIELDS)
    write_markdown(ROOT / "reports" / "independent_task_review_packet.md", plan_rows)
    print(
        "wrote data/independent_task_review_plan.csv, "
        "data/independent_task_review_template.csv, and "
        f"reports/independent_task_review_packet.md for {len(plan_rows)} accepted tasks"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
