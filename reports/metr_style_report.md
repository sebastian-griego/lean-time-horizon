# Lean Time-Horizon Benchmark v0.1 Report

## Abstract

This repository is a v0.1 Lean time-horizon evaluation artifact for studying how far models get on realistic formalization and verification tasks as task horizon increases. It is not a locked benchmark. The release set contains 6 accepted core tasks and 8 calibration-only tasks. The remaining 12 tasks are retained as a rejected archive, and 0 tasks remain pending review.

The accepted core set is intentionally smaller than the original target of 20. The original task batch was downgraded because many rows were dominated by `rfl`, `simp`, `omega`, `cases`, or one obvious library lemma. A stricter accepted-task review is maintained in `reports/accepted_task_review.md`; v0.1 keeps downgraded rows out of benchmark statistics unless they serve a calibration role.

## Research Questions

This artifact is designed to support three narrow evaluation questions:

1. Can a model recover the intended Lean proof or formalization from a public prompt and scaffold?
2. Which failures are diagnostic of time-horizon bottlenecks such as semantic formalization, theorem decomposition, proof debugging, codebase navigation, invariant design, or library/API search?
3. How much do scaffold affordances change outcomes, especially lookup and iterative compile/debug attempts?

The artifact is not yet suitable for population-level claims about frontier-model capability. It has limited task count, author-estimated human times, and only tiny smoke-model evidence.

## Unit Of Analysis And Scoring

The unit of analysis is a `(task, model, scaffold, k)` row. A task attempt is scored as pass only if the submitted Lean file:

- passes forbidden-construct scanning;
- compiles with the public scaffold files;
- compiles hidden `PinCheck.lean` against the submitted declarations;
- passes axiom audit on the metadata-listed declarations.

`successes_out_of_k` is the number of successful attempts among the allowed attempts for that row. `pass_at_k` is binary for that task row: `1.0` if any attempt succeeds and `0.0` otherwise. Local QA rows for reference solutions and wrong submissions are validation evidence, not model performance.

## Task Selection Protocol

Task status is assigned by metadata, not by directory alone:

- `accepted_v0`: core task retained after manual review and local validation.
- `calibration_only`: release task retained for lower-bound calibration, harness checks, or simple semantic-pin regression tests.
- `rejected_*`: archived task retained for auditability but excluded from release claims.
- `candidate_review_pending`: generated task not yet accepted.

Acceptance requires more than a passing reference solution: wrong submissions must fail, hidden checks must test meaningful behavior where possible, metadata must include human-time and diagnostic fields, and the accepted-task review must document known limitations. Tasks can be downgraded after review even when they validate.

## Accepted v0.1 Core Task Set

| task | split | family | bucket | p50/p90 | diagnostic role |
| --- | --- | --- | --- | ---: | --- |
| `lt-201` | dev | proof_repair_codebase | T2 | 75/150 | accepted_v0_keep_with_caveat: reference proof is automation-dominated, but the task is retained for multi-file navigation, fixed API semantics, and generalized batch repair; needs independent review before any locked benchmark claim. |
| `lt-203` | dev | informal_spec_to_formal | T2 | 90/180 | accepted_v0: spec-to-formal task with hidden pins rejecting vacuous, equality-only, and duplicate-sensitive interpretations. |
| `lt-202` | test | direct_theorem_proving | T2 | 90/180 | accepted_v0_keep_with_caveat: Mathlib-adjacent theorem package requiring image/preimage API lookup, premise selection, and witness decomposition; hidden checks mostly protect fixed theorem signatures rather than semantic formalization choices. |
| `lt-204` | test | invariant_verification_ml_optimization | T2 | 100/200 | accepted_v0: optimizer-style invariant package with helper lemmas for cap bounds, list preservation, and sum monotonicity. |
| `lt-205` | test | small_formal_library_construction | T3 | 150/300 | accepted_v0: T3 small library construction with dependent count lemmas and downstream BagEq reuse; expected to be hard one-shot. |
| `lt-206` | test | algorithm_correctness | T2 | 100/210 | accepted_v0_keep_with_caveat: reference proof uses substantial simp/omega automation, but the task is retained for the multi-lemma partition invariant, side predicates, and duplicate-sensitive count preservation; needs independent review before any locked benchmark claim. |

## Accepted Core Evidence Matrix

| task | proof lines | automation dominated | hidden pins | wrongs | one-shot estimate | diagnostic value |
| --- | ---: | --- | --- | ---: | --- | --- |
| `lt-201` | 25 | true | semantic | 2 | maybe | high |
| `lt-203` | 30 | false | semantic | 2 | maybe | high |
| `lt-202` | 46 | false | mixed | 2 | maybe | medium_high |
| `lt-204` | 36 | false | semantic | 2 | maybe | high |
| `lt-205` | 42 | false | semantic | 2 | unlikely | high |
| `lt-206` | 60 | true | semantic | 2 | maybe | high |

## Calibration-Only Release Tasks

| task | split | family | bucket | p50/p90 | diagnostic role |
| --- | --- | --- | --- | ---: | --- |
| `lt-001` | dev | algorithm_correctness | T1 | 25/45 | calibration_only: T1 list induction smoke row; retained to verify harness behavior, not counted as core benchmark difficulty. |
| `lt-002` | dev | algorithm_correctness | T1 | 20/40 | calibration_only: T1 Bool/list induction row; useful for lower-bound calibration and wrong-definition pins. |
| `lt-003` | dev | proof_repair_codebase | T1 | 35/60 | calibration_only: small proof-repair shape retained as a codebase-navigation smoke row; too short for core benchmark status. |
| `lt-004` | dev | informal_spec_to_formal | T1 | 30/55 | calibration_only: compact semantic-formalization row retained to test vacuity and endpoint-only wrong specs. |
| `lt-101` | test | algorithm_correctness | T1 | 35/70 | calibration_only: tail-recursive accumulator proof retained as a T1 calibration row; not core long-horizon material. |
| `lt-105` | test | proof_repair_codebase | T1 | 40/80 | calibration_only: same-signature semantic wrongs are useful, but the reference proof is short and automation-dominated; T2/core status was too generous. |
| `lt-107` | test | informal_spec_to_formal | T1 | 35/70 | calibration_only: hidden pins catch vacuous and nonempty-only specs, but the formalization surface is too compact for accepted core status. |
| `lt-108` | test | informal_spec_to_formal | T1 | 40/80 | calibration_only: good semantic pins for dropped-tail and first-pair-only definitions, but the proof surface is too small for core benchmark status. |

## Calibration Evidence Matrix

| task | proof lines | automation dominated | hidden pins | wrongs | one-shot estimate | diagnostic value |
| --- | ---: | --- | --- | ---: | --- | --- |
| `lt-001` | 8 | true | semantic | 2 | likely | medium |
| `lt-002` | 8 | true | semantic | 2 | likely | medium |
| `lt-003` | 11 | true | semantic | 2 | likely | medium |
| `lt-004` | 5 | false | semantic | 2 | likely | medium |
| `lt-101` | 11 | true | semantic | 2 | likely | medium |
| `lt-105` | 11 | true | semantic | 2 | likely | medium |
| `lt-107` | 10 | false | semantic | 2 | likely | medium |
| `lt-108` | 9 | false | semantic | 2 | likely | medium |

## Portfolio Counts

Acceptance status:

- `accepted_v0`: 6
- `calibration_only`: 8
- `rejected_duplicate`: 2
- `rejected_too_easy`: 10

Accepted core families:

- `algorithm_correctness`: 1
- `direct_theorem_proving`: 1
- `informal_spec_to_formal`: 1
- `invariant_verification_ml_optimization`: 1
- `proof_repair_codebase`: 1
- `small_formal_library_construction`: 1

Release human-time buckets:

- `T1`: 8
- `T2`: 5
- `T3`: 1

## What The Tasks Measure

The accepted core tasks are intended to test library/API search, theorem decomposition, semantic formalization, proof debugging, codebase navigation, invariant design, and small library construction. The calibration-only rows are retained to verify the harness, establish lower time-bucket behavior, and catch regressions in simple Lean proof generation.

Scaffold-sensitive tasks are marked in metadata. Lookup-sensitive rows include Mathlib image/preimage reasoning and semantic-list formalization. Iterative compile/debug sensitivity is expected for multi-file proof repair, invariant packages, and library-construction rows.

## Human-Time Estimates

Human-time buckets follow the project playbook:

- `T0`: 5-15 minutes.
- `T1`: 15-45 minutes.
- `T2`: 45-120 minutes.
- `T3`: 2-6 hours.
- `T4`: 6+ hours.

The p50/p90 estimates in metadata are reviewer estimates, not measured independent solves. The hard review downgraded three rows from accepted core to calibration-only because their proof surface and likely one-shot solvability did not justify accepted T2 status.

## Grader And Integrity Controls

The grader is Lean-first. For each submission it copies the public files listed in `metadata.json`, replaces the submission file, scans forbidden constructs, compiles public Lean files, compiles hidden semantic pins, and audits axioms on declared targets. Accepted and calibration tasks must have at least two wrong submissions.

Hidden pins check more than type signatures where possible: semantic formalization tasks include positive and negative examples; invariant tasks include edge cases and downstream bundled consequences; library tasks include downstream reuse through public lemmas. The grader still cannot prove that a task measures every intended cognitive skill, and it cannot replace human review of whether a task is too automation-dominated.

The axiom policy allows only the standard Lean axioms documented in `docs/axiom_policy.md`. Source-level escape hatches such as `sorry`, `admit`, `axiom`, `constant`, `unsafe`, custom elaboration, and command execution are rejected by the forbidden-construct scanner before Lean grading.

## Public Export

`scripts/export_public_tasks.py` exports the release set by default: `accepted_v0`, `calibration_only`, and pending candidates if any. It copies every file listed in metadata `public_files` plus `Prompt.md` and `metadata.json`. `scripts/validate_public_export.py` checks that hidden and wrong directories are absent, all public files are present, exported Lean files compile, and obvious hidden-reference path strings do not leak.

## Scaffold And Model-Run Support

The supported scaffold ladder is `one-shot`, `lookup`, and `lookup_unlimited`. Lookup is a real read-only command, `python scripts/lean_lookup.py QUERY`, which searches local Lean task files and installed Std/Mathlib files when available. External model runners receive `PROMPT_PATH`, `MODEL`, `TASK_ID`, `ATTEMPT_INDEX`, `SCAFFOLD`, `LEAN_LOOKUP_COMMAND`, `TASK_PUBLIC_DIR`, and `TASK_PUBLIC_FILES`.

## Committed Run Results

66 local QA rows are committed for reference solutions and plausible wrong submissions. These rows are not model performance and are excluded from benchmark pass-rate summaries.

Local QA row status:

- `expected_failure`: 40
- `passed`: 26

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

## Accepted Task Review

`reports/accepted_task_review.md` records the per-task reviewer judgment for every row that was marked `accepted_v0` at the start of the hardening pass. It explicitly distinguishes keep, downgrade, and keep-with-caveat recommendations; checks whether buckets are deserved; audits hidden pins and wrong submissions; and lists what must change before each task can be treated as benchmark-grade.

## Reproducibility Checklist

The intended local regeneration gate is:

```powershell
lake build
python scripts/validate_all.py
python scripts/audit_difficulty.py
python scripts/record_local_qa_results.py
python scripts/generate_report.py
python scripts/export_public_tasks.py --out public_tasks
python scripts/validate_public_export.py --out public_tasks
```

The public export validator checks that hidden references and wrong submissions are absent from `public_tasks`, all metadata-listed public files are present, exported Lean files compile, and obvious hidden-reference path strings do not leak.

## Threats To Validity

Construct validity:

- Lean success is a strong signal for formal correctness of fixed theorems, but it does not by itself prove that a task measures the intended cognitive capability.
- Hidden semantic pins are finite probes. They reject known vacuous or weakened formalizations but cannot exhaustively characterize semantic equivalence.
- Fixed-statement proof tasks cannot always have a same-signature wrong answer that compiles publicly and then fails hidden semantic pins; if the theorem statement and definitions are fixed, a compiled proof is already semantically decisive.

Internal validity:

- Difficulty labels rely on author/reviewer estimates and mechanical proof profiles, not independent human solves.
- Automation-dominated references can understate model difficulty if models fail earlier on decomposition or API search, but they can also overstate benchmark quality if retained without caveats.
- The tiny committed provider smoke sweep is insufficient for performance claims and includes an infra-failure row.

External validity:

- v0.1 has only 6 accepted core tasks and limited T3/T4 coverage.
- Most tasks are small Lean packages rather than large real-world formalization projects.
- Mathlib coverage is narrow.

Reliability and security:

- Validation is reproducible locally through committed scripts and CSVs, but hosted Taiga/Env Linter QA has not been run.
- API credentials are expected only through environment variables and are not part of the repo.

## Claim Ledger

| claim | current evidence | status |
| --- | --- | --- |
| Local references and wrong submissions validate as expected | `python scripts/validate_all.py`; `data/run_results.csv`; local QA transcripts | supported locally |
| Public task export excludes hidden material | `python scripts/export_public_tasks.py --out public_tasks`; `python scripts/validate_public_export.py --out public_tasks` | supported locally |
| Accepted core tasks are higher quality than the original pool | `reports/accepted_task_review.md`; `reports/difficulty_audit.md`; downgraded metadata statuses | supported by internal review |
| v0.1 is a locked benchmark | independent timing, hosted QA, broader model sweeps, and freeze review are missing | not supported |
| Reported model pass rates characterize frontier performance | only tiny smoke-sweep rows are committed | not supported |

## Limitations

- The v0.1 accepted core is below the 20-task target because the original pool did not meet the diagnostic-quality bar.
- The release has limited T3 coverage and no accepted T4 stretch task yet.
- Human-time estimates are author/reviewer estimates, not measured independent solves.
- Hidden pins are stronger than type checks, but they remain finite semantic probes.
- Only a tiny real provider smoke sweep is committed; it is adapter/proof-debugging evidence, not a benchmark performance claim.
- Hosted Taiga/Env Linter QA is not represented in this local artifact.
- The artifact is not a locked benchmark. The accepted rows still need independent human timing, broader scaffold data, and external QA before a freeze.

## Before Claiming A Locked Benchmark

The next step is to add more high-quality T2/T3/T4 tasks, run independent human review, execute real provider smoke sweeps across the scaffold ladder, run hosted QA, settle linter findings, and freeze exact public task versions.
