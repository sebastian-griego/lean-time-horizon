from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "reports" / "validation_manifest.json"

FIELDS = [
    "check_id",
    "area",
    "status",
    "evidence",
    "limitation",
    "next_action",
]

REQUIRED_COMMANDS = {
    "lake exe cache get",
    "lake build",
    "python scripts/validate_all.py",
    "python scripts/audit_difficulty.py",
    "python scripts/generate_task_quality_matrix.py",
    "python scripts/generate_candidate_pruning_audit.py",
    "python scripts/generate_accepted_task_cards.py",
    "python scripts/generate_independent_review_packet.py",
    "python scripts/audit_independent_review_status.py",
    "python scripts/audit_diagnostic_coverage.py",
    "python scripts/generate_construct_validity_matrix.py",
    "python scripts/record_local_qa_results.py",
    "python scripts/audit_failure_label_reviews.py",
    "python scripts/audit_run_integrity.py",
    "python scripts/generate_report.py",
    "python scripts/audit_figure_manifest.py",
    "python scripts/audit_data_schema_manifest.py",
    "python scripts/generate_reviewer_reproduction_packet.py",
    "python scripts/run_clean_workspace_replay.py",
    "python scripts/generate_statistical_analysis_plan.py",
    "python scripts/audit_model_sweep_coverage.py",
    "python scripts/audit_passk_claim_boundaries.py",
    "python scripts/audit_statistical_reporting.py",
    "python scripts/audit_report_source_traceability.py",
    "python scripts/export_public_tasks.py --out public_tasks",
    "python scripts/validate_public_export.py --out public_tasks",
    "python scripts/audit_security_leakage.py",
    "python scripts/generate_taiga_problem_metadata.py",
    "python scripts/audit_taiga_wrapper_isolation.py",
    "python scripts/audit_threat_coverage.py",
    "python scripts/audit_requirement_coverage.py --public-export public_tasks",
    "python scripts/audit_claim_evidence.py",
    "python scripts/generate_claim_authorization_matrix.py",
    "python scripts/generate_concise_report.py",
    "python scripts/audit_report_claim_conformance.py",
    "python scripts/audit_report_shape.py",
    "python scripts/audit_report_count_consistency.py",
    "python scripts/generate_peer_review_matrix.py",
    "python scripts/audit_final_delivery_checklist.py",
    "python scripts/audit_regeneration_commands.py",
    "python scripts/write_validation_manifest.py --public-export public_tasks",
    "python scripts/audit_validation_manifest.py",
}

ALLOWED_UNHASHED_ARTIFACTS = {
    # Written after the manifest or intentionally excluded to avoid circular hashes.
    "data/validation_manifest_audit.csv",
    "reports/validation_manifest_audit.md",
    "reports/metr_style_report.md",
    "reports/evidence_appendix.md",
    # Human-readable progress log, not a source artifact for report claims.
    "reports/overnight_progress.md",
}


def read_manifest() -> dict:
    if not MANIFEST.exists():
        return {}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def build_rows() -> list[dict[str, str]]:
    manifest = read_manifest()
    note = str(manifest.get("note", ""))
    git = manifest.get("git", {}) if isinstance(manifest.get("git"), dict) else {}
    commands = [str(command) for command in manifest.get("regeneration_commands", [])]
    artifacts = manifest.get("artifacts", [])
    if not isinstance(artifacts, list):
        artifacts = []
    public_export = manifest.get("public_export", {}) if isinstance(manifest.get("public_export"), dict) else {}

    rows: list[dict[str, str]] = []
    schema_ok = (
        manifest.get("schema_version") == 1
        and bool(manifest.get("generated_at_utc"))
        and isinstance(manifest.get("tool_versions"), dict)
        and isinstance(manifest.get("task_summary"), dict)
        and isinstance(manifest.get("run_result_summary"), dict)
        and "dirty status can reflect" in note
        and "omits reports/metr_style_report.md and reports/evidence_appendix.md" in note
    )
    rows.append(row(
        "schema_and_policy_note",
        "manifest_schema",
        "pass" if schema_ok else "fail",
        (
            f"schema_version={manifest.get('schema_version')}; generated_at_present={bool(manifest.get('generated_at_utc'))}; "
            f"tool_versions_present={isinstance(manifest.get('tool_versions'), dict)}; policy_note_present={schema_ok}"
        ),
        "The manifest records generation-time state and intentionally omits self-referential main-report hashes.",
        "Regenerate reports/validation_manifest.json with scripts/write_validation_manifest.py and keep the policy note explicit.",
    ))

    command_set = set(commands)
    missing_commands = sorted(REQUIRED_COMMANDS - command_set)
    rows.append(row(
        "regeneration_command_coverage",
        "commands",
        "pass" if not missing_commands and len(commands) >= len(REQUIRED_COMMANDS) else "fail",
        f"commands={len(commands)}; required={len(REQUIRED_COMMANDS)}; missing={compact_json(missing_commands)}",
        "Command coverage proves the intended local gate is listed, not that it was run on a clean hosted environment.",
        "Keep the README, manifest, and full validation command list in sync.",
    ))

    mismatches: list[str] = []
    missing_paths: list[str] = []
    checked_hashes = 0
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        rel = str(artifact.get("path", ""))
        if not rel:
            continue
        path = ROOT / rel
        recorded_exists = bool(artifact.get("exists"))
        if not path.exists():
            if recorded_exists:
                missing_paths.append(rel)
            continue
        if not recorded_exists:
            mismatches.append(f"{rel}: recorded missing but exists")
            continue
        recorded_hash = str(artifact.get("sha256", ""))
        if recorded_hash:
            checked_hashes += 1
            actual_hash = sha256(path)
            if actual_hash != recorded_hash:
                mismatches.append(rel)
    rows.append(row(
        "artifact_hash_integrity",
        "artifact_hashes",
        "pass" if not mismatches and not missing_paths and checked_hashes > 0 else "fail",
        (
            f"artifacts={len(artifacts)}; checked_hashes={checked_hashes}; "
            f"hash_mismatches={len(mismatches)}; missing_recorded_paths={len(missing_paths)}; "
            f"examples={compact_json((mismatches + missing_paths)[:8])}"
        ),
        "The manifest hashes generated local artifacts but intentionally avoids self-referential report hashes.",
        "Regenerate the full local gate if any hash mismatch appears.",
    ))

    recorded_paths = {
        str(artifact.get("path", ""))
        for artifact in artifacts
        if isinstance(artifact, dict) and str(artifact.get("path", ""))
    }
    inventory_candidates = set()
    inventory_candidates.update(path.relative_to(ROOT).as_posix() for path in (ROOT / "data").glob("*.csv"))
    inventory_candidates.update(path.relative_to(ROOT).as_posix() for path in (ROOT / "reports").glob("*.md"))
    inventory_candidates.update(path.relative_to(ROOT).as_posix() for path in (ROOT / "scripts").glob("*.py"))
    missing_inventory = sorted(
        path for path in inventory_candidates
        if path not in recorded_paths and path not in ALLOWED_UNHASHED_ARTIFACTS
    )
    rows.append(row(
        "artifact_inventory_coverage",
        "artifact_hashes",
        "pass" if not missing_inventory else "fail",
        (
            f"inventory_candidates={len(inventory_candidates)}; recorded_artifacts={len(recorded_paths)}; "
            f"allowed_unhashed={len(ALLOWED_UNHASHED_ARTIFACTS)}; missing_inventory={len(missing_inventory)}; "
            f"examples={compact_json(missing_inventory[:12])}"
        ),
        "The inventory check covers data CSVs, report markdown, and scripts. It intentionally excludes self-referential final reports, the validation-manifest audit output, and the progress log.",
        "Add omitted evidence files to HASHED_ARTIFACTS or document them in ALLOWED_UNHASHED_ARTIFACTS.",
    ))

    omitted_report_hashes = (
        not any(artifact.get("path") == "reports/metr_style_report.md" for artifact in artifacts if isinstance(artifact, dict))
        and not any(artifact.get("path") == "reports/evidence_appendix.md" for artifact in artifacts if isinstance(artifact, dict))
        and "omits reports/metr_style_report.md and reports/evidence_appendix.md" in note
    )
    rows.append(row(
        "self_reference_boundary",
        "artifact_hashes",
        "pass" if omitted_report_hashes else "fail",
        f"main_report_omitted=True; evidence_appendix_omitted=True; policy_note_mentions_omission={'omits reports/metr_style_report.md and reports/evidence_appendix.md' in note}",
        "The main report and appendix are regenerated after manifest writing and therefore cannot be hashed by the manifest without circularity.",
        "Use git history plus report-source traceability for those final rendered reports.",
    ))

    public_ok = (
        public_export.get("configured") is True
        and public_export.get("exists") is True
        and int(public_export.get("task_count", 0) or 0) >= 1
        and int(public_export.get("hidden_or_wrong_path_count", 0) or 0) == 0
    )
    rows.append(row(
        "public_export_snapshot",
        "public_export",
        "pass" if public_ok else "fail",
        (
            f"configured={public_export.get('configured')}; exists={public_export.get('exists')}; "
            f"task_count={public_export.get('task_count')}; hidden_or_wrong_path_count={public_export.get('hidden_or_wrong_path_count')}"
        ),
        "This is a local public-export snapshot, not hosted QA evidence.",
        "Run hosted QA before treating the public export as a locked problem set.",
    ))

    dirty = bool(git.get("dirty"))
    status_short = git.get("status_short", [])
    if not isinstance(status_short, list):
        status_short = []
    dirty_policy_ok = (
        (not dirty)
        or (
            dirty
            and bool(status_short)
            and "dirty status can reflect" in note
        )
    )
    rows.append(row(
        "git_snapshot_policy",
        "git_state",
        "pass" if dirty_policy_ok else "fail",
        f"dirty={dirty}; status_entries={len(status_short)}; policy_note_present={'dirty status can reflect' in note}",
        "A dirty generation-time snapshot is expected for committed report updates; this is not a clean-checkout proof.",
        "For a release tag, run the full gate from a clean checkout or CI and record that evidence separately.",
    ))

    task_summary = manifest.get("task_summary", {}) if isinstance(manifest.get("task_summary"), dict) else {}
    run_summary = manifest.get("run_result_summary", {}) if isinstance(manifest.get("run_result_summary"), dict) else {}
    rows.append(row(
        "summary_count_snapshot",
        "counts",
        "pass" if task_summary and run_summary else "fail",
        (
            f"task_count={task_summary.get('task_count')}; "
            f"acceptance_status_counts={compact_json(task_summary.get('acceptance_status_counts', {}))}; "
            f"run_rows={run_summary.get('row_count')}; local_qa_rows={run_summary.get('local_qa_row_count')}; "
            f"model_rows={run_summary.get('model_sweep_row_count')}"
        ),
        "Count snapshots are local evidence and do not imply benchmark-scale sufficiency.",
        "Keep count snapshots aligned with requirement coverage and release-decision gates.",
    ))

    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row["status"] for row in rows)
    area_counts = Counter(row["area"] for row in rows)
    lines = [
        "# Validation Manifest Audit",
        "",
        "This generated audit checks `reports/validation_manifest.json` as reproducibility evidence. It verifies schema fields, command coverage, current artifact hashes, public-export summary, and the policy that the manifest records generation-time git state rather than a post-commit clean-checkout proof.",
        "",
        "## Summary",
        "",
        f"- checks: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- areas: `{compact_json(dict(sorted(area_counts.items())))}`",
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
        "`pass` means the manifest is internally consistent for the local reproducibility role it claims. It does not mean the benchmark has been validated from a clean checkout, hosted environment, or final release tag.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "validation_manifest_audit.csv", rows)
    write_markdown(ROOT / "reports" / "validation_manifest_audit.md", rows)
    failures = sum(1 for row_data in rows if row_data["status"] == "fail")
    print(
        "wrote data/validation_manifest_audit.csv and "
        f"reports/validation_manifest_audit.md with {len(rows)} checks; failures={failures}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
