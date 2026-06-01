# Lean Time-Horizon Benchmark

This repository contains a v0.1 Lean-based time-horizon evaluation artifact for measuring realistic formalization and verification work. It is no longer treated as a raw candidate pool: task status is explicit in metadata, reports, and generated CSVs.

Current v0.1 state:

- 6 accepted core tasks
- 8 calibration-only tasks
- 12 rejected archive tasks retained for auditability
- dev/test split recorded in task metadata and public export
- Lean 4.28.0 via `lean-toolchain`

The accepted core set is intentionally smaller than the original target of 20. The original pool was downgraded because many rows were too automation-dominated or duplicated the same short proof pattern. v0.1 favors diagnostic value over task count.

## Validate

Run the local acceptance gate from the repo root:

```powershell
lake build
python scripts/validate_all.py
python scripts/audit_difficulty.py
python scripts/generate_task_quality_matrix.py
python scripts/audit_diagnostic_coverage.py
python scripts/audit_human_time_calibration.py
python scripts/record_local_qa_results.py
python scripts/audit_pin_coverage.py
python scripts/audit_run_integrity.py
python scripts/audit_grader_hardening.py
python scripts/generate_evaluation_protocol.py
python scripts/analyze_model_results.py
python scripts/generate_report.py
python scripts/audit_statistical_reporting.py
python scripts/audit_provider_readiness.py
python scripts/generate_report.py
python scripts/export_public_tasks.py --out public_tasks
python scripts/validate_public_export.py --out public_tasks
python scripts/audit_hosted_qa_readiness.py
python scripts/generate_task_asset_manifest.py --public-export public_tasks
python scripts/audit_prompt_contracts.py
python scripts/audit_scaffold_support.py
python scripts/audit_requirement_coverage.py --public-export public_tasks
python scripts/audit_claim_evidence.py
python scripts/generate_release_decision_log.py
python scripts/generate_freeze_readiness_roadmap.py
python scripts/audit_scaffold_support.py
python scripts/audit_requirement_coverage.py --public-export public_tasks
python scripts/audit_claim_evidence.py
python scripts/generate_release_decision_log.py
python scripts/generate_freeze_readiness_roadmap.py
python scripts/audit_scaffold_support.py
python scripts/audit_requirement_coverage.py --public-export public_tasks
python scripts/audit_claim_evidence.py
python scripts/generate_release_decision_log.py
python scripts/generate_freeze_readiness_roadmap.py
python scripts/write_validation_manifest.py --public-export public_tasks
python scripts/generate_report.py
```

`validate_all.py` checks every tracked task by compiling the hidden reference, scanning forbidden constructs, compiling hidden semantic pins, auditing axioms, and confirming wrong submissions fail. Accepted and calibration-only tasks must have at least two wrong submissions.

Run one task manually:

```powershell
python scripts/validate_task.py tasks/test/lt-206-partition-count-correctness --submission tasks/test/lt-206-partition-count-correctness/hidden/Reference.lean --expect pass
```

## Task Statuses

Task status is stored in each `metadata.json`:

- `accepted_v0`: core benchmark task
- `calibration_only`: release task used for T0/T1 calibration and harness smoke checks
- `candidate_review_pending`: generated but not accepted
- `rejected_too_easy`, `rejected_invalid`, `rejected_duplicate`, `rejected_grader_weak`: retained archive rows

Rejected and calibration tasks are not counted as accepted benchmark performance rows in `reports/metr_style_report.md`.

## Task Layout

Each validated task has:

- `Prompt.md`
- all public Lean files listed in metadata `public_files`
- `metadata.json`
- `hidden/Reference.lean`
- `hidden/PinCheck.lean`
- `wrong/*.lean`

The multi-file cache task demonstrates public multi-file support with `Model.lean` plus `Task.lean`.

## Grading

The grader is Lean-first:

1. copy all metadata-listed public files into a clean temporary task directory
2. replace the submission file
3. scan source for forbidden constructs with comments and strings stripped
4. compile public Lean files
5. compile hidden semantic pins against submitted declarations
6. audit axioms used by declared targets

The axiom policy is documented in `docs/axiom_policy.md`.

## Scaffold Variants

Supported scaffold names are listed in `data/scaffold_variants.csv`:

- `one-shot`
- `lookup`
- `lookup_unlimited`

Lookup is a real read-only helper:

```powershell
python scripts/lean_lookup.py "Set.image"
```

Model runners receive `LEAN_LOOKUP_COMMAND`, `TASK_PUBLIC_DIR`, and `TASK_PUBLIC_FILES` in the environment.

## Model Runs

Do not fake results. Local QA rows are validation evidence, not model performance.
`record_local_qa_results.py` writes deterministic local QA transcripts with ephemeral temporary paths scrubbed so repeated local regeneration does not create meaningless transcript churn.

Run a local reference sweep:

```powershell
python scripts/run_model_sweep.py --provider local_reference --model lean-reference --scaffold one-shot --split dev --attempts 1 --acceptance-status accepted_v0
```

For real model runs, configure an external runner command. Example:

```powershell
$env:ANTHROPIC_LEAN_RUNNER = "python scripts/anthropic_runner.py"
$env:ANTHROPIC_MAX_TOKENS = "4096"
python scripts/run_model_sweep.py --provider anthropic --model claude-sonnet-4-6 --scaffold one-shot --task-id lt-201 --attempts 1
```

API keys stay in environment variables such as `ANTHROPIC_API_KEY`; do not commit secrets. `scripts/anthropic_runner.py` is a minimal adapter for smoke sweeps.

## Public Export

Create a public-only task bundle:

```powershell
python scripts/export_public_tasks.py --out public_tasks
python scripts/validate_public_export.py --out public_tasks
```

By default, the export includes `accepted_v0`, `calibration_only`, and any `candidate_review_pending` tasks. It excludes hidden references and wrong submissions, copies every metadata-listed public file, and validates exported Lean compilation.

## Reports And Data

Regenerated outputs:

- `data/task_metadata.csv`
- `data/validation_commands.csv`
- `data/run_results.csv`
- `data/benchmark_requirements.csv`
- `data/difficulty_audit.csv`
- `data/task_quality_matrix.csv`
- `data/diagnostic_coverage_audit.csv`
- `data/human_time_observations.csv`
- `data/human_time_observations_schema.json`
- `data/human_time_calibration_audit.csv`
- `data/task_asset_manifest.csv`
- `data/prompt_contract_audit.csv`
- `data/pin_coverage_audit.csv`
- `data/run_integrity_audit.csv`
- `data/grader_hardening_audit.csv`
- `data/claim_evidence_audit.csv`
- `data/release_decision_log.csv`
- `data/freeze_readiness_roadmap.csv`
- `data/scaffold_support_audit.csv`
- `data/model_sweep_plan.csv`
- `data/model_result_summary.csv`
- `data/statistical_reporting_audit.csv`
- `data/provider_readiness_audit.csv`
- `data/hosted_qa_readiness_audit.csv`
- `data/requirement_coverage.csv`
- `reports/difficulty_audit.md`
- `reports/task_quality_matrix.md`
- `reports/diagnostic_coverage_audit.md`
- `reports/human_time_calibration_audit.md`
- `reports/task_asset_manifest.md`
- `reports/prompt_contract_audit.md`
- `reports/pin_coverage_audit.md`
- `reports/run_integrity_audit.md`
- `reports/grader_hardening_audit.md`
- `reports/claim_evidence_audit.md`
- `reports/release_decision_log.md`
- `reports/freeze_readiness_roadmap.md`
- `reports/scaffold_support_audit.md`
- `reports/accepted_task_review.md`
- `reports/evaluation_protocol.md`
- `reports/model_run_analysis.md`
- `reports/statistical_reporting_audit.md`
- `reports/provider_readiness_audit.md`
- `reports/hosted_qa_readiness_audit.md`
- `reports/requirement_coverage.md`
- `reports/validation_manifest.json`
- `reports/metr_style_report.md`
- `reports/figures/*.svg`

`reports/metr_style_report.md` is the main METR-style review memo. `reports/accepted_task_review.md` is the stricter per-task reviewer audit for the v0.1 accepted set. `reports/task_quality_matrix.md` is a generated one-row-per-task quality ledger that joins metadata and difficulty-audit fields for reviewer inspection. `reports/diagnostic_coverage_audit.md` maps accepted tasks to playbook families, diagnostic capabilities, failure labels, automation caveats, and construct-validity gaps. `reports/human_time_calibration_audit.md` checks p50/p90 bucket consistency and records that accepted tasks still lack independent timing observations. `reports/task_asset_manifest.md` records per-task public, hidden, and wrong asset hashes plus public-export mapping without copying hidden proof contents into the report. `reports/prompt_contract_audit.md` checks release prompts for edit scope, theorem/import policy, helper-lemma policy, forbidden-construct disclosure, runner-supplied scaffold fields, and hidden-material leak patterns. `reports/pin_coverage_audit.md` distinguishes public-stage wrong failures from wrong submissions that actually reach hidden pins and records whether same-signature hidden wrongs are feasible for the task surface. `reports/run_integrity_audit.md` checks committed run rows against transcripts, score vectors, failure labels, and metadata. `reports/grader_hardening_audit.md` probes forbidden-construct scanning, task-specific bans, grader stage ordering, axiom allowlist consistency, validation-command coverage, and local QA reference/wrong outcomes. `reports/statistical_reporting_audit.md` records which recommended performance plots and claims are blocked by current provider sample sizes. `reports/provider_readiness_audit.md` checks model-runner contracts, provider adapter surface, credential policy, transcript evidence, planned sweep commands, and smoke-only provider coverage limits without using API keys. `reports/hosted_qa_readiness_audit.md` records that local validation and public export are ready while Taiga packaging, hosted problem-version evidence, Full Env QA, Env Linter rows, and finding dispositions are still missing. `reports/claim_evidence_audit.md` maps report claims to evidence and marks unsupported overclaims explicitly. `reports/release_decision_log.md` turns the evidence audits into explicit pass/caution/block gates for local release, report use, and blocked benchmark claims. `reports/freeze_readiness_roadmap.md` synthesizes the remaining blockers into measurable gates for locked-benchmark readiness. `reports/scaffold_support_audit.md` checks scaffold prompt contracts, runner attempt semantics, lookup safety, planned sweep coverage, and observed scaffold-data limits. `reports/evaluation_protocol.md` defines the planned primary model-sweep analysis before broad runs. `reports/model_run_analysis.md` summarizes committed provider rows against that plan without turning smoke rows into benchmark claims. `data/benchmark_requirements.csv` is the committed checklist used by `reports/requirement_coverage.md` for requirement-by-requirement evidence auditing. `reports/validation_manifest.json` records the local toolchain, regeneration commands, task/run counts, public-export summary, and artifact hashes for reproducibility. `reports/overnight_progress.md` records implementation checkpoints and blockers.
