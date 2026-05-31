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

    scaffold_support_ok = len(scaffold_rows) >= 3 and "LEAN_LOOKUP_COMMAND" in run_model_sweep and "lookup_unlimited" in read_text(ROOT / "data" / "scaffold_variants.csv") and "attempts_allowed = args.attempts" in run_model_sweep
    requirement_rows.append(row(
        "scaffold_support",
        "scaffolds",
        "The repo should support one-shot, lookup, and lookup plus iterative compile/debug scaffold variants.",
        status_from_bool(scaffold_support_ok),
        f"{len(scaffold_rows)} scaffold variants configured; runner exposes lookup command: {'LEAN_LOOKUP_COMMAND' in run_model_sweep}; runner preserves requested k attempts: {'attempts_allowed = args.attempts' in run_model_sweep}.",
        "No gap." if scaffold_support_ok else "Complete scaffold CSV and runner adapter support.",
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

    human_independent_ok = "independent" in " ".join(task.get("human_estimate_confidence", "").lower() for task in metadata)
    human_review_partial = any(task.get("difficulty_review_status") == "manual_review_complete" for task in accepted)
    requirement_rows.append(row(
        "independent_human_time_review",
        "calibration",
        "Human-time estimates should be separately reviewed or measured, not inferred from model pass rates.",
        status_from_bool(human_independent_ok, partial=human_review_partial),
        f"Accepted tasks with manual_review_complete: {sum(task.get('difficulty_review_status') == 'manual_review_complete' for task in accepted)}/{len(accepted)}; no independent timed solves detected in metadata.",
        "Collect independent Lean-human timed solves or second-reviewer timing notes before freeze.",
    ))

    hosted_artifacts = [ROOT / "reports" / "hosted_qa.md", ROOT / "data" / "hosted_qa_results.csv"]
    hosted_present, hosted_total = file_count_status(hosted_artifacts)
    requirement_rows.append(row(
        "hosted_qa_env_linter",
        "qa",
        "Hosted Taiga/Env Linter QA should be run before delivery/freeze.",
        status_from_bool(hosted_present == hosted_total and hosted_total > 0, partial=hosted_present > 0),
        f"Hosted QA artifacts present: {hosted_present}/{hosted_total}.",
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
