from __future__ import annotations

import csv
import json
import os
import py_compile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "check_id",
    "area",
    "status",
    "evidence",
    "required_for_hosted_qa",
    "current_state",
    "next_action",
]

REQUIRED_CHECKS = [
    "local_validation_gate",
    "public_export_ready",
    "taiga_container_artifact",
    "taiga_problem_metadata",
    "mcp_hooks",
    "hidden_material_isolation",
    "problem_version_evidence",
    "hosted_preflight_or_stage1",
    "transcript_health_or_full_env_qa",
    "env_linter",
    "qa_findings_resolution",
    "exact_version_freeze_mapping",
]
SKIP_DIRS = {".git", ".lake", "__pycache__", "public_tasks", "tmp"}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def iter_repo_files() -> list[str]:
    files: list[str] = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        base = Path(dirpath)
        for filename in filenames:
            files.append((base / filename).relative_to(ROOT).as_posix())
    return sorted(files)


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def bool_text(value: bool) -> str:
    return str(value).lower()


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def run_result_failures() -> int:
    return sum(1 for row in read_csv(ROOT / "data" / "run_integrity_audit.csv") if row.get("integrity_status") == "fail")


def public_export_summary() -> dict[str, object]:
    public_export = ROOT / "public_tasks"
    if not public_export.exists():
        return {"exists": False, "task_count": 0, "hidden_or_wrong_path_count": 0}
    metadata_files = list(public_export.rglob("metadata.json"))
    hidden_or_wrong = [path for path in public_export.rglob("*") if "hidden" in path.parts or "wrong" in path.parts]
    return {
        "exists": True,
        "task_count": len(metadata_files),
        "hidden_or_wrong_path_count": len(hidden_or_wrong),
    }


def py_compiles(path: Path) -> tuple[bool, str]:
    try:
        py_compile.compile(str(path), doraise=True)
    except py_compile.PyCompileError as exc:
        return False, str(exc)
    return True, ""


def problem_metadata_summary(paths: list[str], expected_count: int) -> dict[str, object]:
    files: list[dict[str, object]] = []
    total_problems = 0
    missing_required = 0
    placeholder_images = 0
    immutable_digest_images = 0
    latest_images = 0
    startup_wrapper_count = 0
    problem_ids: list[str] = []
    required = {"image", "startup_command", "id", "required_tools", "scratchpad"}
    for rel_path in paths:
        path = ROOT / rel_path
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            files.append({"path": rel_path, "valid_json": False, "error": str(exc)})
            continue
        problems = payload.get("problem_set", {}).get("problems", [])
        if not isinstance(problems, list):
            files.append({"path": rel_path, "valid_json": True, "problem_count": 0, "error": "missing problems list"})
            continue
        file_ids: list[str] = []
        for problem in problems:
            if not isinstance(problem, dict):
                missing_required += 1
                continue
            file_ids.append(str(problem.get("id", "")))
            problem_ids.append(str(problem.get("id", "")))
            missing_required += len([field for field in required if field not in problem])
            image = str(problem.get("image", ""))
            if "REPLACE_WITH" in image or "PLACEHOLDER" in image:
                placeholder_images += 1
            if "@sha256:" in image:
                immutable_digest_images += 1
            if image.endswith(":latest"):
                latest_images += 1
            if "taiga/mcp_server.py" in str(problem.get("startup_command", "")):
                startup_wrapper_count += 1
        total_problems += len(problems)
        files.append({
            "path": rel_path,
            "valid_json": True,
            "problem_count": len(problems),
            "first_ids": file_ids[:5],
        })
    return {
        "files": files,
        "total_problems": total_problems,
        "expected_count": expected_count,
        "missing_required_fields": missing_required,
        "placeholder_images": placeholder_images,
        "immutable_digest_images": immutable_digest_images,
        "latest_images": latest_images,
        "startup_wrapper_count": startup_wrapper_count,
        "unique_problem_ids": len(set(problem_ids)),
    }


def row(
    check_id: str,
    area: str,
    status: str,
    evidence: str,
    required_for_hosted_qa: str,
    current_state: str,
    next_action: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "status": status,
        "evidence": evidence,
        "required_for_hosted_qa": required_for_hosted_qa,
        "current_state": current_state,
        "next_action": next_action,
    }


def build_rows() -> list[dict[str, str]]:
    public_export = public_export_summary()
    metadata_rows = read_csv(ROOT / "data" / "task_metadata.csv")
    release_statuses = {"accepted_v0", "calibration_only", "candidate_review_pending"}
    expected_public_task_count = sum(
        1 for row_data in metadata_rows
        if row_data.get("acceptance_status") in release_statuses
    )
    repo_files = iter_repo_files()
    run_integrity_failures = run_result_failures()
    hosted_results = ROOT / "data" / "hosted_qa_results.csv"
    hosted_report = ROOT / "reports" / "hosted_qa.md"
    hosted_result_rows = read_csv(hosted_results)
    hosted_report_text = read_text(hosted_report)

    container_files = [
        path for path in repo_files
        if path.lower().endswith("dockerfile")
        or Path(path).name.lower() in {"dockerfile", "containerfile"}
    ]
    docker_text = "\n".join(read_text(ROOT / path) for path in container_files)
    problem_metadata_files = [
        path for path in repo_files
        if "problem" in path.lower()
        and "metadata" in path.lower()
        and path.lower().endswith((".json", ".jsonl"))
    ]
    mcp_hook_files = [
        path for path in repo_files
        if path.endswith(".py")
        and ("mcp" in path.lower() or "taiga" in path.lower())
        and "setup_problem" in read_text(ROOT / path)
        and "grade_problem" in read_text(ROOT / path)
    ]
    mcp_compile_results = {
        path: py_compiles(ROOT / path)
        for path in mcp_hook_files
    }
    mcp_compile_failures = {
        path: err
        for path, (ok, err) in mcp_compile_results.items()
        if not ok
    }
    problem_metadata = problem_metadata_summary(problem_metadata_files, expected_public_task_count)
    metadata_has_expected_release_rows = (
        int(problem_metadata["total_problems"]) == expected_public_task_count
        and int(problem_metadata["unique_problem_ids"]) == expected_public_task_count
    )
    metadata_template_ready = (
        bool(problem_metadata_files)
        and metadata_has_expected_release_rows
        and int(problem_metadata["missing_required_fields"]) == 0
        and int(problem_metadata["latest_images"]) == 0
        and int(problem_metadata["startup_wrapper_count"]) == expected_public_task_count
    )
    metadata_has_immutable_images = (
        metadata_template_ready
        and int(problem_metadata["immutable_digest_images"]) == expected_public_task_count
        and int(problem_metadata["placeholder_images"]) == 0
    )
    full_repo_copy = "COPY . " in docker_text or "COPY ./" in docker_text
    hidden_dirs_present = any((ROOT / "tasks" / split).exists() for split in ["dev", "test", "candidates"])
    filesystem_tools_present = bool(problem_metadata_files)
    hidden_isolation_documented = "hidden-material-safe" in read_text(ROOT / "taiga" / "README.md")

    local_ok = (
        (ROOT / "data" / "run_integrity_audit.csv").exists()
        and (ROOT / "data" / "validation_commands.csv").exists()
        and run_integrity_failures == 0
    )
    public_export_ok = (
        bool(public_export.get("exists"))
        and int(public_export.get("task_count", 0) or 0) == expected_public_task_count
        and int(public_export.get("hidden_or_wrong_path_count", 1)) == 0
    )

    stage1_rows = [row for row in hosted_result_rows if row.get("qa_stage") in {"preflight", "stage1_individual_checks"}]
    transcript_rows = [row for row in hosted_result_rows if row.get("qa_stage") in {"transcript_health", "full_env_qa"}]
    env_linter_rows = [row for row in hosted_result_rows if row.get("qa_stage") == "env_linter"]
    unresolved_findings = [
        row for row in hosted_result_rows
        if row.get("severity") in {"warning", "error", "critical"}
        and row.get("disposition") not in {"fixed", "false_positive_rebutted", "not_applicable"}
    ]
    freeze_mapping_present = "problem_version" in hosted_report_text and "snapshot" in hosted_report_text

    return [
        row(
            "local_validation_gate",
            "local_prerequisite",
            "pass" if local_ok else "fail",
            f"run_integrity_audit_exists={bool((ROOT / 'data' / 'run_integrity_audit.csv').exists())}; validation_commands_exists={bool((ROOT / 'data' / 'validation_commands.csv').exists())}; run_integrity_failures={run_integrity_failures}",
            "Clean local validation before upload or hosted runs.",
            "Local validation evidence is present and passing." if local_ok else "Local validation evidence is missing or failing.",
            "Keep local validation passing before any hosted upload.",
        ),
        row(
            "public_export_ready",
            "local_prerequisite",
            "pass" if public_export_ok else "fail",
            f"public_export={compact_json(public_export)}; expected_public_task_count={expected_public_task_count}",
            "Public task bundle must exclude hidden references and wrong submissions.",
            "Public export evidence is present in the validation manifest." if public_export_ok else "Public export evidence is missing or incomplete.",
            "Regenerate and validate public export immediately before hosted packaging.",
        ),
        row(
            "taiga_container_artifact",
            "hosted_packaging",
            "caution" if container_files else "block",
            f"container_artifacts={compact_json(container_files[:12])}",
            "A Docker/container artifact compatible with Taiga infrastructure.",
            "No committed Taiga container artifact was found." if not container_files else "A candidate Dockerfile is committed, but no uploaded immutable image digest or hosted preflight result is committed.",
            "Build and upload the container, then record the immutable image digest and hosted preflight result before upgrading this to hosted evidence.",
        ),
        row(
            "taiga_problem_metadata",
            "hosted_packaging",
            "pass" if metadata_has_immutable_images else ("caution" if metadata_template_ready else "block"),
            f"problem_metadata={compact_json(problem_metadata)}",
            "Problems-metadata JSON with image, startup command, ids, tools, scratchpad, and metadata.",
            (
                "No committed Taiga problems-metadata JSON was found."
                if not problem_metadata_files
                else (
                    "Generated problems-metadata covers the public release task set but still uses placeholder image values."
                    if metadata_template_ready and not metadata_has_immutable_images
                    else "Problems-metadata contains immutable image digests for the public release task set."
                )
            ),
            "Replace placeholder image values with immutable uploaded image digests and commit hosted problem-version IDs after upload.",
        ),
        row(
            "mcp_hooks",
            "hosted_packaging",
            "fail" if mcp_compile_failures else ("pass" if mcp_hook_files else "block"),
            f"mcp_hook_files={compact_json(mcp_hook_files[:12])}; py_compile_failures={compact_json(mcp_compile_failures)}",
            "Container exposes setup_problem and grade_problem hooks through MCP.",
            "No committed MCP hook implementation was found." if not mcp_hook_files else "A local wrapper with setup_problem and grade_problem is present and syntactically valid; Taiga preflight has not run it.",
            "Run Taiga local tunnel/preflight against the wrapper and record exact failures or pass evidence.",
        ),
        row(
            "hidden_material_isolation",
            "hosted_packaging",
            "block" if full_repo_copy and hidden_dirs_present and filesystem_tools_present else "caution",
            (
                f"full_repo_copy={bool_text(full_repo_copy)}; hidden_dirs_present={bool_text(hidden_dirs_present)}; "
                f"problem_metadata_files={len(problem_metadata_files)}; isolation_documented={bool_text(hidden_isolation_documented)}"
            ),
            "Hosted model tools must not be able to read hidden references, hidden PinCheck files, or wrong submissions.",
            (
                "The scaffold documents the risk, but the candidate Dockerfile still copies the full repo and no hosted tool-isolation proof is committed."
                if full_repo_copy and hidden_dirs_present and filesystem_tools_present
                else "Hidden-material isolation still needs hosted confirmation."
            ),
            "Before upload, split public workdir material from grader-private files or enforce unreadable permissions, then verify with hosted preflight/Env Linter evidence.",
        ),
        row(
            "problem_version_evidence",
            "hosted_evidence",
            "pass" if hosted_result_rows and any(row.get("problem_version_id") for row in hosted_result_rows) else "block",
            f"hosted_result_rows={len(hosted_result_rows)}; hosted_report_exists={hosted_report.exists()}",
            "Hosted problem/problem-version IDs for exact uploaded task versions.",
            "No hosted problem-version evidence is committed.",
            "After upload, record environment, problem, problem-version, image digest, and snapshot IDs.",
        ),
        row(
            "hosted_preflight_or_stage1",
            "hosted_evidence",
            "pass" if stage1_rows else "block",
            f"stage1_rows={len(stage1_rows)}",
            "Taiga preflight or Stage 1 individual problem checks on uploaded versions.",
            "No hosted preflight or Stage 1 rows are committed.",
            "Run Taiga preflight/Stage 1 checks and record warning/error/critical findings.",
        ),
        row(
            "transcript_health_or_full_env_qa",
            "hosted_evidence",
            "pass" if transcript_rows else "block",
            f"transcript_health_or_full_env_rows={len(transcript_rows)}",
            "Transcript Health or Full Env QA on sampled hosted runs.",
            "No Transcript Health or Full Env QA result rows are committed.",
            "Run Full Env QA after hosted smoke runs and record result IDs and findings.",
        ),
        row(
            "env_linter",
            "hosted_evidence",
            "pass" if env_linter_rows else "block",
            f"env_linter_rows={len(env_linter_rows)}",
            "Env Linter result rows for exact hosted problem versions.",
            "No Env Linter rows are committed.",
            "Run Env Linter on the hosted environment/snapshot and record dispositions.",
        ),
        row(
            "qa_findings_resolution",
            "hosted_evidence",
            "pass" if hosted_result_rows and not unresolved_findings else "block",
            f"hosted_result_rows={len(hosted_result_rows)}; unresolved_warning_or_higher={len(unresolved_findings)}",
            "All warning/error/critical findings fixed or rebutted with concrete rationale.",
            "No finding-resolution evidence is committed." if not hosted_result_rows else "Finding rows exist but some are unresolved.",
            "Record each finding with severity, disposition, fix/rebuttal, and affected problem version.",
        ),
        row(
            "exact_version_freeze_mapping",
            "hosted_evidence",
            "pass" if freeze_mapping_present else "block",
            f"hosted_report_exists={hosted_report.exists()}; freeze_mapping_terms_present={freeze_mapping_present}",
            "Mapping from committed repo state to exact hosted problem versions/snapshot/tag.",
            "No hosted freeze mapping is committed.",
            "After hosted QA, commit the exact version/snapshot mapping and tag policy.",
        ),
    ]


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row["status"] for row in rows)
    area_counts = Counter(row["area"] for row in rows)
    table_lines = [
        "| check | area | status | evidence | current state | next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        table_lines.append(
            f"| `{row['check_id']}` | {row['area']} | {row['status']} | "
            f"{row['evidence'].replace('|', '/')} | {row['current_state'].replace('|', '/')} | "
            f"{row['next_action'].replace('|', '/')} |"
        )
    lines = [
        "# Hosted QA Readiness Audit",
        "",
        "This generated audit checks the local artifact against the Taiga/hosted QA flow described in the playbook and Taiga wiki. `block` rows are expected before upload; they are evidence that hosted QA has not happened and should not be claimed.",
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
        "The repo is locally validated and now includes a Taiga packaging scaffold, but it does not yet include hidden-material isolation proof, immutable uploaded image digests, hosted problem-version IDs, preflight/Stage 1 evidence, Full Env QA, Env Linter rows, or finding dispositions. The locked-benchmark hosted-QA gate must remain not met until those artifacts are real and committed.",
        "",
        "Packaging `caution` means the repository contains a concrete local scaffold, such as a Dockerfile or generated problems-metadata template, but not immutable uploaded image digests or hosted preflight evidence. Hosted-evidence `block` rows are still the authoritative reason the benchmark is not hosted-QA-cleared.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "hosted_qa_readiness_audit.csv", rows)
    write_markdown(ROOT / "reports" / "hosted_qa_readiness_audit.md", rows)
    print(f"wrote data/hosted_qa_readiness_audit.csv and reports/hosted_qa_readiness_audit.md with {len(rows)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
