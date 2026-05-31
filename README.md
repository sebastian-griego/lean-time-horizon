# Lean Time-Horizon Benchmark

This repo contains a Lean-based evaluation benchmark for measuring how far models get on realistic formalization and verification tasks as task horizon increases.

The accepted batch has 20 tasks:

- 5 dev tasks in `tasks/dev`
- 15 test tasks in `tasks/test`
- task families covering algorithm correctness, proof repair, informal-spec formalization, invariant verification, small library construction, and direct theorem proving

The project is pinned to Lean 4.28.0 in `lean-toolchain`.

## Validate

Run the full local acceptance gate:

```powershell
python scripts/validate_all.py
```

This checks every accepted task by:

- compiling the hidden reference solution
- scanning forbidden constructs
- compiling hidden semantic pins
- auditing axioms
- confirming at least one plausible wrong solution fails
- regenerating `data/task_metadata.csv`

Run one task manually:

```powershell
python scripts/validate_task.py tasks/test/lt-111-clip-interval-invariant --submission path\to\Task.lean --expect pass
```

## Task Layout

Each accepted task has:

- `Prompt.md`: public instructions
- `Task.lean`: public scaffold
- `metadata.json`: task metadata
- `hidden/Reference.lean`: hidden reference solution
- `hidden/PinCheck.lean`: hidden semantic checks
- `wrong/*.lean`: plausible wrong submissions that must fail

Candidate and discarded tasks are separated under `tasks/candidates` and `tasks/discarded`. Rejected design candidates are tracked in `data/discarded_candidates.csv`.

## Scoring

The grader is Lean-first:

1. copy the submitted Lean file into a clean temporary directory
2. scan source for forbidden constructs with comments and strings stripped
3. compile `Task.lean`
4. compile hidden `PinCheck.lean`
5. audit axioms used by submitted declarations

The axiom policy is documented in `docs/axiom_policy.md`.

## Scaffold Variants

Supported scaffold names are listed in `data/scaffold_variants.csv`:

- `one-shot`
- `lookup`
- `lookup_unlimited`

Run a local reference sweep:

```powershell
python scripts/run_model_sweep.py --provider local_reference --model lean-reference --scaffold one-shot --split dev --attempts 1
```

For real model runs, configure an external runner command. Example:

```powershell
$env:OPENAI_LEAN_RUNNER = "python path/to/openai_runner.py"
python scripts/run_model_sweep.py --provider openai --model your-model --scaffold lookup_unlimited --split test --attempts 10
```

The external command receives `PROMPT_PATH`, `MODEL`, `TASK_ID`, and `ATTEMPT_INDEX` in the environment and must print a complete `Task.lean` file to stdout. API keys should stay in environment variables such as `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GEMINI_API_KEY`; do not commit secrets.

## Transcripts And Labels

Model sweeps write JSONL transcripts under `transcripts/<job_id>/`.

Failure labels are defined in:

- `data/failure_labels.csv`
- `data/failure_label_schema.json`
- `data/failure_annotations.csv`

Use one primary label per failed run.

## Regenerate Data And Report

Record local QA result rows:

```powershell
python scripts/record_local_qa_results.py
```

Regenerate plots and report:

```powershell
python scripts/generate_report.py
```

Outputs:

- `data/task_metadata.csv`
- `data/validation_commands.csv`
- `data/run_results.csv`
- `reports/metr_style_report.md`
- `reports/figures/*.svg`

Committed local QA rows are not frontier-model results. Real model pass@10 rows should be generated with `scripts/run_model_sweep.py` and reviewed before being used as benchmark claims.

## Public Export

To create a public-only task bundle without hidden references:

```powershell
python scripts/export_public_tasks.py --out public_tasks
```

The export includes only `Prompt.md`, `Task.lean`, and `metadata.json`.
