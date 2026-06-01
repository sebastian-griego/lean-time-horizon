from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "step_id",
    "phase",
    "status",
    "command",
    "expected_artifacts",
    "claim_supported",
    "evidence_basis",
    "failure_interpretation",
    "limitation",
    "next_action",
]

STEPS = [
    {
        "step_id": "mathlib_cache_get",
        "phase": "local_replay",
        "command": "lake exe cache get",
        "expected_artifacts": ".lake/packages/mathlib/.lake/build/lib/lean",
        "claim_supported": "Mathlib dependency artifacts can be materialized before tasks importing Mathlib are validated.",
        "evidence_basis": "Process exit code plus clean-workspace replay for dependency materialization.",
        "failure_interpretation": "A failure blocks clean-checkout validation for Mathlib-heavy public tasks until cache/build setup is repaired.",
        "limitation": "This is local dependency-cache evidence; hosted environments may use a different cache path.",
        "next_action": "Run before lake build in fresh workspaces or CI.",
    },
    {
        "step_id": "toolchain_build",
        "phase": "local_replay",
        "command": "lake build",
        "expected_artifacts": "",
        "claim_supported": "Lean project and imported task libraries build in the configured toolchain.",
        "evidence_basis": "Process exit code plus current validation manifest command coverage.",
        "failure_interpretation": "A failure blocks local artifact validity until the Lean toolchain, dependencies, or repository sources are repaired.",
        "limitation": "This is local build evidence; it is not hosted QA or provider-sandbox evidence.",
        "next_action": "Run from a clean checkout before release tagging and record the environment.",
    },
    {
        "step_id": "task_validation",
        "phase": "local_replay",
        "command": "python scripts/validate_all.py",
        "expected_artifacts": "data/task_metadata.csv;data/validation_commands.csv",
        "claim_supported": "Reference solutions pass and plausible wrong submissions fail for every task under the local grader.",
        "evidence_basis": "Validation command output, task metadata projection, and local QA transcripts after record_local_qa_results.py.",
        "failure_interpretation": "Any failed reference, accepted wrong, missing metadata, or invalid task row blocks release claims for that task.",
        "limitation": "This validates local hidden checks and wrong submissions; it does not prove model performance.",
        "next_action": "Fix the task or downgrade it, then rerun the full local gate.",
    },
    {
        "step_id": "difficulty_review",
        "phase": "local_replay",
        "command": "python scripts/audit_difficulty.py",
        "expected_artifacts": "data/difficulty_audit.csv;reports/difficulty_audit.md",
        "claim_supported": "Accepted and calibration rows have mechanical proof-profile evidence and manual difficulty-review fields.",
        "evidence_basis": "Reference proof length, tactic profile, automation flags, hidden-pin strength, and reviewer notes.",
        "failure_interpretation": "Missing or stale difficulty evidence weakens task-quality claims and should block acceptance changes.",
        "limitation": "The audit combines static heuristics with human judgment; it is not independent human timing.",
        "next_action": "Refresh after any task, proof, metadata, or acceptance-status edit.",
    },
    {
        "step_id": "local_qa_rows",
        "phase": "local_replay",
        "command": "python scripts/record_local_qa_results.py",
        "expected_artifacts": "data/run_results.csv;transcripts",
        "claim_supported": "Local QA rows are replayable validation evidence for references and plausible wrong submissions.",
        "evidence_basis": "Local transcript JSONL files and run_results rows with qa_stage=local_qa.",
        "failure_interpretation": "Bad local QA rows block run-data integrity and task acceptance claims.",
        "limitation": "Local QA rows must stay excluded from model-performance estimates.",
        "next_action": "Regenerate after task or grader edits, then rerun run-integrity checks.",
    },
    {
        "step_id": "run_integrity",
        "phase": "local_replay",
        "command": "python scripts/audit_run_integrity.py",
        "expected_artifacts": "data/run_integrity_audit.csv;reports/run_integrity_audit.md",
        "claim_supported": "run_results rows are internally consistent with transcripts, pass@k arithmetic, and failure labels.",
        "evidence_basis": "Transcript existence/parse checks, score-vector checks, and pass_at_k/successes_out_of_k validation.",
        "failure_interpretation": "Integrity failures block use of committed run rows until repaired or removed.",
        "limitation": "Passing integrity checks do not imply adequate provider sample size.",
        "next_action": "Run after any provider sweep or local QA regeneration.",
    },
    {
        "step_id": "grader_hardening",
        "phase": "local_replay",
        "command": "python scripts/audit_grader_hardening.py",
        "expected_artifacts": "data/grader_hardening_audit.csv;reports/grader_hardening_audit.md",
        "claim_supported": "Forbidden-construct scanning, axiom allowlists, grader ordering, and validation-command coverage are reviewable.",
        "evidence_basis": "Generated hardening probes and local QA outcome summaries.",
        "failure_interpretation": "A hardening failure blocks claims that the grader is difficult to game.",
        "limitation": "The scanner remains lexical source scanning, not a complete Lean parser.",
        "next_action": "Add regression probes whenever new forbidden constructs or task-specific bans are introduced.",
    },
    {
        "step_id": "public_export",
        "phase": "local_replay",
        "command": "python scripts/export_public_tasks.py --out public_tasks",
        "expected_artifacts": "public_tasks",
        "claim_supported": "Public release assets can be exported without hidden references or wrong submissions.",
        "evidence_basis": "Generated public_tasks directory plus validation_public_export.py checks.",
        "failure_interpretation": "Export failures block public release and hosted-upload preparation.",
        "limitation": "The export is a local directory snapshot, not a hosted problem version.",
        "next_action": "Rerun after task metadata or public-file edits.",
    },
    {
        "step_id": "public_export_validation",
        "phase": "local_replay",
        "command": "python scripts/validate_public_export.py --out public_tasks",
        "expected_artifacts": "",
        "claim_supported": "The public export omits hidden/wrong directories and exported Lean files compile.",
        "evidence_basis": "Validator exit code, hidden-path scan, public-file existence checks, and exported Lean compilation.",
        "failure_interpretation": "Any leak, missing file, or compile failure blocks public release claims.",
        "limitation": "This does not run Taiga Full Env QA or Env Linter.",
        "next_action": "Run immediately before hosted packaging or release tagging.",
    },
    {
        "step_id": "taiga_metadata_template",
        "phase": "local_replay",
        "command": "python scripts/generate_taiga_problem_metadata.py",
        "expected_artifacts": "taiga/problems_metadata.template.json",
        "claim_supported": "The public release task set can be rendered into a Taiga problems-metadata template.",
        "evidence_basis": "Generated template row count and hosted-readiness audit checks.",
        "failure_interpretation": "A generation failure blocks hosted-upload preparation but does not affect local Lean validation.",
        "limitation": "The template uses placeholder image values; it is not a hosted problem-version record or QA result.",
        "next_action": "Replace placeholders with immutable uploaded image digests only after building and uploading the container.",
    },
    {
        "step_id": "report_regeneration",
        "phase": "local_replay",
        "command": "python scripts/generate_report.py",
        "expected_artifacts": "reports/metr_style_report.md;reports/evidence_appendix.md;reports/figures",
        "claim_supported": "The main report, appendix, and descriptive figures regenerate from committed CSV inputs.",
        "evidence_basis": "Generated markdown and figure files, plus report-source traceability and figure-manifest audits.",
        "failure_interpretation": "Report-generation failures block use of the report as a reproducible artifact.",
        "limitation": "Generated report text can still overclaim unless claim-conformance checks pass.",
        "next_action": "Follow with traceability, claim-conformance, and shape audits.",
    },
    {
        "step_id": "claim_and_shape_audits",
        "phase": "local_replay",
        "command": "python scripts/audit_report_claim_conformance.py; python scripts/audit_report_shape.py",
        "expected_artifacts": "data/report_claim_conformance_audit.csv;data/report_shape_audit.csv;reports/report_claim_conformance_audit.md;reports/report_shape_audit.md",
        "claim_supported": "The report keeps blocked claims blocked and answers the playbook report-shape questions where evidence allows.",
        "evidence_basis": "Claim authorization matrix, report text scans, and report-shape audit rows.",
        "failure_interpretation": "Any failure means the report wording must be revised before publication.",
        "limitation": "Text audits are guardrails, not substitutes for substantive external evidence.",
        "next_action": "Regenerate report text and rerun claim/shape audits after claim-policy edits.",
    },
    {
        "step_id": "validation_manifest",
        "phase": "local_replay",
        "command": "python scripts/write_validation_manifest.py --public-export public_tasks; python scripts/audit_validation_manifest.py",
        "expected_artifacts": "reports/validation_manifest.json;data/validation_manifest_audit.csv;reports/validation_manifest_audit.md",
        "claim_supported": "The local validation gate, artifact hashes, public-export summary, and dirty-status policy are recorded.",
        "evidence_basis": "Validation manifest plus audit rows for schema, command coverage, hashes, and public export.",
        "failure_interpretation": "Manifest failures block reproducibility claims until commands and artifacts are synchronized.",
        "limitation": "The manifest intentionally omits self-referential report hashes and is not clean-checkout proof.",
        "next_action": "For a release tag, rerun from a clean checkout or CI and record that separate evidence.",
    },
    {
        "step_id": "provider_sweep",
        "phase": "external_evidence",
        "command": "python scripts/run_model_sweep.py --provider PROVIDER --model MODEL --scaffold SCAFFOLD --attempts 10 --acceptance-status accepted_v0",
        "expected_artifacts": "data/run_results.csv;transcripts;reports/model_run_analysis.md",
        "claim_supported": "Future pass@k, scaffold-effect, and frontier/open-model claims.",
        "evidence_basis": "Provider transcripts, run_results rows, model-result analysis, integrity checks, and statistical audits.",
        "failure_interpretation": "Without these rows, empirical performance and scaffold-effect claims remain blocked.",
        "limitation": "Requires external provider runners and API keys kept only in environment variables.",
        "next_action": "Run only after local and hosted QA are stable enough for reported sweeps.",
    },
    {
        "step_id": "independent_human_timing",
        "phase": "external_evidence",
        "command": "Fill data/human_time_observations.csv from non-author timed solves",
        "expected_artifacts": "data/human_time_observations.csv;reports/human_time_calibration_audit.md",
        "claim_supported": "Future calibrated time-horizon bucket and human-time trend claims.",
        "evidence_basis": "Independent timing observations and refreshed calibration audits.",
        "failure_interpretation": "Without observations, time-horizon claims remain author-estimate-only.",
        "limitation": "Must not be inferred from model pass rates or author expectations.",
        "next_action": "Collect non-author timed solves before claiming calibrated human-time measurement.",
    },
    {
        "step_id": "hosted_qa",
        "phase": "external_evidence",
        "command": "Run hosted Full Env QA and Env Linter on exact final problem versions",
        "expected_artifacts": "data/hosted_qa_readiness_audit.csv;reports/hosted_qa_readiness_audit.md",
        "claim_supported": "Future hosted-QA-cleared and locked-benchmark claims.",
        "evidence_basis": "Problem-version mapping, Full Env QA results, Env Linter findings, and fix/rebuttal dispositions.",
        "failure_interpretation": "Hosted-QA gaps keep locked-benchmark and deployment-reliability claims blocked.",
        "limitation": "This repository currently records readiness only, not hosted QA pass evidence.",
        "next_action": "Package, upload, run QA, wait for late findings, and commit dispositions.",
    },
]


def read_json(path: Path) -> object:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def artifact_exists(value: str) -> bool:
    if not value:
        return True
    for part in value.split(";"):
        part = part.strip()
        if not part:
            continue
        if not (ROOT / part).exists():
            return False
    return True


def command_script_exists(command: str) -> bool:
    if command.startswith("lake "):
        return True
    if command.startswith("Fill ") or command.startswith("Run hosted "):
        return False
    for segment in command.split(";"):
        pieces = segment.strip().split()
        if len(pieces) >= 2 and pieces[0] == "python" and pieces[1].startswith("scripts/"):
            if not (ROOT / pieces[1]).exists():
                return False
    return True


def validation_manifest_commands() -> set[str]:
    manifest = read_json(ROOT / "reports" / "validation_manifest.json")
    if not isinstance(manifest, dict):
        return set()
    commands = manifest.get("regeneration_commands", [])
    return {str(command) for command in commands if isinstance(command, str)}


def derive_status(step: dict[str, str], manifest_commands: set[str]) -> str:
    phase = step["phase"]
    command = step["command"]
    if phase == "external_evidence":
        return "blocked_external_evidence"
    scripts_ok = command_script_exists(command)
    artifacts_ok = artifact_exists(step["expected_artifacts"])
    command_segments = [segment.strip() for segment in command.split(";") if segment.strip()]
    manifest_ok = all(segment in manifest_commands or not segment.startswith("python scripts/") for segment in command_segments)
    if scripts_ok and artifacts_ok and manifest_ok:
        return "ready"
    if scripts_ok and artifacts_ok:
        return "manifest_gap"
    if scripts_ok:
        return "artifact_gap"
    return "script_gap"


def build_rows() -> list[dict[str, str]]:
    manifest_commands = validation_manifest_commands()
    rows: list[dict[str, str]] = []
    for step in STEPS:
        row = {field: step.get(field, "") for field in FIELDS}
        row["status"] = derive_status(row, manifest_commands)
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    status_counts = Counter(row["status"] for row in rows)
    phase_counts = Counter(row["phase"] for row in rows)
    local_rows = [row for row in rows if row["phase"] == "local_replay"]
    blocked_rows = [row for row in rows if row["status"] == "blocked_external_evidence"]
    problem_rows = [
        row for row in rows
        if row["phase"] == "local_replay" and row["status"] != "ready"
    ]
    lines = [
        "| step | phase | status | command | supports | limitation |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['step_id']}` | {row['phase']} | {row['status']} | "
            f"`{row['command']}` | {row['claim_supported'].replace('|', '/')} | "
            f"{row['limitation'].replace('|', '/')} |"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join([
            "# Reviewer Reproduction Packet",
            "",
            "This generated packet converts the local validation and report-generation surface into a reviewer workflow. It is not new model evidence; it states which commands reproduce local evidence, which external evidence is still missing, and how failures should be interpreted.",
            "",
            "## Summary",
            "",
            f"- steps: `{len(rows)}`",
            f"- phases: `{compact_json(dict(sorted(phase_counts.items())))}`",
            f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
            f"- local replay steps ready: `{sum(1 for row in local_rows if row['status'] == 'ready')}/{len(local_rows)}`",
            f"- local replay problem rows: `{len(problem_rows)}`",
            f"- external evidence rows still blocked: `{len(blocked_rows)}`",
            "",
            "## Reviewer Workflow",
            "",
            "Run the local replay steps in order after dependency setup. Treat any nonzero exit code, missing expected artifact, or `manifest_gap` row as a report-blocking finding until repaired. External-evidence rows intentionally remain blocked in v0.1; do not replace them with local smoke rows or synthetic data.",
            "",
            "## Step Table",
            "",
            *lines,
            "",
            "## Interpretation",
            "",
            "`ready` means the command and expected committed artifacts are present and the command is covered by the validation manifest where applicable. `blocked_external_evidence` means the step requires real provider runs, independent human timing, or hosted QA before the corresponding stronger claim can be made.",
            "",
        ]),
        encoding="utf-8",
    )


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "reviewer_reproduction_steps.csv", rows)
    write_markdown(ROOT / "reports" / "reviewer_reproduction_packet.md", rows)
    problems = sum(1 for row in rows if row["phase"] == "local_replay" and row["status"] != "ready")
    print(
        "wrote data/reviewer_reproduction_steps.csv and "
        f"reports/reviewer_reproduction_packet.md with {len(rows)} steps; "
        f"local_problem_rows={problems}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
