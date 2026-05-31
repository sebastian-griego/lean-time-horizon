# Lean Time-Horizon Benchmark v0.1 Report

## Executive Summary

This repository is now organized as a v0.1 Lean time-horizon evaluation artifact rather than a raw candidate pool. The release set contains 9 accepted core tasks and 5 calibration-only tasks. The remaining 12 tasks are retained as a rejected archive, and 0 tasks remain pending review.

The accepted core set is intentionally smaller than the original target of 20. The original task batch was downgraded because many rows were dominated by `rfl`, `simp`, `omega`, `cases`, or one obvious library lemma. v0.1 keeps those rows out of benchmark statistics unless they serve a calibration role.

## Accepted v0.1 Core Task Set

| task | split | family | bucket | p50/p90 | diagnostic role |
| --- | --- | --- | --- | ---: | --- |
| `lt-201` | dev | proof_repair_codebase | T2 | 75/150 | accepted_v0: multi-file cache repair requires preserving Model.lean API semantics and proving batch count lemmas. |
| `lt-203` | dev | informal_spec_to_formal | T2 | 90/180 | accepted_v0: spec-to-formal task with hidden pins rejecting vacuous, equality-only, and duplicate-sensitive interpretations. |
| `lt-105` | test | proof_repair_codebase | T2 | 55/110 | accepted_v0: lower-end T2 proof-repair task requiring generalized induction over a batched API and sum accounting; strengthened with semantic pins. |
| `lt-107` | test | informal_spec_to_formal | T2 | 50/100 | accepted_v0: semantic formalization task where vacuous and nonempty-only specifications pass superficial lemmas but fail hidden pins. |
| `lt-108` | test | informal_spec_to_formal | T2 | 60/120 | accepted_v0: recursive predicate formalization with hidden pins for dropped tail invariants and first-pair-only specifications. |
| `lt-202` | test | direct_theorem_proving | T2 | 90/180 | accepted_v0: Mathlib-adjacent theorem package requiring image/preimage API lookup, premise selection, and witness decomposition. |
| `lt-204` | test | invariant_verification_ml_optimization | T2 | 100/200 | accepted_v0: optimizer-style invariant package with helper lemmas for cap bounds, list preservation, and sum monotonicity. |
| `lt-205` | test | small_formal_library_construction | T3 | 150/300 | accepted_v0: T3 small library construction with dependent count lemmas and downstream BagEq reuse; expected to be hard one-shot. |
| `lt-206` | test | algorithm_correctness | T2 | 100/210 | accepted_v0: algorithm-correctness package with side predicates, length, and duplicate-sensitive count preservation. |

## Calibration-Only Release Tasks

| task | split | family | bucket | p50/p90 | diagnostic role |
| --- | --- | --- | --- | ---: | --- |
| `lt-001` | dev | algorithm_correctness | T1 | 25/45 | calibration_only: T1 list induction smoke row; retained to verify harness behavior, not counted as core benchmark difficulty. |
| `lt-002` | dev | algorithm_correctness | T1 | 20/40 | calibration_only: T1 Bool/list induction row; useful for lower-bound calibration and wrong-definition pins. |
| `lt-003` | dev | proof_repair_codebase | T1 | 35/60 | calibration_only: small proof-repair shape retained as a codebase-navigation smoke row; too short for core benchmark status. |
| `lt-004` | dev | informal_spec_to_formal | T1 | 30/55 | calibration_only: compact semantic-formalization row retained to test vacuity and endpoint-only wrong specs. |
| `lt-101` | test | algorithm_correctness | T1 | 35/70 | calibration_only: tail-recursive accumulator proof retained as a T1 calibration row; not core long-horizon material. |

## Portfolio Counts

Acceptance status:

- `accepted_v0`: 9
- `calibration_only`: 5
- `rejected_duplicate`: 2
- `rejected_too_easy`: 10

Accepted core families:

- `algorithm_correctness`: 1
- `direct_theorem_proving`: 1
- `informal_spec_to_formal`: 3
- `invariant_verification_ml_optimization`: 1
- `proof_repair_codebase`: 2
- `small_formal_library_construction`: 1

Release human-time buckets:

- `T1`: 5
- `T2`: 8
- `T3`: 1

## What The Tasks Measure

The accepted core tasks are intended to test library/API search, theorem decomposition, semantic formalization, proof debugging, codebase navigation, invariant design, and small library construction. The calibration-only rows are retained to verify the harness, establish lower time-bucket behavior, and catch regressions in simple Lean proof generation.

Scaffold-sensitive tasks are marked in metadata. Lookup-sensitive rows include Mathlib image/preimage reasoning and semantic-list formalization. Iterative compile/debug sensitivity is expected for multi-file proof repair, invariant packages, and library-construction rows.

## Grader And Integrity Controls

The grader is Lean-first. For each submission it copies the public files listed in `metadata.json`, replaces the submission file, scans forbidden constructs, compiles public Lean files, compiles hidden semantic pins, and audits axioms on declared targets. Accepted and calibration tasks must have at least two wrong submissions.

Hidden pins check more than type signatures where possible: semantic formalization tasks include positive and negative examples; invariant tasks include edge cases and downstream bundled consequences; library tasks include downstream reuse through public lemmas. The grader still cannot prove that a task measures every intended cognitive skill, and it cannot replace human review of whether a task is too automation-dominated.

## Public Export

`scripts/export_public_tasks.py` exports the release set by default: `accepted_v0`, `calibration_only`, and pending candidates if any. It copies every file listed in metadata `public_files` plus `Prompt.md` and `metadata.json`. `scripts/validate_public_export.py` checks that hidden and wrong directories are absent, all public files are present, exported Lean files compile, and obvious hidden-reference path strings do not leak.

## Scaffold And Model-Run Support

The supported scaffold ladder is `one-shot`, `lookup`, and `lookup_unlimited`. Lookup is a real read-only command, `python scripts/lean_lookup.py QUERY`, which searches local Lean task files and installed Std/Mathlib files when available. External model runners receive `PROMPT_PATH`, `MODEL`, `TASK_ID`, `ATTEMPT_INDEX`, `SCAFFOLD`, `LEAN_LOOKUP_COMMAND`, `TASK_PUBLIC_DIR`, and `TASK_PUBLIC_FILES`.

## Committed Run Results

66 local QA rows are committed for reference solutions and plausible wrong submissions. These rows are not model performance and are excluded from benchmark pass-rate summaries.

Real model-sweep rows:

- `one-shot`: pass@k mean 0.50 over 2 task rows, CI proxy 0.69

| task | provider | model | scaffold | k | pass@k | failure | transcript |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| `lt-001` | anthropic | claude-sonnet-4-6 | one-shot | 1 | 1.0 | none | `transcripts/anthropic-claude-sonnet-4-6-one-shot-1780206109/lt-001.jsonl` |
| `lt-201` | anthropic | claude-sonnet-4-6 | one-shot | 1 | 0.0 | infra_failure | `transcripts/anthropic-claude-sonnet-4-6-one-shot-1780206126/lt-201.jsonl` |
| `lt-201` | anthropic | claude-sonnet-4-6 | one-shot | 1 | 0.0 | proof_debugging | `transcripts/anthropic-claude-sonnet-4-6-one-shot-1780206167/lt-201.jsonl` |

Model-sweep infra failures: 1. Infra-failure rows are retained in `data/run_results.csv` and transcripts, but excluded from pass-rate summaries.

No provider API credentials or runner commands are committed. To run a real smoke sweep, configure one of `OPENAI_LEAN_RUNNER`, `ANTHROPIC_LEAN_RUNNER`, `GEMINI_LEAN_RUNNER`, or `LEAN_MODEL_RUNNER` and use `scripts/run_model_sweep.py`.

Observed model-sweep failure labels:

- `infra_failure`: 1
- `proof_debugging`: 1

## Difficulty Audit Summary

The regenerated difficulty audit separates mechanical signals from manual judgments. Mechanical signals include reference proof lines, declaration count, public file count, public lemma count, tactic profile, automation dominance, Mathlib use, multi-file context, hidden pin strength, and wrong-submission count. Manual fields include frontier one-shot solvability estimates, p50/p90 human time, scaffold sensitivity, diagnostic value, and final accept/reject rationale.

## Limitations

- The v0.1 accepted core is below the 20-task target because the original pool did not meet the diagnostic-quality bar.
- The release has limited T3 coverage and no accepted T4 stretch task yet.
- Human-time estimates are author/reviewer estimates, not measured independent solves.
- Hidden pins are stronger than type checks, but they remain finite semantic probes.
- Only a tiny real provider smoke sweep is committed; it is adapter/proof-debugging evidence, not a benchmark performance claim.
- Hosted Taiga/Env Linter QA is not represented in this local artifact.

## Before Claiming A Locked Benchmark

The next step is to add more high-quality T2/T3/T4 tasks, run independent human review, execute real provider smoke sweeps across the scaffold ladder, run hosted QA, settle linter findings, and freeze exact public task versions.
