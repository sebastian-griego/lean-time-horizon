from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "check_id",
    "area",
    "status",
    "evidence",
    "limitation",
    "next_action",
]


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


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def validate_review_rows(rows: list[dict[str, str]], fields: list[str], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = list(schema.get("required", []))
    properties = schema.get("properties", {})
    missing_fields = [field for field in required if field not in fields]
    if missing_fields:
        errors.append(f"missing fields: {missing_fields}")
        return errors
    for index, review in enumerate(rows, start=2):
        record_id = review.get("task_id") or f"row_{index}"
        for field in required:
            value = review.get(field, "")
            if value == "":
                errors.append(f"{record_id}: empty {field}")
                continue
            spec = properties.get(field, {})
            if spec.get("type") == "boolean" and value.lower() not in {"true", "false"}:
                errors.append(f"{record_id}: {field} not boolean")
            enum = spec.get("enum")
            if enum is not None and value not in enum:
                errors.append(f"{record_id}: {field} not in enum")
    return errors


def build_rows() -> list[dict[str, str]]:
    metadata, _ = read_csv(ROOT / "data" / "task_metadata.csv")
    accepted = [task for task in metadata if task.get("acceptance_status") == "accepted_v0"]
    accepted_ids = {task.get("task_id", "") for task in accepted}
    plan, plan_fields = read_csv(ROOT / "data" / "independent_task_review_plan.csv")
    template, template_fields = read_csv(ROOT / "data" / "independent_task_review_template.csv")
    reviews, review_fields = read_csv(ROOT / "data" / "independent_task_reviews.csv")
    schema = read_json(ROOT / "data" / "independent_task_review_schema.json")

    rows: list[dict[str, str]] = []
    plan_ids = {item.get("task_id", "") for item in plan}
    template_ids = {item.get("task_id", "") for item in template}
    rows.append(row(
        "review_plan_coverage",
        "packet",
        "pass" if accepted_ids == plan_ids and accepted_ids == template_ids and plan and template else "fail",
        (
            f"accepted={len(accepted_ids)}; plan_rows={len(plan)}; template_rows={len(template)}; "
            f"missing_plan={compact_json(sorted(accepted_ids - plan_ids))}; "
            f"missing_template={compact_json(sorted(accepted_ids - template_ids))}"
        ),
        "The plan and template make review collection operational but do not prove reviews happened.",
        "Regenerate scripts/generate_independent_review_packet.py after accepted task metadata changes.",
    ))

    required_template_fields = set(schema.get("required", []))
    template_fields_ok = required_template_fields.issubset(set(template_fields))
    review_fields_ok = required_template_fields.issubset(set(review_fields))
    rows.append(row(
        "review_schema_and_template",
        "schema",
        "pass" if schema and template_fields_ok and review_fields_ok else "fail",
        (
            f"schema_required_fields={len(required_template_fields)}; "
            f"template_fields_ok={template_fields_ok}; review_fields_ok={review_fields_ok}; "
            f"plan_fields={len(plan_fields)}"
        ),
        "Schema/template validity checks row shape, not review quality.",
        "Keep schema, template, and audit in sync if review categories change.",
    ))

    review_errors = validate_review_rows(reviews, review_fields, schema)
    rows.append(row(
        "review_row_validity",
        "observations",
        "pass" if not review_errors else "fail",
        f"review_rows={len(reviews)}; validation_errors={len(review_errors)}; examples={compact_json(review_errors[:8])}",
        "Zero review rows is a valid empty-ready state; it does not satisfy independent review coverage.",
        "Append real non-author review rows, then rerun this audit.",
    ))

    review_task_ids = {review.get("task_id", "") for review in reviews}
    reviewed_accepted = accepted_ids & review_task_ids
    rows.append(row(
        "accepted_review_coverage",
        "coverage",
        "block" if reviewed_accepted != accepted_ids else "pass",
        (
            f"accepted reviewed={len(reviewed_accepted)}/{len(accepted_ids)}; "
            f"missing={compact_json(sorted(accepted_ids - reviewed_accepted))}; "
            f"review_rows={len(reviews)}"
        ),
        "Independent review coverage is absent until real non-author rows are committed.",
        "Collect at least one non-author review row for every accepted_v0 task before freeze.",
    ))

    recommendation_counts = Counter(review.get("benchmark_grade_recommendation", "") for review in reviews)
    rows.append(row(
        "review_recommendation_distribution",
        "observations",
        "empty_ready" if not reviews else "pass",
        f"recommendations={compact_json(dict(sorted(recommendation_counts.items())))}; review_rows={len(reviews)}",
        "No distributional review claim is supported without real rows and reviewer provenance.",
        "Use recommendations only after rows are collected and checked against task evidence.",
    ))
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row_data["status"] for row_data in rows)
    lines = [
        "# Independent Review Status Audit",
        "",
        "This generated audit checks whether the independent task-review packet is ready and whether any real non-author task reviews have been committed. It intentionally treats an empty review file as collection-ready but not as independent validation evidence.",
        "",
        "## Summary",
        "",
        f"- checks: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
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
        "`pass` on packet checks means the collection workflow is ready. `block` on accepted-review coverage means the current repository still lacks independent non-author review evidence and should not upgrade accepted-task quality claims beyond internal review.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "independent_review_status_audit.csv", rows)
    write_markdown(ROOT / "reports" / "independent_review_status_audit.md", rows)
    failures = sum(1 for row_data in rows if row_data["status"] == "fail")
    blocks = sum(1 for row_data in rows if row_data["status"] == "block")
    print(
        "wrote data/independent_review_status_audit.csv and "
        f"reports/independent_review_status_audit.md with {len(rows)} checks; "
        f"failures={failures}; blocks={blocks}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
