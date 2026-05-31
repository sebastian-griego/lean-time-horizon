# Evaluation Protocol v0.1

This protocol defines how to turn the current local artifact into a defensible model-evaluation run. It does not claim that those model runs have happened. The current report remains a v0.1 audit artifact until the planned sweeps, independent timing review, and hosted QA are complete.

## Analysis Sets

- Primary analysis set: `accepted_v0` tasks only.
- Calibration set: `calibration_only` tasks, used for lower-bound checks and harness sanity, not headline capability claims.
- Excluded from capability claims: `rejected_*` tasks, infra-failure rows, local QA rows, and any task whose public export or hidden validation fails after the run.

Current primary set: `6` accepted tasks. Family counts: `{"algorithm_correctness": 1, "direct_theorem_proving": 1, "informal_spec_to_formal": 1, "invariant_verification_ml_optimization": 1, "proof_repair_codebase": 1, "small_formal_library_construction": 1}`. Human-time bucket counts: `{"T2": 5, "T3": 1}`.

Current calibration set: `8` tasks.

## Scaffold Ladder

| scaffold | lookup | iterative compile feedback | submission limit per attempt | description |
| --- | --- | --- | --- | --- |
| `one-shot` | false | false | 1 | One submission with no repository or API lookup beyond the prompt and public scaffold. |
| `lookup` | true | false | 1 | Read-only Lean/Std lookup is available before a single submission. |
| `lookup_unlimited` | true | true | unlimited | Read-only lookup plus iterative compile/debug submissions until timeout. |

The primary sweep plan is every accepted task crossed with every scaffold at `k=10`. `data/model_sweep_plan.csv` contains `18` planned rows: `{"lookup": 6, "lookup_unlimited": 6, "one-shot": 6}`.

## Primary Endpoint

The primary endpoint is task-level `pass_at_k` for `(task, model, scaffold, k)` rows:

- `successes_out_of_k` is the number of successful completed attempts in the row.
- `pass_at_k` is binary: `1.0` if `successes_out_of_k > 0`, else `0.0`.
- `attempts_completed` must equal `k` for ordinary pass@k rows unless the row is explicitly marked as an infra failure or aborted QA row.
- Local QA rows validate graders and wrong submissions; they are excluded from model capability summaries.

The runner now treats `--attempts 10` as `10` independent attempts for `one-shot` and `lookup`. Only `lookup_unlimited` carries grader feedback from a failed attempt into the next attempt.

## Secondary Analyses

Report these only after the primary sweep exists:

- mean `pass_at_k` by scaffold over accepted tasks;
- mean `pass_at_k` by human-time bucket;
- mean `pass_at_k` by task family and required skill, when group sizes are large enough to state the denominator clearly;
- scaffold deltas for the same task set, especially `lookup - one-shot` and `lookup_unlimited - lookup`;
- timeout and infra-failure rates by scaffold/provider;
- primary failure-label counts by scaffold and task family.

Calibration rows may be reported separately to identify lower-bound behavior, but they must not be mixed into accepted-core pass-rate claims.

## Statistical Reporting

All estimates are task-row descriptive statistics until the benchmark has enough accepted tasks and independent timing review.

- Always report numerators and denominators, not just percentages.
- For binary task-row means, report Wilson 95% intervals when shown in tables.
- For family, bucket, or skill summaries, avoid interpreting groups with fewer than five accepted tasks as stable estimates.
- Do not tune task inclusion on test-set model results except to remove broken or invalid tasks with documented reasons.
- Infra-failure rows are retained in `data/run_results.csv`, counted in reliability summaries, and excluded from capability means.

## Failure Labeling Protocol

Each failed model row gets one primary label and optional secondary labels after transcript review. Use `data/failure_label_schema.json` for row shape and the following codebook:

- `none`
- `library_search`
- `premise_selection`
- `theorem_decomposition`
- `semantic_formalization`
- `hidden_pin_failure`
- `proof_debugging`
- `codebase_navigation`
- `invariant_design`
- `termination`
- `timeout`
- `reward_hack_attempt`
- `grader_false_negative`
- `infra_failure`

Labeling order:

1. Mark `infra_failure`, `timeout`, or `reward_hack_attempt` first when applicable.
2. If public Lean compilation passes but hidden pins fail, use `hidden_pin_failure` unless the transcript clearly shows a more specific semantic-formalization error.
3. Prefer `library_search` for missing API names, `premise_selection` for wrong available lemmas, and `theorem_decomposition` for failures to create viable intermediate goals.
4. Use `proof_debugging` for close Lean proofs with unresolved tactic/type errors.
5. Use `grader_false_negative` only after manual inspection shows the submitted solution is valid and the grader is wrong.

## Human-Time Calibration

Before freeze, each accepted task should receive independent timing evidence from at least one competent Lean user who did not author the task. Record:

- solver background;
- elapsed minutes to first accepted solution;
- whether lookup or compile/debug feedback was used;
- whether the prompt was ambiguous;
- any reason the metadata p50/p90 estimate should change.

Do not infer human time from model pass rates.

## Hosted QA And Freeze Criteria

Before claiming a locked benchmark:

1. Run the local regeneration gate from `README.md`.
2. Export and validate `public_tasks`.
3. Run the primary model-sweep plan or explicitly mark it as deferred.
4. Run hosted Taiga/Full Env QA and Env Linter on the exact intended public task versions.
5. Record hosted QA findings, fixes, and rebuttals in committed artifacts.
6. Freeze task versions only after warning/error/critical QA findings are fixed or rebutted.

## Planned Sweep Commands

Replace `MODEL` and `LEAN_MODEL_RUNNER` with the provider/model adapter under test. API keys must stay in environment variables and must not be committed.

```powershell
$env:LEAN_MODEL_RUNNER = "python scripts/your_runner.py"
python scripts/run_model_sweep.py --provider command --model MODEL --scaffold one-shot --attempts 10 --acceptance-status accepted_v0
```

```powershell
$env:LEAN_MODEL_RUNNER = "python scripts/your_runner.py"
python scripts/run_model_sweep.py --provider command --model MODEL --scaffold lookup --attempts 10 --acceptance-status accepted_v0
```

```powershell
$env:LEAN_MODEL_RUNNER = "python scripts/your_runner.py"
python scripts/run_model_sweep.py --provider command --model MODEL --scaffold lookup_unlimited --attempts 10 --acceptance-status accepted_v0
```
