from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "check_id",
    "playbook_item",
    "status",
    "evidence",
    "source_artifacts",
    "limitation",
    "next_action",
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
    playbook_item: str,
    status: str,
    evidence: str,
    source_artifacts: list[str],
    limitation: str,
    next_action: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "playbook_item": playbook_item,
        "status": status,
        "evidence": evidence,
        "source_artifacts": ";".join(source_artifacts),
        "limitation": limitation,
        "next_action": next_action,
    }


def status_counts(rows: list[dict[str, str]], field: str) -> Counter[str]:
    return Counter(row_data.get(field, "unknown") for row_data in rows)


def as_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def model_primary_coverage(model_summary: list[dict[str, str]]) -> dict[str, str]:
    for row_data in model_summary:
        if (
            row_data.get("analysis_set") == "primary_plan_coverage"
            and row_data.get("group_by") == "all"
            and row_data.get("group") == "all"
        ):
            return row_data
    return {}


def public_export_summary() -> dict[str, object]:
    root = ROOT / "public_tasks"
    if not root.exists():
        return {"exists": False, "task_count": 0, "hidden_or_wrong_path_count": 0}
    hidden_or_wrong = [
        path for path in root.rglob("*")
        if "hidden" in path.parts or "wrong" in path.parts
    ]
    task_count = len([path for path in root.rglob("metadata.json")])
    return {
        "exists": True,
        "task_count": task_count,
        "hidden_or_wrong_path_count": len(hidden_or_wrong),
    }


def build_rows() -> list[dict[str, str]]:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    run_results = read_csv(ROOT / "data" / "run_results.csv")
    model_summary = read_csv(ROOT / "data" / "model_result_summary.csv")
    model_sweep_plan = read_csv(ROOT / "data" / "model_sweep_plan.csv")
    hosted = read_csv(ROOT / "data" / "hosted_qa_readiness_audit.csv")
    figure_manifest = read_csv(ROOT / "data" / "figure_manifest.csv")
    report_count = read_csv(ROOT / "data" / "report_count_consistency_audit.csv")
    report_claim_conformance = read_csv(ROOT / "data" / "report_claim_conformance_audit.csv")
    task_asset_manifest = read_csv(ROOT / "data" / "task_asset_manifest.csv")
    taiga_isolation = read_csv(ROOT / "data" / "taiga_wrapper_isolation_audit.csv")
    main_report = read_text(ROOT / "reports" / "metr_style_report.md")
    concise_report = read_text(ROOT / "reports" / "concise_metr_report.md")

    release_tasks = [
        row_data for row_data in metadata
        if row_data.get("acceptance_status") in {"accepted_v0", "calibration_only", "candidate_review_pending"}
    ]
    accepted = [row_data for row_data in metadata if row_data.get("acceptance_status") == "accepted_v0"]
    split_counts = status_counts(release_tasks, "split")
    split_ok = bool(release_tasks) and set(split_counts).issubset({"dev", "test", "candidates"})
    accepted_ids = {row_data.get("task_id", "") for row_data in accepted}

    primary = model_primary_coverage(model_summary)
    planned_cells = as_int(primary.get("planned_cells", str(len(model_sweep_plan))))
    covered_noninfra = as_int(primary.get("covered_cells_noninfra", "0"))
    nonlocal_rows = [row_data for row_data in run_results if row_data.get("qa_stage") != "local_qa"]
    noninfra_rows = [
        row_data for row_data in nonlocal_rows
        if row_data.get("infra_fail_count") in {"", "0", 0}
    ]

    plan_by_scaffold: dict[str, set[str]] = {}
    for row_data in model_sweep_plan:
        if row_data.get("analysis_set") != "primary_accepted_v0":
            continue
        plan_by_scaffold.setdefault(row_data.get("scaffold", ""), set()).add(row_data.get("task_id", ""))
    planned_same_set = bool(plan_by_scaffold) and all(task_ids == accepted_ids for task_ids in plan_by_scaffold.values())
    observed_scaffolds = sorted({row_data.get("scaffold", "") for row_data in noninfra_rows if row_data.get("scaffold")})

    hosted_by_id = {row_data.get("check_id", ""): row_data for row_data in hosted}
    hosted_status_counts = status_counts(hosted, "status")
    env_linter = hosted_by_id.get("env_linter", {})
    full_env = hosted_by_id.get("transcript_health_or_full_env_qa", {})
    problem_version = hosted_by_id.get("problem_version_evidence", {})
    freeze_mapping = hosted_by_id.get("exact_version_freeze_mapping", {})
    qa_resolution = hosted_by_id.get("qa_findings_resolution", {})

    figure_status_counts = status_counts(figure_manifest, "current_status")
    generated_figures = [
        row_data for row_data in figure_manifest
        if row_data.get("category", "").startswith("generated")
    ]
    generated_figures_ok = bool(generated_figures) and all(
        row_data.get("figure_exists") == "true"
        and row_data.get("sources_exist") == "true"
        for row_data in generated_figures
    )
    report_count_ok = bool(report_count) and not [row_data for row_data in report_count if row_data.get("status") == "fail"]

    provider_versions_present = "provider/model versions in committed smoke rows" in main_report
    sample_sizes_present = "sample sizes" in main_report and "model versions" in main_report
    count_consistency_ok = report_count_ok and bool(report_count)
    claim_conformance_ok = bool(report_claim_conformance) and not [
        row_data for row_data in report_claim_conformance
        if row_data.get("status") == "fail"
    ]

    public_export = public_export_summary()
    public_export_ok = (
        public_export.get("exists") is True
        and as_int(str(public_export.get("task_count", "0"))) == len(release_tasks)
        and as_int(str(public_export.get("hidden_or_wrong_path_count", "0"))) == 0
    )
    validation_manifest_exists = (ROOT / "reports" / "validation_manifest.json").exists()
    taiga_isolation_ok = bool(taiga_isolation) and not [
        row_data for row_data in taiga_isolation
        if row_data.get("status") == "fail"
    ]

    hidden_asset_rows = [
        row_data for row_data in task_asset_manifest
        if row_data.get("asset_role", "").startswith("hidden")
    ]
    public_hidden_rows = [
        row_data for row_data in hidden_asset_rows
        if row_data.get("public_export_expected") == "true"
        or row_data.get("public_export_exists") == "true"
    ]

    rows: list[dict[str, str]] = []
    rows.append(row(
        "final_versions_have_pass_at_k",
        "all exact final problem versions have pass@10 or the agreed pass@k",
        "block",
        (
            f"planned_primary_cells={planned_cells}; covered_noninfra_cells={covered_noninfra}; "
            f"noninfra_provider_rows={len(noninfra_rows)}; nonlocal_rows={len(nonlocal_rows)}"
        ),
        ["data/model_sweep_plan.csv", "data/model_result_summary.csv", "data/run_results.csv"],
        "The plan specifies pass@10 cells, but committed provider rows do not cover the accepted task/scaffold plan.",
        "Run the planned accepted-core pass@10 sweep on exact final problem versions and commit transcripts/results.",
    ))
    rows.append(row(
        "scaffolds_use_same_task_set",
        "every scaffold uses the same task set unless explicitly documented",
        "caution" if planned_same_set else "block",
        (
            f"planned_scaffolds={compact_json(sorted(plan_by_scaffold))}; "
            f"planned_same_accepted_set={planned_same_set}; observed_noninfra_scaffolds={compact_json(observed_scaffolds)}"
        ),
        ["data/model_sweep_plan.csv", "data/run_results.csv"],
        "The planned sweep uses the same accepted task set, but observed committed provider evidence has not yet covered the scaffold ladder.",
        "Keep the same accepted task IDs across one-shot, lookup, and lookup_unlimited runs; document any exclusion before running.",
    ))
    rows.append(row(
        "env_linter_findings_resolved",
        "no unresolved warning/error/critical Env Linter findings",
        "block",
        f"env_linter_status={env_linter.get('status', 'missing')}; hosted_status_counts={compact_json(dict(sorted(hosted_status_counts.items())))}",
        ["data/hosted_qa_readiness_audit.csv", "reports/hosted_qa_readiness_audit.md"],
        "No Env Linter result rows are committed, so absence of unresolved findings is unproven.",
        "Run Env Linter on exact hosted problem versions and record each warning/error/critical finding disposition.",
    ))
    rows.append(row(
        "full_env_qa_10_attempts",
        "final QA used Full Env QA on 10 attempts",
        "block",
        f"full_env_status={full_env.get('status', 'missing')}; evidence={full_env.get('evidence', '')}",
        ["data/hosted_qa_readiness_audit.csv", "reports/hosted_qa_readiness_audit.md"],
        "No Full Env QA result rows on final exact problem versions are committed.",
        "Run Full Env QA on 10 attempts after hosted smoke stability and commit result IDs/findings.",
    ))
    rows.append(row(
        "late_qa_findings_settled",
        "late QA findings have settled",
        "block",
        f"qa_resolution_status={qa_resolution.get('status', 'missing')}; evidence={qa_resolution.get('evidence', '')}",
        ["data/hosted_qa_readiness_audit.csv", "reports/hosted_qa_readiness_audit.md"],
        "There are no hosted QA rows or late-finding timestamps to prove the 30-45 minute settling window has elapsed.",
        "Record hosted QA completion times and final finding dispositions after the settling window.",
    ))
    rows.append(row(
        "repo_matches_uploaded_environment",
        "repo source matches the uploaded environment",
        "block",
        (
            f"problem_version_status={problem_version.get('status', 'missing')}; "
            f"freeze_mapping_status={freeze_mapping.get('status', 'missing')}"
        ),
        ["data/hosted_qa_readiness_audit.csv", "taiga/problems_metadata.template.json", "reports/validation_manifest.json"],
        "The local Taiga package scaffold exists, but no immutable uploaded image digest or hosted problem-version mapping is committed.",
        "Commit image digest, environment/problem-version IDs, and snapshot/tag mapping for the exact uploaded package.",
    ))
    rows.append(row(
        "plots_regenerate_from_committed_csv",
        "plots regenerate from committed CSV files",
        "pass" if generated_figures_ok and report_count_ok else "block",
        (
            f"generated_figures={len(generated_figures)}; generated_figures_ok={generated_figures_ok}; "
            f"figure_status_counts={compact_json(dict(sorted(figure_status_counts.items())))}; report_count_failures={sum(1 for item in report_count if item.get('status') == 'fail')}"
        ),
        ["data/figure_manifest.csv", "reports/figure_manifest.md", "data/report_count_consistency_audit.csv", "reports/figures"],
        "Generated descriptive/provenance plots are covered; blocked performance plots intentionally remain absent.",
        "Keep performance plots blocked until provider/scaffold coverage satisfies the statistical plan.",
    ))
    rows.append(row(
        "report_states_sample_sizes_and_model_versions",
        "report text states sample sizes and model versions",
        "pass" if provider_versions_present and sample_sizes_present and count_consistency_ok and claim_conformance_ok else "block",
        (
            f"provider_versions_phrase={provider_versions_present}; sample_sizes_phrase={sample_sizes_present}; "
            f"report_count_ok={count_consistency_ok}; claim_conformance_ok={claim_conformance_ok}"
        ),
        ["reports/metr_style_report.md", "reports/model_evidence_provenance_audit.md", "data/report_count_consistency_audit.csv", "data/report_claim_conformance_audit.csv"],
        "The report states sample sizes and model versions for smoke rows, but performance conclusions remain blocked by undercoverage.",
        "After broad sweeps, regenerate model provenance, count consistency, and claim-conformance audits before interpreting pass rates.",
    ))
    rows.append(row(
        "dev_test_split_marked",
        "dev/test split is clearly marked",
        "pass" if split_ok and split_counts.get("dev", 0) > 0 and split_counts.get("test", 0) > 0 else "block",
        f"release_split_counts={compact_json(dict(sorted(split_counts.items())))}; release_task_count={len(release_tasks)}",
        ["data/task_metadata.csv", "public_tasks"],
        "Split labels are local metadata/export evidence, not evidence of hosted problem-version mapping.",
        "Preserve split labels in metadata and hosted problem metadata when uploading exact versions.",
    ))
    rows.append(row(
        "hidden_references_not_public_runtime_assets",
        "hidden references are not in public runtime assets",
        "caution" if public_export_ok and validation_manifest_exists and taiga_isolation_ok and not public_hidden_rows else "block",
        (
            f"public_export={compact_json(public_export)}; validation_manifest_exists={validation_manifest_exists}; "
            f"hidden_asset_rows={len(hidden_asset_rows)}; hidden_assets_with_public_export_path={len(public_hidden_rows)}; "
            f"taiga_wrapper_isolation_ok={taiga_isolation_ok}"
        ),
        ["public_tasks", "data/task_asset_manifest.csv", "reports/validation_manifest.json", "data/taiga_wrapper_isolation_audit.csv"],
        "Local public export and wrapper mitigation pass, but hosted filesystem-tool isolation on uploaded images is still unproven.",
        "Run hosted preflight/Env Linter and record proof that tools cannot read hidden references, hidden pins, wrong submissions, or transient bundles.",
    ))
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter(row_data["status"] for row_data in rows)
    lines = [
        "# Final Delivery Checklist Audit",
        "",
        "This generated audit maps the `docs/lean_eval_project_playbook.md` final-delivery checklist to committed evidence. It is intentionally strict: a `block` means the final-delivery condition is not proven by current artifacts, while a `caution` means local evidence exists but hosted or execution evidence is still missing.",
        "",
        "## Summary",
        "",
        f"- checklist rows: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(counts.items())))}`",
        "",
        "## Checklist Table",
        "",
        "| check | status | playbook item | evidence | limitation | next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row_data in rows:
        lines.append(
            f"| `{row_data['check_id']}` | {row_data['status']} | {escaped(row_data['playbook_item'])} | "
            f"{escaped(row_data['evidence'])} | {escaped(row_data['limitation'])} | {escaped(row_data['next_action'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`pass` rows are supported by committed local artifacts. `caution` rows have useful local evidence but still need hosted or execution proof before final delivery. `block` rows are missing required final-delivery evidence and must remain blockers for locked-benchmark wording.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "final_delivery_checklist_audit.csv", rows)
    write_markdown(ROOT / "reports" / "final_delivery_checklist_audit.md", rows)
    counts = Counter(row_data["status"] for row_data in rows)
    print(
        "wrote data/final_delivery_checklist_audit.csv and "
        f"reports/final_delivery_checklist_audit.md with {len(rows)} rows; "
        f"statuses={compact_json(dict(sorted(counts.items())))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
