from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REGENERATION_COMMANDS = [
    "lake build",
    "python scripts/validate_all.py",
    "python scripts/audit_difficulty.py",
    "python scripts/generate_task_quality_matrix.py",
    "python scripts/audit_diagnostic_coverage.py",
    "python scripts/audit_human_time_calibration.py",
    "python scripts/generate_human_timing_packet.py",
    "python scripts/record_local_qa_results.py",
    "python scripts/audit_pin_coverage.py",
    "python scripts/audit_run_integrity.py",
    "python scripts/audit_grader_hardening.py",
    "python scripts/generate_evaluation_protocol.py",
    "python scripts/generate_model_sweep_packet.py",
    "python scripts/analyze_model_results.py",
    "python scripts/generate_report.py",
    "python scripts/audit_statistical_reporting.py",
    "python scripts/audit_provider_readiness.py",
    "python scripts/generate_report.py",
    "python scripts/export_public_tasks.py --out public_tasks",
    "python scripts/validate_public_export.py --out public_tasks",
    "python scripts/audit_hosted_qa_readiness.py",
    "python scripts/generate_task_asset_manifest.py --public-export public_tasks",
    "python scripts/audit_prompt_contracts.py",
    "python scripts/audit_scaffold_support.py",
    "python scripts/audit_requirement_coverage.py --public-export public_tasks",
    "python scripts/audit_claim_evidence.py",
    "python scripts/generate_release_decision_log.py",
    "python scripts/generate_freeze_readiness_roadmap.py",
    "python scripts/audit_scaffold_support.py",
    "python scripts/audit_requirement_coverage.py --public-export public_tasks",
    "python scripts/audit_claim_evidence.py",
    "python scripts/generate_release_decision_log.py",
    "python scripts/generate_freeze_readiness_roadmap.py",
    "python scripts/audit_scaffold_support.py",
    "python scripts/audit_requirement_coverage.py --public-export public_tasks",
    "python scripts/audit_claim_evidence.py",
    "python scripts/generate_release_decision_log.py",
    "python scripts/generate_freeze_readiness_roadmap.py",
    "python scripts/write_validation_manifest.py --public-export public_tasks",
    "python scripts/generate_report.py",
]

HASHED_ARTIFACTS = [
    "lean-toolchain",
    "lakefile.lean",
    "lake-manifest.json",
    "README.md",
    "docs/axiom_policy.md",
    "data/benchmark_requirements.csv",
    "data/task_metadata.csv",
    "data/task_metadata_schema.json",
    "data/run_results.csv",
    "data/run_results_schema.json",
    "data/failure_label_schema.json",
    "data/scaffold_variants.csv",
    "data/model_sweep_plan.csv",
    "data/model_sweep_execution_commands.csv",
    "data/model_sweep_execution_checklist.csv",
    "data/model_result_summary.csv",
    "data/statistical_reporting_audit.csv",
    "data/provider_readiness_audit.csv",
    "data/hosted_qa_readiness_audit.csv",
    "data/validation_commands.csv",
    "data/difficulty_audit.csv",
    "data/task_quality_matrix.csv",
    "data/diagnostic_coverage_audit.csv",
    "data/human_time_observations.csv",
    "data/human_time_observations_schema.json",
    "data/human_time_calibration_audit.csv",
    "data/human_timing_collection_plan.csv",
    "data/human_time_observations_template.csv",
    "data/task_asset_manifest.csv",
    "data/prompt_contract_audit.csv",
    "data/pin_coverage_audit.csv",
    "data/run_integrity_audit.csv",
    "data/grader_hardening_audit.csv",
    "data/claim_evidence_audit.csv",
    "data/release_decision_log.csv",
    "data/freeze_readiness_roadmap.csv",
    "data/scaffold_support_audit.csv",
    "data/requirement_coverage.csv",
    "reports/difficulty_audit.md",
    "reports/task_quality_matrix.md",
    "reports/diagnostic_coverage_audit.md",
    "reports/human_time_calibration_audit.md",
    "reports/human_timing_collection_packet.md",
    "reports/task_asset_manifest.md",
    "reports/prompt_contract_audit.md",
    "reports/pin_coverage_audit.md",
    "reports/run_integrity_audit.md",
    "reports/grader_hardening_audit.md",
    "reports/claim_evidence_audit.md",
    "reports/release_decision_log.md",
    "reports/freeze_readiness_roadmap.md",
    "reports/scaffold_support_audit.md",
    "reports/accepted_task_review.md",
    "reports/evaluation_protocol.md",
    "reports/model_sweep_execution_packet.md",
    "reports/model_run_analysis.md",
    "reports/statistical_reporting_audit.md",
    "reports/provider_readiness_audit.md",
    "reports/hosted_qa_readiness_audit.md",
    "reports/requirement_coverage.md",
    "reports/figures/task_counts_by_family.svg",
    "reports/figures/task_counts_by_bucket.svg",
    "reports/figures/top_skills.svg",
    "reports/figures/run_rows_by_model.svg",
    "reports/figures/task_minutes_by_bucket.svg",
    "scripts/validate_all.py",
    "scripts/validate_task.py",
    "scripts/audit_difficulty.py",
    "scripts/generate_task_quality_matrix.py",
    "scripts/audit_diagnostic_coverage.py",
    "scripts/audit_human_time_calibration.py",
    "scripts/generate_human_timing_packet.py",
    "scripts/generate_task_asset_manifest.py",
    "scripts/audit_prompt_contracts.py",
    "scripts/audit_pin_coverage.py",
    "scripts/audit_run_integrity.py",
    "scripts/audit_grader_hardening.py",
    "scripts/audit_claim_evidence.py",
    "scripts/generate_release_decision_log.py",
    "scripts/generate_freeze_readiness_roadmap.py",
    "scripts/audit_scaffold_support.py",
    "scripts/audit_requirement_coverage.py",
    "scripts/generate_evaluation_protocol.py",
    "scripts/generate_model_sweep_packet.py",
    "scripts/analyze_model_results.py",
    "scripts/audit_statistical_reporting.py",
    "scripts/audit_provider_readiness.py",
    "scripts/audit_hosted_qa_readiness.py",
    "scripts/record_local_qa_results.py",
    "scripts/generate_report.py",
    "scripts/export_public_tasks.py",
    "scripts/validate_public_export.py",
    "scripts/run_model_sweep.py",
    "scripts/lean_lookup.py",
    "scripts/write_validation_manifest.py",
]


def run(cmd: list[str]) -> dict[str, object]:
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return {
        "command": cmd,
        "returncode": result.returncode,
        "stdout_first_line": (result.stdout or "").splitlines()[:1],
    }


def git_info() -> dict[str, object]:
    branch = run(["git", "branch", "--show-current"])
    head = run(["git", "rev-parse", "HEAD"])
    status = run(["git", "status", "--short"])
    status_lines = status["stdout_first_line"]
    full_status = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    ).stdout.splitlines()
    return {
        "branch": (branch["stdout_first_line"][0] if branch["stdout_first_line"] else "").strip(),
        "head": (head["stdout_first_line"][0] if head["stdout_first_line"] else "").strip(),
        "dirty": bool(full_status),
        "status_short": full_status,
        "status_summary_first_line": status_lines[0] if status_lines else "",
    }


def tool_versions() -> dict[str, object]:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "lean": run(["lean", "--version"]),
        "lake": run(["lake", "--version"]),
        "git": run(["git", "--version"]),
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_rows(path: Path) -> int | None:
    if path.suffix.lower() != ".csv":
        return None
    with path.open(newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))


def line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f)


def artifact_record(relative: str) -> dict[str, object]:
    path = ROOT / relative
    if not path.exists():
        return {"path": relative, "exists": False}
    record: dict[str, object] = {
        "path": relative,
        "exists": True,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "line_count": line_count(path),
    }
    rows = csv_rows(path)
    if rows is not None:
        record["row_count"] = rows
    return record


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def count_by(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = row.get(field, "")
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def task_summary() -> dict[str, object]:
    rows = read_csv(ROOT / "data" / "task_metadata.csv")
    return {
        "task_count": len(rows),
        "acceptance_status_counts": count_by(rows, "acceptance_status"),
        "split_counts": count_by(rows, "split"),
        "family_counts": count_by(rows, "family"),
        "human_time_bucket_counts": count_by(rows, "human_time_bucket"),
    }


def run_result_summary() -> dict[str, object]:
    rows = read_csv(ROOT / "data" / "run_results.csv")
    local_rows = [row for row in rows if row.get("qa_stage") == "local_qa"]
    model_rows = [row for row in rows if row.get("qa_stage") != "local_qa"]
    return {
        "row_count": len(rows),
        "local_qa_row_count": len(local_rows),
        "model_sweep_row_count": len(model_rows),
        "local_qa_status_counts": count_by(local_rows, "qa_findings_status"),
        "model_failure_label_counts": count_by(model_rows, "failure_label"),
    }


def public_export_summary(public_export: Path | None) -> dict[str, object]:
    if public_export is None:
        return {"configured": False}
    path = public_export.resolve()
    metadata_files = list(path.rglob("metadata.json")) if path.exists() else []
    hidden_paths = [p for p in path.rglob("*") if "hidden" in p.parts or "wrong" in p.parts] if path.exists() else []
    try:
        relative_path = str(path.relative_to(ROOT))
    except ValueError:
        relative_path = str(path)
    return {
        "configured": True,
        "path": str(path),
        "relative_path": relative_path,
        "exists": path.exists(),
        "task_count": len(metadata_files),
        "hidden_or_wrong_path_count": len(hidden_paths),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "reports" / "validation_manifest.json")
    parser.add_argument("--public-export", type=Path, default=None)
    args = parser.parse_args()

    manifest = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "note": (
            "This manifest is written after the local regeneration gate has passed. "
            "It hashes inputs and generated evidence files, but intentionally omits "
            "reports/metr_style_report.md to avoid a self-referential report hash. "
            "Git status is captured before the final commit, so a dirty status can "
            "reflect the in-progress report commit rather than a validation failure."
        ),
        "git": git_info(),
        "tool_versions": tool_versions(),
        "regeneration_commands": REGENERATION_COMMANDS,
        "task_summary": task_summary(),
        "run_result_summary": run_result_summary(),
        "public_export": public_export_summary(args.public_export),
        "artifacts": [artifact_record(relative) for relative in HASHED_ARTIFACTS],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
