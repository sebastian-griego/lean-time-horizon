from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "requirement_id",
    "area",
    "requirement",
    "freeze_relevance",
    "source_note",
    "status",
    "evidence",
    "gap_or_next_step",
]

RELEASE_STATUSES = {"accepted_v0", "calibration_only", "candidate_review_pending"}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def discover_task_dirs() -> dict[str, Path]:
    task_dirs: dict[str, Path] = {}
    for split in ["dev", "test", "candidates"]:
        base = ROOT / "tasks" / split
        if not base.exists():
            continue
        for path in sorted(base.iterdir()):
            metadata_path = path / "metadata.json"
            if not metadata_path.exists():
                continue
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            task_dirs[str(metadata["task_id"])] = path
    return task_dirs


def parse_json_list(value: str) -> list[str]:
    if not value:
        return []
    try:
        data = json.loads(value)
        if isinstance(data, list):
            return [str(item) for item in data]
    except json.JSONDecodeError:
        pass
    return [item.strip() for item in value.split(";") if item.strip()]


def status_from_bool(ok: bool, partial: bool = False) -> str:
    if ok:
        return "supported"
    if partial:
        return "partial"
    return "not_met"


def row(requirement_id: str, area: str, requirement: str, status: str, evidence: str, gap: str) -> dict[str, str]:
    return {
        "requirement_id": requirement_id,
        "area": area,
        "requirement": requirement,
        "freeze_relevance": "",
        "source_note": "",
        "status": status,
        "evidence": evidence,
        "gap_or_next_step": gap,
    }


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def load_requirement_catalog(path: Path = ROOT / "data" / "benchmark_requirements.csv") -> dict[str, dict[str, str]]:
    return {row_data["requirement_id"]: row_data for row_data in read_csv(path)}


def apply_requirement_catalog(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    catalog = load_requirement_catalog()
    covered_ids = {row_data["requirement_id"] for row_data in rows}
    missing_from_catalog = sorted(covered_ids - set(catalog))
    missing_from_coverage = sorted(set(catalog) - covered_ids)
    if missing_from_catalog or missing_from_coverage:
        raise ValueError(
            "requirement coverage/catalog mismatch: "
            f"missing_from_catalog={missing_from_catalog}; missing_from_coverage={missing_from_coverage}"
        )
    out: list[dict[str, str]] = []
    for row_data in rows:
        definition = catalog[row_data["requirement_id"]]
        merged = dict(row_data)
        merged["area"] = definition["area"]
        merged["requirement"] = definition["requirement"]
        merged["freeze_relevance"] = definition["freeze_relevance"]
        merged["source_note"] = definition["source_note"]
        out.append(merged)
    return out


def file_count_status(paths: list[Path]) -> tuple[int, int]:
    present = sum(1 for path in paths if path.exists())
    return present, len(paths)


def task_asset_counts(rows: list[dict[str, str]], task_dirs: dict[str, Path]) -> dict[str, int]:
    counts = Counter()
    for task in rows:
        task_id = task["task_id"]
        task_dir = task_dirs.get(task_id)
        if not task_dir:
            counts["missing_task_dir"] += 1
            continue
        if (task_dir / "Prompt.md").exists():
            counts["prompt_present"] += 1
        public_files = parse_json_list(task.get("public_files", "")) or ["Task.lean"]
        if all((task_dir / public_file).exists() for public_file in public_files):
            counts["public_files_present"] += 1
        if (task_dir / "hidden" / "Reference.lean").exists():
            counts["reference_present"] += 1
        if (task_dir / "hidden" / "PinCheck.lean").exists():
            counts["pincheck_present"] += 1
        wrong_count = len(list((task_dir / "wrong").glob("*.lean"))) if (task_dir / "wrong").exists() else 0
        if wrong_count >= 2:
            counts["two_wrong_submissions"] += 1
        elif wrong_count >= 1:
            counts["one_wrong_submission"] += 1
    counts["total"] = len(rows)
    return dict(counts)


def metadata_complete(rows: list[dict[str, str]]) -> tuple[bool, list[str]]:
    required_fields = [
        "task_id",
        "split",
        "family",
        "domain",
        "human_time_bucket",
        "human_minutes_p50",
        "human_minutes_p90",
        "skills",
        "scaffolds",
        "expected_failure_modes",
        "scaffold_sensitivity",
        "acceptance_status",
        "difficulty_review_status",
        "difficulty_review_notes",
        "public_files",
        "submission_file",
        "entry_file",
    ]
    missing: list[str] = []
    for task in rows:
        for field in required_fields:
            if not str(task.get(field, "")).strip():
                missing.append(f"{task.get('task_id', '<unknown>')}:{field}")
    return not missing, missing[:12]


def run_result_semantics(rows: list[dict[str, str]]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    for row_data in rows:
        try:
            successes = int(row_data.get("successes_out_of_k", ""))
            k = int(row_data.get("k", ""))
            pass_at_k = float(row_data.get("pass_at_k", ""))
        except ValueError:
            errors.append(f"{row_data.get('task_id', '<unknown>')}: nonnumeric k/success/pass")
            continue
        expected = 1.0 if successes > 0 else 0.0
        if successes > k:
            errors.append(f"{row_data.get('task_id', '<unknown>')}: successes_out_of_k > k")
        if pass_at_k != expected:
            errors.append(f"{row_data.get('task_id', '<unknown>')}: pass_at_k should be {expected}")
    return not errors, errors[:12]


def public_export_counts(public_export: Path | None) -> dict[str, object]:
    if public_export is None:
        return {"configured": False, "exists": False, "task_count": 0, "hidden_or_wrong_paths": 0}
    out = public_export.resolve()
    if not out.exists():
        return {"configured": True, "exists": False, "task_count": 0, "hidden_or_wrong_paths": 0}
    metadata_files = list(out.rglob("metadata.json"))
    hidden_or_wrong = [p for p in out.rglob("*") if "hidden" in p.parts or "wrong" in p.parts]
    return {
        "configured": True,
        "exists": True,
        "task_count": len(metadata_files),
        "hidden_or_wrong_paths": len(hidden_or_wrong),
    }


def build_rows(public_export: Path | None) -> list[dict[str, str]]:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    difficulty = read_csv(ROOT / "data" / "difficulty_audit.csv")
    task_quality = read_csv(ROOT / "data" / "task_quality_matrix.csv")
    accepted_task_cards = read_csv(ROOT / "data" / "accepted_task_cards.csv")
    diagnostic_coverage = read_csv(ROOT / "data" / "diagnostic_coverage_audit.csv")
    construct_validity = read_csv(ROOT / "data" / "construct_validity_matrix.csv")
    candidate_pruning = read_csv(ROOT / "data" / "candidate_pruning_audit.csv")
    human_time_audit = read_csv(ROOT / "data" / "human_time_calibration_audit.csv")
    human_time_observations = read_csv(ROOT / "data" / "human_time_observations.csv")
    human_timing_plan = read_csv(ROOT / "data" / "human_timing_collection_plan.csv")
    human_timing_template = read_csv(ROOT / "data" / "human_time_observations_template.csv")
    independent_task_reviews = read_csv(ROOT / "data" / "independent_task_reviews.csv")
    independent_task_review_plan = read_csv(ROOT / "data" / "independent_task_review_plan.csv")
    independent_task_review_template = read_csv(ROOT / "data" / "independent_task_review_template.csv")
    independent_review_status = read_csv(ROOT / "data" / "independent_review_status_audit.csv")
    pin_coverage = read_csv(ROOT / "data" / "pin_coverage_audit.csv")
    run_integrity = read_csv(ROOT / "data" / "run_integrity_audit.csv")
    grader_hardening = read_csv(ROOT / "data" / "grader_hardening_audit.csv")
    statistical_design = read_csv(ROOT / "data" / "statistical_design_thresholds.csv")
    wilson_precision = read_csv(ROOT / "data" / "wilson_precision_table.csv")
    statistical_audit = read_csv(ROOT / "data" / "statistical_reporting_audit.csv")
    provider_readiness = read_csv(ROOT / "data" / "provider_readiness_audit.csv")
    hosted_qa_readiness = read_csv(ROOT / "data" / "hosted_qa_readiness_audit.csv")
    taiga_wrapper_isolation = read_csv(ROOT / "data" / "taiga_wrapper_isolation_audit.csv")
    threats_to_validity = read_csv(ROOT / "data" / "threats_to_validity.csv")
    threat_coverage = read_csv(ROOT / "data" / "threat_coverage_audit.csv")
    claim_evidence = read_csv(ROOT / "data" / "claim_evidence_audit.csv")
    claim_authorization = read_csv(ROOT / "data" / "claim_authorization_matrix.csv")
    research_claim_gap = read_csv(ROOT / "data" / "research_claim_gap_matrix.csv")
    report_claim_conformance = read_csv(ROOT / "data" / "report_claim_conformance_audit.csv")
    release_decision = read_csv(ROOT / "data" / "release_decision_log.csv")
    freeze_roadmap = read_csv(ROOT / "data" / "freeze_readiness_roadmap.csv")
    scaffold_audit = read_csv(ROOT / "data" / "scaffold_support_audit.csv")
    task_assets = read_csv(ROOT / "data" / "task_asset_manifest.csv")
    prompt_contract = read_csv(ROOT / "data" / "prompt_contract_audit.csv")
    figure_manifest = read_csv(ROOT / "data" / "figure_manifest.csv")
    data_schema_manifest = read_csv(ROOT / "data" / "data_schema_manifest.csv")
    report_shape = read_csv(ROOT / "data" / "report_shape_audit.csv")
    report_count_consistency = read_csv(ROOT / "data" / "report_count_consistency_audit.csv")
    peer_review_matrix = read_csv(ROOT / "data" / "peer_review_matrix.csv")
    security_leakage = read_csv(ROOT / "data" / "security_leakage_audit.csv")
    final_delivery_checklist = read_csv(ROOT / "data" / "final_delivery_checklist_audit.csv")
    report_source_traceability = read_csv(ROOT / "data" / "report_source_traceability.csv")
    regeneration_command_consistency = read_csv(ROOT / "data" / "regeneration_command_consistency.csv")
    validation_manifest_audit = read_csv(ROOT / "data" / "validation_manifest_audit.csv")
    reviewer_reproduction_steps = read_csv(ROOT / "data" / "reviewer_reproduction_steps.csv")
    clean_workspace_replay = read_csv(ROOT / "data" / "clean_workspace_replay.csv")
    run_results = read_csv(ROOT / "data" / "run_results.csv")
    transcript_review_queue = read_csv(ROOT / "data" / "transcript_review_queue.csv")
    failure_label_review_template = read_csv(ROOT / "data" / "failure_label_review_template.csv")
    failure_label_reviews = read_csv(ROOT / "data" / "failure_label_reviews.csv")
    failure_label_review_audit = read_csv(ROOT / "data" / "failure_label_review_audit.csv")
    model_sweep_plan = read_csv(ROOT / "data" / "model_sweep_plan.csv")
    analysis_decision_register = read_csv(ROOT / "data" / "analysis_decision_register.csv")
    model_sweep_execution_commands = read_csv(ROOT / "data" / "model_sweep_execution_commands.csv")
    model_sweep_execution_checklist = read_csv(ROOT / "data" / "model_sweep_execution_checklist.csv")
    model_result_summary = read_csv(ROOT / "data" / "model_result_summary.csv")
    model_sweep_coverage = read_csv(ROOT / "data" / "model_sweep_coverage_audit.csv")
    passk_claim_boundary = read_csv(ROOT / "data" / "passk_claim_boundary_audit.csv")
    model_evidence_provenance = read_csv(ROOT / "data" / "model_evidence_provenance_audit.csv")
    task_dirs = discover_task_dirs()
    accepted = [task for task in metadata if task.get("acceptance_status") == "accepted_v0"]
    calibration = [task for task in metadata if task.get("acceptance_status") == "calibration_only"]
    release = [task for task in metadata if task.get("acceptance_status") in RELEASE_STATUSES]
    rejected = [task for task in metadata if task.get("acceptance_status", "").startswith("rejected_")]
    split_counts = Counter(task.get("split", "") for task in accepted)
    family_counts = Counter(task.get("family", "") for task in accepted)
    bucket_counts = Counter(task.get("human_time_bucket", "") for task in accepted + calibration)
    accepted_bucket_counts = Counter(task.get("human_time_bucket", "") for task in accepted)
    asset_counts = task_asset_counts(release, task_dirs)
    accepted_asset_counts = task_asset_counts(accepted, task_dirs)
    metadata_ok, metadata_missing = metadata_complete(metadata)
    semantics_ok, semantics_errors = run_result_semantics(run_results)
    public_counts = public_export_counts(public_export)
    validate_task = read_text(ROOT / "scripts" / "validate_task.py")
    generate_report = read_text(ROOT / "scripts" / "generate_report.py")
    run_model_sweep = read_text(ROOT / "scripts" / "run_model_sweep.py")
    scaffold_rows = read_csv(ROOT / "data" / "scaffold_variants.csv")
    scaffold_audit_by_id = {row_data.get("check_id", ""): row_data for row_data in scaffold_audit}
    scaffold_audit_failures = [row_data for row_data in scaffold_audit if row_data.get("status") == "fail"]
    model_rows = [row_data for row_data in run_results if row_data.get("qa_stage") != "local_qa"]
    non_infra_model_rows = [row_data for row_data in model_rows if row_data.get("infra_fail_count") in {"", "0", 0}]
    local_rows = [row_data for row_data in run_results if row_data.get("qa_stage") == "local_qa"]
    requirement_rows: list[dict[str, str]] = []

    accepted_count = len(accepted)
    target_ok = 20 <= accepted_count <= 50
    requirement_rows.append(row(
        "portfolio_accepted_count",
        "portfolio",
        "Final benchmark should contain 20-50 accepted tasks after QA and filtering.",
        status_from_bool(target_ok),
        f"{accepted_count} accepted_v0 tasks; {len(calibration)} calibration-only tasks; {len(rejected)} rejected archive tasks.",
        "Add and hard-review more high-quality T2/T3/T4 tasks before claiming a full benchmark." if not target_ok else "No gap.",
    ))

    split_ok = split_counts.get("dev", 0) > 0 and split_counts.get("test", 0) > 0
    requirement_rows.append(row(
        "dev_test_split",
        "portfolio",
        "Accepted tasks should preserve a dev/test split.",
        status_from_bool(split_ok),
        f"Accepted split counts: {compact_json(dict(sorted(split_counts.items())))}.",
        "No gap." if split_ok else "Add accepted tasks to both dev and test splits.",
    ))

    family_ok = len(family_counts) >= 5 and family_counts.get("direct_theorem_proving", 0) <= max(1, accepted_count // 3)
    requirement_rows.append(row(
        "mixed_realistic_portfolio",
        "portfolio",
        "Task families should be mixed and not mostly direct theorem proving.",
        status_from_bool(family_ok),
        f"Accepted family counts: {compact_json(dict(sorted(family_counts.items())))}.",
        "No gap." if family_ok else "Broaden accepted families and avoid theorem-proving-only composition.",
    ))

    bucket_ok = any(bucket in accepted_bucket_counts for bucket in ["T2", "T3", "T4"])
    stretch_ok = any(bucket in accepted_bucket_counts for bucket in ["T3", "T4"])
    strong_spread_ok = stretch_ok and accepted_bucket_counts.get("T3", 0) + accepted_bucket_counts.get("T4", 0) >= 2 and accepted_bucket_counts.get("T4", 0) >= 1
    requirement_rows.append(row(
        "time_horizon_spread",
        "portfolio",
        "Accepted tasks should span increasing human-time horizons, not only T0/T1/T2 calibration.",
        status_from_bool(strong_spread_ok, partial=bucket_ok and stretch_ok),
        f"Accepted bucket counts: {compact_json(dict(sorted(accepted_bucket_counts.items())))}; release bucket counts: {compact_json(dict(sorted(bucket_counts.items())))}.",
        "Add more accepted T3/T4 tasks, including a T4 stretch row, and independently review human times." if not strong_spread_ok else "No gap.",
    ))

    public_ok = asset_counts.get("prompt_present", 0) == asset_counts["total"] and asset_counts.get("public_files_present", 0) == asset_counts["total"]
    requirement_rows.append(row(
        "public_prompts_scaffolds",
        "assets",
        "Each release task should include public prompt and public Lean scaffold files.",
        status_from_bool(public_ok),
        f"Release assets: {asset_counts.get('prompt_present', 0)}/{asset_counts['total']} prompts; {asset_counts.get('public_files_present', 0)}/{asset_counts['total']} public-file sets.",
        "No gap." if public_ok else "Fix missing prompts or metadata-listed public files.",
    ))

    prompt_contract_fields = set(prompt_contract[0].keys()) if prompt_contract else set()
    required_prompt_contract_fields = {
        "task_id",
        "status",
        "prompt_checks_passed",
        "prompt_checks_total",
        "runner_supplied_fields",
        "missing_or_caution_fields",
        "leak_patterns_found",
    }
    prompt_contract_failures = [row_data for row_data in prompt_contract if row_data.get("status") == "fail"]
    prompt_contract_leaks = [row_data for row_data in prompt_contract if row_data.get("leak_patterns_found") != "[]"]
    prompt_contract_ok = (
        bool(prompt_contract)
        and len(prompt_contract) == len(release)
        and required_prompt_contract_fields.issubset(prompt_contract_fields)
        and not prompt_contract_failures
        and not prompt_contract_leaks
        and (ROOT / "reports" / "prompt_contract_audit.md").exists()
    )
    requirement_rows.append(row(
        "prompt_contract_audit",
        "reporting",
        "Prompt contract audit should check release prompts for edit scope theorem/import policy helper-lemma policy forbidden constructs submission format tool affordance and hidden-material leaks.",
        status_from_bool(prompt_contract_ok, partial=bool(prompt_contract)),
        f"prompt contract rows: {len(prompt_contract)}; release rows: {len(release)}; failures: {len(prompt_contract_failures)}; leak rows: {len(prompt_contract_leaks)}; report exists: {(ROOT / 'reports' / 'prompt_contract_audit.md').exists()}.",
        "No gap." if prompt_contract_ok else "Regenerate scripts/audit_prompt_contracts.py and fix failed prompt-contract or leak rows.",
    ))

    hidden_ok = asset_counts.get("reference_present", 0) == asset_counts["total"] and asset_counts.get("pincheck_present", 0) == asset_counts["total"]
    requirement_rows.append(row(
        "hidden_references_pins",
        "grading",
        "Each release task should have hidden reference proof and hidden semantic PinCheck.",
        status_from_bool(hidden_ok),
        f"Release hidden assets: {asset_counts.get('reference_present', 0)}/{asset_counts['total']} references; {asset_counts.get('pincheck_present', 0)}/{asset_counts['total']} PinCheck files.",
        "No gap." if hidden_ok else "Add missing hidden Reference.lean or PinCheck.lean files.",
    ))

    wrong_ok = accepted_asset_counts.get("two_wrong_submissions", 0) == accepted_asset_counts["total"]
    requirement_rows.append(row(
        "wrong_submission_controls",
        "grading",
        "Accepted tasks should include plausible wrong submissions that fail for meaningful reasons.",
        status_from_bool(wrong_ok),
        f"Accepted tasks with at least two wrong submissions: {accepted_asset_counts.get('two_wrong_submissions', 0)}/{accepted_asset_counts['total']}.",
        "No gap." if wrong_ok else "Add same-signature semantic wrong submissions and document failure reasons.",
    ))

    lean_scoring_ok = all((ROOT / "scripts" / name).exists() for name in ["validate_task.py", "validate_all.py"]) and len(read_csv(ROOT / "data" / "validation_commands.csv")) > 0
    requirement_rows.append(row(
        "automatic_lean_scoring",
        "grading",
        "Scoring should use Lean wherever possible and provide validation commands.",
        status_from_bool(lean_scoring_ok),
        f"validate_task.py exists: {(ROOT / 'scripts' / 'validate_task.py').exists()}; validation command rows: {len(read_csv(ROOT / 'data' / 'validation_commands.csv'))}.",
        "No gap." if lean_scoring_ok else "Restore Lean validation scripts and command CSV.",
    ))

    forbidden_ok = (ROOT / "harness" / "forbidden_constructs.py").exists() and "find_forbidden" in validate_task
    requirement_rows.append(row(
        "forbidden_construct_scan",
        "integrity",
        "Submissions should be scanned for forbidden constructs before Lean grading.",
        status_from_bool(forbidden_ok),
        f"forbidden_constructs.py exists: {(ROOT / 'harness' / 'forbidden_constructs.py').exists()}; validate_task calls scanner: {'find_forbidden' in validate_task}.",
        "No gap." if forbidden_ok else "Wire forbidden construct scanner into validation.",
    ))

    axiom_ok = (ROOT / "docs" / "axiom_policy.md").exists() and "#print axioms" in validate_task and "ALLOWED_AXIOMS" in validate_task
    requirement_rows.append(row(
        "axiom_audit_policy",
        "integrity",
        "Axiom usage should be audited or governed by a documented policy.",
        status_from_bool(axiom_ok),
        f"docs/axiom_policy.md exists: {(ROOT / 'docs' / 'axiom_policy.md').exists()}; validate_task uses #print axioms: {'#print axioms' in validate_task}.",
        "No gap." if axiom_ok else "Document axiom policy and enforce it in the grader.",
    ))

    requirement_rows.append(row(
        "metadata_completeness",
        "data",
        "Task metadata should include family, domain, human-time, skills, scaffold sensitivity, and failure modes.",
        status_from_bool(metadata_ok),
        f"{len(metadata)} task metadata rows checked; missing fields sample: {compact_json(metadata_missing)}.",
        "No gap." if metadata_ok else "Fill missing metadata fields before using affected rows.",
    ))

    schema_ok = all((ROOT / "data" / name).exists() for name in [
        "run_results_schema.json",
        "failure_label_schema.json",
        "failure_label_review_schema.json",
        "task_metadata_schema.json",
        "independent_task_review_schema.json",
    ])
    requirement_rows.append(row(
        "schemas_present",
        "data",
        "Task metadata, run results, and failure labels should have schemas.",
        status_from_bool(schema_ok),
        f"Schema files present: run={((ROOT / 'data' / 'run_results_schema.json').exists())}, failure={((ROOT / 'data' / 'failure_label_schema.json').exists())}, failure_review={((ROOT / 'data' / 'failure_label_review_schema.json').exists())}, metadata={((ROOT / 'data' / 'task_metadata_schema.json').exists())}, independent_task_review={((ROOT / 'data' / 'independent_task_review_schema.json').exists())}.",
        "No gap." if schema_ok else "Add or restore missing JSON schema files.",
    ))

    required_schema_manifest_ids = {
        "task_metadata_json",
        "task_metadata_csv_projection",
        "run_results",
        "failure_annotations",
        "failure_label_reviews",
        "human_time_observations",
        "independent_task_reviews",
        "failure_label_codebook",
        "derived_reporting_csv_inventory",
    }
    schema_manifest_ids = {row_data.get("dataset_id", "") for row_data in data_schema_manifest}
    schema_manifest_fields = set(data_schema_manifest[0].keys()) if data_schema_manifest else set()
    required_schema_manifest_fields = {
        "dataset_id",
        "path",
        "schema_path",
        "record_scope",
        "row_count",
        "column_count",
        "required_fields_present",
        "validation_status",
        "error_count",
        "error_examples",
        "coverage_note",
        "limitation",
        "next_action",
    }
    schema_problem_rows = [
        row_data for row_data in data_schema_manifest
        if row_data.get("validation_status") in {"schema_error", "projection_mismatch", "codebook_gap"}
        or row_data.get("error_count") not in {"", "0"}
    ]
    schema_status_counts = Counter(row_data.get("validation_status", "unknown") for row_data in data_schema_manifest)
    data_schema_manifest_ok = (
        bool(data_schema_manifest)
        and required_schema_manifest_ids.issubset(schema_manifest_ids)
        and required_schema_manifest_fields.issubset(schema_manifest_fields)
        and not schema_problem_rows
        and (ROOT / "reports" / "data_schema_manifest.md").exists()
    )
    requirement_rows.append(row(
        "data_schema_manifest",
        "data",
        "Data schema manifest should validate schema-backed datasets and document generated CSV schema boundaries.",
        status_from_bool(data_schema_manifest_ok, partial=bool(data_schema_manifest)),
        f"schema rows: {len(data_schema_manifest)}; required datasets covered: {len(required_schema_manifest_ids & schema_manifest_ids)}/{len(required_schema_manifest_ids)}; statuses: {compact_json(dict(sorted(schema_status_counts.items())))}; problem rows: {len(schema_problem_rows)}; report exists: {(ROOT / 'reports' / 'data_schema_manifest.md').exists()}.",
        "No gap." if data_schema_manifest_ok else "Run scripts/audit_data_schema_manifest.py and inspect schema errors, projection mismatches, or codebook gaps.",
    ))

    requirement_rows.append(row(
        "run_result_semantics",
        "data",
        "run_results should represent successes_out_of_k and pass@k consistently.",
        status_from_bool(semantics_ok),
        f"{len(run_results)} run-result rows checked; semantic errors sample: {compact_json(semantics_errors)}.",
        "No gap." if semantics_ok else "Fix successes_out_of_k, k, or pass_at_k rows.",
    ))

    scaffold_support_ok = (
        len(scaffold_rows) >= 3
        and "LEAN_LOOKUP_COMMAND" in run_model_sweep
        and "lookup_unlimited" in read_text(ROOT / "data" / "scaffold_variants.csv")
        and "attempts_allowed = args.attempts" in run_model_sweep
        and bool(scaffold_audit)
        and not scaffold_audit_failures
    )
    requirement_rows.append(row(
        "scaffold_support",
        "scaffolds",
        "The repo should support one-shot, lookup, and lookup plus iterative compile/debug scaffold variants.",
        status_from_bool(scaffold_support_ok),
        f"{len(scaffold_rows)} scaffold variants configured; runner exposes lookup command: {'LEAN_LOOKUP_COMMAND' in run_model_sweep}; runner preserves requested k attempts: {'attempts_allowed = args.attempts' in run_model_sweep}; scaffold audit rows: {len(scaffold_audit)}; scaffold audit failures: {len(scaffold_audit_failures)}.",
        "No gap." if scaffold_support_ok else "Complete scaffold CSV, runner adapter support, and scaffold_support_audit pass checks.",
    ))

    lookup_leak_rows = [
        scaffold_audit_by_id.get("lookup_roots_public_only", {}),
        scaffold_audit_by_id.get("lookup_hidden_leak_scan", {}),
    ]
    lookup_leak_ok = bool(scaffold_audit) and all(row_data.get("status") == "pass" for row_data in lookup_leak_rows)
    requirement_rows.append(row(
        "lookup_scaffold_no_hidden_leak",
        "integrity",
        "Lookup scaffold must not expose hidden references or wrong submissions.",
        status_from_bool(lookup_leak_ok, partial=bool(scaffold_audit)),
        f"lookup_roots_public_only={scaffold_audit_by_id.get('lookup_roots_public_only', {}).get('status', 'missing')}; lookup_hidden_leak_scan={scaffold_audit_by_id.get('lookup_hidden_leak_scan', {}).get('status', 'missing')}.",
        "No gap." if lookup_leak_ok else "Fix scripts/lean_lookup.py roots and rerun scaffold support audit.",
    ))

    planned_scaffolds = {row_data.get("scaffold") for row_data in model_sweep_plan}
    planned_tasks = {row_data.get("task_id") for row_data in model_sweep_plan}
    protocol_ok = (ROOT / "reports" / "evaluation_protocol.md").exists() and len(model_sweep_plan) >= len(accepted) * max(1, len(scaffold_rows)) and planned_scaffolds.issuperset({row_data.get("scaffold") for row_data in scaffold_rows}) and planned_tasks.issuperset({task.get("task_id") for task in accepted})
    requirement_rows.append(row(
        "evaluation_protocol_plan",
        "runs",
        "A prospective evaluation protocol should define the primary accepted-task scaffold sweep before broad model runs.",
        status_from_bool(protocol_ok),
        f"evaluation_protocol.md exists: {(ROOT / 'reports' / 'evaluation_protocol.md').exists()}; model_sweep_plan rows: {len(model_sweep_plan)}; planned scaffolds: {compact_json(sorted(planned_scaffolds))}.",
        "No gap." if protocol_ok else "Generate an accepted_v0 x scaffold sweep plan and protocol before broad model runs.",
    ))

    required_analysis_decisions = {
        "analysis_unit",
        "primary_endpoint",
        "primary_task_set",
        "scaffold_ladder",
        "exact_k_coverage",
        "infra_timeout_handling",
        "wilson_interval_rule",
        "subgroup_threshold_rule",
        "scaffold_delta_rule",
        "failure_label_rule",
        "human_time_rule",
        "hosted_freeze_rule",
    }
    analysis_decision_ids = {row_data.get("decision_id", "") for row_data in analysis_decision_register}
    analysis_decision_fields = set(analysis_decision_register[0].keys()) if analysis_decision_register else set()
    required_analysis_decision_fields = {
        "decision_id",
        "analysis_area",
        "decision_type",
        "preregistered_decision",
        "current_evidence_status",
        "evidence",
        "permitted_current_output",
        "blocked_output",
        "upgrade_condition",
        "source_artifacts",
    }
    analysis_decision_status_counts = Counter(
        row_data.get("current_evidence_status", "unknown")
        for row_data in analysis_decision_register
    )
    analysis_decision_ok = (
        bool(analysis_decision_register)
        and required_analysis_decisions.issubset(analysis_decision_ids)
        and required_analysis_decision_fields.issubset(analysis_decision_fields)
        and analysis_decision_status_counts.get("ready_for_future_rows", 0) >= 1
        and sum(count for status_name, count in analysis_decision_status_counts.items() if status_name.startswith("blocked_")) >= 1
        and (ROOT / "reports" / "analysis_decision_register.md").exists()
    )
    requirement_rows.append(row(
        "analysis_decision_register",
        "reporting",
        "Analysis decision register should preregister inclusion exclusion endpoint exact-k subgroup scaffold-delta failure-label human-time and freeze rules before broad provider sweeps.",
        status_from_bool(analysis_decision_ok, partial=bool(analysis_decision_register)),
        f"analysis decisions: {len(analysis_decision_register)}; required decisions covered: {len(required_analysis_decisions & analysis_decision_ids)}/{len(required_analysis_decisions)}; statuses: {compact_json(dict(sorted(analysis_decision_status_counts.items())))}; report exists: {(ROOT / 'reports' / 'analysis_decision_register.md').exists()}.",
        "No gap." if analysis_decision_ok else "Run scripts/generate_analysis_decision_register.py and inspect missing preregistered analysis decisions.",
    ))

    analysis_ok = (ROOT / "reports" / "model_run_analysis.md").exists() and bool(model_result_summary)
    primary_rows = [row_data for row_data in model_result_summary if row_data.get("analysis_set") == "primary_plan_coverage" and row_data.get("group_by") == "all"]
    requirement_rows.append(row(
        "model_result_analysis",
        "runs",
        "Committed provider rows should be analyzed separately from local QA and against the planned primary sweep.",
        status_from_bool(analysis_ok),
        f"model_run_analysis.md exists: {(ROOT / 'reports' / 'model_run_analysis.md').exists()}; model_result_summary rows: {len(model_result_summary)}; primary coverage rows: {len(primary_rows)}.",
        "No gap." if analysis_ok else "Generate model result analysis before interpreting provider rows.",
    ))

    coverage_fields = set(model_sweep_coverage[0].keys()) if model_sweep_coverage else set()
    required_coverage_fields = {
        "cell_id",
        "task_id",
        "scaffold",
        "planned_k",
        "provider_rows",
        "noninfra_rows",
        "exact_k_noninfra_rows",
        "coverage_status",
        "evidence",
        "limitation",
        "next_action",
    }
    coverage_status_counts = Counter(row_data.get("coverage_status", "unknown") for row_data in model_sweep_coverage)
    planned_cell_count = len(model_sweep_plan)
    coverage_cell_ids = {row_data.get("cell_id", "") for row_data in model_sweep_coverage}
    planned_cell_ids = {f"{row_data.get('task_id', '')}:{row_data.get('scaffold', '')}" for row_data in model_sweep_plan}
    coverage_ok = (
        bool(model_sweep_coverage)
        and required_coverage_fields.issubset(coverage_fields)
        and planned_cell_ids.issubset(coverage_cell_ids)
        and len(model_sweep_coverage) == planned_cell_count
        and (ROOT / "reports" / "model_sweep_coverage_audit.md").exists()
    )
    requirement_rows.append(row(
        "model_sweep_coverage_audit",
        "runs",
        "Model sweep coverage audit should map planned accepted-core task/scaffold/pass@k cells to committed provider rows and distinguish smoke-only rows from pass@k-ready evidence.",
        status_from_bool(coverage_ok, partial=bool(model_sweep_coverage)),
        f"coverage rows: {len(model_sweep_coverage)}; planned cells: {planned_cell_count}; required fields present: {required_coverage_fields.issubset(coverage_fields)}; planned cell ids covered: {len(planned_cell_ids & coverage_cell_ids)}/{len(planned_cell_ids)}; statuses: {compact_json(dict(sorted(coverage_status_counts.items())))}; report exists: {(ROOT / 'reports' / 'model_sweep_coverage_audit.md').exists()}.",
        "No gap." if coverage_ok else "Regenerate scripts/audit_model_sweep_coverage.py after model-result or sweep-plan changes.",
    ))

    required_passk_boundary_ids = {
        "strict_coverage_ledger_counts",
        "main_report_passk_boundary",
        "concise_report_passk_boundary",
        "release_and_freeze_passk_boundary",
        "statistical_and_plot_passk_boundary",
        "claim_and_requirement_passk_boundary",
        "legacy_aggregate_phrase_scan",
    }
    passk_boundary_ids = {row_data.get("check_id", "") for row_data in passk_claim_boundary}
    passk_boundary_fields = set(passk_claim_boundary[0].keys()) if passk_claim_boundary else set()
    required_passk_boundary_fields = {
        "check_id",
        "area",
        "status",
        "evidence",
        "bad_matches",
        "source_artifacts",
        "required_action",
    }
    passk_boundary_failures = [
        row_data for row_data in passk_claim_boundary
        if row_data.get("status") == "fail"
    ]
    passk_boundary_ok = (
        bool(passk_claim_boundary)
        and required_passk_boundary_ids.issubset(passk_boundary_ids)
        and required_passk_boundary_fields.issubset(passk_boundary_fields)
        and not passk_boundary_failures
        and (ROOT / "reports" / "passk_claim_boundary_audit.md").exists()
    )
    requirement_rows.append(row(
        "passk_claim_boundary_audit",
        "reporting",
        "Pass@k claim-boundary audit should verify that reports separate exact-k pass@k-ready planned cells from smoke-only or missing provider rows.",
        status_from_bool(passk_boundary_ok, partial=bool(passk_claim_boundary)),
        f"pass@k-boundary rows: {len(passk_claim_boundary)}; required checks covered: {len(required_passk_boundary_ids & passk_boundary_ids)}/{len(required_passk_boundary_ids)}; failures: {len(passk_boundary_failures)}; report exists: {(ROOT / 'reports' / 'passk_claim_boundary_audit.md').exists()}.",
        "No gap." if passk_boundary_ok else "Regenerate scripts/audit_passk_claim_boundaries.py after report or model-sweep coverage changes.",
    ))

    required_model_provenance_ids = {
        "provider_row_inventory",
        "model_version_and_k_completeness",
        "transcript_provenance",
        "summary_count_consistency",
        "report_sample_size_and_version_disclosure",
        "local_qa_exclusion_boundary",
        "infra_policy_boundary",
    }
    model_provenance_ids = {row_data.get("check_id", "") for row_data in model_evidence_provenance}
    model_provenance_fields = set(model_evidence_provenance[0].keys()) if model_evidence_provenance else set()
    required_model_provenance_fields = {
        "check_id",
        "area",
        "status",
        "evidence",
        "limitation",
        "required_action",
        "source_artifacts",
    }
    model_provenance_failures = [
        row_data for row_data in model_evidence_provenance
        if row_data.get("status") == "fail"
    ]
    model_provenance_ok = (
        bool(model_evidence_provenance)
        and required_model_provenance_ids.issubset(model_provenance_ids)
        and required_model_provenance_fields.issubset(model_provenance_fields)
        and not model_provenance_failures
        and (ROOT / "reports" / "model_evidence_provenance_audit.md").exists()
    )
    requirement_rows.append(row(
        "model_evidence_provenance_audit",
        "reporting",
        "Model evidence provenance audit should verify sample sizes model versions k values transcripts infra accounting and local-QA exclusion in report text and committed data.",
        status_from_bool(model_provenance_ok, partial=bool(model_evidence_provenance)),
        f"model evidence provenance rows: {len(model_evidence_provenance)}; required checks covered: {len(required_model_provenance_ids & model_provenance_ids)}/{len(required_model_provenance_ids)}; failures: {len(model_provenance_failures)}; report exists: {(ROOT / 'reports' / 'model_evidence_provenance_audit.md').exists()}.",
        "No gap." if model_provenance_ok else "Regenerate scripts/audit_model_evidence_provenance.py after model-result analysis and inspect failing provenance rows.",
    ))

    pass_at_k_ready_cells = [
        row_data for row_data in model_sweep_coverage
        if row_data.get("coverage_status") in {"covered_pass", "covered_fail"}
    ]
    pass_at_k_ready_scaffolds = {row_data.get("scaffold", "") for row_data in pass_at_k_ready_cells}
    coverage_status_counts_for_result = Counter(row_data.get("coverage_status", "unknown") for row_data in model_sweep_coverage)
    scaffold_results_ok = (
        bool(model_sweep_plan)
        and len(pass_at_k_ready_cells) >= len(model_sweep_plan)
        and len(pass_at_k_ready_scaffolds) >= 3
    )
    requirement_rows.append(row(
        "scaffold_result_comparison",
        "scaffolds",
        "The report should compare real model performance across scaffolds, ideally pass@10.",
        status_from_bool(scaffold_results_ok, partial=bool(non_infra_model_rows) or bool(model_sweep_coverage)),
        (
            f"Non-infra model rows: {len(non_infra_model_rows)}; smoke scaffolds observed: "
            f"{compact_json(sorted({row_data.get('scaffold') for row_data in non_infra_model_rows}))}; "
            f"pass@k-ready cells: {len(pass_at_k_ready_cells)}/{len(model_sweep_plan)}; "
            f"pass@k-ready scaffolds: {compact_json(sorted(pass_at_k_ready_scaffolds))}; "
            f"coverage statuses: {compact_json(dict(sorted(coverage_status_counts_for_result.items())))}."
        ),
        "Run real pass@10 or comparable sweeps across one-shot, lookup, and lookup_unlimited before performance claims.",
    ))

    transcript_ok = bool(local_rows) and all(row_data.get("transcript_link") for row_data in run_results) and (ROOT / "data" / "failure_label_schema.json").exists()
    requirement_rows.append(row(
        "transcript_failure_workflow",
        "runs",
        "Run rows should link transcripts and carry failure labels for review.",
        status_from_bool(transcript_ok),
        f"run_results rows: {len(run_results)}; local QA rows: {len(local_rows)}; model rows: {len(model_rows)}.",
        "No gap for workflow; broader model sweeps are still needed." if transcript_ok else "Populate transcript links and failure labels.",
    ))

    transcript_queue_fields = set(transcript_review_queue[0].keys()) if transcript_review_queue else set()
    transcript_template_fields = set(failure_label_review_template[0].keys()) if failure_label_review_template else set()
    required_transcript_queue_fields = {
        "run_id",
        "task_id",
        "scaffold",
        "model",
        "job_id",
        "pass_at_k",
        "failure_label_current",
        "qa_findings_status",
        "transcript_link",
        "transcript_exists",
        "transcript_record_count",
        "transcript_labels",
        "review_priority",
        "review_action",
    }
    required_transcript_template_fields = {
        "run_id",
        "task_id",
        "reviewer_id",
        "review_timestamp_utc",
        "primary_label",
        "secondary_labels",
        "confidence",
        "rationale",
        "evidence_excerpt",
        "adjudication_needed",
        "adjudication_notes",
    }
    nonlocal_run_ids = {f"{row_data.get('job_id', '')}:{row_data.get('task_id', '')}" for row_data in model_rows}
    queued_run_ids = {row_data.get("run_id", "") for row_data in transcript_review_queue}
    template_run_ids = {row_data.get("run_id", "") for row_data in failure_label_review_template}
    missing_transcript_queue = [
        row_data for row_data in transcript_review_queue
        if row_data.get("transcript_exists") != "true"
    ]
    fabricated_template_labels = [
        row_data for row_data in failure_label_review_template
        if row_data.get("primary_label") or row_data.get("rationale") or row_data.get("reviewer_id")
    ]
    transcript_review_ok = (
        bool(transcript_review_queue)
        and required_transcript_queue_fields.issubset(transcript_queue_fields)
        and required_transcript_template_fields.issubset(transcript_template_fields)
        and nonlocal_run_ids.issubset(queued_run_ids)
        and queued_run_ids.issubset(template_run_ids)
        and not missing_transcript_queue
        and not fabricated_template_labels
        and (ROOT / "reports" / "transcript_review_packet.md").exists()
    )
    requirement_rows.append(row(
        "transcript_review_packet",
        "runs",
        "Transcript review packet should provide a non-local run review queue failure-label codebook blank adjudication template and label-claim boundary without fabricating review labels.",
        status_from_bool(transcript_review_ok, partial=bool(transcript_review_queue)),
        f"queue rows: {len(transcript_review_queue)}; non-local run ids covered: {len(nonlocal_run_ids & queued_run_ids)}/{len(nonlocal_run_ids)}; template rows: {len(failure_label_review_template)}; missing transcripts in queue: {len(missing_transcript_queue)}; prefilled template labels: {len(fabricated_template_labels)}; report exists: {(ROOT / 'reports' / 'transcript_review_packet.md').exists()}.",
        "No gap." if transcript_review_ok else "Regenerate scripts/generate_transcript_review_packet.py and inspect queue/template coverage.",
    ))

    required_failure_review_checks = {
        "review_schema",
        "queue_coverage",
        "label_validity",
        "transcript_evidence",
        "review_metadata",
        "claim_boundary",
    }
    failure_review_check_ids = {row_data.get("check_id", "") for row_data in failure_label_review_audit}
    failure_review_fields = set(failure_label_review_audit[0].keys()) if failure_label_review_audit else set()
    required_failure_review_fields = {
        "check_id",
        "area",
        "status",
        "evidence",
        "limitation",
        "next_action",
    }
    failure_review_failures = [
        row_data for row_data in failure_label_review_audit
        if row_data.get("status") == "fail"
    ]
    failure_review_run_ids = {row_data.get("run_id", "") for row_data in failure_label_reviews}
    failure_review_ok = (
        bool(failure_label_reviews)
        and bool(failure_label_review_audit)
        and required_failure_review_checks.issubset(failure_review_check_ids)
        and required_failure_review_fields.issubset(failure_review_fields)
        and queued_run_ids.issubset(failure_review_run_ids)
        and not failure_review_failures
        and (ROOT / "reports" / "failure_label_review_audit.md").exists()
    )
    requirement_rows.append(row(
        "failure_label_review_audit",
        "runs",
        "Failure-label review audit should verify committed non-local transcript reviews against transcripts and keep smoke-label claims caveated.",
        status_from_bool(failure_review_ok, partial=bool(failure_label_reviews)),
        f"review rows: {len(failure_label_reviews)}; queue rows covered: {len(queued_run_ids & failure_review_run_ids)}/{len(queued_run_ids)}; audit checks: {len(failure_label_review_audit)}; required checks covered: {len(required_failure_review_checks & failure_review_check_ids)}/{len(required_failure_review_checks)}; failures: {len(failure_review_failures)}; report exists: {(ROOT / 'reports' / 'failure_label_review_audit.md').exists()}.",
        "No gap." if failure_review_ok else "Run scripts/audit_failure_label_reviews.py after transcript packet generation and inspect failed review rows.",
    ))

    model_ok = len(non_infra_model_rows) >= len(accepted)
    requirement_rows.append(row(
        "frontier_model_evidence",
        "runs",
        "Frontier/open-model runs should provide evidence beyond local QA.",
        status_from_bool(model_ok, partial=bool(non_infra_model_rows)),
        f"Non-infra model rows: {len(non_infra_model_rows)} over {len(accepted)} accepted tasks; total model rows including infra failures: {len(model_rows)}.",
        "Run broader provider sweeps only after local and hosted QA are stable.",
    ))

    public_export_ok = bool(public_counts.get("exists")) and public_counts.get("hidden_or_wrong_paths") == 0 and int(public_counts.get("task_count", 0)) >= len(accepted) + len(calibration)
    requirement_rows.append(row(
        "public_export_no_hidden_leak",
        "integrity",
        "Public export should include public assets and exclude hidden references and wrong submissions.",
        status_from_bool(public_export_ok),
        f"Public export exists: {public_counts.get('exists')}; exported tasks: {public_counts.get('task_count')}; hidden/wrong paths: {public_counts.get('hidden_or_wrong_paths')}.",
        "No gap." if public_export_ok else "Run export_public_tasks.py and validate_public_export.py, then inspect leaks.",
    ))

    required_security_checks = {
        "tracked_secret_pattern_scan",
        "tracked_sensitive_filename_scan",
        "public_export_hidden_path_scan",
        "hidden_content_fingerprint_scan",
        "provider_credential_policy_scan",
    }
    security_check_ids = {row_data.get("check_id", "") for row_data in security_leakage}
    security_fields = set(security_leakage[0].keys()) if security_leakage else set()
    required_security_fields = {
        "check_id",
        "area",
        "status",
        "finding_count",
        "evidence",
        "scanned_scope",
        "limitation",
        "next_action",
    }
    security_failures = [
        row_data for row_data in security_leakage
        if row_data.get("status") == "fail"
    ]
    security_ok = (
        bool(security_leakage)
        and required_security_checks.issubset(security_check_ids)
        and required_security_fields.issubset(security_fields)
        and not security_failures
        and (ROOT / "reports" / "security_leakage_audit.md").exists()
    )
    requirement_rows.append(row(
        "security_leakage_audit",
        "integrity",
        "Security and leakage audit should scan committed/exported artifacts for hard-coded credential patterns hidden public-export paths and verbatim hidden Lean content leaks without printing secrets or hidden snippets.",
        status_from_bool(security_ok, partial=bool(security_leakage)),
        f"security checks: {len(security_leakage)}; required checks covered: {len(required_security_checks & security_check_ids)}/{len(required_security_checks)}; failures: {len(security_failures)}; report exists: {(ROOT / 'reports' / 'security_leakage_audit.md').exists()}.",
        "No gap." if security_ok else "Run scripts/audit_security_leakage.py after public export, then inspect failed scan rows without exposing matched values.",
    ))

    task_asset_fields = set(task_assets[0].keys()) if task_assets else set()
    required_task_asset_fields = {
        "task_id",
        "split",
        "acceptance_status",
        "asset_role",
        "relative_path",
        "public_export_expected",
        "public_export_exists",
        "exists",
        "sha256",
    }
    task_asset_missing = [row_data for row_data in task_assets if row_data.get("exists") != "true"]
    release_public_missing = [
        row_data for row_data in task_assets
        if row_data.get("public_export_expected") == "true" and row_data.get("public_export_exists") != "true"
    ]
    hidden_exported = [
        row_data for row_data in task_assets
        if row_data.get("asset_role", "").startswith("hidden") or row_data.get("asset_role") == "wrong_submission"
        if row_data.get("public_export_exists") == "true"
    ]
    accepted_ids = {task.get("task_id") for task in accepted}
    accepted_wrong_counts = Counter(
        row_data.get("task_id")
        for row_data in task_assets
        if row_data.get("asset_role") == "wrong_submission" and row_data.get("task_id") in accepted_ids
    )
    accepted_wrong_gaps = [task_id for task_id in accepted_ids if accepted_wrong_counts.get(task_id, 0) < 2]
    accepted_hidden_gaps = [
        row_data for row_data in task_assets
        if row_data.get("task_id") in accepted_ids
        and row_data.get("asset_role") in {"hidden_reference", "hidden_pincheck"}
        and row_data.get("exists") != "true"
    ]
    task_asset_ok = (
        bool(task_assets)
        and required_task_asset_fields.issubset(task_asset_fields)
        and not task_asset_missing
        and not release_public_missing
        and not hidden_exported
        and not accepted_wrong_gaps
        and not accepted_hidden_gaps
        and (ROOT / "reports" / "task_asset_manifest.md").exists()
    )
    requirement_rows.append(row(
        "task_asset_manifest",
        "reproducibility",
        "Task asset manifest should record per-task public hidden and wrong asset hashes plus public-export mapping.",
        status_from_bool(task_asset_ok, partial=bool(task_assets)),
        f"task asset rows: {len(task_assets)}; missing assets: {len(task_asset_missing)}; release public export misses: {len(release_public_missing)}; hidden/wrong exported: {len(hidden_exported)}; accepted wrong gaps: {len(accepted_wrong_gaps)}; accepted hidden gaps: {len(accepted_hidden_gaps)}; report exists: {(ROOT / 'reports' / 'task_asset_manifest.md').exists()}.",
        "No gap." if task_asset_ok else "Regenerate scripts/generate_task_asset_manifest.py after public export and fix missing/hash/export mismatches.",
    ))

    report_ok = (ROOT / "reports" / "metr_style_report.md").exists() and "read_csv" in generate_report
    requirement_rows.append(row(
        "report_from_committed_data",
        "reporting",
        "The METR-style report and plots should regenerate from committed CSVs.",
        status_from_bool(report_ok),
        f"metr_style_report.md exists: {(ROOT / 'reports' / 'metr_style_report.md').exists()}; generate_report reads CSV: {'read_csv' in generate_report}.",
        "No gap." if report_ok else "Restore report generation from data CSVs.",
    ))

    required_figure_ids = {
        "task_counts_by_family",
        "task_counts_by_bucket",
        "top_skills",
        "run_rows_by_model",
        "task_minutes_by_bucket",
        "scaffold_pass_at_k_plot",
        "bucket_success_plot",
        "family_success_plot",
        "failure_taxonomy_plot",
        "problem_pass_vs_time",
    }
    figure_ids = {row_data.get("plot_id", "") for row_data in figure_manifest}
    figure_fields = set(figure_manifest[0].keys()) if figure_manifest else set()
    required_figure_fields = {
        "plot_id",
        "category",
        "current_status",
        "figure_path",
        "figure_exists",
        "source_artifacts",
        "sources_exist",
        "allowed_interpretation",
        "blocked_overclaim",
        "evidence",
        "next_action",
    }
    generated_figures = [
        row_data for row_data in figure_manifest
        if row_data.get("category") in {"generated_descriptive", "generated_provenance"}
    ]
    blocked_figures = [
        row_data for row_data in figure_manifest
        if row_data.get("category") == "blocked_performance"
    ]
    figure_problem_rows = [
        row_data for row_data in figure_manifest
        if row_data.get("current_status") in {
            "missing_generated_artifact",
            "unexpected_performance_plot",
            "missing_source_artifact",
            "needs_audit_review",
        }
    ]
    figure_manifest_ok = (
        bool(figure_manifest)
        and required_figure_ids.issubset(figure_ids)
        and required_figure_fields.issubset(figure_fields)
        and len(generated_figures) >= 5
        and len(blocked_figures) >= 5
        and not figure_problem_rows
        and (ROOT / "reports" / "figure_manifest.md").exists()
    )
    requirement_rows.append(row(
        "figure_manifest_audit",
        "reporting",
        "Figure manifest should map generated SVGs to source CSVs allowed interpretations and blocked performance-plot overclaims.",
        status_from_bool(figure_manifest_ok, partial=bool(figure_manifest)),
        f"figure rows: {len(figure_manifest)}; required plots covered: {len(required_figure_ids & figure_ids)}/{len(required_figure_ids)}; generated rows: {len(generated_figures)}; blocked performance rows: {len(blocked_figures)}; problem rows: {len(figure_problem_rows)}; report exists: {(ROOT / 'reports' / 'figure_manifest.md').exists()}.",
        "No gap." if figure_manifest_ok else "Run scripts/audit_figure_manifest.py after report generation and inspect missing generated or unexpected performance plots.",
    ))

    main_report_path = ROOT / "reports" / "metr_style_report.md"
    appendix_path = ROOT / "reports" / "evidence_appendix.md"
    main_report = read_text(main_report_path)
    evidence_appendix = read_text(appendix_path)
    main_line_count = len(main_report.splitlines())
    appendix_line_count = len(evidence_appendix.splitlines())
    appendix_required_phrases = [
        "Evidence Appendix",
        "Validation Manifest",
        "Requirement Coverage Audit",
        "Hidden Pin Coverage Audit",
    ]
    missing_appendix_phrases = [
        phrase for phrase in appendix_required_phrases
        if phrase.lower() not in evidence_appendix.lower()
    ]
    appendix_boundary_ok = (
        main_report_path.exists()
        and appendix_path.exists()
        and main_line_count <= 800
        and appendix_line_count > main_line_count
        and not missing_appendix_phrases
        and "reports/evidence_appendix.md" in main_report
    )
    requirement_rows.append(row(
        "evidence_appendix_boundary",
        "reporting",
        "Main report should stay skimmable while row-level generated evidence lives in a dedicated appendix.",
        status_from_bool(appendix_boundary_ok, partial=main_report_path.exists() or appendix_path.exists()),
        (
            f"main report lines: {main_line_count}; appendix exists: {appendix_path.exists()}; "
            f"appendix lines: {appendix_line_count}; missing appendix phrases: {compact_json(missing_appendix_phrases)}; "
            f"main links appendix: {'reports/evidence_appendix.md' in main_report}."
        ),
        "No gap." if appendix_boundary_ok else "Regenerate scripts/generate_report.py and keep long generated tables in reports/evidence_appendix.md.",
    ))

    required_trace_ids = {
        "main_section_inventory",
        "abstract_scope",
        "reader_guide",
        "research_questions",
        "unit_scoring",
        "task_selection",
        "candidate_pruning",
        "accepted_core",
        "accepted_evidence_matrix",
        "accepted_task_cards",
        "independent_task_review_packet",
        "calibration_tasks",
        "portfolio_counts",
        "capabilities",
        "construct_validity_trace",
        "human_time",
        "grading_integrity",
        "public_export",
        "scaffold_support",
        "model_result_analysis",
        "model_provenance",
        "committed_runs",
        "claim_authorization",
        "remaining_blockers",
        "evidence_files",
        "reproducibility",
        "claim_ledger",
        "limitations",
    }
    trace_ids = {row_data.get("section_id", "") for row_data in report_source_traceability}
    trace_fields = set(report_source_traceability[0].keys()) if report_source_traceability else set()
    required_trace_fields = {
        "section_id",
        "heading",
        "status",
        "evidence",
        "source_artifacts",
        "missing_sources",
        "missing_phrases",
        "limitation",
        "next_action",
    }
    trace_failures = [
        row_data for row_data in report_source_traceability
        if row_data.get("status") == "fail"
    ]
    traceability_ok = (
        bool(report_source_traceability)
        and required_trace_ids.issubset(trace_ids)
        and required_trace_fields.issubset(trace_fields)
        and not trace_failures
        and (ROOT / "reports" / "report_source_traceability.md").exists()
    )
    requirement_rows.append(row(
        "report_source_traceability",
        "reporting",
        "Report source-traceability audit should map main-report sections to committed CSV report script and export evidence and check section-level boundary phrases.",
        status_from_bool(traceability_ok, partial=bool(report_source_traceability)),
        (
            f"traceability rows: {len(report_source_traceability)}; required sections covered: "
            f"{len(required_trace_ids & trace_ids)}/{len(required_trace_ids)}; failures: {len(trace_failures)}; "
            f"report exists: {(ROOT / 'reports' / 'report_source_traceability.md').exists()}."
        ),
        "No gap." if traceability_ok else "Run scripts/audit_report_source_traceability.py after generating the main report and inspect missing sources or boundary phrases.",
    ))

    required_regeneration_command_ids = {
        "readme_matches_manifest_source",
        "json_manifest_matches_source",
        "required_commands_in_public_gate",
        "reviewer_packet_local_subset",
    }
    regeneration_command_ids = {
        row_data.get("check_id", "") for row_data in regeneration_command_consistency
    }
    regeneration_command_failures = [
        row_data for row_data in regeneration_command_consistency
        if row_data.get("status") == "fail"
    ]
    regeneration_command_ok = (
        bool(regeneration_command_consistency)
        and required_regeneration_command_ids.issubset(regeneration_command_ids)
        and not regeneration_command_failures
        and (ROOT / "reports" / "regeneration_command_consistency.md").exists()
    )
    requirement_rows.append(row(
        "regeneration_command_consistency",
        "reproducibility",
        "Regeneration command consistency audit should verify that README validation commands manifest source commands committed manifest commands and reviewer local-replay commands stay synchronized.",
        status_from_bool(regeneration_command_ok, partial=bool(regeneration_command_consistency)),
        (
            f"command-consistency rows: {len(regeneration_command_consistency)}; required checks covered: "
            f"{len(required_regeneration_command_ids & regeneration_command_ids)}/{len(required_regeneration_command_ids)}; "
            f"failures: {len(regeneration_command_failures)}; report exists: "
            f"{(ROOT / 'reports' / 'regeneration_command_consistency.md').exists()}."
        ),
        "No gap." if regeneration_command_ok else "Run scripts/audit_regeneration_commands.py after writing the validation manifest and inspect command drift.",
    ))

    concise_report_path = ROOT / "reports" / "concise_metr_report.md"
    concise_report = read_text(concise_report_path)
    concise_lines = concise_report.splitlines()
    concise_required_phrases = [
        "not a locked benchmark",
        "accepted core tasks",
        "calibration-only tasks",
        "Capabilities And Expected Failures",
        "Claim Boundaries",
        "Remaining Blockers",
        "Next Work",
        "Evidence Appendix",
    ]
    missing_concise_phrases = [
        phrase for phrase in concise_required_phrases
        if phrase.lower() not in concise_report.lower()
    ]
    concise_ok = (
        concise_report_path.exists()
        and "read_csv" in read_text(ROOT / "scripts" / "generate_concise_report.py")
        and len(concise_lines) <= 220
        and not missing_concise_phrases
    )
    requirement_rows.append(row(
        "concise_metr_report",
        "reporting",
        "Concise METR-style report should provide a skimmable reviewer-facing narrative while detailed generated tables remain in appendices and CSVs.",
        status_from_bool(concise_ok, partial=concise_report_path.exists()),
        f"concise report exists: {concise_report_path.exists()}; line_count: {len(concise_lines)}; missing required phrases: {compact_json(missing_concise_phrases)}; generator reads CSV: {'read_csv' in read_text(ROOT / 'scripts' / 'generate_concise_report.py')}.",
        "No gap." if concise_ok else "Regenerate scripts/generate_concise_report.py and keep the concise report under 220 lines with claim boundaries and next-work sections.",
    ))

    required_shape_ids = {
        "tasks_built",
        "capabilities_tested",
        "scaffolds_compared",
        "success_changes_by_scaffold_and_bucket",
        "failure_modes_dominate",
        "next_batch_needs",
        "skimmability",
    }
    report_shape_ids = {row_data.get("check_id", "") for row_data in report_shape}
    report_shape_fields = set(report_shape[0].keys()) if report_shape else set()
    required_shape_fields = {
        "check_id",
        "playbook_question",
        "answer_status",
        "evidence",
        "limitation",
        "next_action",
        "source_artifacts",
    }
    shape_needs_attention = [
        row_data for row_data in report_shape
        if row_data.get("answer_status") == "needs_attention"
    ]
    shape_blocked = [
        row_data for row_data in report_shape
        if row_data.get("answer_status") == "blocked_by_evidence"
    ]
    shape_ok = (
        bool(report_shape)
        and required_shape_ids.issubset(report_shape_ids)
        and required_shape_fields.issubset(report_shape_fields)
        and not shape_needs_attention
        and (ROOT / "reports" / "report_shape_audit.md").exists()
    )
    requirement_rows.append(row(
        "report_shape_audit",
        "reporting",
        "Report-shape audit should check the concise METR-style report against the playbook questions and distinguish answered limitations from unsupported performance claims.",
        status_from_bool(shape_ok, partial=bool(report_shape)),
        f"report-shape rows: {len(report_shape)}; required checks covered: {len(required_shape_ids & report_shape_ids)}/{len(required_shape_ids)}; needs_attention rows: {len(shape_needs_attention)}; blocked_by_evidence rows: {len(shape_blocked)}; report exists: {(ROOT / 'reports' / 'report_shape_audit.md').exists()}.",
        "No gap." if shape_ok else "Regenerate scripts/audit_report_shape.py after the concise report and inspect any needs_attention rows.",
    ))

    required_count_consistency_ids = {
        "task_status_counts",
        "requirement_status_counts",
        "claim_authorization_counts",
        "release_and_freeze_gate_counts",
        "model_coverage_counts",
        "run_and_manifest_counts",
        "locked_benchmark_blocker_counts",
        "public_export_counts",
    }
    count_consistency_ids = {
        row_data.get("check_id", "") for row_data in report_count_consistency
    }
    count_consistency_failures = [
        row_data for row_data in report_count_consistency
        if row_data.get("status") == "fail"
    ]
    count_consistency_ok = (
        bool(report_count_consistency)
        and required_count_consistency_ids.issubset(count_consistency_ids)
        and not count_consistency_failures
        and (ROOT / "reports" / "report_count_consistency_audit.md").exists()
    )
    requirement_rows.append(row(
        "report_count_consistency_audit",
        "reporting",
        "Report count-consistency audit should verify that repeated top-line counts in reports and manifests agree with committed CSV and JSON sources.",
        status_from_bool(count_consistency_ok, partial=bool(report_count_consistency)),
        f"count-consistency rows: {len(report_count_consistency)}; required checks covered: {len(required_count_consistency_ids & count_consistency_ids)}/{len(required_count_consistency_ids)}; failures: {len(count_consistency_failures)}; report exists: {(ROOT / 'reports' / 'report_count_consistency_audit.md').exists()}.",
        "No gap." if count_consistency_ok else "Regenerate scripts/audit_report_count_consistency.py after report generation and inspect stale top-line counts.",
    ))

    required_peer_review_questions = {
        "scope_status",
        "task_portfolio_scale",
        "diagnostic_task_quality",
        "grader_semantic_validity",
        "run_data_and_passk_semantics",
        "model_performance_evidence",
        "statistical_reporting",
        "human_time_evidence",
        "hosted_qa_and_public_export",
        "local_reproducibility",
        "claim_control_system",
        "upgrade_path",
    }
    peer_review_ids = {row_data.get("question_id", "") for row_data in peer_review_matrix}
    peer_review_fields = set(peer_review_matrix[0].keys()) if peer_review_matrix else set()
    required_peer_review_fields = {
        "question_id",
        "review_area",
        "verdict",
        "reviewer_question",
        "current_answer",
        "evidence",
        "residual_risk",
        "required_upgrade_evidence",
        "source_artifacts",
    }
    peer_review_verdicts = Counter(row_data.get("verdict", "unknown") for row_data in peer_review_matrix)
    peer_review_ok = (
        bool(peer_review_matrix)
        and required_peer_review_questions.issubset(peer_review_ids)
        and required_peer_review_fields.issubset(peer_review_fields)
        and peer_review_verdicts.get("pass", 0) >= 1
        and peer_review_verdicts.get("caution", 0) >= 1
        and peer_review_verdicts.get("block", 0) >= 1
        and (ROOT / "reports" / "peer_review_matrix.md").exists()
    )
    requirement_rows.append(row(
        "peer_review_matrix",
        "reporting",
        "Peer review matrix should summarize skeptical reviewer questions current defensible answers residual risks and upgrade evidence from committed audits.",
        status_from_bool(peer_review_ok, partial=bool(peer_review_matrix)),
        f"peer-review rows: {len(peer_review_matrix)}; required questions covered: {len(required_peer_review_questions & peer_review_ids)}/{len(required_peer_review_questions)}; verdicts: {compact_json(dict(sorted(peer_review_verdicts.items())))}; report exists: {(ROOT / 'reports' / 'peer_review_matrix.md').exists()}.",
        "No gap." if peer_review_ok else "Run scripts/generate_peer_review_matrix.py after requirement and claim audits, then inspect missing reviewer questions.",
    ))

    requirement_rows.append(row(
        "difficulty_audit_report",
        "reporting",
        "Difficulty audit should include proof length, tactic profile, automation dominance, hidden-pin strength, and model-solvability estimates.",
        status_from_bool(bool(difficulty) and (ROOT / "reports" / "difficulty_audit.md").exists()),
        f"difficulty_audit rows: {len(difficulty)}; report exists: {(ROOT / 'reports' / 'difficulty_audit.md').exists()}.",
        "No gap." if difficulty else "Regenerate scripts/audit_difficulty.py.",
    ))

    review_ok = (ROOT / "reports" / "accepted_task_review.md").exists()
    requirement_rows.append(row(
        "manual_accepted_task_review",
        "reporting",
        "Accepted tasks should have hard reviewer-style notes and benchmark-grade caveats.",
        status_from_bool(review_ok),
        f"accepted_task_review.md exists: {review_ok}.",
        "No gap." if review_ok else "Create or restore accepted-task reviewer notes.",
    ))

    quality_fields = set(task_quality[0].keys()) if task_quality else set()
    required_quality_fields = {
        "benchmark_grade_status",
        "next_review_action",
        "automation_dominated",
        "hidden_pin_strength",
        "frontier_one_shot_likelihood",
        "diagnostic_value",
    }
    quality_ok = (
        bool(task_quality)
        and len(task_quality) == len(metadata)
        and required_quality_fields.issubset(quality_fields)
        and (ROOT / "reports" / "task_quality_matrix.md").exists()
    )
    requirement_rows.append(row(
        "task_quality_matrix",
        "reporting",
        "Reviewer-facing task quality matrix should join metadata, difficulty signals, caveats, and next-review actions.",
        status_from_bool(quality_ok),
        f"task_quality_matrix rows: {len(task_quality)}; metadata rows: {len(metadata)}; report exists: {(ROOT / 'reports' / 'task_quality_matrix.md').exists()}.",
        "No gap." if quality_ok else "Regenerate scripts/generate_task_quality_matrix.py after difficulty audit.",
    ))

    card_fields = set(accepted_task_cards[0].keys()) if accepted_task_cards else set()
    required_card_fields = {
        "task_id",
        "review_recommendation",
        "benchmark_grade_status",
        "proof_lines",
        "tactic_profile",
        "automation_dominated",
        "pin_coverage_grade",
        "wrong_stage_summary",
        "local_qa_summary",
        "asset_summary",
        "claim_boundary",
        "before_benchmark_grade",
    }
    card_ids = {row_data.get("task_id", "") for row_data in accepted_task_cards}
    accepted_ids = {row_data.get("task_id", "") for row_data in accepted}
    missing_card_ids = sorted(accepted_ids - card_ids)
    extra_card_ids = sorted(card_ids - accepted_ids)
    card_blocker_rows = [
        row_data for row_data in accepted_task_cards
        if row_data.get("before_benchmark_grade", "").strip()
    ]
    card_ok = (
        bool(accepted_task_cards)
        and len(accepted_task_cards) == len(accepted)
        and required_card_fields.issubset(card_fields)
        and not missing_card_ids
        and not extra_card_ids
        and len(card_blocker_rows) == len(accepted_task_cards)
        and (ROOT / "reports" / "accepted_task_cards.md").exists()
    )
    requirement_rows.append(row(
        "accepted_task_cards",
        "reporting",
        "Accepted-task cards should synthesize each accepted_v0 row's review status proof signals pin coverage local QA evidence asset counts and benchmark-grade blockers.",
        status_from_bool(card_ok, partial=bool(accepted_task_cards)),
        f"accepted task cards: {len(accepted_task_cards)}; accepted rows: {len(accepted)}; missing ids: {len(missing_card_ids)}; extra ids: {len(extra_card_ids)}; blocker rows: {len(card_blocker_rows)}; report exists: {(ROOT / 'reports' / 'accepted_task_cards.md').exists()}.",
        "No gap." if card_ok else "Regenerate scripts/generate_accepted_task_cards.py after task quality, construct-validity, pin coverage, asset, and local-QA evidence.",
    ))

    required_diagnostic_checks = {
        "family_mix",
        "direct_theorem_balance",
        "capability_library_search",
        "capability_theorem_decomposition",
        "capability_semantic_formalization",
        "capability_proof_debugging",
        "capability_codebase_navigation",
        "capability_invariant_design",
        "capability_long_horizon_construction",
        "failure_mode_metadata_density",
        "capability_failure_label_alignment",
        "automation_caveat_coverage",
        "one_shot_solvability_balance",
        "time_horizon_construct_limit",
        "quality_matrix_join_integrity",
    }
    diagnostic_check_ids = {row_data.get("check_id", "") for row_data in diagnostic_coverage}
    diagnostic_fields = set(diagnostic_coverage[0].keys()) if diagnostic_coverage else set()
    required_diagnostic_fields = {
        "check_id",
        "area",
        "status",
        "accepted_task_count",
        "accepted_task_ids",
        "release_task_count",
        "evidence",
        "diagnostic_limit",
        "next_action",
    }
    diagnostic_failures = [row_data for row_data in diagnostic_coverage if row_data.get("status") == "fail"]
    diagnostic_blocks = [row_data for row_data in diagnostic_coverage if row_data.get("status") == "block"]
    diagnostic_cautions = [row_data for row_data in diagnostic_coverage if row_data.get("status") == "caution"]
    diagnostic_ok = (
        bool(diagnostic_coverage)
        and required_diagnostic_checks.issubset(diagnostic_check_ids)
        and required_diagnostic_fields.issubset(diagnostic_fields)
        and not diagnostic_failures
        and (ROOT / "reports" / "diagnostic_coverage_audit.md").exists()
    )
    requirement_rows.append(row(
        "diagnostic_coverage_audit",
        "reporting",
        "Diagnostic coverage audit should map accepted tasks to playbook capabilities families failure labels and construct-validity gaps.",
        status_from_bool(diagnostic_ok, partial=bool(diagnostic_coverage)),
        f"diagnostic coverage rows: {len(diagnostic_coverage)}; required checks covered: {len(required_diagnostic_checks & diagnostic_check_ids)}/{len(required_diagnostic_checks)}; failures: {len(diagnostic_failures)}; cautions: {len(diagnostic_cautions)}; blocks: {len(diagnostic_blocks)}; report exists: {(ROOT / 'reports' / 'diagnostic_coverage_audit.md').exists()}.",
        "No gap." if diagnostic_ok else "Regenerate scripts/audit_diagnostic_coverage.py and fix failed diagnostic data checks.",
    ))

    construct_fields = set(construct_validity[0].keys()) if construct_validity else set()
    required_construct_fields = {
        "task_id",
        "capabilities_claimed",
        "singleton_capabilities",
        "construct_evidence",
        "claim_support_level",
        "claim_limit",
        "next_evidence_needed",
    }
    accepted_ids = {row_data.get("task_id", "") for row_data in accepted}
    construct_ids = {row_data.get("task_id", "") for row_data in construct_validity}
    missing_construct_ids = sorted(accepted_ids - construct_ids)
    extra_construct_ids = sorted(construct_ids - accepted_ids)
    construct_singleton_rows = [
        row_data for row_data in construct_validity
        if row_data.get("singleton_capabilities", "")
    ]
    construct_limit_rows = [
        row_data for row_data in construct_validity
        if "singleton" in row_data.get("claim_limit", "")
        or "task-level evidence only" in row_data.get("claim_limit", "")
        or "caveat" in row_data.get("claim_limit", "")
    ]
    construct_ok = (
        bool(construct_validity)
        and required_construct_fields.issubset(construct_fields)
        and not missing_construct_ids
        and not extra_construct_ids
        and len(construct_limit_rows) == len(construct_validity)
        and (ROOT / "reports" / "construct_validity_matrix.md").exists()
    )
    requirement_rows.append(row(
        "construct_validity_matrix",
        "reporting",
        "Construct-validity matrix should trace each accepted task to claimed capabilities evidence singleton limits and task-level claim boundaries.",
        status_from_bool(construct_ok, partial=bool(construct_validity)),
        f"construct rows: {len(construct_validity)}; accepted rows: {len(accepted)}; missing accepted ids: {len(missing_construct_ids)}; extra ids: {len(extra_construct_ids)}; singleton-limit rows: {len(construct_singleton_rows)}; claim-limit rows: {len(construct_limit_rows)}; report exists: {(ROOT / 'reports' / 'construct_validity_matrix.md').exists()}.",
        "No gap." if construct_ok else "Regenerate scripts/generate_construct_validity_matrix.py after diagnostic coverage and inspect missing task or claim-limit rows.",
    ))

    human_time_fields = set(human_time_audit[0].keys()) if human_time_audit else set()
    required_human_time_fields = {
        "task_id",
        "human_time_bucket",
        "human_minutes_p50",
        "human_minutes_p90",
        "p50_bucket_consistent",
        "p90_at_or_above_p50",
        "independent_observation_count",
        "successful_independent_observation_count",
        "calibration_status",
        "issues",
    }
    human_time_failures = [row_data for row_data in human_time_audit if row_data.get("calibration_status") == "fail"]
    accepted_human_time_rows = [row_data for row_data in human_time_audit if row_data.get("acceptance_status") == "accepted_v0"]
    accepted_without_timing = [
        row_data for row_data in accepted_human_time_rows
        if int(row_data.get("successful_independent_observation_count", "0") or "0") == 0
    ]
    human_time_audit_ok = (
        bool(human_time_audit)
        and len(human_time_audit) == len(metadata)
        and required_human_time_fields.issubset(human_time_fields)
        and not human_time_failures
        and (ROOT / "data" / "human_time_observations.csv").exists()
        and (ROOT / "data" / "human_time_observations_schema.json").exists()
        and (ROOT / "reports" / "human_time_calibration_audit.md").exists()
    )
    requirement_rows.append(row(
        "human_time_calibration_audit",
        "reporting",
        "Human-time calibration audit should verify bucket and p50/p90 consistency and explicitly track missing independent timing evidence.",
        status_from_bool(human_time_audit_ok, partial=bool(human_time_audit)),
        f"human-time audit rows: {len(human_time_audit)}; metadata rows: {len(metadata)}; failures: {len(human_time_failures)}; accepted without independent timing: {len(accepted_without_timing)}/{len(accepted_human_time_rows)}; observation rows: {len(human_time_observations)}; report exists: {(ROOT / 'reports' / 'human_time_calibration_audit.md').exists()}.",
        "No gap." if human_time_audit_ok else "Regenerate scripts/audit_human_time_calibration.py and fix failed bucket or estimate rows.",
    ))

    human_plan_fields = set(human_timing_plan[0].keys()) if human_timing_plan else set()
    human_template_fields = set(human_timing_template[0].keys()) if human_timing_template else set()
    required_human_plan_fields = {
        "task_id",
        "minimum_reviewer_count_before_freeze",
        "recommended_reviewer_profile",
        "recommended_timing_condition",
        "validation_command",
        "ambiguity_review_prompt",
    }
    required_human_template_fields = {
        "task_id",
        "reviewer_id_hash",
        "reviewer_role",
        "observed_minutes",
        "outcome",
        "date_utc",
        "notes",
        "scaffold_used",
        "lookup_used",
        "compile_feedback_used",
        "prompt_ambiguity",
        "validation_passed",
    }
    accepted_ids = {task.get("task_id", "") for task in accepted}
    human_plan_ids = {row_data.get("task_id", "") for row_data in human_timing_plan}
    human_template_ids = {row_data.get("task_id", "") for row_data in human_timing_template}
    human_plan_hidden_leak = any(
        "hidden" in row_data.get("validation_command", "").lower()
        or "Reference.lean" in row_data.get("validation_command", "")
        for row_data in human_timing_plan
    )
    human_timing_packet_ok = (
        bool(human_timing_plan)
        and accepted_ids.issubset(human_plan_ids)
        and accepted_ids.issubset(human_template_ids)
        and required_human_plan_fields.issubset(human_plan_fields)
        and required_human_template_fields.issubset(human_template_fields)
        and not human_plan_hidden_leak
        and (ROOT / "reports" / "human_timing_collection_packet.md").exists()
    )
    requirement_rows.append(row(
        "human_timing_collection_packet",
        "calibration",
        "Human timing collection packet should give independent reviewers per-task timing instructions validation commands and a blank observation template without containing fabricated observations.",
        status_from_bool(human_timing_packet_ok, partial=bool(human_timing_plan)),
        f"timing plan rows: {len(human_timing_plan)}; accepted tasks covered: {len(accepted_ids & human_plan_ids)}/{len(accepted_ids)}; template rows: {len(human_timing_template)}; hidden-reference command leaks: {human_plan_hidden_leak}; report exists: {(ROOT / 'reports' / 'human_timing_collection_packet.md').exists()}.",
        "No gap." if human_timing_packet_ok else "Regenerate scripts/generate_human_timing_packet.py and inspect timing plan/template coverage.",
    ))

    independent_review_plan_fields = set(independent_task_review_plan[0].keys()) if independent_task_review_plan else set()
    independent_review_template_fields = set(independent_task_review_template[0].keys()) if independent_task_review_template else set()
    independent_review_observation_fields = set(independent_task_reviews[0].keys()) if independent_task_reviews else set()
    if not independent_review_observation_fields and (ROOT / "data" / "independent_task_reviews.csv").exists():
        with (ROOT / "data" / "independent_task_reviews.csv").open(newline="", encoding="utf-8") as f:
            independent_review_observation_fields = set(csv.DictReader(f).fieldnames or [])
    required_independent_review_plan_fields = {
        "task_id",
        "benchmark_grade_status",
        "automation_dominated",
        "hidden_pin_strength",
        "wrong_submission_count",
        "frontier_one_shot_likelihood",
        "diagnostic_value",
        "required_reviewer_profile",
        "review_scope",
        "review_questions",
        "validation_command",
    }
    required_independent_review_template_fields = {
        "task_id",
        "reviewer_id_hash",
        "reviewer_role",
        "review_date_utc",
        "reviewed_public_assets_only",
        "hidden_grader_files_inspected",
        "validation_command_run",
        "prompt_clarity",
        "time_bucket_assessment",
        "diagnostic_value_assessment",
        "hidden_pin_assessment",
        "wrong_submission_assessment",
        "automation_caveat_acknowledged",
        "benchmark_grade_recommendation",
        "notes",
    }
    independent_review_plan_ids = {row_data.get("task_id", "") for row_data in independent_task_review_plan}
    independent_review_template_ids = {row_data.get("task_id", "") for row_data in independent_task_review_template}
    independent_review_command_leak = any(
        "hidden" in row_data.get("validation_command", "").lower()
        or "Reference.lean" in row_data.get("validation_command", "")
        for row_data in independent_task_review_plan
    )
    independent_review_packet_ok = (
        bool(independent_task_review_plan)
        and accepted_ids == independent_review_plan_ids
        and accepted_ids == independent_review_template_ids
        and required_independent_review_plan_fields.issubset(independent_review_plan_fields)
        and required_independent_review_template_fields.issubset(independent_review_template_fields)
        and required_independent_review_template_fields.issubset(independent_review_observation_fields)
        and not independent_review_command_leak
        and (ROOT / "data" / "independent_task_review_schema.json").exists()
        and (ROOT / "reports" / "independent_task_review_packet.md").exists()
    )
    requirement_rows.append(row(
        "independent_task_review_packet",
        "calibration",
        "Independent accepted-task review packet should provide non-author review instructions per-task plan blank template and schema without fabricating observations.",
        status_from_bool(independent_review_packet_ok, partial=bool(independent_task_review_plan)),
        f"review plan rows: {len(independent_task_review_plan)}; accepted tasks covered: {len(accepted_ids & independent_review_plan_ids)}/{len(accepted_ids)}; template rows: {len(independent_task_review_template)}; observation rows: {len(independent_task_reviews)}; hidden-reference command leaks: {independent_review_command_leak}; report exists: {(ROOT / 'reports' / 'independent_task_review_packet.md').exists()}.",
        "No gap." if independent_review_packet_ok else "Regenerate scripts/generate_independent_review_packet.py and inspect review plan/template/schema coverage.",
    ))

    required_independent_review_status_ids = {
        "review_plan_coverage",
        "review_schema_and_template",
        "review_row_validity",
        "accepted_review_coverage",
        "review_recommendation_distribution",
    }
    independent_review_status_ids = {row_data.get("check_id", "") for row_data in independent_review_status}
    independent_review_status_fields = set(independent_review_status[0].keys()) if independent_review_status else set()
    required_independent_review_status_fields = {
        "check_id",
        "area",
        "status",
        "evidence",
        "limitation",
        "next_action",
    }
    independent_review_failures = [row_data for row_data in independent_review_status if row_data.get("status") == "fail"]
    independent_review_blocks = [row_data for row_data in independent_review_status if row_data.get("status") == "block"]
    independent_review_status_ok = (
        bool(independent_review_status)
        and required_independent_review_status_ids.issubset(independent_review_status_ids)
        and required_independent_review_status_fields.issubset(independent_review_status_fields)
        and not independent_review_failures
        and any(row_data.get("check_id") == "accepted_review_coverage" and row_data.get("status") == "block" for row_data in independent_review_status)
        and (ROOT / "reports" / "independent_review_status_audit.md").exists()
    )
    requirement_rows.append(row(
        "independent_task_review_status_audit",
        "calibration",
        "Independent task-review status audit should distinguish packet readiness from missing completed non-author reviews.",
        status_from_bool(independent_review_status_ok, partial=bool(independent_review_status)),
        f"review-status rows: {len(independent_review_status)}; required checks covered: {len(required_independent_review_status_ids & independent_review_status_ids)}/{len(required_independent_review_status_ids)}; failures: {len(independent_review_failures)}; blocks: {len(independent_review_blocks)}; report exists: {(ROOT / 'reports' / 'independent_review_status_audit.md').exists()}.",
        "No gap." if independent_review_status_ok else "Run scripts/audit_independent_review_status.py and inspect missing status checks or fabricated-coverage risk.",
    ))

    accepted_pin_rows = [row_data for row_data in pin_coverage if row_data.get("acceptance_status") == "accepted_v0"]
    pin_fields = set(pin_coverage[0].keys()) if pin_coverage else set()
    required_pin_fields = {
        "pin_coverage_grade",
        "wrongs_failing_public_stage",
        "wrongs_failing_hidden_pin_stage",
        "theorem_shape_checks",
        "negative_examples",
        "submission_surface",
        "same_signature_hidden_wrong_feasibility",
        "hidden_pin_role",
    }
    mutable_pin_rows = [
        row_data for row_data in accepted_pin_rows
        if row_data.get("same_signature_hidden_wrong_feasibility") == "feasible_via_definition_semantics"
    ]
    mutable_with_hidden = sum(
        1 for row_data in mutable_pin_rows
        if row_data.get("wrongs_failing_hidden_pin_stage", "0").isdigit()
        and int(row_data.get("wrongs_failing_hidden_pin_stage", "0")) > 0
    )
    proof_only_pin_rows = [
        row_data for row_data in accepted_pin_rows
        if row_data.get("same_signature_hidden_wrong_feasibility")
        == "structurally_infeasible_for_same_signature_proof_wrongs"
    ]
    accepted_with_hidden = sum(
        int(row_data.get("wrongs_failing_hidden_pin_stage", "0"))
        for row_data in accepted_pin_rows
        if row_data.get("wrongs_failing_hidden_pin_stage", "0").isdigit()
    )
    pin_audit_ok = (
        bool(pin_coverage)
        and len(pin_coverage) == len(metadata)
        and len(accepted_pin_rows) == len(accepted)
        and accepted_with_hidden > 0
        and mutable_with_hidden == len(mutable_pin_rows)
        and len(mutable_pin_rows) + len(proof_only_pin_rows) == len(accepted_pin_rows)
        and required_pin_fields.issubset(pin_fields)
        and (ROOT / "reports" / "pin_coverage_audit.md").exists()
    )
    requirement_rows.append(row(
        "pin_coverage_audit",
        "reporting",
        "Hidden-pin audit should distinguish public-stage wrong failures from wrong submissions that reach semantic pins.",
        status_from_bool(pin_audit_ok, partial=bool(pin_coverage)),
        f"pin_coverage rows: {len(pin_coverage)}; accepted rows: {len(accepted_pin_rows)}; accepted hidden-pin wrong failures: {accepted_with_hidden}; mutable accepted rows with hidden-pin failures: {mutable_with_hidden}/{len(mutable_pin_rows)}; proof-only fixed-statement rows: {len(proof_only_pin_rows)}; report exists: {(ROOT / 'reports' / 'pin_coverage_audit.md').exists()}.",
        "No gap." if pin_audit_ok else "Regenerate scripts/audit_pin_coverage.py after local QA transcripts and inspect accepted rows without hidden-pin wrong failures.",
    ))

    integrity_failures = [row_data for row_data in run_integrity if row_data.get("integrity_status") == "fail"]
    integrity_fields = set(run_integrity[0].keys()) if run_integrity else set()
    required_integrity_fields = {
        "transcript_exists",
        "transcript_parse_ok",
        "arithmetic_ok",
        "failure_label_known",
        "transcript_consistency_ok",
        "integrity_status",
    }
    integrity_ok = (
        bool(run_integrity)
        and len(run_integrity) == len(run_results)
        and not integrity_failures
        and required_integrity_fields.issubset(integrity_fields)
        and (ROOT / "reports" / "run_integrity_audit.md").exists()
    )
    requirement_rows.append(row(
        "run_integrity_audit",
        "reporting",
        "Run-result integrity audit should verify transcripts, score vectors, failure labels, and pass@k arithmetic.",
        status_from_bool(integrity_ok, partial=bool(run_integrity)),
        f"run_integrity rows: {len(run_integrity)}; run_results rows: {len(run_results)}; failing rows: {len(integrity_failures)}; report exists: {(ROOT / 'reports' / 'run_integrity_audit.md').exists()}.",
        "No gap." if integrity_ok else "Regenerate scripts/audit_run_integrity.py after run_results and transcripts, then fix any failing rows.",
    ))

    required_grader_checks = {
        "default_forbidden_detection",
        "comment_string_false_positive_control",
        "task_specific_forbidden_control",
        "grader_stage_order",
        "axiom_policy_allowlist_match",
        "release_axiom_declaration_coverage",
        "validation_command_manifest_coverage",
        "local_qa_reference_wrong_outcomes",
        "structural_validation_controls",
    }
    grader_check_ids = {row_data.get("check_id", "") for row_data in grader_hardening}
    grader_fields = set(grader_hardening[0].keys()) if grader_hardening else set()
    required_grader_fields = {
        "check_id",
        "area",
        "status",
        "evidence",
        "hardening_limit",
        "next_action",
    }
    grader_failures = [row_data for row_data in grader_hardening if row_data.get("status") == "fail"]
    grader_hardening_ok = (
        bool(grader_hardening)
        and required_grader_checks.issubset(grader_check_ids)
        and required_grader_fields.issubset(grader_fields)
        and not grader_failures
        and (ROOT / "reports" / "grader_hardening_audit.md").exists()
    )
    requirement_rows.append(row(
        "grader_hardening_audit",
        "reporting",
        "Grader hardening audit should probe forbidden scanning false-positive controls task-specific bans grader stage ordering axiom allowlists validation-command coverage and local QA outcomes.",
        status_from_bool(grader_hardening_ok, partial=bool(grader_hardening)),
        f"grader hardening rows: {len(grader_hardening)}; required checks covered: {len(required_grader_checks & grader_check_ids)}/{len(required_grader_checks)}; failures: {len(grader_failures)}; report exists: {(ROOT / 'reports' / 'grader_hardening_audit.md').exists()}.",
        "No gap." if grader_hardening_ok else "Regenerate scripts/audit_grader_hardening.py and fix failing grader-hardening checks.",
    ))

    required_statistical_checks = {
        "primary_sweep_coverage",
        "main_report_performance_estimate_suppression",
        "scaffold_pass_at_k_plot",
        "bucket_success_plot",
        "family_success_plot",
        "failure_taxonomy_plot",
        "wilson_interval_reporting",
        "local_qa_exclusion",
        "infra_failure_policy",
    }
    statistical_check_ids = {row_data.get("check_id", "") for row_data in statistical_audit}
    statistical_fields = set(statistical_audit[0].keys()) if statistical_audit else set()
    required_statistical_fields = {
        "check_id",
        "area",
        "status",
        "evidence",
        "current_sample",
        "minimum_for_claim",
        "supported_output",
        "limitation",
        "next_action",
    }
    statistical_failures = [row_data for row_data in statistical_audit if row_data.get("status") == "fail"]
    statistical_blocks = [row_data for row_data in statistical_audit if row_data.get("status") == "block"]
    statistical_ok = (
        bool(statistical_audit)
        and required_statistical_checks.issubset(statistical_check_ids)
        and required_statistical_fields.issubset(statistical_fields)
        and not statistical_failures
        and (ROOT / "reports" / "statistical_reporting_audit.md").exists()
    )
    requirement_rows.append(row(
        "statistical_reporting_audit",
        "reporting",
        "Statistical reporting audit should determine which recommended performance plots and claims are supported by committed provider sample sizes.",
        status_from_bool(statistical_ok, partial=bool(statistical_audit)),
        f"statistical audit rows: {len(statistical_audit)}; required checks covered: {len(required_statistical_checks & statistical_check_ids)}/{len(required_statistical_checks)}; failures: {len(statistical_failures)}; blocked performance outputs: {len(statistical_blocks)}; report exists: {(ROOT / 'reports' / 'statistical_reporting_audit.md').exists()}.",
        "No gap." if statistical_ok else "Regenerate scripts/audit_statistical_reporting.py and fix failing statistical hygiene checks.",
    ))

    required_statistical_tiers = {
        "smoke_run_provenance",
        "v0_1_primary_descriptive_performance",
        "scaffold_effect_comparison",
        "time_horizon_bucket_trend",
        "family_or_skill_summary",
        "failure_taxonomy_distribution",
        "locked_benchmark_population_claims",
    }
    statistical_tier_ids = {row_data.get("tier_id", "") for row_data in statistical_design}
    statistical_design_fields = set(statistical_design[0].keys()) if statistical_design else set()
    required_statistical_design_fields = {
        "tier_id",
        "claim_type",
        "current_status",
        "minimum_accepted_tasks",
        "minimum_noninfra_primary_cells",
        "minimum_k",
        "minimum_scaffold_count",
        "minimum_group_n",
        "minimum_independent_timing",
        "minimum_failure_reviews",
        "hosted_qa_required",
        "current_evidence",
        "allowed_output_now",
        "blocked_overclaim",
        "stronger_claim_requires",
    }
    precision_fields = set(wilson_precision[0].keys()) if wilson_precision else set()
    required_precision_fields = {
        "n",
        "assumed_p",
        "successes",
        "wilson_low",
        "wilson_high",
        "interval_width",
        "interpretation",
    }
    blocked_tiers = [row_data for row_data in statistical_design if row_data.get("current_status") == "blocked"]
    supported_tiers = [row_data for row_data in statistical_design if row_data.get("current_status") == "supported"]
    precision_n_values = {row_data.get("n", "") for row_data in wilson_precision}
    statistical_plan_ok = (
        bool(statistical_design)
        and bool(wilson_precision)
        and required_statistical_tiers.issubset(statistical_tier_ids)
        and required_statistical_design_fields.issubset(statistical_design_fields)
        and required_precision_fields.issubset(precision_fields)
        and len(blocked_tiers) >= 4
        and len(supported_tiers) >= 1
        and {"1", "20", "50"}.issubset(precision_n_values)
        and (ROOT / "reports" / "statistical_analysis_plan.md").exists()
    )
    requirement_rows.append(row(
        "statistical_analysis_plan",
        "reporting",
        "Statistical analysis plan should define claim-tier evidence thresholds and Wilson precision limits before broad model runs.",
        status_from_bool(statistical_plan_ok, partial=bool(statistical_design) or bool(wilson_precision)),
        f"statistical tiers: {len(statistical_design)}; required tiers covered: {len(required_statistical_tiers & statistical_tier_ids)}/{len(required_statistical_tiers)}; blocked tiers: {len(blocked_tiers)}; supported tiers: {len(supported_tiers)}; precision rows: {len(wilson_precision)}; precision n values: {compact_json(sorted(precision_n_values))}; report exists: {(ROOT / 'reports' / 'statistical_analysis_plan.md').exists()}.",
        "No gap." if statistical_plan_ok else "Run scripts/generate_statistical_analysis_plan.py and inspect missing claim-tier or precision rows.",
    ))

    required_provider_checks = {
        "provider_catalog_contract",
        "external_runner_env_contract",
        "bundled_provider_adapters",
        "anthropic_adapter_static_safety",
        "anthropic_adapter_utf8_stdout",
        "tracked_secret_scan",
        "credential_and_no_fake_policy_text",
        "primary_sweep_command_plan",
        "provider_transcript_evidence",
        "local_qa_provider_separation",
        "provider_sweep_coverage",
        "provider_claim_boundary",
    }
    provider_check_ids = {row_data.get("check_id", "") for row_data in provider_readiness}
    provider_fields = set(provider_readiness[0].keys()) if provider_readiness else set()
    required_provider_fields = {
        "check_id",
        "area",
        "status",
        "evidence",
        "current_state",
        "limitation",
        "next_action",
    }
    provider_failures = [row_data for row_data in provider_readiness if row_data.get("status") == "fail"]
    provider_cautions = [row_data for row_data in provider_readiness if row_data.get("status") == "caution"]
    provider_blocks = [row_data for row_data in provider_readiness if row_data.get("status") == "block"]
    provider_readiness_ok = (
        bool(provider_readiness)
        and required_provider_checks.issubset(provider_check_ids)
        and required_provider_fields.issubset(provider_fields)
        and not provider_failures
        and (ROOT / "reports" / "provider_readiness_audit.md").exists()
    )
    requirement_rows.append(row(
        "provider_readiness_audit",
        "reporting",
        "Provider readiness audit should verify model-runner contracts adapter coverage credential policy transcript evidence planned sweep commands and smoke-only coverage limits.",
        status_from_bool(provider_readiness_ok, partial=bool(provider_readiness)),
        f"provider readiness rows: {len(provider_readiness)}; required checks covered: {len(required_provider_checks & provider_check_ids)}/{len(required_provider_checks)}; failures: {len(provider_failures)}; cautions: {len(provider_cautions)}; blocks: {len(provider_blocks)}; report exists: {(ROOT / 'reports' / 'provider_readiness_audit.md').exists()}.",
        "No gap." if provider_readiness_ok else "Regenerate scripts/audit_provider_readiness.py and fix failing provider-readiness checks.",
    ))

    model_sweep_command_fields = set(model_sweep_execution_commands[0].keys()) if model_sweep_execution_commands else set()
    model_sweep_checklist_fields = set(model_sweep_execution_checklist[0].keys()) if model_sweep_execution_checklist else set()
    required_model_sweep_command_fields = {
        "scaffold",
        "planned_task_count",
        "planned_k",
        "provider_route",
        "runner_env_var",
        "credential_policy",
        "full_sweep_command",
        "smoke_command",
        "post_run_commands",
        "required_evidence",
    }
    required_model_sweep_checklist_fields = {
        "check_id",
        "phase",
        "required_before_claim",
        "current_status",
        "evidence",
        "next_action",
    }
    required_model_sweep_checks = {
        "local_validation_before_sweep",
        "provider_runner_contract",
        "scaffold_ladder_contract",
        "planned_primary_cells",
        "transcript_and_run_result_evidence",
        "frontier_claim_boundary",
        "statistical_report_refresh",
    }
    model_sweep_check_ids = {row_data.get("check_id", "") for row_data in model_sweep_execution_checklist}
    command_scaffolds = {row_data.get("scaffold", "") for row_data in model_sweep_execution_commands}
    command_providers = {row_data.get("provider_route", "") for row_data in model_sweep_execution_commands}
    command_key_leaks = [
        row_data for row_data in model_sweep_execution_commands
        if "API_KEY=" in row_data.get("full_sweep_command", "")
        or "API_KEY=" in row_data.get("smoke_command", "")
    ]
    model_sweep_packet_ok = (
        bool(model_sweep_execution_commands)
        and bool(model_sweep_execution_checklist)
        and {"one-shot", "lookup", "lookup_unlimited"}.issubset(command_scaffolds)
        and {"command", "openai", "anthropic", "gemini"}.issubset(command_providers)
        and required_model_sweep_command_fields.issubset(model_sweep_command_fields)
        and required_model_sweep_checklist_fields.issubset(model_sweep_checklist_fields)
        and required_model_sweep_checks.issubset(model_sweep_check_ids)
        and not command_key_leaks
        and (ROOT / "reports" / "model_sweep_execution_packet.md").exists()
    )
    requirement_rows.append(row(
        "model_sweep_execution_packet",
        "runs",
        "Model sweep execution packet should provide concrete provider scaffold commands credential policy post-run evidence checks and claim-boundary reminders without creating fake model results.",
        status_from_bool(model_sweep_packet_ok, partial=bool(model_sweep_execution_commands)),
        f"command rows: {len(model_sweep_execution_commands)}; checklist rows: {len(model_sweep_execution_checklist)}; scaffolds: {compact_json(sorted(command_scaffolds))}; providers: {compact_json(sorted(command_providers))}; key assignment leaks: {len(command_key_leaks)}; report exists: {(ROOT / 'reports' / 'model_sweep_execution_packet.md').exists()}.",
        "No gap." if model_sweep_packet_ok else "Regenerate scripts/generate_model_sweep_packet.py and inspect provider/scaffold command coverage.",
    ))

    required_hosted_qa_checks = {
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
    }
    hosted_qa_check_ids = {row_data.get("check_id", "") for row_data in hosted_qa_readiness}
    hosted_qa_fields = set(hosted_qa_readiness[0].keys()) if hosted_qa_readiness else set()
    required_hosted_qa_fields = {
        "check_id",
        "area",
        "status",
        "evidence",
        "required_for_hosted_qa",
        "current_state",
        "next_action",
    }
    hosted_qa_failures = [row_data for row_data in hosted_qa_readiness if row_data.get("status") == "fail"]
    hosted_qa_blocks = [row_data for row_data in hosted_qa_readiness if row_data.get("status") == "block"]
    hosted_qa_readiness_ok = (
        bool(hosted_qa_readiness)
        and required_hosted_qa_checks.issubset(hosted_qa_check_ids)
        and required_hosted_qa_fields.issubset(hosted_qa_fields)
        and not hosted_qa_failures
        and (ROOT / "reports" / "hosted_qa_readiness_audit.md").exists()
    )
    requirement_rows.append(row(
        "hosted_qa_readiness_audit",
        "reporting",
        "Hosted QA readiness audit should distinguish local readiness from missing Taiga packaging problem-version QA and finding-resolution evidence.",
        status_from_bool(hosted_qa_readiness_ok, partial=bool(hosted_qa_readiness)),
        f"hosted QA readiness rows: {len(hosted_qa_readiness)}; required checks covered: {len(required_hosted_qa_checks & hosted_qa_check_ids)}/{len(required_hosted_qa_checks)}; failures: {len(hosted_qa_failures)}; blocked hosted-QA steps: {len(hosted_qa_blocks)}; report exists: {(ROOT / 'reports' / 'hosted_qa_readiness_audit.md').exists()}.",
        "No gap." if hosted_qa_readiness_ok else "Regenerate scripts/audit_hosted_qa_readiness.py and fix failing local readiness checks.",
    ))

    required_taiga_wrapper_checks = {
        "hidden_bundle_generation",
        "bundle_runtime_grading_smoke",
        "docker_static_isolation_controls",
    }
    taiga_wrapper_check_ids = {row_data.get("check_id", "") for row_data in taiga_wrapper_isolation}
    taiga_wrapper_fields = set(taiga_wrapper_isolation[0].keys()) if taiga_wrapper_isolation else set()
    required_taiga_wrapper_fields = {
        "check_id",
        "area",
        "status",
        "evidence",
        "limitation",
        "next_action",
    }
    taiga_wrapper_failures = [row_data for row_data in taiga_wrapper_isolation if row_data.get("status") == "fail"]
    taiga_wrapper_ok = (
        bool(taiga_wrapper_isolation)
        and required_taiga_wrapper_checks.issubset(taiga_wrapper_check_ids)
        and required_taiga_wrapper_fields.issubset(taiga_wrapper_fields)
        and not taiga_wrapper_failures
        and (ROOT / "reports" / "taiga_wrapper_isolation_audit.md").exists()
    )
    requirement_rows.append(row(
        "taiga_wrapper_isolation_audit",
        "reporting",
        "Taiga wrapper isolation audit should exercise the local hidden-bundle grading path without source-task fallback while keeping hosted isolation claims blocked.",
        status_from_bool(taiga_wrapper_ok, partial=bool(taiga_wrapper_isolation)),
        f"taiga wrapper isolation rows: {len(taiga_wrapper_isolation)}; required checks covered: {len(required_taiga_wrapper_checks & taiga_wrapper_check_ids)}/{len(required_taiga_wrapper_checks)}; failures: {len(taiga_wrapper_failures)}; report exists: {(ROOT / 'reports' / 'taiga_wrapper_isolation_audit.md').exists()}.",
        "No gap." if taiga_wrapper_ok else "Regenerate scripts/audit_taiga_wrapper_isolation.py and fix failing local wrapper mitigation checks.",
    ))

    required_threat_ids = {
        "construct_time_horizon_depth",
        "portfolio_scale_and_balance",
        "author_estimated_human_time",
        "automation_dominated_retained_tasks",
        "semantic_pin_finiteness",
        "scaffold_sweep_undercoverage",
        "frontier_performance_undercoverage",
        "statistical_power_and_plots",
        "failure_taxonomy_forecast",
        "hosted_environment_gap",
        "secret_and_runner_boundary",
        "public_export_hidden_leakage",
    }
    required_threat_categories = {
        "construct_validity",
        "internal_validity",
        "external_validity",
        "statistical_validity",
        "operational_validity",
        "operational_security",
    }
    threat_ids = {row_data.get("threat_id", "") for row_data in threats_to_validity}
    threat_categories = {row_data.get("category", "") for row_data in threats_to_validity}
    threat_statuses = Counter(row_data.get("current_status", "unknown") for row_data in threats_to_validity)
    threat_fields = set(threats_to_validity[0].keys()) if threats_to_validity else set()
    required_threat_fields = {
        "threat_id",
        "category",
        "severity",
        "current_status",
        "evidence",
        "mitigation_in_repo",
        "stronger_evidence_needed",
        "claims_limited",
        "source_artifacts",
    }
    invalid_threat_statuses = [
        row_data for row_data in threats_to_validity
        if row_data.get("current_status") not in {"controlled", "caution", "block"}
    ]
    threats_ok = (
        bool(threats_to_validity)
        and required_threat_ids.issubset(threat_ids)
        and required_threat_categories.issubset(threat_categories)
        and required_threat_fields.issubset(threat_fields)
        and not invalid_threat_statuses
        and threat_statuses.get("block", 0) >= 1
        and threat_statuses.get("caution", 0) >= 1
        and (ROOT / "reports" / "threats_to_validity.md").exists()
    )
    requirement_rows.append(row(
        "threats_to_validity_register",
        "reporting",
        "Threats-to-validity register should turn construct internal external statistical operational and security limitations into generated evidence rows with mitigations and stronger-evidence requirements.",
        status_from_bool(threats_ok, partial=bool(threats_to_validity)),
        f"threat rows: {len(threats_to_validity)}; required threats covered: {len(required_threat_ids & threat_ids)}/{len(required_threat_ids)}; categories: {compact_json(sorted(threat_categories))}; statuses: {compact_json(dict(sorted(threat_statuses.items())))}; invalid statuses: {len(invalid_threat_statuses)}; report exists: {(ROOT / 'reports' / 'threats_to_validity.md').exists()}.",
        "No gap." if threats_ok else "Regenerate scripts/generate_threats_to_validity.py and inspect missing threat categories or statuses.",
    ))

    required_threat_coverage_ids = {
        "locked_blocker_threat_mapping",
        "non_allowed_claim_threat_mapping",
        "threat_row_completeness",
        "high_block_threat_freeze_alignment",
    }
    threat_coverage_ids = {
        row_data.get("check_id", "") for row_data in threat_coverage
    }
    threat_coverage_failures = [
        row_data for row_data in threat_coverage
        if row_data.get("status") == "fail"
    ]
    threat_coverage_ok = (
        bool(threat_coverage)
        and required_threat_coverage_ids.issubset(threat_coverage_ids)
        and not threat_coverage_failures
        and (ROOT / "reports" / "threat_coverage_audit.md").exists()
    )
    requirement_rows.append(row(
        "threat_coverage_audit",
        "reporting",
        "Threat coverage audit should verify that open locked-benchmark blockers and non-allowed claims are represented in threats-to-validity rows with mitigations and stronger-evidence requirements.",
        status_from_bool(threat_coverage_ok, partial=bool(threat_coverage)),
        f"threat-coverage rows: {len(threat_coverage)}; required checks covered: {len(required_threat_coverage_ids & threat_coverage_ids)}/{len(required_threat_coverage_ids)}; failures: {len(threat_coverage_failures)}; report exists: {(ROOT / 'reports' / 'threat_coverage_audit.md').exists()}.",
        "No gap." if threat_coverage_ok else "Regenerate scripts/audit_threat_coverage.py and inspect unmapped blockers, claims, or threat rows.",
    ))

    required_claim_ids = {
        "local_release_artifact",
        "research_report_evidence",
        "accepted_core_reviewed",
        "hidden_pin_strength",
        "run_data_integrity",
        "time_horizon_measurement",
        "scaffold_effects",
        "frontier_performance",
        "locked_benchmark",
    }
    claim_ids = {row_data.get("claim_id", "") for row_data in claim_evidence}
    unsupported_claims = [row_data for row_data in claim_evidence if row_data.get("support_status") == "unsupported"]
    claim_fields = set(claim_evidence[0].keys()) if claim_evidence else set()
    required_claim_fields = {
        "claim_id",
        "claim_type",
        "support_status",
        "evidence_strength",
        "primary_evidence",
        "counterevidence_or_limits",
        "stronger_claim_requires",
    }
    claim_audit_ok = (
        bool(claim_evidence)
        and required_claim_ids.issubset(claim_ids)
        and len(unsupported_claims) >= 2
        and required_claim_fields.issubset(claim_fields)
        and (ROOT / "reports" / "claim_evidence_audit.md").exists()
    )
    requirement_rows.append(row(
        "claim_evidence_audit",
        "reporting",
        "Claim-evidence audit should map artifact, report, performance, and benchmark-status claims to evidence strength and limits.",
        status_from_bool(claim_audit_ok, partial=bool(claim_evidence)),
        f"claim_evidence rows: {len(claim_evidence)}; required claims covered: {len(required_claim_ids & claim_ids)}/{len(required_claim_ids)}; unsupported overclaim rows: {len(unsupported_claims)}; report exists: {(ROOT / 'reports' / 'claim_evidence_audit.md').exists()}.",
        "No gap." if claim_audit_ok else "Regenerate scripts/audit_claim_evidence.py after requirement coverage and inspect missing claim rows.",
    ))

    required_authorization_ids = {
        "local_artifact_validity",
        "research_report_scope",
        "accepted_core_quality",
        "hidden_pin_and_grader_strength",
        "run_data_integrity",
        "time_horizon_scope",
        "scaffold_effects",
        "frontier_model_performance",
        "failure_taxonomy_results",
        "statistical_performance_reporting",
        "hosted_qa_status",
        "locked_benchmark_status",
    }
    authorization_ids = {row_data.get("claim_id", "") for row_data in claim_authorization}
    authorization_fields = set(claim_authorization[0].keys()) if claim_authorization else set()
    required_authorization_fields = {
        "claim_id",
        "claim_area",
        "authorization_status",
        "allowed_wording",
        "required_caveat",
        "forbidden_wording",
        "current_evidence",
        "evidence_to_upgrade",
        "blocking_requirements",
        "source_artifacts",
    }
    invalid_authorization_statuses = [
        row_data for row_data in claim_authorization
        if row_data.get("authorization_status") not in {"allowed", "allowed_with_caveat", "blocked"}
    ]
    blocked_authorizations = [
        row_data for row_data in claim_authorization
        if row_data.get("authorization_status") == "blocked"
    ]
    caveated_authorizations = [
        row_data for row_data in claim_authorization
        if row_data.get("authorization_status") == "allowed_with_caveat"
    ]
    missing_wording = [
        row_data.get("claim_id", "")
        for row_data in claim_authorization
        if not row_data.get("allowed_wording", "").strip()
        or not row_data.get("forbidden_wording", "").strip()
        or not row_data.get("evidence_to_upgrade", "").strip()
    ]
    authorization_ok = (
        bool(claim_authorization)
        and required_authorization_ids.issubset(authorization_ids)
        and required_authorization_fields.issubset(authorization_fields)
        and not invalid_authorization_statuses
        and len(blocked_authorizations) >= 4
        and len(caveated_authorizations) >= 4
        and not missing_wording
        and (ROOT / "reports" / "claim_authorization_matrix.md").exists()
    )
    requirement_rows.append(row(
        "claim_authorization_matrix",
        "reporting",
        "Claim authorization matrix should translate evidence audits into allowed caveated and blocked report wording, including forbidden overclaim language.",
        status_from_bool(authorization_ok, partial=bool(claim_authorization)),
        f"authorization rows: {len(claim_authorization)}; required claims covered: {len(required_authorization_ids & authorization_ids)}/{len(required_authorization_ids)}; blocked rows: {len(blocked_authorizations)}; caveated rows: {len(caveated_authorizations)}; invalid statuses: {len(invalid_authorization_statuses)}; missing wording rows: {len(missing_wording)}; report exists: {(ROOT / 'reports' / 'claim_authorization_matrix.md').exists()}.",
        "No gap." if authorization_ok else "Regenerate scripts/generate_claim_authorization_matrix.py after claim evidence and inspect missing or under-specified authorization rows.",
    ))

    gap_ids = {row_data.get("claim_id", "") for row_data in research_claim_gap}
    gap_fields = set(research_claim_gap[0].keys()) if research_claim_gap else set()
    required_gap_fields = {
        "claim_id",
        "claim_area",
        "authorization_status",
        "claim_support_status",
        "evidence_strength",
        "upgrade_priority",
        "blocking_requirements",
        "blocking_requirement_statuses",
        "minimum_evidence_package",
        "exit_criteria",
        "allowed_wording_now",
        "forbidden_overclaim",
        "source_artifacts",
    }
    non_allowed_authorization_ids = {
        row_data.get("claim_id", "")
        for row_data in claim_authorization
        if row_data.get("authorization_status") != "allowed"
    }
    high_gap_rows = [
        row_data for row_data in research_claim_gap
        if row_data.get("upgrade_priority") in {"high", "highest"}
        or row_data.get("authorization_status") == "blocked"
    ]
    missing_gap_packages = [
        row_data.get("claim_id", "")
        for row_data in research_claim_gap
        if not row_data.get("minimum_evidence_package", "").strip()
        or not row_data.get("exit_criteria", "").strip()
        or not row_data.get("forbidden_overclaim", "").strip()
    ]
    missing_gap_support = [
        row_data.get("claim_id", "")
        for row_data in research_claim_gap
        if row_data.get("claim_support_status") == "missing"
        or row_data.get("evidence_strength") == "missing"
    ]
    gap_ok = (
        bool(research_claim_gap)
        and required_gap_fields.issubset(gap_fields)
        and non_allowed_authorization_ids.issubset(gap_ids)
        and not missing_gap_packages
        and not missing_gap_support
        and len(high_gap_rows) >= 5
        and (ROOT / "reports" / "research_claim_gap_matrix.md").exists()
    )
    requirement_rows.append(row(
        "research_claim_gap_matrix",
        "reporting",
        "Research claim gap matrix should map caveated and blocked claims to the minimum evidence packages and requirement gates needed before stronger wording is allowed.",
        status_from_bool(gap_ok, partial=bool(research_claim_gap)),
        f"gap rows: {len(research_claim_gap)}; non-allowed claims covered: {len(non_allowed_authorization_ids & gap_ids)}/{len(non_allowed_authorization_ids)}; high-or-blocked rows: {len(high_gap_rows)}; missing package rows: {len(missing_gap_packages)}; missing support rows: {len(missing_gap_support)}; report exists: {(ROOT / 'reports' / 'research_claim_gap_matrix.md').exists()}.",
        "No gap." if gap_ok else "Regenerate scripts/generate_research_claim_gap_matrix.py after claim authorization and inspect missing evidence packages.",
    ))

    required_conformance_ids = {
        "authorization_matrix_loaded",
        "main_report_authorization_section",
        "abstract_scope_boundaries",
        "run_result_boundary_wording",
        "claim_ledger_blocks_overclaims",
        "concise_report_scope_and_length",
        "locked_benchmark_blocker_consistency",
        "blocked_phrase_context_scan",
        "readme_scope_boundaries",
        "limitations_cover_blockers",
        "report_length_and_appendix_boundary",
    }
    conformance_ids = {row_data.get("check_id", "") for row_data in report_claim_conformance}
    conformance_fields = set(report_claim_conformance[0].keys()) if report_claim_conformance else set()
    required_conformance_fields = {
        "check_id",
        "scope",
        "status",
        "evidence",
        "failure_examples",
        "required_action",
        "source_artifacts",
    }
    conformance_failures = [
        row_data for row_data in report_claim_conformance
        if row_data.get("status") == "fail"
    ]
    conformance_cautions = [
        row_data for row_data in report_claim_conformance
        if row_data.get("status") == "caution"
    ]
    conformance_ok = (
        bool(report_claim_conformance)
        and required_conformance_ids.issubset(conformance_ids)
        and required_conformance_fields.issubset(conformance_fields)
        and not conformance_failures
        and (ROOT / "reports" / "report_claim_conformance_audit.md").exists()
    )
    requirement_rows.append(row(
        "report_claim_conformance_audit",
        "reporting",
        "Report claim-conformance audit should check the main report and README against the claim authorization matrix so blocked claims remain caveated or explicitly unsupported.",
        status_from_bool(conformance_ok, partial=bool(report_claim_conformance)),
        f"conformance rows: {len(report_claim_conformance)}; required checks covered: {len(required_conformance_ids & conformance_ids)}/{len(required_conformance_ids)}; failures: {len(conformance_failures)}; cautions: {len(conformance_cautions)}; report exists: {(ROOT / 'reports' / 'report_claim_conformance_audit.md').exists()}.",
        "No gap." if conformance_ok else "Regenerate scripts/audit_report_claim_conformance.py after report generation and inspect any failed claim-boundary rows.",
    ))

    required_gate_ids = {
        "local_release_artifact",
        "research_report_readiness",
        "accepted_core_stats_scope",
        "hidden_pin_confidence",
        "time_horizon_claim",
        "scaffold_effect_claim",
        "frontier_performance_claim",
        "locked_benchmark_freeze",
    }
    gate_ids = {row_data.get("gate_id", "") for row_data in release_decision}
    gate_fields = set(release_decision[0].keys()) if release_decision else set()
    required_gate_fields = {
        "gate_id",
        "decision_scope",
        "decision",
        "status",
        "evidence_basis",
        "blocking_or_caution_items",
        "required_next_action",
    }
    block_gates = [row_data for row_data in release_decision if row_data.get("status") == "block"]
    pass_gates = [row_data for row_data in release_decision if row_data.get("status") == "pass"]
    release_decision_ok = (
        bool(release_decision)
        and required_gate_ids.issubset(gate_ids)
        and required_gate_fields.issubset(gate_fields)
        and len(block_gates) >= 3
        and len(pass_gates) >= 1
        and (ROOT / "reports" / "release_decision_log.md").exists()
    )
    requirement_rows.append(row(
        "release_decision_log",
        "reporting",
        "Release decision log should translate evidence audits into explicit pass/caution/block gates and next actions.",
        status_from_bool(release_decision_ok, partial=bool(release_decision)),
        f"release_decision rows: {len(release_decision)}; required gates covered: {len(required_gate_ids & gate_ids)}/{len(required_gate_ids)}; block gates: {len(block_gates)}; pass gates: {len(pass_gates)}; report exists: {(ROOT / 'reports' / 'release_decision_log.md').exists()}.",
        "No gap." if release_decision_ok else "Regenerate scripts/generate_release_decision_log.py after claim and requirement audits, then inspect missing gates.",
    ))

    required_freeze_gate_ids = {
        "local_artifact_validation",
        "accepted_portfolio_scale",
        "time_horizon_depth",
        "family_balance_and_diagnostics",
        "independent_human_timing",
        "scaffold_sweep_coverage",
        "frontier_and_open_model_evidence",
        "hosted_qa_and_env_linter",
        "statistical_reporting_readiness",
        "freeze_versioning",
    }
    freeze_gate_ids = {row_data.get("gate_id", "") for row_data in freeze_roadmap}
    freeze_fields = set(freeze_roadmap[0].keys()) if freeze_roadmap else set()
    required_freeze_fields = {
        "gate_id",
        "category",
        "roadmap_status",
        "current_state",
        "evidence",
        "exit_criteria",
        "concrete_next_action",
        "blocks_claims",
        "source_artifacts",
    }
    freeze_statuses = Counter(row_data.get("roadmap_status", "unknown") for row_data in freeze_roadmap)
    freeze_roadmap_ok = (
        bool(freeze_roadmap)
        and required_freeze_gate_ids.issubset(freeze_gate_ids)
        and required_freeze_fields.issubset(freeze_fields)
        and freeze_statuses.get("ready", 0) >= 1
        and freeze_statuses.get("block", 0) >= 1
        and (ROOT / "reports" / "freeze_readiness_roadmap.md").exists()
    )
    requirement_rows.append(row(
        "freeze_readiness_roadmap",
        "reporting",
        "Freeze-readiness roadmap should synthesize requirement claim hosted QA statistical model-run and metadata audits into measurable gates for locked-benchmark readiness.",
        status_from_bool(freeze_roadmap_ok, partial=bool(freeze_roadmap)),
        f"freeze roadmap rows: {len(freeze_roadmap)}; required gates covered: {len(required_freeze_gate_ids & freeze_gate_ids)}/{len(required_freeze_gate_ids)}; statuses: {compact_json(dict(sorted(freeze_statuses.items())))}; report exists: {(ROOT / 'reports' / 'freeze_readiness_roadmap.md').exists()}.",
        "No gap." if freeze_roadmap_ok else "Regenerate scripts/generate_freeze_readiness_roadmap.py after requirement, claim, release, and readiness audits.",
    ))

    required_final_delivery_checks = {
        "final_versions_have_pass_at_k",
        "scaffolds_use_same_task_set",
        "env_linter_findings_resolved",
        "full_env_qa_10_attempts",
        "late_qa_findings_settled",
        "repo_matches_uploaded_environment",
        "plots_regenerate_from_committed_csv",
        "report_states_sample_sizes_and_model_versions",
        "dev_test_split_marked",
        "hidden_references_not_public_runtime_assets",
    }
    final_delivery_ids = {row_data.get("check_id", "") for row_data in final_delivery_checklist}
    final_delivery_fields = set(final_delivery_checklist[0].keys()) if final_delivery_checklist else set()
    required_final_delivery_fields = {
        "check_id",
        "playbook_item",
        "status",
        "evidence",
        "source_artifacts",
        "limitation",
        "next_action",
    }
    final_delivery_statuses = Counter(row_data.get("status", "unknown") for row_data in final_delivery_checklist)
    final_delivery_ok = (
        bool(final_delivery_checklist)
        and required_final_delivery_checks.issubset(final_delivery_ids)
        and required_final_delivery_fields.issubset(final_delivery_fields)
        and final_delivery_statuses.get("pass", 0) >= 1
        and final_delivery_statuses.get("block", 0) >= 1
        and (ROOT / "reports" / "final_delivery_checklist_audit.md").exists()
    )
    requirement_rows.append(row(
        "final_delivery_checklist_audit",
        "reporting",
        "Final delivery checklist audit should map the playbook final-delivery checklist to committed evidence and explicitly block unmet pass@k hosted QA and version-freeze requirements.",
        status_from_bool(final_delivery_ok, partial=bool(final_delivery_checklist)),
        f"final-delivery rows: {len(final_delivery_checklist)}; required checks covered: {len(required_final_delivery_checks & final_delivery_ids)}/{len(required_final_delivery_checks)}; statuses: {compact_json(dict(sorted(final_delivery_statuses.items())))}; report exists: {(ROOT / 'reports' / 'final_delivery_checklist_audit.md').exists()}.",
        "No gap." if final_delivery_ok else "Regenerate scripts/audit_final_delivery_checklist.py and keep playbook final-delivery blockers visible.",
    ))

    required_scaffold_checks = {
        "scaffold_catalog_complete",
        "prompt_affordance_contract",
        "runner_env_contract",
        "iterative_feedback_gate",
        "attempt_count_semantics",
        "lookup_roots_public_only",
        "lookup_command_smoke",
        "lookup_hidden_leak_scan",
        "planned_sweep_coverage",
        "observed_scaffold_data_coverage",
        "scaffold_claim_boundary",
    }
    scaffold_check_ids = {row_data.get("check_id", "") for row_data in scaffold_audit}
    scaffold_audit_fields = set(scaffold_audit[0].keys()) if scaffold_audit else set()
    required_scaffold_fields = {
        "check_id",
        "area",
        "status",
        "evidence",
        "risk_or_limit",
        "required_next_action",
    }
    scaffold_cautions = [row_data for row_data in scaffold_audit if row_data.get("status") == "caution"]
    scaffold_audit_ok = (
        bool(scaffold_audit)
        and required_scaffold_checks.issubset(scaffold_check_ids)
        and required_scaffold_fields.issubset(scaffold_audit_fields)
        and not scaffold_audit_failures
        and scaffold_audit_by_id.get("lookup_hidden_leak_scan", {}).get("status") == "pass"
        and (ROOT / "reports" / "scaffold_support_audit.md").exists()
    )
    requirement_rows.append(row(
        "scaffold_support_audit",
        "reporting",
        "Scaffold support audit should verify prompt contracts runner semantics lookup safety planned coverage and observed coverage limits.",
        status_from_bool(scaffold_audit_ok, partial=bool(scaffold_audit)),
        f"scaffold audit rows: {len(scaffold_audit)}; required checks covered: {len(required_scaffold_checks & scaffold_check_ids)}/{len(required_scaffold_checks)}; failures: {len(scaffold_audit_failures)}; cautions: {len(scaffold_cautions)}; report exists: {(ROOT / 'reports' / 'scaffold_support_audit.md').exists()}.",
        "No gap." if scaffold_audit_ok else "Regenerate scripts/audit_scaffold_support.py and fix failed scaffold or lookup checks.",
    ))

    accepted_successful_timing = {
        row_data.get("task_id")
        for row_data in human_time_audit
        if row_data.get("acceptance_status") == "accepted_v0"
        and int(row_data.get("successful_independent_observation_count", "0") or "0") > 0
    }
    human_independent_ok = bool(accepted) and len(accepted_successful_timing) == len(accepted)
    human_review_partial = any(task.get("difficulty_review_status") == "manual_review_complete" for task in accepted)
    requirement_rows.append(row(
        "independent_human_time_review",
        "calibration",
        "Human-time estimates should be separately reviewed or measured, not inferred from model pass rates.",
        status_from_bool(human_independent_ok, partial=human_review_partial or bool(human_time_audit)),
        f"Accepted tasks with manual_review_complete: {sum(task.get('difficulty_review_status') == 'manual_review_complete' for task in accepted)}/{len(accepted)}; accepted tasks with successful independent timing observations: {len(accepted_successful_timing)}/{len(accepted)}; observation rows: {len(human_time_observations)}.",
        "Collect independent Lean-human timed solves or second-reviewer timing notes before freeze.",
    ))

    accepted_task_ids = {task.get("task_id", "") for task in accepted}
    reviewed_accepted_ids = {
        row_data.get("task_id", "")
        for row_data in independent_task_reviews
        if row_data.get("task_id", "") in accepted_task_ids
    }
    task_quality_review_ok = bool(accepted_task_ids) and reviewed_accepted_ids == accepted_task_ids
    requirement_rows.append(row(
        "independent_task_quality_review",
        "calibration",
        "Accepted task-quality claims should receive completed independent non-author task review before benchmark freeze.",
        status_from_bool(task_quality_review_ok, partial=bool(reviewed_accepted_ids)),
        (
            f"Accepted tasks with completed independent task reviews: {len(reviewed_accepted_ids)}/{len(accepted_task_ids)}; "
            f"review rows: {len(independent_task_reviews)}; status-audit rows: {len(independent_review_status)}."
        ),
        "Collect non-author task-quality reviews for every accepted_v0 task before freeze.",
    ))

    hosted_artifacts = [ROOT / "reports" / "hosted_qa.md", ROOT / "data" / "hosted_qa_results.csv"]
    hosted_present, hosted_total = file_count_status(hosted_artifacts)
    hosted_readiness_report_exists = (ROOT / "reports" / "hosted_qa_readiness_audit.md").exists()
    hosted_readiness_blocks = sum(1 for row_data in hosted_qa_readiness if row_data.get("status") == "block")
    requirement_rows.append(row(
        "hosted_qa_env_linter",
        "qa",
        "Hosted Taiga/Env Linter QA should be run before delivery/freeze.",
        status_from_bool(hosted_present == hosted_total and hosted_total > 0, partial=hosted_present > 0),
        f"Hosted QA artifacts present: {hosted_present}/{hosted_total}; hosted readiness report exists: {hosted_readiness_report_exists}; blocked hosted-readiness checks: {hosted_readiness_blocks}.",
        "Run hosted Full Env QA and record findings/rebuttals before claiming a locked benchmark.",
    ))

    manifest_ok = (ROOT / "reports" / "validation_manifest.json").exists()
    requirement_rows.append(row(
        "reproducibility_manifest",
        "reproducibility",
        "A clean regeneration trail should record toolchain, commands, counts, and artifact hashes.",
        status_from_bool(manifest_ok),
        f"validation_manifest.json exists: {manifest_ok}.",
        "No gap." if manifest_ok else "Run write_validation_manifest.py after validation.",
    ))

    required_manifest_audit_ids = {
        "schema_and_policy_note",
        "regeneration_command_coverage",
        "artifact_hash_integrity",
        "artifact_inventory_coverage",
        "self_reference_boundary",
        "public_export_snapshot",
        "git_snapshot_policy",
        "summary_count_snapshot",
    }
    manifest_audit_ids = {row_data.get("check_id", "") for row_data in validation_manifest_audit}
    manifest_audit_fields = set(validation_manifest_audit[0].keys()) if validation_manifest_audit else set()
    required_manifest_audit_fields = {
        "check_id",
        "area",
        "status",
        "evidence",
        "limitation",
        "next_action",
    }
    manifest_audit_failures = [
        row_data for row_data in validation_manifest_audit
        if row_data.get("status") == "fail"
    ]
    manifest_audit_ok = (
        bool(validation_manifest_audit)
        and required_manifest_audit_ids.issubset(manifest_audit_ids)
        and required_manifest_audit_fields.issubset(manifest_audit_fields)
        and not manifest_audit_failures
        and (ROOT / "reports" / "validation_manifest_audit.md").exists()
    )
    requirement_rows.append(row(
        "validation_manifest_audit",
        "reproducibility",
        "Validation manifest audit should verify manifest schema command coverage artifact hashes public-export summary and dirty-status policy.",
        status_from_bool(manifest_audit_ok, partial=bool(validation_manifest_audit)),
        f"manifest audit rows: {len(validation_manifest_audit)}; required checks covered: {len(required_manifest_audit_ids & manifest_audit_ids)}/{len(required_manifest_audit_ids)}; failures: {len(manifest_audit_failures)}; report exists: {(ROOT / 'reports' / 'validation_manifest_audit.md').exists()}.",
        "No gap." if manifest_audit_ok else "Run scripts/audit_validation_manifest.py after writing the validation manifest and inspect failed manifest checks.",
    ))

    required_reproduction_step_ids = {
        "toolchain_build",
        "mathlib_cache_get",
        "task_validation",
        "difficulty_review",
        "local_qa_rows",
        "run_integrity",
        "peer_review_matrix",
        "security_leakage",
        "passk_claim_boundaries",
        "grader_hardening",
        "public_export",
        "public_export_validation",
        "report_regeneration",
        "claim_and_shape_audits",
        "validation_manifest",
        "provider_sweep",
        "independent_human_timing",
        "hosted_qa",
    }
    reproduction_step_ids = {row_data.get("step_id", "") for row_data in reviewer_reproduction_steps}
    reproduction_fields = set(reviewer_reproduction_steps[0].keys()) if reviewer_reproduction_steps else set()
    required_reproduction_fields = {
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
    }
    local_replay_problem_rows = [
        row_data for row_data in reviewer_reproduction_steps
        if row_data.get("phase") == "local_replay" and row_data.get("status") != "ready"
    ]
    external_evidence_rows = [
        row_data for row_data in reviewer_reproduction_steps
        if row_data.get("phase") == "external_evidence"
    ]
    reviewer_reproduction_ok = (
        bool(reviewer_reproduction_steps)
        and required_reproduction_step_ids.issubset(reproduction_step_ids)
        and required_reproduction_fields.issubset(reproduction_fields)
        and not local_replay_problem_rows
        and external_evidence_rows
        and (ROOT / "reports" / "reviewer_reproduction_packet.md").exists()
    )
    requirement_rows.append(row(
        "reviewer_reproduction_packet",
        "reproducibility",
        "Reviewer reproduction packet should give an ordered local replay workflow external-evidence boundaries expected artifacts and failure interpretations.",
        status_from_bool(reviewer_reproduction_ok, partial=bool(reviewer_reproduction_steps)),
        f"reproduction steps: {len(reviewer_reproduction_steps)}; required covered: {len(required_reproduction_step_ids & reproduction_step_ids)}/{len(required_reproduction_step_ids)}; local problem rows: {len(local_replay_problem_rows)}; external evidence rows: {len(external_evidence_rows)}; report exists: {(ROOT / 'reports' / 'reviewer_reproduction_packet.md').exists()}.",
        "No gap." if reviewer_reproduction_ok else "Run scripts/generate_reviewer_reproduction_packet.py and inspect missing local replay or external-boundary rows.",
    ))

    required_clean_replay_ids = {
        "workspace_materialization",
        "mathlib_cache_get",
        "clean_lake_build",
        "reference_validation_smoke",
        "wrong_submission_smoke",
        "public_export_smoke",
        "public_export_validation_smoke",
    }
    clean_replay_ids = {row_data.get("check_id", "") for row_data in clean_workspace_replay}
    clean_replay_fields = set(clean_workspace_replay[0].keys()) if clean_workspace_replay else set()
    required_clean_replay_fields = {
        "check_id",
        "phase",
        "status",
        "command",
        "returncode",
        "duration_seconds",
        "workspace_path",
        "stdout_tail",
        "artifacts_checked",
        "limitation",
        "next_action",
    }
    clean_replay_failures = [
        row_data for row_data in clean_workspace_replay
        if row_data.get("status") != "pass"
    ]
    clean_workspace_replay_ok = (
        bool(clean_workspace_replay)
        and required_clean_replay_ids.issubset(clean_replay_ids)
        and required_clean_replay_fields.issubset(clean_replay_fields)
        and not clean_replay_failures
        and (ROOT / "reports" / "clean_workspace_replay.md").exists()
    )
    requirement_rows.append(row(
        "clean_workspace_replay",
        "reproducibility",
        "Clean workspace replay should exercise dependency materialization Lean build grader pass/fail behavior and public export validation outside the dirty working directory.",
        status_from_bool(clean_workspace_replay_ok, partial=bool(clean_workspace_replay)),
        f"clean replay rows: {len(clean_workspace_replay)}; required covered: {len(required_clean_replay_ids & clean_replay_ids)}/{len(required_clean_replay_ids)}; failures: {len(clean_replay_failures)}; report exists: {(ROOT / 'reports' / 'clean_workspace_replay.md').exists()}.",
        "No gap." if clean_workspace_replay_ok else "Run scripts/run_clean_workspace_replay.py and inspect dependency, grader, or public-export failures.",
    ))

    pruning_fields = set(candidate_pruning[0].keys()) if candidate_pruning else set()
    required_pruning_fields = {
        "task_id",
        "acceptance_status",
        "pruning_decision",
        "counts_toward_accepted_core",
        "public_export_role",
        "decision_flags",
        "decision_basis",
        "core_exclusion_reason",
        "retained_role",
        "next_action",
    }
    pruning_ids = {row_data.get("task_id", "") for row_data in candidate_pruning}
    metadata_ids = {row_data.get("task_id", "") for row_data in metadata}
    missing_pruning_ids = sorted(metadata_ids - pruning_ids)
    extra_pruning_ids = sorted(pruning_ids - metadata_ids)
    rejected_pruning_rows = [
        row_data for row_data in candidate_pruning
        if row_data.get("acceptance_status", "").startswith("rejected_")
    ]
    calibration_pruning_rows = [
        row_data for row_data in candidate_pruning
        if row_data.get("acceptance_status") == "calibration_only"
    ]
    core_exclusion_rows = [
        row_data for row_data in candidate_pruning
        if row_data.get("acceptance_status") != "accepted_v0"
        and row_data.get("core_exclusion_reason", "").strip()
    ]
    pruning_ok = (
        bool(candidate_pruning)
        and len(candidate_pruning) == len(metadata)
        and required_pruning_fields.issubset(pruning_fields)
        and not missing_pruning_ids
        and not extra_pruning_ids
        and len(rejected_pruning_rows) == len(rejected)
        and len(calibration_pruning_rows) == len(calibration)
        and len(core_exclusion_rows) == len(rejected) + len(calibration)
        and (ROOT / "reports" / "candidate_pruning_audit.md").exists()
    )
    requirement_rows.append(row(
        "candidate_pruning_audit",
        "portfolio",
        "Candidate tasks should be separated from accepted tasks and pruned aggressively.",
        status_from_bool(pruning_ok, partial=bool(candidate_pruning)),
        f"pruning rows: {len(candidate_pruning)}; metadata rows: {len(metadata)}; rejected rows: {len(rejected_pruning_rows)}/{len(rejected)}; calibration rows: {len(calibration_pruning_rows)}/{len(calibration)}; non-core rows with exclusion reasons: {len(core_exclusion_rows)}/{len(rejected) + len(calibration)}; report exists: {(ROOT / 'reports' / 'candidate_pruning_audit.md').exists()}.",
        "No gap." if pruning_ok else "Run scripts/generate_candidate_pruning_audit.py and inspect missing pruning decisions, core-exclusion reasons, or archive separation.",
    ))

    semantic_rows = [row_data for row_data in difficulty if row_data.get("family") == "informal_spec_to_formal" and row_data.get("acceptance_status") == "accepted_v0"]
    semantic_ok = bool(semantic_rows) and all(row_data.get("mechanical_hidden_pin_strength") == "semantic" for row_data in semantic_rows)
    requirement_rows.append(row(
        "semantic_formalization_pins",
        "grading",
        "Formalization tasks should use semantic pins rather than brittle exact-text matching.",
        status_from_bool(semantic_ok, partial=bool(semantic_rows)),
        f"Accepted informal-spec rows in difficulty audit: {len(semantic_rows)}; semantic pin rows: {sum(row_data.get('mechanical_hidden_pin_strength') == 'semantic' for row_data in semantic_rows)}.",
        "No gap." if semantic_ok else "Strengthen formalization pins beyond type/signature checks.",
    ))

    return requirement_rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter(row_data["status"] for row_data in rows)
    freeze_counts = Counter(f"{row_data['freeze_relevance']}:{row_data['status']}" for row_data in rows)
    lines = [
        "# Requirement Coverage Audit",
        "",
        "This generated audit maps the local repository state to the committed checklist in `data/benchmark_requirements.csv`. It is an evidence index, not a claim that the benchmark is frozen.",
        "",
        "## Status Counts",
        "",
    ]
    for status in ["supported", "partial", "not_met"]:
        lines.append(f"- `{status}`: {counts.get(status, 0)}")
    lines.extend([
        "",
        "## Freeze Relevance Counts",
        "",
    ])
    for freeze_relevance in sorted({row_data["freeze_relevance"] for row_data in rows}):
        for status in ["supported", "partial", "not_met"]:
            key = f"{freeze_relevance}:{status}"
            if freeze_counts.get(key, 0):
                lines.append(f"- `{freeze_relevance}` / `{status}`: {freeze_counts[key]}")
    lines.extend([
        "",
        "## Coverage Table",
        "",
        "| id | area | freeze relevance | status | requirement | evidence | gap / next step |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ])
    for row_data in rows:
        lines.append(
            f"| `{row_data['requirement_id']}` | {row_data['area']} | {row_data['freeze_relevance']} | {row_data['status']} | "
            f"{row_data['requirement']} | {row_data['evidence']} | {row_data['gap_or_next_step']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-export", type=Path, default=ROOT / "public_tasks")
    parser.add_argument("--csv-out", type=Path, default=ROOT / "data" / "requirement_coverage.csv")
    parser.add_argument("--md-out", type=Path, default=ROOT / "reports" / "requirement_coverage.md")
    args = parser.parse_args()

    rows = apply_requirement_catalog(build_rows(args.public_export))
    write_csv(args.csv_out, rows)
    write_markdown(args.md_out, rows)
    print(f"wrote {args.csv_out.relative_to(ROOT)} and {args.md_out.relative_to(ROOT)} with {len(rows)} requirement rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
