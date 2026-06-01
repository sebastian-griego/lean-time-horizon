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
    "accepted_task_count",
    "accepted_task_ids",
    "release_task_count",
    "evidence",
    "diagnostic_limit",
    "next_action",
]

PLAYBOOK_FAMILIES = [
    "algorithm_correctness",
    "proof_repair_codebase",
    "informal_spec_to_formal",
    "invariant_verification_ml_optimization",
    "small_formal_library_construction",
    "direct_theorem_proving",
]

CAPABILITY_FIELDS = {
    "library_search": "requires_library_search",
    "theorem_decomposition": "requires_decomposition",
    "semantic_formalization": "requires_semantic_formalization",
    "proof_debugging": "requires_proof_debugging",
    "codebase_navigation": "requires_codebase_navigation",
    "invariant_design": "requires_invariant_design",
    "long_horizon_construction": "requires_long_horizon_construction",
}

CAPABILITY_LABEL_MAP = {
    "library_search": "library_search",
    "theorem_decomposition": "theorem_decomposition",
    "semantic_formalization": "semantic_formalization",
    "proof_debugging": "proof_debugging",
    "codebase_navigation": "codebase_navigation",
    "invariant_design": "invariant_design",
    "long_horizon_construction": "timeout",
}

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


def parse_list(value: str) -> list[str]:
    if not value:
        return []
    try:
        data = json.loads(value)
        if isinstance(data, list):
            return [str(item) for item in data]
    except json.JSONDecodeError:
        pass
    return [item.strip() for item in value.split(";") if item.strip()]


def as_bool(value: str) -> bool:
    return str(value).strip().lower() == "true"


def row(
    check_id: str,
    area: str,
    status: str,
    accepted_task_ids: list[str],
    release_task_count: int,
    evidence: str,
    diagnostic_limit: str,
    next_action: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "status": status,
        "accepted_task_count": str(len(accepted_task_ids)),
        "accepted_task_ids": compact_json(sorted(accepted_task_ids)),
        "release_task_count": str(release_task_count),
        "evidence": evidence,
        "diagnostic_limit": diagnostic_limit,
        "next_action": next_action,
    }


def build_rows() -> list[dict[str, str]]:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    quality = read_csv(ROOT / "data" / "task_quality_matrix.csv")
    failure_labels = read_csv(ROOT / "data" / "failure_labels.csv")
    accepted_meta = [task for task in metadata if task.get("acceptance_status") == "accepted_v0"]
    release = [task for task in metadata if task.get("acceptance_status") in RELEASE_STATUSES]
    accepted_quality = [task for task in quality if task.get("release_role") == "accepted_core"]
    accepted_ids = [task["task_id"] for task in accepted_meta]
    quality_by_id = {task["task_id"]: task for task in accepted_quality}
    release_count = len(release)
    rows: list[dict[str, str]] = []

    family_counts = Counter(task.get("family", "") for task in accepted_meta)
    missing_families = [family for family in PLAYBOOK_FAMILIES if not family_counts.get(family)]
    rows.append(row(
        "family_mix",
        "portfolio_shape",
        "pass" if not missing_families and len(accepted_meta) > 0 else "block",
        accepted_ids,
        release_count,
        f"accepted_family_counts={compact_json(dict(sorted(family_counts.items())))}; missing_playbook_families={compact_json(missing_families)}",
        "Family diversity is represented, but most families have only one accepted task.",
        "Add more accepted rows per family before using family-level performance summaries.",
    ))

    direct_ids = [task["task_id"] for task in accepted_meta if task.get("family") == "direct_theorem_proving"]
    direct_limit = max(1, len(accepted_meta) // 3)
    rows.append(row(
        "direct_theorem_balance",
        "portfolio_shape",
        "pass" if 0 < len(direct_ids) <= direct_limit else "caution",
        direct_ids,
        release_count,
        f"direct_theorem_tasks={len(direct_ids)}; accepted_tasks={len(accepted_meta)}; direct_limit={direct_limit}",
        "Direct theorem proving is present but does not dominate accepted_v0.",
        "Keep direct theorem proving as one slice of the portfolio rather than the main task type.",
    ))

    for capability, field in CAPABILITY_FIELDS.items():
        capability_ids = [
            task["task_id"] for task in accepted_quality
            if as_bool(task.get(field, "false"))
        ]
        if len(capability_ids) >= 2:
            status = "pass"
            limit = "Capability is represented by more than one accepted task."
        elif len(capability_ids) == 1:
            status = "caution"
            limit = "Capability is represented by a singleton accepted task, so task-specific quirks can dominate."
        else:
            status = "block"
            limit = "Capability is not represented in accepted_v0."
        rows.append(row(
            f"capability_{capability}",
            "diagnostic_capability",
            status,
            capability_ids,
            release_count,
            f"capability={capability}; source_field={field}; accepted_task_ids={compact_json(sorted(capability_ids))}",
            limit,
            "Add at least two independently reviewed accepted tasks for each core diagnostic capability before making capability-level claims.",
        ))

    failure_mode_counts = {
        task["task_id"]: len(parse_list(task.get("expected_failure_modes", "")))
        for task in accepted_meta
    }
    sparse_failure_modes = [task_id for task_id, count in failure_mode_counts.items() if count < 3]
    rows.append(row(
        "failure_mode_metadata_density",
        "diagnostic_metadata",
        "pass" if not sparse_failure_modes and len(failure_mode_counts) == len(accepted_meta) else "fail",
        accepted_ids,
        release_count,
        f"accepted_failure_mode_counts={compact_json(failure_mode_counts)}; sparse_failure_mode_tasks={compact_json(sparse_failure_modes)}",
        "Expected failure modes are documented, but they are author forecasts until provider transcripts accumulate.",
        "Compare predicted failure modes to independently labeled model transcripts after the full scaffold sweep.",
    ))

    label_set = {label.get("label", "") for label in failure_labels}
    missing_label_mappings = [
        capability for capability, label in CAPABILITY_LABEL_MAP.items()
        if label not in label_set
    ]
    rows.append(row(
        "capability_failure_label_alignment",
        "failure_taxonomy",
        "pass" if not missing_label_mappings else "fail",
        accepted_ids,
        release_count,
        f"capability_label_map={compact_json(CAPABILITY_LABEL_MAP)}; missing_label_mappings={compact_json(missing_label_mappings)}",
        "Failure labels can describe the intended capabilities, but committed provider transcripts are too sparse for distributional analysis.",
        "Use the mapped labels during transcript review and revisit the taxonomy after broad model sweeps.",
    ))

    automation_ids = [
        task["task_id"] for task in accepted_quality
        if as_bool(task.get("automation_dominated", "false"))
    ]
    automation_without_caveat = [
        task["task_id"] for task in accepted_quality
        if as_bool(task.get("automation_dominated", "false"))
        and "caveat" not in task.get("benchmark_grade_status", "")
        and "caveat" not in task.get("manual_review_note", "").lower()
    ]
    rows.append(row(
        "automation_caveat_coverage",
        "task_validity",
        "pass" if not automation_without_caveat else "fail",
        automation_ids,
        release_count,
        f"automation_dominated_accepted={compact_json(sorted(automation_ids))}; automation_without_caveat={compact_json(sorted(automation_without_caveat))}",
        "Automation-dominated retained tasks are visible caveat rows, not hidden as benchmark-grade proof difficulty.",
        "Keep automation caveats in task metadata and do not use these rows as standalone evidence of long-horizon proof difficulty.",
    ))

    likely_ids = [
        task["task_id"] for task in accepted_quality
        if task.get("frontier_one_shot_likelihood") in {"likely", "very_likely"}
    ]
    rows.append(row(
        "one_shot_solvability_balance",
        "task_validity",
        "pass" if len(likely_ids) <= max(1, len(accepted_quality) // 3) else "caution",
        likely_ids,
        release_count,
        f"likely_or_very_likely_one_shot={compact_json(sorted(likely_ids))}; accepted_quality_rows={len(accepted_quality)}",
        "The accepted core is not dominated by rows expected to be easy one-shot, but estimates are internal judgments.",
        "Replace internal solvability estimates with measured scaffold runs before performance claims.",
    ))

    bucket_counts = Counter(task.get("human_time_bucket", "") for task in accepted_meta)
    rows.append(row(
        "time_horizon_construct_limit",
        "construct_validity",
        "block" if not bucket_counts.get("T4") else "pass",
        accepted_ids,
        release_count,
        f"accepted_bucket_counts={compact_json(dict(sorted(bucket_counts.items())))}",
        "Accepted_v0 has no T4 task and only one T3 task; the current set cannot support strong time-horizon claims.",
        "Add independently timed T3/T4 tasks, including a T4 stretch row, before claiming robust time-horizon measurement.",
    ))

    missing_quality_rows = [task_id for task_id in accepted_ids if task_id not in quality_by_id]
    rows.append(row(
        "quality_matrix_join_integrity",
        "data_integrity",
        "pass" if not missing_quality_rows and len(accepted_quality) == len(accepted_meta) else "fail",
        accepted_ids,
        release_count,
        f"accepted_metadata_rows={len(accepted_meta)}; accepted_quality_rows={len(accepted_quality)}; missing_quality_rows={compact_json(missing_quality_rows)}",
        "Diagnostic coverage depends on the task quality matrix joining metadata and difficulty audit rows correctly.",
        "Regenerate difficulty audit and task quality matrix before this audit whenever task metadata changes.",
    ))
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row["status"] for row in rows)
    area_counts = Counter(row["area"] for row in rows)
    table_lines = [
        "| check | area | status | accepted tasks | evidence | diagnostic limit | next action |",
        "| --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for row_data in rows:
        table_lines.append(
            f"| `{row_data['check_id']}` | {row_data['area']} | {row_data['status']} | "
            f"{row_data['accepted_task_count']} | {escaped(row_data['evidence'])} | "
            f"{escaped(row_data['diagnostic_limit'])} | {escaped(row_data['next_action'])} |"
        )
    lines = [
        "# Diagnostic Coverage Audit",
        "",
        "This generated audit maps accepted_v0 tasks to the diagnostic capabilities emphasized by the playbook. It is a construct-validity check, not a performance result. `caution` and `block` rows are retained because they identify undercoverage that should stay visible in the research report.",
        "",
        "## Summary",
        "",
        f"- checks: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- areas: `{compact_json(dict(sorted(area_counts.items())))}`",
        "",
        "## Check Table",
        "",
        "\n".join(table_lines),
        "",
        "## Interpretation",
        "",
        "The accepted core covers the six playbook task families and is not mostly direct theorem proving. However, several diagnostic capabilities are singleton-covered, and the time-horizon construct remains blocked by the absence of accepted T4 work and independent timing. Treat capability-level and horizon-level conclusions as design intent until more accepted tasks and model transcripts are available.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "diagnostic_coverage_audit.csv", rows)
    write_markdown(ROOT / "reports" / "diagnostic_coverage_audit.md", rows)
    print(f"wrote data/diagnostic_coverage_audit.csv and reports/diagnostic_coverage_audit.md with {len(rows)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
