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
    "human_time_bucket",
    "human_minutes_p50",
    "human_minutes_p90",
    "minimum_reviewer_count_before_freeze",
    "recommended_reviewer_profile",
    "recommended_timing_condition",
    "max_single_session_minutes",
    "validation_command",
    "ambiguity_review_prompt",
    "notes_required",
]

TEMPLATE_FIELDS = [
    "task_id",
    "reviewer_id_hash",
    "reviewer_role",
    "observed_minutes",
    "outcome",
    "date_utc",
    "notes",
    "scaffold_used",
    "lookup_used",
    "compile_feedback_used",
    "prompt_ambiguity",
    "validation_passed",
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


def accepted_tasks() -> list[dict[str, str]]:
    return [
        row for row in read_csv(ROOT / "data" / "task_metadata.csv")
        if row.get("acceptance_status") == "accepted_v0"
    ]


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


def session_cap(bucket: str, p90: str) -> str:
    try:
        p90_minutes = int(p90)
    except ValueError:
        p90_minutes = 180
    if bucket == "T4":
        return "split sessions allowed; record elapsed active minutes and wall-clock breaks"
    return str(max(60, min(360, p90_minutes + 30)))


def timing_condition(bucket: str) -> str:
    if bucket in {"T3", "T4"}:
        return "public prompt plus public scaffold; read-only lookup allowed only if recorded; compile/debug feedback allowed only if recorded"
    return "public prompt plus public scaffold; use one consistent condition per reviewer and record lookup/compile feedback use"


def build_plan_rows(tasks: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for task in tasks:
        task_id = task.get("task_id", "")
        rows.append({
            "task_id": task_id,
            "title": task.get("title", ""),
            "split": task.get("split", ""),
            "family": task.get("family", ""),
            "human_time_bucket": task.get("human_time_bucket", ""),
            "human_minutes_p50": task.get("human_minutes_p50", ""),
            "human_minutes_p90": task.get("human_minutes_p90", ""),
            "minimum_reviewer_count_before_freeze": "1",
            "recommended_reviewer_profile": "Lean user who did not author or repair this task; record relevant Mathlib/verification background in notes",
            "recommended_timing_condition": timing_condition(task.get("human_time_bucket", "")),
            "max_single_session_minutes": session_cap(task.get("human_time_bucket", ""), task.get("human_minutes_p90", "")),
            "validation_command": validation_command(task_id),
            "ambiguity_review_prompt": "Record any prompt ambiguity, unstated-assumption concern, or mismatch between observed effort and metadata p50/p90.",
            "notes_required": "background; scaffold condition; whether lookup was used; whether compile/debug feedback was used; ambiguity; validation outcome",
        })
    return rows


def build_template_rows(tasks: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for task in tasks:
        rows.append({
            "task_id": task.get("task_id", ""),
            "reviewer_id_hash": "",
            "reviewer_role": "",
            "observed_minutes": "",
            "outcome": "",
            "date_utc": "",
            "notes": "",
            "scaffold_used": "",
            "lookup_used": "",
            "compile_feedback_used": "",
            "prompt_ambiguity": "",
            "validation_passed": "",
        })
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, plan_rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bucket_counts = Counter(row["human_time_bucket"] for row in plan_rows)
    family_counts = Counter(row["family"] for row in plan_rows)
    lines = [
        "# Human Timing Collection Packet",
        "",
        "This generated packet tells independent Lean reviewers how to collect timing evidence for accepted tasks. It does not contain measured human timings and must not be used as a substitute for `data/human_time_observations.csv` rows from real solves.",
        "",
        "## Summary",
        "",
        f"- accepted tasks requiring timing: `{len(plan_rows)}`",
        f"- bucket counts: `{compact_json(dict(sorted(bucket_counts.items())))}`",
        f"- family counts: `{compact_json(dict(sorted(family_counts.items())))}`",
        "- minimum timing requirement before freeze: `one independent successful solve or second-review timing note per accepted task`",
        "- observation data file: `data/human_time_observations.csv`",
        "- blank reviewer template: `data/human_time_observations_template.csv`",
        "",
        "## Collection Rules",
        "",
        "1. Use a reviewer who did not author, repair, or manually tune the task.",
        "2. Start timing after the reviewer opens the public prompt and public scaffold; stop timing at the first submission that passes local validation, or at timeout/abandonment.",
        "3. Record active working minutes. For long tasks, exclude breaks but note split sessions in `notes`.",
        "4. Record scaffold condition exactly: `one-shot`, `lookup`, or `lookup_unlimited`; also record whether lookup or compile/debug feedback was actually used.",
        "5. Validate the final solution with the task-specific validation command before recording `validation_passed=true`.",
        "6. Record prompt ambiguity, missing-context concerns, and any reason the metadata p50/p90 should change.",
        "",
        "## Accepted Task Timing Plan",
        "",
        "| task | bucket | p50/p90 | reviewer profile | condition | session cap | validation command |",
        "| --- | --- | ---: | --- | --- | --- | --- |",
    ]
    for row in plan_rows:
        lines.append(
            f"| `{row['task_id']}` | {row['human_time_bucket']} | "
            f"{row['human_minutes_p50']}/{row['human_minutes_p90']} | "
            f"{escaped(row['recommended_reviewer_profile'])} | "
            f"{escaped(row['recommended_timing_condition'])} | "
            f"{escaped(row['max_single_session_minutes'])} | "
            f"`{escaped(row['validation_command'])}` |"
        )
    lines.extend([
        "",
        "## Observation Row Guidance",
        "",
        "`reviewer_id_hash` should be a stable pseudonymous hash, not a name or email. `outcome` should use the values allowed by `data/human_time_observations_schema.json`: `solved`, `completed`, `pass`, `partial`, `unsolved`, `timeout`, or `abandoned`. The additional template fields are collection aids; the canonical audit currently reads the schema-required columns and preserves the rest as reviewer notes.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    tasks = accepted_tasks()
    plan_rows = build_plan_rows(tasks)
    template_rows = build_template_rows(tasks)
    write_csv(ROOT / "data" / "human_timing_collection_plan.csv", plan_rows, PLAN_FIELDS)
    write_csv(ROOT / "data" / "human_time_observations_template.csv", template_rows, TEMPLATE_FIELDS)
    write_markdown(ROOT / "reports" / "human_timing_collection_packet.md", plan_rows)
    print(
        "wrote data/human_timing_collection_plan.csv, "
        "data/human_time_observations_template.csv, and "
        f"reports/human_timing_collection_packet.md for {len(plan_rows)} accepted tasks"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
