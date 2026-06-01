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
    human_time_audit = read_csv(ROOT / "data" / "human_time_calibration_audit.csv")
    human_time_observations = read_csv(ROOT / "data" / "human_time_observations.csv")
    pin_coverage = read_csv(ROOT / "data" / "pin_coverage_audit.csv")
    run_integrity = read_csv(ROOT / "data" / "run_integrity_audit.csv")
    statistical_audit = read_csv(ROOT / "data" / "statistical_reporting_audit.csv")
    hosted_qa_readiness = read_csv(ROOT / "data" / "hosted_qa_readiness_audit.csv")
    claim_evidence = read_csv(ROOT / "data" / "claim_evidence_audit.csv")
    release_decision = read_csv(ROOT / "data" / "release_decision_log.csv")
    scaffold_audit = read_csv(ROOT / "data" / "scaffold_support_audit.csv")
    task_assets = read_csv(ROOT / "data" / "task_asset_manifest.csv")
    prompt_contract = read_csv(ROOT / "data" / "prompt_contract_audit.csv")
    run_results = read_csv(ROOT / "data" / "run_results.csv")
    model_sweep_plan = read_csv(ROOT / "data" / "model_sweep_plan.csv")
    model_result_summary = read_csv(ROOT / "data" / "model_result_summary.csv")
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

    schema_ok = all((ROOT / "data" / name).exists() for name in ["run_results_schema.json", "failure_label_schema.json", "task_metadata_schema.json"])
    requirement_rows.append(row(
        "schemas_present",
        "data",
        "Task metadata, run results, and failure labels should have schemas.",
        status_from_bool(schema_ok),
        f"Schema files present: run={((ROOT / 'data' / 'run_results_schema.json').exists())}, failure={((ROOT / 'data' / 'failure_label_schema.json').exists())}, metadata={((ROOT / 'data' / 'task_metadata_schema.json').exists())}.",
        "No gap." if schema_ok else "Add or restore missing JSON schema files.",
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

    scaffold_results_ok = len({row_data.get("scaffold") for row_data in non_infra_model_rows}) >= 3 and any(int(row_data.get("k", "1")) >= 10 for row_data in non_infra_model_rows if row_data.get("k", "1").isdigit())
    requirement_rows.append(row(
        "scaffold_result_comparison",
        "scaffolds",
        "The report should compare real model performance across scaffolds, ideally pass@10.",
        status_from_bool(scaffold_results_ok, partial=bool(non_infra_model_rows)),
        f"Non-infra model rows: {len(non_infra_model_rows)}; scaffolds observed: {compact_json(sorted({row_data.get('scaffold') for row_data in non_infra_model_rows}))}; planned rows: {len(model_sweep_plan)}.",
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

    accepted_pin_rows = [row_data for row_data in pin_coverage if row_data.get("acceptance_status") == "accepted_v0"]
    pin_fields = set(pin_coverage[0].keys()) if pin_coverage else set()
    required_pin_fields = {
        "pin_coverage_grade",
        "wrongs_failing_public_stage",
        "wrongs_failing_hidden_pin_stage",
        "theorem_shape_checks",
        "negative_examples",
    }
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
        and required_pin_fields.issubset(pin_fields)
        and (ROOT / "reports" / "pin_coverage_audit.md").exists()
    )
    requirement_rows.append(row(
        "pin_coverage_audit",
        "reporting",
        "Hidden-pin audit should distinguish public-stage wrong failures from wrong submissions that reach semantic pins.",
        status_from_bool(pin_audit_ok, partial=bool(pin_coverage)),
        f"pin_coverage rows: {len(pin_coverage)}; accepted rows: {len(accepted_pin_rows)}; accepted hidden-pin wrong failures: {accepted_with_hidden}; report exists: {(ROOT / 'reports' / 'pin_coverage_audit.md').exists()}.",
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

    required_statistical_checks = {
        "primary_sweep_coverage",
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

    required_hosted_qa_checks = {
        "local_validation_gate",
        "public_export_ready",
        "taiga_container_artifact",
        "taiga_problem_metadata",
        "mcp_hooks",
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

    requirement_rows.append(row(
        "candidate_pruning_audit",
        "portfolio",
        "Candidate tasks should be separated from accepted tasks and pruned aggressively.",
        status_from_bool(bool(rejected)),
        f"Rejected archive tasks: {len(rejected)}; calibration-only tasks: {len(calibration)}; accepted tasks: {len(accepted)}.",
        "No gap." if rejected else "Retain rejected/candidate archive and rejection rationales.",
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
