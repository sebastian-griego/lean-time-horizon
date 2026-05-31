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
python scripts/record_local_qa_results.py
python scripts/generate_report.py
python scripts/export_public_tasks.py --out public_tasks
python scripts/validate_public_export.py --out public_tasks
python scripts/audit_requirement_coverage.py --public-export public_tasks
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
- `data/difficulty_audit.csv`
- `data/requirement_coverage.csv`
- `reports/difficulty_audit.md`
- `reports/accepted_task_review.md`
- `reports/requirement_coverage.md`
- `reports/validation_manifest.json`
- `reports/metr_style_report.md`
- `reports/figures/*.svg`

`reports/metr_style_report.md` is the main METR-style review memo. `reports/accepted_task_review.md` is the stricter per-task reviewer audit for the v0.1 accepted set. `reports/requirement_coverage.md` is a generated requirement-by-requirement evidence audit. `reports/validation_manifest.json` records the local toolchain, regeneration commands, task/run counts, public-export summary, and artifact hashes for reproducibility. `reports/overnight_progress.md` records implementation checkpoints and blockers.
