# Lean Time-Horizon Benchmark Report

## Summary

This repository contains 20 accepted Lean tasks for evaluating how far models get on realistic formalization and verification work as task horizon increases.

The split is:

- `dev`: 5
- `test`: 15

Task families:

- `algorithm_correctness`: 5
- `direct_theorem_proving`: 1
- `informal_spec_to_formal`: 4
- `invariant_verification_ml_optimization`: 4
- `proof_repair_codebase`: 3
- `small_formal_library_construction`: 3

Human-time buckets:

- `T1`: 15
- `T2`: 5

## Task Portfolio

The task set intentionally mixes algorithm correctness, proof repair, semantic formalization, invariant verification, small formal library construction, and a small direct theorem-proving slice. The benchmark is not designed as an olympiad theorem-proving set.

The current accepted set is Lean/Std-only and pinned to Lean 4.28.0. This keeps clean-checkout validation fast and reduces dependency drift, at the cost of excluding Mathlib-heavy domains from this first batch.

## Grading

Each accepted task has:

- a public prompt and public `Task.lean`
- hidden reference solution and hidden semantic pins
- at least one plausible wrong submission
- metadata with split, family, domain, human-time estimate, skills, scaffold sensitivity, and expected failures
- local validation through `scripts/validate_task.py`

The grader scans forbidden constructs before Lean runs, compiles the submitted task, compiles hidden pins against the submitted declarations, and audits axioms. The allowed axiom policy is documented in `docs/axiom_policy.md`.

## Scaffold Variants

The supported scaffold ladder is:

- `one-shot`: one submission, no lookup
- `lookup`: one submission with read-only Lean/Std lookup available
- `lookup_unlimited`: lookup plus iterative compile/debug attempts

`scripts/run_model_sweep.py` implements the scaffold loop and transcript/result writing. Provider-specific API calls are intentionally delegated to environment-configured commands so API keys remain outside the repo.

## Committed Results

Committed run-result rows currently summarize local QA or explicitly run sweeps only. They are not presented as frontier-model performance unless a real provider sweep has been run and committed.

- `one-shot`: mean score 0.50 over 40 committed rows, CI proxy 0.15

## Figures

- `reports/figures/task_counts_by_family.svg`
- `reports/figures/task_counts_by_bucket.svg`
- `reports/figures/task_minutes_by_bucket.svg`
- `reports/figures/top_skills.svg`
- `reports/figures/run_rows_by_model.svg` when run-result rows exist

## Failure Taxonomy

Failures should be labeled with one primary label from `data/failure_labels.csv`. The most important expected labels for this batch are semantic formalization, hidden pin failure, proof debugging, library search, codebase navigation, invariant design, and theorem decomposition.

## Limitations

- No expensive frontier-model pass@10 sweep is committed by default. The repo includes the runner and schema; users can run real sweeps with environment-provided model commands.
- Hosted Taiga/Env Linter QA is not represented in this local artifact. The local gate enforces the playbook acceptance checklist, but hosted QA would still be required before platform delivery.
- Human-time estimates are author estimates with confidence notes, not second-reviewer measured times.
- The first accepted batch uses Lean/Std only. A future Mathlib batch should add richer algebra, analysis, and real verification codebases.

## Next Batch

The next increment should add Mathlib-backed tasks, at least one T3 codebase repair package, and real pass@10 model results across the three scaffold variants.
