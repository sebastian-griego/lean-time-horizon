from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

RELEASE_STATUSES = {"accepted_v0", "calibration_only", "candidate_review_pending"}
REQUIRED_RELEASE_WRONGS = 2
LEAK_PATTERNS = [
    "hidden/",
    "hidden\\",
    "PinCheck",
    "Reference.lean",
    "/wrong/",
    "\\wrong\\",
]

METADATA_PROJECTION_FIELDS = [
    "task_id",
    "title",
    "split",
    "family",
    "domain",
    "source_type",
    "human_time_bucket",
    "human_minutes_p50",
    "human_minutes_p90",
    "human_estimate_confidence",
    "skills",
    "scaffolds",
    "expected_failure_modes",
    "scaffold_sensitivity",
    "qa_status",
    "acceptance_status",
    "difficulty_review_status",
    "difficulty_review_notes",
    "public_files",
    "submission_file",
    "entry_file",
]

FIELDS = [
    "check_id",
    "area",
    "status",
    "evidence",
    "problems",
    "source_artifacts",
    "required_action",
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        return [], []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_row(
    check_id: str,
    area: str,
    evidence: str,
    problems: list[str],
    source_artifacts: list[str],
    required_action: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "status": "fail" if problems else "pass",
        "evidence": evidence,
        "problems": compact_json(problems[:24]),
        "source_artifacts": ";".join(source_artifacts),
        "required_action": required_action,
    }


def discover_tasks(root: Path) -> list[Path]:
    task_dirs: list[Path] = []
    for split in ["dev", "test", "candidates"]:
        base = root / "tasks" / split
        if base.exists():
            task_dirs.extend(sorted(path for path in base.iterdir() if (path / "metadata.json").exists()))
    return task_dirs


def load_tasks(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    return [(task_dir, read_json(task_dir / "metadata.json")) for task_dir in discover_tasks(root)]


def path_policy_problem(field: str, value: object, *, allow_metadata_prompt: bool = True) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return f"{field} must be a non-empty relative path string"
    if "\\" in value:
        return f"{field} uses backslash path separators: {value!r}"
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or (pure.parts and ":" in pure.parts[0]):
        return f"{field} must stay within the task directory: {value!r}"
    if any(part in {"hidden", "wrong"} for part in pure.parts):
        return f"{field} may not point at hidden or wrong assets: {value!r}"
    if not allow_metadata_prompt and value in {"Prompt.md", "metadata.json"}:
        return f"{field} must be a Lean public asset, not {value!r}"
    return None


def schema_record_problems(metadata: dict[str, Any], schema: dict[str, Any], record_id: str) -> list[str]:
    problems: list[str] = []
    properties = schema.get("properties", {}) if isinstance(schema.get("properties"), dict) else {}
    for field in schema.get("required", []):
        if field not in metadata:
            problems.append(f"{record_id}: missing required metadata field {field}")
            continue
        value = metadata[field]
        spec = properties.get(field, {}) if isinstance(properties.get(field), dict) else {}
        enum = spec.get("enum")
        if isinstance(enum, list) and value not in enum:
            problems.append(f"{record_id}: {field}={value!r} is not in enum {enum!r}")
        expected_type = spec.get("type")
        if expected_type == "string" and not isinstance(value, str):
            problems.append(f"{record_id}: {field} must be a string")
        elif expected_type == "integer":
            if not isinstance(value, int):
                problems.append(f"{record_id}: {field} must be an integer")
            elif isinstance(spec.get("minimum"), int) and value < spec["minimum"]:
                problems.append(f"{record_id}: {field} is below minimum {spec['minimum']}")
        elif expected_type == "array":
            if not isinstance(value, list):
                problems.append(f"{record_id}: {field} must be an array")
            else:
                item_spec = spec.get("items", {}) if isinstance(spec.get("items"), dict) else {}
                item_enum = item_spec.get("enum")
                item_type = item_spec.get("type")
                for index, item in enumerate(value):
                    if item_type == "string" and not isinstance(item, str):
                        problems.append(f"{record_id}: {field}[{index}] must be a string")
                    if isinstance(item_enum, list) and item not in item_enum:
                        problems.append(f"{record_id}: {field}[{index}]={item!r} is not in enum {item_enum!r}")
    return problems


def task_structure_problems(root: Path, task_dir: Path, metadata: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    task_id = str(metadata.get("task_id", task_dir.name))
    problems = schema_record_problems(metadata, schema, task_id)
    split = metadata.get("split")
    if split != task_dir.parent.name:
        problems.append(f"{task_id}: metadata split {split!r} does not match path split {task_dir.parent.name!r}")
    if not isinstance(metadata.get("task_id"), str) or not task_dir.name.startswith(str(metadata.get("task_id"))):
        problems.append(f"{task_id}: task directory name should start with task_id")

    public_files = metadata.get("public_files", ["Task.lean"])
    if not isinstance(public_files, list) or not public_files:
        problems.append(f"{task_id}: public_files must be a non-empty list")
        public_files = []
    if len(public_files) != len(set(str(item) for item in public_files)):
        problems.append(f"{task_id}: public_files contains duplicates")

    for required in ["Prompt.md", "metadata.json", "hidden/Reference.lean", "hidden/PinCheck.lean"]:
        if not (task_dir / required).exists():
            problems.append(f"{task_id}: missing {required}")

    for public_file in public_files:
        policy_problem = path_policy_problem("public_files[]", public_file, allow_metadata_prompt=False)
        if policy_problem:
            problems.append(f"{task_id}: {policy_problem}")
            continue
        if not (task_dir / public_file).exists():
            problems.append(f"{task_id}: public_files lists missing file {public_file}")

    submission_file = metadata.get("submission_file", "Task.lean")
    entry_file = metadata.get("entry_file", submission_file)
    for field, value in [("submission_file", submission_file), ("entry_file", entry_file)]:
        policy_problem = path_policy_problem(field, value, allow_metadata_prompt=False)
        if policy_problem:
            problems.append(f"{task_id}: {policy_problem}")
        elif value not in public_files:
            problems.append(f"{task_id}: {field} {value!r} is not listed in public_files")

    wrong_files = sorted((task_dir / "wrong").glob("*.lean")) if (task_dir / "wrong").exists() else []
    if not wrong_files:
        problems.append(f"{task_id}: no wrong submissions")
    status = metadata.get("acceptance_status")
    if status in RELEASE_STATUSES and len(wrong_files) < REQUIRED_RELEASE_WRONGS:
        problems.append(
            f"{task_id}: {status} tasks require at least {REQUIRED_RELEASE_WRONGS} wrong submissions"
        )
    if status == "accepted_v0" and metadata.get("human_time_bucket") in {"T0", "T1"}:
        problems.append(f"{task_id}: accepted_v0 should not use T0/T1 calibration bucket")
    return problems


def expected_metadata_projection(tasks: list[tuple[Path, dict[str, Any]]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for _, metadata in tasks:
        projected: dict[str, str] = {}
        for field in METADATA_PROJECTION_FIELDS:
            value = metadata.get(field, "")
            projected[field] = json.dumps(value) if isinstance(value, list) else str(value)
        rows.append(projected)
    return rows


def metadata_projection_problems(root: Path, tasks: list[tuple[Path, dict[str, Any]]]) -> list[str]:
    actual_rows, actual_fields = read_csv(root / "data" / "task_metadata.csv")
    expected_rows = expected_metadata_projection(tasks)
    problems: list[str] = []
    if actual_fields != METADATA_PROJECTION_FIELDS:
        problems.append(
            f"task_metadata.csv header mismatch: actual={actual_fields!r}; expected={METADATA_PROJECTION_FIELDS!r}"
        )
    if len(actual_rows) != len(expected_rows):
        problems.append(f"task_metadata.csv row count mismatch: actual={len(actual_rows)}; expected={len(expected_rows)}")
    for index, expected in enumerate(expected_rows):
        if index >= len(actual_rows):
            break
        actual = {field: actual_rows[index].get(field, "") for field in METADATA_PROJECTION_FIELDS}
        if actual == expected:
            continue
        changed = [field for field in METADATA_PROJECTION_FIELDS if actual.get(field, "") != expected.get(field, "")]
        task_id = expected.get("task_id", f"row_{index + 1}")
        examples = ", ".join(changed[:6])
        problems.append(f"task_metadata.csv row {index + 1} for {task_id} differs in {examples}")
        if len(problems) >= 12:
            break
    return problems


def exported_task_dirs(public_export: Path) -> list[Path]:
    return sorted(path.parent for path in public_export.rglob("metadata.json"))


def compare_public_asset(source: Path, exported: Path, task_id: str, relative_asset: str) -> list[str]:
    if not exported.exists():
        return [f"{task_id}: export missing {relative_asset}"]
    if sha256(source) != sha256(exported):
        return [f"{task_id}: export {relative_asset} does not match source"]
    return []


def public_export_problems(root: Path, public_export: Path, tasks: list[tuple[Path, dict[str, Any]]]) -> list[str]:
    problems: list[str] = []
    if not public_export.exists():
        return [f"public export does not exist: {public_export}"]

    source_by_rel = {
        task_dir.relative_to(root / "tasks").as_posix(): (task_dir, metadata)
        for task_dir, metadata in tasks
    }
    expected_rels = {
        task_dir.relative_to(root / "tasks").as_posix()
        for task_dir, metadata in tasks
        if metadata.get("acceptance_status") in RELEASE_STATUSES
    }
    actual_rels = {task_dir.relative_to(public_export).as_posix() for task_dir in exported_task_dirs(public_export)}
    for missing in sorted(expected_rels - actual_rels):
        problems.append(f"export missing release task {missing}")
    for extra in sorted(actual_rels - expected_rels):
        problems.append(f"export includes unexpected task {extra}")

    for exported_task in exported_task_dirs(public_export):
        exported_rel = exported_task.relative_to(public_export).as_posix()
        if exported_rel not in source_by_rel:
            continue
        source_task, metadata = source_by_rel[exported_rel]
        task_id = str(metadata.get("task_id", exported_task.name))
        if (exported_task / "hidden").exists():
            problems.append(f"{task_id}: export contains hidden directory")
        if (exported_task / "wrong").exists():
            problems.append(f"{task_id}: export contains wrong directory")

        public_names = ["Prompt.md", "metadata.json", *metadata.get("public_files", ["Task.lean"])]
        for asset in dict.fromkeys(public_names):
            problems.extend(compare_public_asset(source_task / asset, exported_task / asset, task_id, asset))

    for path in public_export.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".lean", ".md"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in LEAK_PATTERNS:
            if pattern in text:
                problems.append(f"exported public file {rel(path, public_export)} contains leak pattern {pattern!r}")
                break
    return problems


def build_rows(root: Path = ROOT, public_export: Path | None = None) -> list[dict[str, str]]:
    tasks = load_tasks(root)
    task_ids = [str(metadata.get("task_id", "")) for _, metadata in tasks]
    status_counts = Counter(str(metadata.get("acceptance_status", "")) for _, metadata in tasks)
    duplicate_ids = sorted(task_id for task_id, count in Counter(task_ids).items() if count > 1)
    inventory_problems = []
    if not tasks:
        inventory_problems.append("no tasks with metadata.json were discovered")
    for task_id in duplicate_ids:
        inventory_problems.append(f"duplicate task_id {task_id}")

    schema_path = root / "data" / "task_metadata_schema.json"
    schema = read_json(schema_path) if schema_path.exists() else {}
    structure_problems: list[str] = []
    for task_dir, metadata in tasks:
        structure_problems.extend(task_structure_problems(root, task_dir, metadata, schema))

    projection_problems = metadata_projection_problems(root, tasks)
    export_problems = public_export_problems(root, public_export, tasks) if public_export is not None else []

    rows = [
        check_row(
            "task_inventory",
            "source_tasks",
            (
                f"tasks={len(tasks)}; statuses={compact_json(dict(sorted(status_counts.items())))}; "
                f"duplicate_task_ids={len(duplicate_ids)}"
            ),
            inventory_problems,
            ["tasks/dev", "tasks/test", "tasks/candidates"],
            "Keep one unique task_id per tracked task metadata file.",
        ),
        check_row(
            "task_source_structure",
            "source_tasks",
            f"tasks_checked={len(tasks)}; release_statuses={compact_json(sorted(RELEASE_STATUSES))}",
            structure_problems,
            ["tasks/*/*/metadata.json", "data/task_metadata_schema.json"],
            (
                "Fix task metadata, public files, hidden checks, and wrong submissions before promoting "
                "or exporting a task."
            ),
        ),
        check_row(
            "task_metadata_csv_projection",
            "generated_data",
            (
                f"expected_rows={len(tasks)}; projection_fields={len(METADATA_PROJECTION_FIELDS)}; "
                f"csv_path=data/task_metadata.csv"
            ),
            projection_problems,
            ["data/task_metadata.csv", "tasks/*/*/metadata.json", "scripts/validate_all.py"],
            "Rerun scripts/validate_all.py after metadata edits and commit the regenerated CSV.",
        ),
    ]
    if public_export is not None:
        try:
            public_export_display = public_export.relative_to(root).as_posix()
        except ValueError:
            public_export_display = public_export.as_posix()
        rows.append(check_row(
            "public_export_bundle",
            "public_export",
            f"public_export={public_export_display}; expected_release_tasks={sum(1 for _, m in tasks if m.get('acceptance_status') in RELEASE_STATUSES)}",
            export_problems,
            ["public_tasks", "scripts/export_public_tasks.py", "scripts/validate_public_export.py"],
            "Regenerate the public export and remove any hidden, wrong, stale, or unexpected public assets.",
        ))
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row["status"] for row in rows)
    fail_rows = [row for row in rows if row["status"] == "fail"]
    lines = [
        "# Benchmark Package Audit",
        "",
        "This generated audit checks that source task metadata, required task assets, the committed metadata CSV, and the public export agree. It is intentionally lighter than full Lean validation, so it can run in PR CI as a packaging and release-integrity gate.",
        "",
        "## Summary",
        "",
        f"- checks: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- failed checks: `{len(fail_rows)}`",
        "",
        "## Check Table",
        "",
        "| check | area | status | evidence | problems | required action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['check_id']}` | {row['area']} | {row['status']} | "
            f"{escaped(row['evidence'])} | `{escaped(row['problems'])}` | "
            f"{escaped(row['required_action'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`pass` means the source bundle and exported public task package satisfy structural release invariants. This does not replace `validate_all.py`, hidden semantic pins, axiom audits, or independent task-quality review; it prevents stale metadata, missing assets, public-export drift, and accidental hidden-material exposure from passing unnoticed.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-export", type=Path, default=None)
    parser.add_argument("--csv-out", type=Path, default=ROOT / "data" / "benchmark_package_audit.csv")
    parser.add_argument("--report-out", type=Path, default=ROOT / "reports" / "benchmark_package_audit.md")
    args = parser.parse_args()

    public_export = args.public_export.resolve() if args.public_export else None
    rows = build_rows(ROOT, public_export)
    write_csv(args.csv_out, rows)
    write_markdown(args.report_out, rows)
    failures = sum(1 for row in rows if row["status"] == "fail")
    print(
        "wrote data/benchmark_package_audit.csv and reports/benchmark_package_audit.md "
        f"with {len(rows)} checks; failures={failures}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
