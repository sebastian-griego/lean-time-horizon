from __future__ import annotations

import ast
import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(ROOT / "harness"))
from forbidden_constructs import DEFAULT_FORBIDDEN, find_forbidden, load_forbidden  # noqa: E402

FIELDS = [
    "check_id",
    "area",
    "status",
    "evidence",
    "hardening_limit",
    "next_action",
]

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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def row(check_id: str, area: str, status: str, evidence: str, hardening_limit: str, next_action: str) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "status": status,
        "evidence": evidence,
        "hardening_limit": hardening_limit,
        "next_action": next_action,
    }


def discover_task_dirs() -> dict[str, Path]:
    dirs: dict[str, Path] = {}
    for split in ["dev", "test", "candidates"]:
        base = ROOT / "tasks" / split
        if not base.exists():
            continue
        for task_dir in sorted(path for path in base.iterdir() if path.is_dir()):
            metadata_path = task_dir / "metadata.json"
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                dirs[str(metadata["task_id"])] = task_dir
    return dirs


def parse_allowed_axioms(source: str) -> set[str]:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "ALLOWED_AXIOMS":
                return {str(item) for item in ast.literal_eval(node.value)}
    return set()


def parse_policy_axioms(text: str) -> set[str]:
    axioms: set[str] = set()
    in_allowed = False
    for line in text.splitlines():
        if line.strip() == "Allowed axioms:":
            in_allowed = True
            continue
        if in_allowed and line.startswith("- `"):
            axioms.add(line.split("`", 2)[1])
            continue
        if in_allowed and line.startswith("#"):
            break
    return axioms


def source_order(source: str, needle: str) -> int:
    index = source.find(needle)
    return index if index >= 0 else 10**9


def validation_command_expected_set(task_dirs: dict[str, Path]) -> set[tuple[str, str]]:
    expected: set[tuple[str, str]] = set()
    for task_id, task_dir in task_dirs.items():
        expected.add((task_id, "reference_pass"))
        for wrong in sorted((task_dir / "wrong").glob("*.lean")):
            expected.add((task_id, f"wrong_fail:{wrong.stem}"))
    return expected


def build_rows() -> list[dict[str, str]]:
    validate_source = read_text(ROOT / "scripts" / "validate_task.py")
    validate_all_source = read_text(ROOT / "scripts" / "validate_all.py")
    record_local_source = read_text(ROOT / "scripts" / "record_local_qa_results.py")
    axiom_policy = read_text(ROOT / "docs" / "axiom_policy.md")
    metadata_rows = read_csv(ROOT / "data" / "task_metadata.csv")
    validation_commands = read_csv(ROOT / "data" / "validation_commands.csv")
    run_rows = read_csv(ROOT / "data" / "run_results.csv")
    task_dirs = discover_task_dirs()
    release_ids = {
        row_data["task_id"]
        for row_data in metadata_rows
        if row_data.get("acceptance_status") in RELEASE_STATUSES
    }
    rows: list[dict[str, str]] = []

    detection_src = "\n".join(f"{term}" for term in DEFAULT_FORBIDDEN)
    detection_findings = find_forbidden(detection_src, list(DEFAULT_FORBIDDEN))
    detected_terms = {str(finding["term"]) for finding in detection_findings}
    missing_terms = sorted(set(DEFAULT_FORBIDDEN) - detected_terms)
    rows.append(row(
        "default_forbidden_detection",
        "forbidden_scanner",
        "pass" if not missing_terms else "fail",
        f"default_terms={len(DEFAULT_FORBIDDEN)}; detected_terms={len(detected_terms)}; missing_terms={compact_json(missing_terms)}",
        "This probes scanner token matching, not every Lean syntax context where a term can appear.",
        "Add regression cases whenever the forbidden list changes.",
    ))

    ignored_src = """
-- sorry admit axiom constant opaque unsafe macro macro_rules syntax elab run_cmd run_tac Lean.addDecl #eval #exit
/- nested comment with sorry and #eval
   /- inner admit -/
-/
def harmlessString := "sorry admit axiom constant unsafe run_cmd #eval"
def sorryful := 1
def macro_rules_ok_identifier := 2
"""
    ignored_findings = find_forbidden(ignored_src, list(DEFAULT_FORBIDDEN))
    rows.append(row(
        "comment_string_false_positive_control",
        "forbidden_scanner",
        "pass" if not ignored_findings else "fail",
        f"ignored_context_findings={compact_json(ignored_findings)}",
        "The scanner strips comments and strings but remains a lexical source scanner, not a full Lean parser.",
        "Keep false-positive controls broad enough that prompts can mention banned constructs safely.",
    ))

    lt115_metadata = ROOT / "tasks" / "test" / "lt-115-add-cancel-direct" / "metadata.json"
    lt115_forbidden = load_forbidden(lt115_metadata)
    extra_findings = find_forbidden("by omega\n", lt115_forbidden)
    extra_metadata_count = 0
    for task_dir in task_dirs.values():
        metadata = json.loads((task_dir / "metadata.json").read_text(encoding="utf-8"))
        if metadata.get("extra_forbidden"):
            extra_metadata_count += 1
    rows.append(row(
        "task_specific_forbidden_control",
        "forbidden_scanner",
        "pass" if any(finding["term"] == "omega" for finding in extra_findings) else "fail",
        f"metadata_with_extra_forbidden={extra_metadata_count}; lt115_contains_omega={'omega' in lt115_forbidden}; omega_findings={compact_json(extra_findings)}",
        "Only one archived direct-theorem row currently needs task-specific bans.",
        "Use task-specific `extra_forbidden` whenever a shortcut would trivialize a task.",
    ))

    validate_body_start = source_order(validate_source, "def validate_submission")
    validate_body_end = source_order(validate_source, "def write_result_row")
    validate_body = validate_source[validate_body_start:validate_body_end]
    forbidden_order = source_order(validate_body, "forbidden = check_forbidden")
    build_order = source_order(validate_body, "for lean_file in files_to_build")
    pin_order = source_order(validate_body, "pins = run(")
    axiom_order = source_order(validate_body, "audit_axioms(tmp")
    sequencing_ok = forbidden_order < build_order < pin_order < axiom_order
    rows.append(row(
        "grader_stage_order",
        "grader_pipeline",
        "pass" if sequencing_ok else "fail",
        f"forbidden_before_build={forbidden_order < build_order}; build_before_pin={build_order < pin_order}; pin_before_axiom={pin_order < axiom_order}",
        "This is a source-order audit; full behavior is also covered by validate_all and local QA transcripts.",
        "Preserve the order: copy public assets, scan forbidden constructs, compile public files, compile hidden pins, then audit axioms.",
    ))

    policy_axioms = parse_policy_axioms(axiom_policy)
    grader_axioms = parse_allowed_axioms(validate_source)
    rows.append(row(
        "axiom_policy_allowlist_match",
        "axiom_audit",
        "pass" if policy_axioms == grader_axioms and bool(policy_axioms) else "fail",
        f"policy_axioms={compact_json(sorted(policy_axioms))}; grader_axioms={compact_json(sorted(grader_axioms))}",
        "Allowlist equality does not prove each theorem is axiom-free beyond allowed Lean axioms; validate_task performs per-declaration checks.",
        "Update docs/axiom_policy.md and validate_task.py together if the policy changes.",
    ))

    release_without_axiom_decls: list[str] = []
    audited_decl_counts: dict[str, int] = {}
    for task_id in sorted(release_ids):
        task_dir = task_dirs.get(task_id)
        if not task_dir:
            release_without_axiom_decls.append(task_id)
            continue
        metadata = json.loads((task_dir / "metadata.json").read_text(encoding="utf-8"))
        decls = metadata.get("axiom_audit_declarations", [])
        audited_decl_counts[task_id] = len(decls)
        if not decls:
            release_without_axiom_decls.append(task_id)
    rows.append(row(
        "release_axiom_declaration_coverage",
        "axiom_audit",
        "pass" if not release_without_axiom_decls and len(audited_decl_counts) == len(release_ids) else "fail",
        f"release_tasks={len(release_ids)}; audited_decl_counts={compact_json(audited_decl_counts)}; missing={compact_json(release_without_axiom_decls)}",
        "The audit checks metadata coverage, while validate_task checks actual axiom output during grading.",
        "Require nonempty `axiom_audit_declarations` for every release task.",
    ))

    expected_commands = validation_command_expected_set(task_dirs)
    actual_commands = {(row_data.get("task_id", ""), row_data.get("kind", "")) for row_data in validation_commands}
    missing_commands = sorted(expected_commands - actual_commands)
    extra_commands = sorted(actual_commands - expected_commands)
    rows.append(row(
        "validation_command_manifest_coverage",
        "validation_manifest",
        "pass" if not missing_commands and not extra_commands and bool(validation_commands) else "fail",
        f"expected_commands={len(expected_commands)}; actual_commands={len(actual_commands)}; missing={compact_json(missing_commands[:12])}; extra={compact_json(extra_commands[:12])}",
        "The manifest lists validation commands; it does not prove they were run unless paired with validate_all output and run_integrity.",
        "Regenerate validation_commands.csv with validate_all.py after task set changes.",
    ))

    local_rows = [row_data for row_data in run_rows if row_data.get("qa_stage") == "local_qa"]
    reference_bad = [
        row_data.get("task_id", "")
        for row_data in local_rows
        if row_data.get("model") == "reference_solution" and row_data.get("pass_at_k") != "1.0"
    ]
    wrong_bad = [
        f"{row_data.get('task_id')}:{row_data.get('model')}"
        for row_data in local_rows
        if row_data.get("model", "").startswith("plausible_wrong:") and row_data.get("pass_at_k") != "0.0"
    ]
    release_local_ids = {
        row_data.get("task_id", "")
        for row_data in local_rows
        if row_data.get("task_id", "") in release_ids
    }
    rows.append(row(
        "local_qa_reference_wrong_outcomes",
        "validation_manifest",
        "pass" if not reference_bad and not wrong_bad and release_ids.issubset(release_local_ids) else "fail",
        f"local_qa_rows={len(local_rows)}; release_local_tasks={len(release_local_ids)}/{len(release_ids)}; bad_references={compact_json(reference_bad)}; bad_wrongs={compact_json(wrong_bad[:12])}",
        "Local QA rows are validation evidence only, not model-performance evidence.",
        "Require reference rows to pass and plausible-wrong rows to fail before report regeneration.",
    ))

    validate_all_controls = {
        "requires_two_wrongs_for_release": "tasks require at least two wrong submissions" in validate_all_source,
        "accepted_not_t0_t1": "accepted_v0 should not use T0/T1 bucket" in validate_all_source,
        "requires_review_notes": "missing difficulty_review_notes" in validate_all_source,
        "record_local_scrubs_tmp_paths": "tmp/<task-run>" in record_local_source,
    }
    rows.append(row(
        "structural_validation_controls",
        "validation_manifest",
        "pass" if all(validate_all_controls.values()) else "fail",
        compact_json(validate_all_controls),
        "These are static controls; task validity still depends on human review and hidden pins.",
        "Keep structural checks in validate_all.py aligned with acceptance policy.",
    ))
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row_data["status"] for row_data in rows)
    area_counts = Counter(row_data["area"] for row_data in rows)
    lines = [
        "# Grader Hardening Audit",
        "",
        "This generated audit probes local grading controls that are easy to overstate if only source files are listed: forbidden-construct scanning, false-positive controls, task-specific bans, grader stage ordering, axiom allowlist consistency, validation-command coverage, and local QA reference/wrong outcomes.",
        "",
        "## Summary",
        "",
        f"- checks: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- areas: `{compact_json(dict(sorted(area_counts.items())))}`",
        "",
        "## Check Table",
        "",
        "| check | area | status | evidence | hardening limit | next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row_data in rows:
        lines.append(
            f"| `{row_data['check_id']}` | {row_data['area']} | {row_data['status']} | "
            f"{escaped(row_data['evidence'])} | {escaped(row_data['hardening_limit'])} | {escaped(row_data['next_action'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`pass` means the local hardening control has concrete generated evidence. This audit does not prove the grader is impossible to game; it makes the current anti-gaming checks reviewable and keeps the remaining limits explicit.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "grader_hardening_audit.csv", rows)
    write_markdown(ROOT / "reports" / "grader_hardening_audit.md", rows)
    print(f"wrote data/grader_hardening_audit.csv and reports/grader_hardening_audit.md with {len(rows)} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
