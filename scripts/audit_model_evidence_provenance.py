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
    "required_action",
    "source_artifacts",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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


def row(
    check_id: str,
    area: str,
    status: str,
    evidence: str,
    limitation: str,
    required_action: str,
    source_artifacts: list[str],
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "status": status,
        "evidence": evidence,
        "limitation": limitation,
        "required_action": required_action,
        "source_artifacts": ";".join(source_artifacts),
    }


def int_field(data: dict[str, str], key: str) -> int:
    try:
        return int(data.get(key, "0") or "0")
    except ValueError:
        return 0


def summary_row(rows: list[dict[str, str]], analysis_set: str, group_by: str, group: str) -> dict[str, str]:
    return next(
        (
            row_data for row_data in rows
            if row_data.get("analysis_set") == analysis_set
            and row_data.get("group_by") == group_by
            and row_data.get("group") == group
        ),
        {},
    )


def build_rows() -> list[dict[str, str]]:
    run_rows = read_csv(ROOT / "data" / "run_results.csv")
    summary = read_csv(ROOT / "data" / "model_result_summary.csv")
    metadata = {
        row_data.get("task_id", ""): row_data
        for row_data in read_csv(ROOT / "data" / "task_metadata.csv")
    }
    main_report = read_text(ROOT / "reports" / "metr_style_report.md")
    model_report = read_text(ROOT / "reports" / "model_run_analysis.md")

    provider_rows = [row_data for row_data in run_rows if row_data.get("qa_stage") != "local_qa"]
    local_rows = [row_data for row_data in run_rows if row_data.get("qa_stage") == "local_qa"]
    noninfra_provider_rows = [
        row_data for row_data in provider_rows
        if row_data.get("infra_fail_count") in {"", "0", 0}
    ]
    accepted_provider_rows = [
        row_data for row_data in provider_rows
        if metadata.get(row_data.get("task_id", ""), {}).get("acceptance_status") == "accepted_v0"
    ]
    accepted_noninfra_rows = [
        row_data for row_data in accepted_provider_rows
        if row_data.get("infra_fail_count") in {"", "0", 0}
    ]
    calibration_provider_rows = [
        row_data for row_data in provider_rows
        if metadata.get(row_data.get("task_id", ""), {}).get("acceptance_status") == "calibration_only"
    ]
    missing_required_fields = [
        row_data.get("job_id", "<missing-job>")
        for row_data in provider_rows
        if not row_data.get("model", "").strip()
        or not row_data.get("model_version", "").strip()
        or not row_data.get("job_id", "").strip()
        or not row_data.get("transcript_link", "").strip()
        or not row_data.get("k", "").strip()
    ]
    missing_transcripts = [
        row_data.get("transcript_link", "")
        for row_data in provider_rows
        if row_data.get("transcript_link")
        and not (ROOT / row_data.get("transcript_link", "")).exists()
    ]
    duplicate_jobs = [
        job_id for job_id, count in Counter(row_data.get("job_id", "") for row_data in provider_rows).items()
        if job_id and count > 1
    ]
    model_versions = sorted({
        f"{row_data.get('model', '')}:{row_data.get('model_version', '')}"
        for row_data in provider_rows
        if row_data.get("model") and row_data.get("model_version")
    })
    k_values = sorted({row_data.get("k", "") for row_data in provider_rows if row_data.get("k", "")})
    provider_scaffolds = Counter(row_data.get("scaffold", "unknown") for row_data in provider_rows)

    all_smoke_summary = summary_row(summary, "all_provider_smoke_rows", "all", "all")
    accepted_summary = summary_row(summary, "accepted_core_results", "all", "all")
    calibration_summary = summary_row(summary, "calibration_smoke_rows", "all", "all")
    primary_summary = summary_row(summary, "primary_plan_coverage", "all", "all")
    summary_mismatches = []
    if all_smoke_summary and int_field(all_smoke_summary, "rows_total") != len(provider_rows):
        summary_mismatches.append("all_provider_smoke_rows.rows_total")
    if accepted_summary and int_field(accepted_summary, "rows_total") != len(accepted_provider_rows):
        summary_mismatches.append("accepted_core_results.rows_total")
    if accepted_summary and int_field(accepted_summary, "rows_noninfra") != len(accepted_noninfra_rows):
        summary_mismatches.append("accepted_core_results.rows_noninfra")
    if calibration_summary and int_field(calibration_summary, "rows_total") != len(calibration_provider_rows):
        summary_mismatches.append("calibration_smoke_rows.rows_total")
    if primary_summary and int_field(primary_summary, "planned_cells") != 18:
        summary_mismatches.append("primary_plan_coverage.planned_cells")

    lower_main = main_report.lower()
    lower_model = model_report.lower()
    report_missing_versions = [
        version for version in model_versions
        if version.split(":", 1)[1].lower() not in lower_main
    ]
    required_report_phrases = [
        "accepted-core provider rows",
        "all committed non-local rows",
        "not model performance",
        "excluded from benchmark pass-rate summaries",
        "infra-failure rows are retained",
    ]
    missing_report_phrases = [
        phrase for phrase in required_report_phrases
        if phrase.lower() not in lower_main
    ]
    required_model_phrases = [
        "planned accepted-core task/scaffold cells",
        "accepted-core provider rows",
        "all committed provider smoke rows",
        "not a benchmark performance run",
    ]
    missing_model_phrases = [
        phrase for phrase in required_model_phrases
        if phrase.lower() not in lower_model
    ]

    rows: list[dict[str, str]] = []
    rows.append(row(
        "provider_row_inventory",
        "run_data",
        "pass" if provider_rows else "caution",
        (
            f"provider_rows={len(provider_rows)}; noninfra_provider_rows={len(noninfra_provider_rows)}; "
            f"accepted_provider_rows={len(accepted_provider_rows)}; accepted_noninfra_rows={len(accepted_noninfra_rows)}; "
            f"calibration_provider_rows={len(calibration_provider_rows)}; local_qa_rows={len(local_rows)}"
        ),
        "Provider rows are smoke evidence only and are underpowered for benchmark claims.",
        "Keep provider rows separate from local QA rows and rerun this audit after every sweep.",
        ["data/run_results.csv", "data/task_metadata.csv"],
    ))
    rows.append(row(
        "model_version_and_k_completeness",
        "run_data",
        "pass" if not missing_required_fields and not duplicate_jobs else "fail",
        (
            f"model_versions={compact_json(model_versions)}; k_values={compact_json(k_values)}; "
            f"scaffolds={compact_json(dict(sorted(provider_scaffolds.items())))}; "
            f"missing_required_rows={compact_json(missing_required_fields[:8])}; duplicate_jobs={compact_json(duplicate_jobs[:8])}"
        ),
        "Current model-version rows are tiny smoke rows, not a model-comparison dataset.",
        "Require model, model_version, job_id, k, and transcript_link on every future non-local row.",
        ["data/run_results.csv", "data/run_results_schema.json"],
    ))
    rows.append(row(
        "transcript_provenance",
        "run_data",
        "pass" if not missing_transcripts else "fail",
        f"provider_transcripts={len(provider_rows)}; missing_transcripts={compact_json(missing_transcripts[:8])}",
        "Transcript existence does not imply transcript labels have been independently adjudicated.",
        "Keep transcript files committed or explicitly mark infra rows with enough diagnostic detail.",
        ["data/run_results.csv", "transcripts"],
    ))
    rows.append(row(
        "summary_count_consistency",
        "analysis_data",
        "pass" if not summary_mismatches else "fail",
        (
            f"summary_rows={len(summary)}; mismatches={compact_json(summary_mismatches)}; "
            f"primary_planned_cells={primary_summary.get('planned_cells', 'missing')}; "
            f"primary_covered_noninfra={primary_summary.get('covered_cells_noninfra', 'missing')}"
        ),
        "The summary intentionally records undercoverage rather than performance conclusions.",
        "Regenerate scripts/analyze_model_results.py after any run_results change.",
        ["data/model_result_summary.csv", "scripts/analyze_model_results.py"],
    ))
    rows.append(row(
        "report_sample_size_and_version_disclosure",
        "report_text",
        "pass" if not report_missing_versions and not missing_report_phrases and not missing_model_phrases else "fail",
        (
            f"model_versions_in_detailed_report={len(model_versions) - len(report_missing_versions)}/{len(model_versions)}; "
            f"missing_versions={compact_json(report_missing_versions)}; "
            f"missing_main_phrases={compact_json(missing_report_phrases)}; "
            f"missing_model_analysis_phrases={compact_json(missing_model_phrases)}"
        ),
        "The concise report summarizes counts but leaves full model-version rows to the detailed evidence appendix.",
        "Keep sample sizes, k, infra policy, and model versions visible in generated report text.",
        ["reports/metr_style_report.md", "reports/model_run_analysis.md", "data/model_result_summary.csv"],
    ))
    rows.append(row(
        "local_qa_exclusion_boundary",
        "claim_boundary",
        "pass" if "local qa rows" in lower_main and "validation evidence, not model performance" in lower_main else "fail",
        f"local_qa_rows={len(local_rows)}; provider_rows={len(provider_rows)}",
        "Local QA rows validate grading behavior and must not enter model-capability summaries.",
        "Keep local QA excluded from model_result_summary and benchmark pass-rate text.",
        ["reports/metr_style_report.md", "reports/model_run_analysis.md", "data/run_results.csv"],
    ))
    rows.append(row(
        "infra_policy_boundary",
        "claim_boundary",
        "pass" if "infra-failure rows are retained" in lower_main and "excluded from pass-rate summaries" in lower_main else "fail",
        (
            f"provider_infra_rows={len(provider_rows) - len(noninfra_provider_rows)}; "
            f"accepted_infra_rows={len(accepted_provider_rows) - len(accepted_noninfra_rows)}"
        ),
        "Provider reliability claims need many more rows; this row only checks accounting policy disclosure.",
        "Retain infra rows in raw data and report them separately from capability means.",
        ["reports/metr_style_report.md", "data/run_results.csv", "data/model_result_summary.csv"],
    ))
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row_data["status"] for row_data in rows)
    area_counts = Counter(row_data["area"] for row_data in rows)
    lines = [
        "# Model Evidence Provenance Audit",
        "",
        "This generated audit checks whether committed non-local run rows have enough provenance for a research report: model versions, k, transcripts, sample sizes, infra accounting, and a clear boundary between smoke rows and benchmark claims.",
        "",
        "## Summary",
        "",
        f"- checks: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- areas: `{compact_json(dict(sorted(area_counts.items())))}`",
        "",
        "## Check Table",
        "",
        "| check | area | status | evidence | limitation | required action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row_data in rows:
        lines.append(
            f"| `{row_data['check_id']}` | {row_data['area']} | {row_data['status']} | "
            f"{escaped(row_data['evidence'])} | {escaped(row_data['limitation'])} | "
            f"{escaped(row_data['required_action'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`pass` means the current smoke-run evidence is traceable and correctly caveated. It does not mean the sample is large enough for performance claims. `fail` means a report reader could not audit model/version/sample-size provenance from committed artifacts.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "model_evidence_provenance_audit.csv", rows)
    write_markdown(ROOT / "reports" / "model_evidence_provenance_audit.md", rows)
    failures = sum(1 for row_data in rows if row_data["status"] == "fail")
    print(
        "wrote data/model_evidence_provenance_audit.csv and "
        f"reports/model_evidence_provenance_audit.md with {len(rows)} checks; failures={failures}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
