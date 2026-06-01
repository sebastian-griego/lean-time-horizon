from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "dataset_id",
    "path",
    "schema_path",
    "record_scope",
    "row_count",
    "column_count",
    "required_fields_present",
    "validation_status",
    "error_count",
    "error_examples",
    "coverage_note",
    "limitation",
    "next_action",
]

TASK_METADATA_CSV_FIELDS = [
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

RECOMMENDED_FAILURE_LABELS = {
    "library_search",
    "premise_selection",
    "theorem_decomposition",
    "semantic_formalization",
    "hidden_pin_failure",
    "proof_debugging",
    "codebase_navigation",
    "invariant_design",
    "termination",
    "timeout",
    "reward_hack_attempt",
    "grader_false_negative",
    "infra_failure",
}


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        return [], []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader), list(reader.fieldnames or [])


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def discover_task_metadata() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split in ["dev", "test", "candidates"]:
        base = ROOT / "tasks" / split
        if not base.exists():
            continue
        for metadata_path in sorted(base.glob("*/metadata.json")):
            data = read_json(metadata_path)
            data["_path"] = metadata_path.relative_to(ROOT).as_posix()
            rows.append(data)
    return rows


def coerce_csv_value(value: str, spec: dict[str, Any]) -> tuple[bool, str]:
    expected_type = spec.get("type")
    if expected_type == "integer":
        try:
            parsed = int(value)
        except ValueError:
            return False, "not_integer"
        minimum = spec.get("minimum")
        if isinstance(minimum, int) and parsed < minimum:
            return False, f"below_minimum_{minimum}"
    elif expected_type == "number":
        try:
            parsed_float = float(value)
        except ValueError:
            return False, "not_number"
        minimum = spec.get("minimum")
        maximum = spec.get("maximum")
        if isinstance(minimum, (int, float)) and parsed_float < minimum:
            return False, f"below_minimum_{minimum}"
        if isinstance(maximum, (int, float)) and parsed_float > maximum:
            return False, f"above_maximum_{maximum}"
    elif expected_type == "array":
        try:
            parsed_json = json.loads(value)
        except json.JSONDecodeError:
            return False, "not_json_array"
        if not isinstance(parsed_json, list):
            return False, "not_array"
    enum = spec.get("enum")
    if enum is not None and value not in enum:
        return False, f"not_in_enum_{enum}"
    return True, ""


def validate_object_record(record: dict[str, Any], schema: dict[str, Any], record_id: str) -> list[str]:
    errors: list[str] = []
    properties = schema.get("properties", {})
    for field in schema.get("required", []):
        if field not in record:
            errors.append(f"{record_id}: missing {field}")
            continue
        value = record[field]
        spec = properties.get(field, {})
        expected_type = spec.get("type")
        if expected_type == "string" and not isinstance(value, str):
            errors.append(f"{record_id}: {field} not string")
        elif expected_type == "integer":
            if not isinstance(value, int):
                errors.append(f"{record_id}: {field} not integer")
            elif isinstance(spec.get("minimum"), int) and value < spec["minimum"]:
                errors.append(f"{record_id}: {field} below minimum")
        elif expected_type == "array" and not isinstance(value, list):
            errors.append(f"{record_id}: {field} not array")
        if "enum" in spec and value not in spec["enum"]:
            errors.append(f"{record_id}: {field} not in enum")
    return errors


def validate_csv_rows(rows: list[dict[str, str]], fields: list[str], schema: dict[str, Any], record_id_field: str) -> list[str]:
    errors: list[str] = []
    required = list(schema.get("required", []))
    properties = schema.get("properties", {})
    missing_fields = [field for field in required if field not in fields]
    for field in missing_fields:
        errors.append(f"header: missing {field}")
    for index, row in enumerate(rows):
        record_id = row.get(record_id_field) or f"row_{index + 1}"
        for field in required:
            if field not in row:
                continue
            ok, message = coerce_csv_value(row.get(field, ""), properties.get(field, {}))
            if not ok:
                errors.append(f"{record_id}: {field} {message}")
    return errors


def row(
    dataset_id: str,
    path: str,
    schema_path: str,
    record_scope: str,
    row_count: int,
    column_count: int,
    required_fields_present: bool,
    validation_status: str,
    errors: list[str],
    coverage_note: str,
    limitation: str,
    next_action: str,
) -> dict[str, str]:
    return {
        "dataset_id": dataset_id,
        "path": path,
        "schema_path": schema_path,
        "record_scope": record_scope,
        "row_count": str(row_count),
        "column_count": str(column_count),
        "required_fields_present": str(required_fields_present).lower(),
        "validation_status": validation_status,
        "error_count": str(len(errors)),
        "error_examples": compact_json(errors[:8]),
        "coverage_note": coverage_note,
        "limitation": limitation,
        "next_action": next_action,
    }


def build_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    task_schema = read_json(ROOT / "data" / "task_metadata_schema.json")
    metadata_json_rows = discover_task_metadata()
    metadata_errors: list[str] = []
    for item in metadata_json_rows:
        metadata_errors.extend(validate_object_record(item, task_schema, item.get("task_id", item.get("_path", "unknown"))))
    rows.append(row(
        "task_metadata_json",
        "tasks/*/*/metadata.json",
        "data/task_metadata_schema.json",
        "per_task_source_metadata",
        len(metadata_json_rows),
        len(task_schema.get("properties", {})),
        not metadata_errors,
        "schema_valid" if not metadata_errors else "schema_error",
        metadata_errors,
        "Per-task metadata JSON is the authoritative full metadata surface.",
        "The aggregate CSV is a generated projection and intentionally omits some grader-only metadata fields.",
        "Keep metadata.json as the source of truth and rerun validate_all.py after metadata edits.",
    ))

    metadata_csv_rows, metadata_csv_fields = read_csv(ROOT / "data" / "task_metadata.csv")
    missing_projection_fields = [field for field in TASK_METADATA_CSV_FIELDS if field not in metadata_csv_fields]
    extra_projection_fields = [field for field in metadata_csv_fields if field not in TASK_METADATA_CSV_FIELDS]
    projection_errors = missing_projection_fields + extra_projection_fields
    if len(metadata_csv_rows) != len(metadata_json_rows):
        projection_errors.append(f"row_count_mismatch_csv={len(metadata_csv_rows)} json={len(metadata_json_rows)}")
    rows.append(row(
        "task_metadata_csv_projection",
        "data/task_metadata.csv",
        "data/task_metadata_schema.json",
        "generated_metadata_projection",
        len(metadata_csv_rows),
        len(metadata_csv_fields),
        not missing_projection_fields,
        "documented_projection" if not projection_errors else "projection_mismatch",
        projection_errors,
        "CSV columns match the validate_all.py projection used by reports.",
        "This CSV is not the full schema-bearing metadata record; use metadata.json for hidden grading declarations and task-specific bans.",
        "If report columns change, update validate_all.py and this manifest together.",
    ))

    run_schema = read_json(ROOT / "data" / "run_results_schema.json")
    run_rows, run_fields = read_csv(ROOT / "data" / "run_results.csv")
    run_errors = validate_csv_rows(run_rows, run_fields, run_schema, "job_id")
    rows.append(row(
        "run_results",
        "data/run_results.csv",
        "data/run_results_schema.json",
        "attempt_row_data",
        len(run_rows),
        len(run_fields),
        all(field in run_fields for field in run_schema.get("required", [])),
        "schema_valid" if not run_errors else "schema_error",
        run_errors,
        "Run-result rows validate against required columns, enums, numeric ranges, and pass@k field types.",
        "Schema validation does not prove sample-size adequacy or model-result representativeness.",
        "Run scripts/audit_run_integrity.py after edits to check transcript and arithmetic semantics.",
    ))

    failure_schema = read_json(ROOT / "data" / "failure_label_schema.json")
    annotation_rows, annotation_fields = read_csv(ROOT / "data" / "failure_annotations.csv")
    annotation_errors = validate_csv_rows(annotation_rows, annotation_fields, failure_schema, "run_id")
    rows.append(row(
        "failure_annotations",
        "data/failure_annotations.csv",
        "data/failure_label_schema.json",
        "adjudicated_failure_label_rows",
        len(annotation_rows),
        len(annotation_fields),
        all(field in annotation_fields for field in failure_schema.get("required", [])),
        "empty_ready" if not annotation_rows and not annotation_errors else ("schema_valid" if not annotation_errors else "schema_error"),
        annotation_errors,
        "The adjudicated-failure table has schema-compatible headers but no broad-run rows yet.",
        "Empty adjudication data cannot support failure-distribution claims.",
        "Populate after broad provider sweeps and independent transcript review.",
    ))

    review_schema = read_json(ROOT / "data" / "failure_label_review_schema.json")
    review_rows, review_fields = read_csv(ROOT / "data" / "failure_label_reviews.csv")
    review_errors = validate_csv_rows(review_rows, review_fields, review_schema, "run_id")
    rows.append(row(
        "failure_label_reviews",
        "data/failure_label_reviews.csv",
        "data/failure_label_review_schema.json",
        "single_review_smoke_adjudications",
        len(review_rows),
        len(review_fields),
        all(field in review_fields for field in review_schema.get("required", [])),
        "schema_valid" if not review_errors else "schema_error",
        review_errors,
        "Committed smoke transcript reviews satisfy the review-row schema.",
        "These are single-review smoke rows, not independent distributional adjudication.",
        "Use the transcript review packet and adjudication fields for future broad sweeps.",
    ))

    timing_schema = read_json(ROOT / "data" / "human_time_observations_schema.json")
    timing_rows, timing_fields = read_csv(ROOT / "data" / "human_time_observations.csv")
    timing_errors = validate_csv_rows(timing_rows, timing_fields, timing_schema, "task_id")
    rows.append(row(
        "human_time_observations",
        "data/human_time_observations.csv",
        "data/human_time_observations_schema.json",
        "independent_human_timing",
        len(timing_rows),
        len(timing_fields),
        all(field in timing_fields for field in timing_schema.get("required", [])),
        "empty_ready" if not timing_rows and not timing_errors else ("schema_valid" if not timing_errors else "schema_error"),
        timing_errors,
        "The timing-observation table has schema-compatible headers but no independent observations yet.",
        "Author/reviewer estimates remain uncalibrated by independent timed solves.",
        "Collect non-author timing rows before strengthening time-horizon claims.",
    ))

    task_review_schema = read_json(ROOT / "data" / "independent_task_review_schema.json")
    task_review_rows, task_review_fields = read_csv(ROOT / "data" / "independent_task_reviews.csv")
    task_review_errors = validate_csv_rows(task_review_rows, task_review_fields, task_review_schema, "task_id")
    rows.append(row(
        "independent_task_reviews",
        "data/independent_task_reviews.csv",
        "data/independent_task_review_schema.json",
        "independent_non_author_task_quality_reviews",
        len(task_review_rows),
        len(task_review_fields),
        all(field in task_review_fields for field in task_review_schema.get("required", [])),
        "empty_ready" if not task_review_rows and not task_review_errors else ("schema_valid" if not task_review_errors else "schema_error"),
        task_review_errors,
        "The independent accepted-task review table has schema-compatible headers but no non-author task-quality reviews yet.",
        "Empty review data cannot support independent acceptance, time-bucket, hidden-pin, or wrong-submission adequacy claims.",
        "Collect non-author review rows for every accepted_v0 task before strengthening benchmark-grade task-quality claims.",
    ))

    label_rows, label_fields = read_csv(ROOT / "data" / "failure_labels.csv")
    labels = {item.get("label", "") for item in label_rows}
    missing_labels = sorted(RECOMMENDED_FAILURE_LABELS - labels)
    rows.append(row(
        "failure_label_codebook",
        "data/failure_labels.csv",
        "data/failure_label_schema.json",
        "failure_taxonomy_codebook",
        len(label_rows),
        len(label_fields),
        {"label", "description"}.issubset(label_fields),
        "codebook_valid" if not missing_labels and {"label", "description"}.issubset(label_fields) else "codebook_gap",
        missing_labels,
        "Failure-label codebook covers the playbook taxonomy used by run and transcript audits.",
        "The codebook is a taxonomy definition, not evidence that those failures dominate.",
        "Update the codebook and downstream audits together if labels change.",
    ))

    csv_files = sorted((ROOT / "data").glob("*.csv"))
    schema_files = sorted((ROOT / "data").glob("*schema*.json"))
    derived_csv_count = len([
        path for path in csv_files
        if path.name not in {
            "task_metadata.csv",
            "run_results.csv",
            "failure_annotations.csv",
            "failure_label_reviews.csv",
            "human_time_observations.csv",
            "independent_task_reviews.csv",
            "failure_labels.csv",
        }
    ])
    rows.append(row(
        "derived_reporting_csv_inventory",
        "data/*.csv",
        "",
        "generated_audit_and_report_tables",
        len(csv_files),
        0,
        True,
        "inventory_documented",
        [],
        f"CSV files={len(csv_files)}; schema JSON files={len(schema_files)}; derived/reporting CSV files={derived_csv_count}.",
        "Most generated audit CSVs are governed by their producer scripts and manifest hashes rather than standalone JSON schemas.",
        "Add standalone schemas only for files that become external data contracts or model-run inputs.",
    ))
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    status_counts = Counter(item["validation_status"] for item in rows)
    lines = [
        "# Data Schema Manifest",
        "",
        "This generated audit documents the schema status of the benchmark's data inputs. It separates schema-backed external data contracts from generated report/audit CSVs whose structure is governed by producer scripts and validation-manifest hashes.",
        "",
        "## Summary",
        "",
        f"- dataset rows: `{len(rows)}`",
        f"- validation statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        "",
        "## Schema Ledger",
        "",
        "| dataset | status | rows | columns | schema | required fields present | errors | coverage note | limitation | next action |",
        "| --- | --- | ---: | ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for item in rows:
        lines.append(
            f"| `{item['dataset_id']}` | {item['validation_status']} | {item['row_count']} | "
            f"{item['column_count']} | `{item['schema_path']}` | {item['required_fields_present']} | "
            f"`{escaped(item['error_examples'])}` | {escaped(item['coverage_note'])} | "
            f"{escaped(item['limitation'])} | {escaped(item['next_action'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`schema_valid`, `documented_projection`, `empty_ready`, `codebook_valid`, and `inventory_documented` are acceptable for v0.1 research-report evidence. They do not imply that the data are sufficient for locked-benchmark or frontier-performance claims; they only document row shape, codebooks, and schema boundaries.",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "data_schema_manifest.csv", rows)
    write_markdown(ROOT / "reports" / "data_schema_manifest.md", rows)
    problem_rows = [
        item for item in rows
        if item["validation_status"] in {"schema_error", "projection_mismatch", "codebook_gap"}
    ]
    print(
        "wrote data/data_schema_manifest.csv and reports/data_schema_manifest.md "
        f"with {len(rows)} dataset rows; problem_rows={len(problem_rows)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
