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
    "source_value",
    "report_value",
    "evidence",
    "failure_examples",
    "source_artifacts",
    "required_action",
]

MAIN_REPORT = ROOT / "reports" / "metr_style_report.md"
CONCISE_REPORT = ROOT / "reports" / "concise_metr_report.md"
APPENDIX_REPORT = ROOT / "reports" / "evidence_appendix.md"
VALIDATION_MANIFEST = ROOT / "reports" / "validation_manifest.json"
PUBLIC_EXPORT = ROOT / "public_tasks"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def count_by(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(row.get(field, "unknown") for row in rows).items()))


def as_int(value: object) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def row(
    check_id: str,
    area: str,
    ok: bool,
    source_value: object,
    report_value: object,
    evidence: str,
    failure_examples: list[str],
    source_artifacts: list[str],
    required_action: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "status": "pass" if ok else "fail",
        "source_value": compact_json(source_value),
        "report_value": compact_json(report_value),
        "evidence": evidence,
        "failure_examples": compact_json(failure_examples[:10]),
        "source_artifacts": ";".join(source_artifacts),
        "required_action": required_action,
    }


def missing_needles(text_by_report: dict[str, str], expected: dict[str, list[str]]) -> list[str]:
    missing: list[str] = []
    for report_name, needles in expected.items():
        text = text_by_report.get(report_name, "")
        for needle in needles:
            if needle not in text:
                missing.append(f"{report_name}:{needle}")
    return missing


def public_export_counts() -> dict[str, int | bool]:
    if not PUBLIC_EXPORT.exists():
        return {"exists": False, "task_count": 0, "hidden_or_wrong_path_count": 0}
    metadata_files = list(PUBLIC_EXPORT.rglob("metadata.json"))
    hidden_or_wrong = [
        path for path in PUBLIC_EXPORT.rglob("*")
        if "hidden" in path.parts or "wrong" in path.parts
    ]
    return {
        "exists": True,
        "task_count": len(metadata_files),
        "hidden_or_wrong_path_count": len(hidden_or_wrong),
    }


def row_by_key(rows: list[dict[str, str]], **kwargs: str) -> dict[str, str]:
    for row_data in rows:
        if all(row_data.get(key) == value for key, value in kwargs.items()):
            return row_data
    return {}


def build_rows() -> list[dict[str, str]]:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    run_results = read_csv(ROOT / "data" / "run_results.csv")
    requirement_coverage = read_csv(ROOT / "data" / "requirement_coverage.csv")
    claim_authorization = read_csv(ROOT / "data" / "claim_authorization_matrix.csv")
    release_decision = read_csv(ROOT / "data" / "release_decision_log.csv")
    freeze_readiness = read_csv(ROOT / "data" / "freeze_readiness_roadmap.csv")
    model_summary = read_csv(ROOT / "data" / "model_result_summary.csv")
    model_sweep_coverage = read_csv(ROOT / "data" / "model_sweep_coverage_audit.csv")
    research_claim_gap = read_csv(ROOT / "data" / "research_claim_gap_matrix.csv")
    manifest = read_json(VALIDATION_MANIFEST)
    text_by_report = {
        "main": read_text(MAIN_REPORT),
        "concise": read_text(CONCISE_REPORT),
        "appendix": read_text(APPENDIX_REPORT),
    }

    accepted = [row_data for row_data in metadata if row_data.get("acceptance_status") == "accepted_v0"]
    calibration = [row_data for row_data in metadata if row_data.get("acceptance_status") == "calibration_only"]
    rejected = [
        row_data for row_data in metadata
        if row_data.get("acceptance_status", "").startswith("rejected_")
    ]
    pending = [
        row_data for row_data in metadata
        if row_data.get("acceptance_status") == "candidate_review_pending"
    ]
    acceptance_counts = count_by(metadata, "acceptance_status")
    requirement_counts = count_by(requirement_coverage, "status")
    authorization_counts = count_by(claim_authorization, "authorization_status")
    release_counts = count_by(release_decision, "status")
    freeze_counts = count_by(freeze_readiness, "roadmap_status")
    local_rows = [row_data for row_data in run_results if row_data.get("qa_stage") == "local_qa"]
    model_rows = [row_data for row_data in run_results if row_data.get("qa_stage") != "local_qa"]
    manifest_task_summary = manifest.get("task_summary", {}) if isinstance(manifest.get("task_summary"), dict) else {}
    manifest_run_summary = manifest.get("run_result_summary", {}) if isinstance(manifest.get("run_result_summary"), dict) else {}
    manifest_public_export = manifest.get("public_export", {}) if isinstance(manifest.get("public_export"), dict) else {}
    export_counts = public_export_counts()

    rows: list[dict[str, str]] = []

    task_expected = {
        "main": [
            f"{len(accepted)} accepted core tasks",
            f"{len(calibration)} calibration-only tasks",
            f"The remaining {len(rejected)} tasks",
            f"{len(pending)} tasks remain pending review",
            compact_json(acceptance_counts),
        ],
        "concise": [
            f"- accepted core tasks: `{len(accepted)}`",
            f"- calibration-only tasks: `{len(calibration)}`",
            f"- rejected archive tasks: `{len(rejected)}`",
        ],
    }
    task_missing = missing_needles(text_by_report, task_expected)
    task_manifest_ok = (
        manifest_task_summary.get("task_count") == len(metadata)
        and manifest_task_summary.get("acceptance_status_counts") == acceptance_counts
    )
    rows.append(row(
        "task_status_counts",
        "portfolio_counts",
        bool(metadata) and task_manifest_ok and not task_missing,
        {
            "task_count": len(metadata),
            "accepted": len(accepted),
            "calibration": len(calibration),
            "rejected": len(rejected),
            "pending": len(pending),
            "acceptance_status_counts": acceptance_counts,
        },
        {
            "manifest_task_count": manifest_task_summary.get("task_count"),
            "manifest_acceptance_status_counts": manifest_task_summary.get("acceptance_status_counts"),
            "missing_report_needles": task_missing,
        },
        "Task-status counts are checked against task metadata, the validation manifest, and the main/concise report top lines.",
        (["validation manifest task summary mismatch"] if not task_manifest_ok else []) + task_missing,
        [
            "data/task_metadata.csv",
            "reports/validation_manifest.json",
            "reports/metr_style_report.md",
            "reports/concise_metr_report.md",
        ],
        "Regenerate task metadata, validation manifest, concise report, and main report after any task-status change.",
    ))

    requirement_missing = missing_needles(text_by_report, {
        "main": [compact_json(requirement_counts)],
        "concise": [f"- requirement statuses: `{compact_json(requirement_counts)}`"],
        "appendix": [
            f"- `{status}`: {count}"
            for status, count in sorted(requirement_counts.items())
        ],
    })
    rows.append(row(
        "requirement_status_counts",
        "report_counts",
        bool(requirement_coverage) and not requirement_missing,
        requirement_counts,
        {"missing_report_needles": requirement_missing},
        "Requirement status counts are checked where the report summarizes supported/partial/not_met evidence.",
        requirement_missing,
        [
            "data/requirement_coverage.csv",
            "reports/metr_style_report.md",
            "reports/concise_metr_report.md",
            "reports/evidence_appendix.md",
        ],
        "Regenerate requirement coverage and all report layers after requirement status changes.",
    ))

    claim_missing = missing_needles(text_by_report, {
        "main": [compact_json(authorization_counts)],
        "concise": [f"- claim authorizations: `{compact_json(authorization_counts)}`"],
        "appendix": [compact_json(authorization_counts)],
    })
    rows.append(row(
        "claim_authorization_counts",
        "report_counts",
        bool(claim_authorization) and not claim_missing,
        authorization_counts,
        {"missing_report_needles": claim_missing},
        "Claim-authorization status counts are checked against generated report summaries.",
        claim_missing,
        [
            "data/claim_authorization_matrix.csv",
            "reports/metr_style_report.md",
            "reports/concise_metr_report.md",
            "reports/evidence_appendix.md",
        ],
        "Regenerate claim authorization, concise report, and main report after claim status changes.",
    ))

    gate_missing = missing_needles(text_by_report, {
        "main": [compact_json(release_counts), compact_json(freeze_counts)],
        "concise": [
            f"- release-decision gates: `{compact_json(release_counts)}`",
            f"- freeze-readiness gates: `{compact_json(freeze_counts)}`",
        ],
        "appendix": [compact_json(release_counts), compact_json(freeze_counts)],
    })
    rows.append(row(
        "release_and_freeze_gate_counts",
        "gate_counts",
        bool(release_decision) and bool(freeze_readiness) and not gate_missing,
        {
            "release_decision": release_counts,
            "freeze_readiness": freeze_counts,
        },
        {"missing_report_needles": gate_missing},
        "Release-decision and freeze-readiness status counts are checked wherever the report repeats them.",
        gate_missing,
        [
            "data/release_decision_log.csv",
            "data/freeze_readiness_roadmap.csv",
            "reports/metr_style_report.md",
            "reports/concise_metr_report.md",
            "reports/evidence_appendix.md",
        ],
        "Regenerate release/freeze reports and all report layers after gate-status changes.",
    ))

    primary_coverage = row_by_key(model_summary, analysis_set="primary_plan_coverage", group_by="all", group="all")
    accepted_provider = row_by_key(model_summary, analysis_set="accepted_core_results", group_by="all", group="all")
    planned_cells = as_int(primary_coverage.get("planned_cells"))
    covered_noninfra = as_int(primary_coverage.get("covered_cells_noninfra"))
    pass_at_k_ready_cells = sum(
        1 for row_data in model_sweep_coverage
        if row_data.get("coverage_status") in {"covered_pass", "covered_fail"}
    )
    accepted_total = as_int(accepted_provider.get("rows_total"))
    accepted_noninfra = as_int(accepted_provider.get("rows_noninfra"))
    model_missing = missing_needles(text_by_report, {
        "main": [
            f"primary sweep pass@k-ready coverage: `{pass_at_k_ready_cells}/{planned_cells}` planned cells ready",
            f"aggregate non-infra smoke-covered cells: `{covered_noninfra}/{planned_cells}`",
            f"accepted-core non-infra provider smoke rows: `{accepted_noninfra}`",
        ],
        "concise": [
            f"- planned accepted-core task/scaffold cells: `{planned_cells}`",
            f"- pass@k-ready primary cells: `{pass_at_k_ready_cells}`",
            f"- aggregate non-infra smoke-covered primary cells: `{covered_noninfra}`",
            f"- accepted-core provider rows: `{accepted_total}` total, `{accepted_noninfra}` non-infra",
        ],
    })
    rows.append(row(
        "model_coverage_counts",
        "model_counts",
        bool(model_summary) and planned_cells > 0 and not model_missing,
        {
            "planned_primary_cells": planned_cells,
            "pass_at_k_ready_cells": pass_at_k_ready_cells,
            "covered_primary_noninfra": covered_noninfra,
            "accepted_provider_rows_total": accepted_total,
            "accepted_provider_rows_noninfra": accepted_noninfra,
        },
        {"missing_report_needles": model_missing},
        "Model-sweep coverage counts are checked against the source summary and report wording that keeps performance claims blocked.",
        model_missing,
        [
            "data/model_result_summary.csv",
            "data/model_sweep_coverage_audit.csv",
            "reports/metr_style_report.md",
            "reports/concise_metr_report.md",
        ],
        "Regenerate model-result analysis and reports after provider rows or sweep plans change.",
    ))

    run_manifest_ok = (
        manifest_run_summary.get("row_count") == len(run_results)
        and manifest_run_summary.get("local_qa_row_count") == len(local_rows)
        and manifest_run_summary.get("model_sweep_row_count") == len(model_rows)
    )
    run_missing = missing_needles(text_by_report, {
        "appendix": [
            f"- run-result rows: `{len(run_results)}` total, `{len(local_rows)}` local QA, `{len(model_rows)}` model-sweep",
        ],
    })
    rows.append(row(
        "run_and_manifest_counts",
        "manifest_counts",
        bool(run_results) and run_manifest_ok and not run_missing,
        {
            "run_rows": len(run_results),
            "local_qa_rows": len(local_rows),
            "model_rows": len(model_rows),
        },
        {
            "manifest_run_summary": manifest_run_summary,
            "missing_report_needles": run_missing,
        },
        "Run-result counts are checked against the validation manifest and the appendix manifest summary.",
        (["validation manifest run summary mismatch"] if not run_manifest_ok else []) + run_missing,
        [
            "data/run_results.csv",
            "reports/validation_manifest.json",
            "reports/evidence_appendix.md",
        ],
        "Regenerate local QA rows, validation manifest, and report appendix after run-result changes.",
    ))

    locked_blockers = sorted(
        row_data.get("requirement_id", "")
        for row_data in requirement_coverage
        if row_data.get("freeze_relevance") == "required_for_locked_benchmark"
        and row_data.get("status") != "supported"
        and row_data.get("requirement_id")
    )
    locked_gap = row_by_key(research_claim_gap, claim_id="locked_benchmark_status")
    locked_gap_blockers = [
        item.strip()
        for item in locked_gap.get("blocking_requirements", "").split(";")
        if item.strip() and item.strip() != "none"
    ]
    blocker_missing = missing_needles(text_by_report, {
        "main": [*locked_blockers],
        "concise": [*locked_blockers],
        "appendix": [*locked_blockers],
    })
    missing_from_gap = sorted(set(locked_blockers) - set(locked_gap_blockers))
    rows.append(row(
        "locked_benchmark_blocker_counts",
        "blocker_counts",
        bool(locked_blockers) and not blocker_missing and not missing_from_gap,
        {
            "locked_blockers": locked_blockers,
            "locked_blocker_count": len(locked_blockers),
        },
        {
            "gap_blockers": locked_gap_blockers,
            "missing_report_needles": blocker_missing,
            "missing_from_gap": missing_from_gap,
        },
        "Locked-benchmark blocker identifiers are checked against requirement coverage, the claim-gap row, and report blocker tables.",
        [f"missing_from_gap:{item}" for item in missing_from_gap] + blocker_missing,
        [
            "data/requirement_coverage.csv",
            "data/research_claim_gap_matrix.csv",
            "reports/metr_style_report.md",
            "reports/concise_metr_report.md",
            "reports/evidence_appendix.md",
        ],
        "Regenerate requirement coverage, claim gap matrix, and reports when locked-benchmark blockers change.",
    ))

    public_export_ok = (
        manifest_public_export.get("task_count") == export_counts["task_count"]
        and manifest_public_export.get("hidden_or_wrong_path_count") == export_counts["hidden_or_wrong_path_count"]
        and bool(export_counts["exists"])
    )
    public_export_missing = missing_needles(text_by_report, {
        "appendix": [
            f"- public export: `{export_counts['task_count']}` tasks",
            f"hidden/wrong paths found: `{export_counts['hidden_or_wrong_path_count']}`",
        ],
    })
    rows.append(row(
        "public_export_counts",
        "manifest_counts",
        public_export_ok and not public_export_missing,
        export_counts,
        {
            "manifest_public_export": manifest_public_export,
            "missing_report_needles": public_export_missing,
        },
        "Public-export task and hidden/wrong-path counts are checked against the manifest and appendix summary.",
        (["validation manifest public export mismatch"] if not public_export_ok else []) + public_export_missing,
        [
            "public_tasks",
            "reports/validation_manifest.json",
            "reports/evidence_appendix.md",
        ],
        "Regenerate public export, validation manifest, and report appendix after public task export changes.",
    ))

    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row_data["status"] for row_data in rows)
    area_counts = Counter(row_data["area"] for row_data in rows)
    lines = [
        "# Report Count Consistency Audit",
        "",
        "This generated audit checks that repeated top-line counts in the concise report, main report, evidence appendix, and validation manifest agree with the committed CSV/JSON sources. It is a drift detector for reviewer-facing numbers, not a new source of benchmark evidence.",
        "",
        "## Summary",
        "",
        f"- checks: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- areas: `{compact_json(dict(sorted(area_counts.items())))}`",
        "",
        "## Check Table",
        "",
        "| check | area | status | source value | report value | evidence | failure examples | required action |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row_data in rows:
        lines.append(
            f"| `{row_data['check_id']}` | {row_data['area']} | {row_data['status']} | "
            f"`{escaped(row_data['source_value'])}` | `{escaped(row_data['report_value'])}` | "
            f"{escaped(row_data['evidence'])} | `{escaped(row_data['failure_examples'])}` | "
            f"{escaped(row_data['required_action'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`fail` rows mean a generated report or manifest has stale top-line counts relative to the source artifacts. Regenerate the upstream CSV/JSON source and report layer in the order listed by the validation manifest before using the report for review.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "report_count_consistency_audit.csv", rows)
    write_markdown(ROOT / "reports" / "report_count_consistency_audit.md", rows)
    failures = sum(1 for row_data in rows if row_data["status"] == "fail")
    print(
        "wrote data/report_count_consistency_audit.csv and "
        f"reports/report_count_consistency_audit.md with {len(rows)} checks; failures={failures}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
