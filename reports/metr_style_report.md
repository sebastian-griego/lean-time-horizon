# Lean Time-Horizon Benchmark v0.1 Report

## Abstract

This repository is a v0.1 Lean time-horizon evaluation artifact for studying how far models get on realistic formalization and verification tasks as task horizon increases. It is not a locked benchmark. The release set contains 6 accepted core tasks and 8 calibration-only tasks. The remaining 12 tasks are retained as a rejected archive, and 0 tasks remain pending review.

The accepted core set has limited task count, author-estimated human times, and only tiny smoke-model evidence. The original task batch was downgraded because many rows were dominated by `rfl`, `simp`, `omega`, `cases`, or one obvious library lemma. v0.1 keeps downgraded rows out of benchmark statistics unless they serve a calibration role.

## Reader Guide

This is the main research report. It keeps the narrative, methods, claim boundaries, and blocker summary in one skimmable file. `reports/concise_metr_report.md` is the shortest reviewer-facing summary. `reports/evidence_appendix.md` is the generated evidence appendix with long audit tables, hashes, command lists, and row-level ledgers.

## Research Questions

1. Can a model recover the intended Lean proof or formalization from a public prompt and scaffold?
2. Which failures are diagnostic of time-horizon bottlenecks such as semantic formalization, theorem decomposition, proof debugging, codebase navigation, invariant design, or library/API search?
3. How much do scaffold affordances change outcomes, especially lookup and iterative compile/debug attempts?

The current artifact can support local task/grader validity review. It cannot yet answer the third question empirically because committed provider evidence covers only a tiny one-shot smoke sample.

## Unit Of Analysis And Scoring

The unit of analysis is a `(task, model, scaffold, k)` row. A task attempt is scored as pass only if the submitted Lean file passes forbidden-construct scanning, public Lean compilation, hidden `PinCheck.lean`, and axiom audit on the metadata-listed declarations.

`successes_out_of_k` is the number of successful attempts among the allowed attempts for that row. `pass_at_k` is binary for that task row: `1.0` if any attempt succeeds and `0.0` otherwise. Local QA rows for reference solutions and wrong submissions are validation evidence, not model performance.

## Data Schema Manifest

`reports/data_schema_manifest.md` and `data/data_schema_manifest.csv` validate schema-backed datasets and document where generated CSVs are governed by producer scripts rather than standalone JSON schemas.

- dataset rows: `8`
- validation statuses: `{"codebook_valid": 1, "documented_projection": 1, "empty_ready": 2, "inventory_documented": 1, "schema_valid": 3}`
- problem rows: `0`

Data schema ledger:

| dataset | status | rows | schema | limitation | next action |
| --- | --- | ---: | --- | --- | --- |
| `task_metadata_json` | schema_valid | 26 | `data/task_metadata_schema.json` | The aggregate CSV is a generated projection and intentionally omits some grader-only metadata fields. | Keep metadata.json as the source of truth and rerun validate_all.py after metadata edits. |
| `task_metadata_csv_projection` | documented_projection | 26 | `data/task_metadata_schema.json` | This CSV is not the full schema-bearing metadata record; use metadata.json for hidden grading declarations and task-specific bans. | If report columns change, update validate_all.py and this manifest together. |
| `run_results` | schema_valid | 69 | `data/run_results_schema.json` | Schema validation does not prove sample-size adequacy or model-result representativeness. | Run scripts/audit_run_integrity.py after edits to check transcript and arithmetic semantics. |
| `failure_annotations` | empty_ready | 0 | `data/failure_label_schema.json` | Empty adjudication data cannot support failure-distribution claims. | Populate after broad provider sweeps and independent transcript review. |
| `failure_label_reviews` | schema_valid | 3 | `data/failure_label_review_schema.json` | These are single-review smoke rows, not independent distributional adjudication. | Use the transcript review packet and adjudication fields for future broad sweeps. |
| `human_time_observations` | empty_ready | 0 | `data/human_time_observations_schema.json` | Author/reviewer estimates remain uncalibrated by independent timed solves. | Collect non-author timing rows before strengthening time-horizon claims. |
| `failure_label_codebook` | codebook_valid | 13 | `data/failure_label_schema.json` | The codebook is a taxonomy definition, not evidence that those failures dominate. | Update the codebook and downstream audits together if labels change. |
| `derived_reporting_csv_inventory` | inventory_documented | 52 | `` | Most generated audit CSVs are governed by their producer scripts and manifest hashes rather than standalone JSON schemas. | Add standalone schemas only for files that become external data contracts or model-run inputs. |


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

## Portfolio Counts

- acceptance statuses: `{"accepted_v0": 6, "calibration_only": 8, "rejected_duplicate": 2, "rejected_too_easy": 10}`
- accepted core families: `{"algorithm_correctness": 1, "direct_theorem_proving": 1, "informal_spec_to_formal": 1, "invariant_verification_ml_optimization": 1, "proof_repair_codebase": 1, "small_formal_library_construction": 1}`
- release human-time buckets: `{"T1": 8, "T2": 5, "T3": 1}`
- requirement statuses: `{"not_met": 2, "partial": 4, "supported": 58}`
- claim authorizations: `{"allowed": 1, "allowed_with_caveat": 6, "blocked": 5}`
- release-decision gates: `{"block": 4, "caution": 2, "pass": 2}`
- freeze-readiness gates: `{"block": 8, "caution": 1, "ready": 1}`

## What The Tasks Measure

The accepted core tasks are intended to test library/API search, theorem decomposition, semantic formalization, proof debugging, codebase navigation, invariant design, and small library construction. The calibration-only rows are retained to verify the harness, establish lower time-bucket behavior, and catch regressions in simple Lean proof generation.

Capability-level claims are weak where a capability is represented by only one accepted task. The diagnostic-coverage, construct-validity, and task-quality appendices are the row-level evidence for this claim boundary.

## Construct Validity Trace

`reports/construct_validity_matrix.md` and `data/construct_validity_matrix.csv` link each accepted_v0 task to its claimed diagnostic capabilities, mechanical proof/pin/wrong evidence, singleton-coverage limits, and task-level claim boundary.

- accepted construct rows: `6`
- support levels: `{"task_level_internal_review": 2, "task_level_internal_review_singleton_capability": 1, "task_level_with_caveat": 3}`
- rows with singleton-covered capabilities: `3/6`
- automation-dominated accepted rows: `2/6`
- caveated accepted rows: `3/6`

Construct-validity rows:

| task | support level | capabilities | singleton capabilities | claim limit |
| --- | --- | --- | --- | --- |
| `lt-201` | task_level_with_caveat | `theorem_decomposition`, `proof_debugging`, `codebase_navigation` | `codebase_navigation` | singleton capabilities cannot support capability-level generalization; accepted row carries a task-quality caveat; reference proof is automation-dominated |
| `lt-203` | task_level_internal_review_singleton_capability | `theorem_decomposition`, `semantic_formalization`, `proof_debugging` | `semantic_formalization` | singleton capabilities cannot support capability-level generalization |
| `lt-202` | task_level_with_caveat | `library_search`, `theorem_decomposition` | `library_search` | singleton capabilities cannot support capability-level generalization; accepted row carries a task-quality caveat |
| `lt-204` | task_level_internal_review | `theorem_decomposition`, `invariant_design`, `long_horizon_construction` | _none_ | task-level evidence only; aggregate claims still require more accepted tasks and model data |
| `lt-205` | task_level_internal_review | `theorem_decomposition`, `long_horizon_construction` | _none_ | task-level evidence only; aggregate claims still require more accepted tasks and model data |
| `lt-206` | task_level_with_caveat | `theorem_decomposition`, `invariant_design`, `long_horizon_construction` | _none_ | accepted row carries a task-quality caveat; reference proof is automation-dominated |


## Human-Time Estimates

Human-time buckets follow the project playbook: `T0` is 5-15 minutes, `T1` is 15-45 minutes, `T2` is 45-120 minutes, `T3` is 2-6 hours, and `T4` is 6+ hours.

The p50/p90 estimates in metadata are reviewer estimates, not measured independent solves. The current accepted set has T2/T3 coverage only and no accepted T4 row.

## Grader And Integrity Controls

The grader is Lean-first. For each submission it copies the public files listed in `metadata.json`, replaces the submission file, scans forbidden constructs, compiles public Lean files, compiles hidden semantic pins, and audits axioms on declared targets. Accepted and calibration tasks must have at least two wrong submissions.

Hidden pins check more than type signatures where possible, but they remain finite probes. The axiom policy allows only the standard Lean axioms documented in `docs/axiom_policy.md`. Source-level escape hatches such as `sorry`, `admit`, `axiom`, `constant`, `unsafe`, custom elaboration, and command execution are rejected before Lean grading.

## Public Export

`scripts/export_public_tasks.py` exports the release set by default: `accepted_v0`, `calibration_only`, and pending candidates if any. `scripts/validate_public_export.py` checks that hidden and wrong directories are absent, all public files are present, exported Lean files compile, and obvious hidden-reference path strings do not leak.

## Scaffold And Model-Run Support

The supported scaffold ladder is `one-shot`, `lookup`, and `lookup_unlimited`. Lookup is a real read-only command, `python scripts/lean_lookup.py QUERY`, which searches metadata-listed public Lean task files and installed Std/Mathlib files when available.

## Model Result Analysis

`reports/model_run_analysis.md` and `data/model_result_summary.csv` analyze committed provider rows against the planned primary sweep.

- planned accepted-core task/scaffold cells: `18`
- planned cells with any committed accepted-core provider row: `1`
- planned cells with a non-infra accepted-core provider row: `1`
- accepted-core provider rows: `2` total, `1` non-infra
- accepted-core successes among non-infra provider rows: `0`
- all committed provider smoke rows: `3` total, `2` non-infra

The committed provider rows are smoke evidence only; the planned primary sweep remains mostly uncovered.


## Model Evidence Provenance Audit

`reports/model_evidence_provenance_audit.md` checks that committed provider rows expose model versions, `k`, transcripts, sample sizes, infra accounting, and local-QA exclusion.

- provider/model versions in committed smoke rows: `["anthropic:claude-sonnet-4-6"]`
- provenance audit statuses: `{"pass": 7}`

## Statistical Analysis Plan

`reports/statistical_analysis_plan.md`, `data/statistical_design_thresholds.csv`, and `data/wilson_precision_table.csv` define minimum evidence thresholds before stronger model-result claims are allowed. This is a precision and claim-tier ledger, not new model evidence.

- claim tiers: `7`
- tier statuses: `{"blocked": 6, "supported": 1}`
- claim types: `{"benchmark_status": 1, "descriptive_performance": 1, "failure_analysis": 1, "performance_comparison": 1, "run_provenance": 1, "subgroup_performance": 1, "time_horizon_performance": 1}`
- blocked tiers: `6`
- Wilson precision rows: `18`

Claim-tier thresholds:

| tier | status | allowed output now | blocked overclaim |
| --- | --- | --- | --- |
| `smoke_run_provenance` | supported | Adapter, transcript, and run-result provenance only. | Do not treat smoke rows as benchmark performance. |
| `v0_1_primary_descriptive_performance` | blocked | Coverage table and blocked performance statement. | Do not report aggregate pass@k estimates or intervals for accepted-core performance until every planned cell is covered. |
| `scaffold_effect_comparison` | blocked | Planned scaffold comparison only. | Do not claim lookup or iterative compile/debug effects from the current smoke rows. |
| `time_horizon_bucket_trend` | blocked | Task-set time-bucket composition only. | Do not claim calibrated time-horizon scaling from author estimates or singleton T3 coverage. |
| `family_or_skill_summary` | blocked | Family/skill coverage table only. | Do not interpret singleton family or skill rows as stable estimates. |
| `failure_taxonomy_distribution` | blocked | Failure-label workflow and smoke transcript review only. | Do not claim dominant failure modes or failure distributions. |
| `locked_benchmark_population_claims` | blocked | Local v0.1 research artifact only. | Do not call v0.1 locked, final, population-valid, or frontier-performance-characterizing. |

Wilson precision ledger for assumed `p=0.5`:

| n | Wilson low | Wilson high | width | interpretation |
| ---: | ---: | ---: | ---: | --- |
| 1 | 0.0000 | 0.7935 | 0.7935 | very_wide |
| 6 | 0.1876 | 0.8124 | 0.6248 | very_wide |
| 18 | 0.2903 | 0.7097 | 0.4194 | wide |
| 20 | 0.2993 | 0.7007 | 0.4014 | wide |
| 30 | 0.3315 | 0.6685 | 0.3369 | moderate |
| 50 | 0.3664 | 0.6336 | 0.2671 | moderate |


## Figure Manifest And Plot Boundaries

`reports/figure_manifest.md` and `data/figure_manifest.csv` map generated SVGs to source artifacts and mark unsupported performance plots as intentionally absent.

- plot rows: `10`
- statuses: `{"blocked_by_evidence": 5, "generated_descriptive": 4, "generated_provenance": 1}`
- categories: `{"blocked_performance": 5, "generated_descriptive": 4, "generated_provenance": 1}`
- generated descriptive/provenance figures: `5`
- blocked performance plots: `5`
- problem rows: `0`

Figure and plot-boundary ledger:

| plot | status | figure exists | allowed interpretation | blocked overclaim |
| --- | --- | --- | --- | --- |
| `task_counts_by_family` | generated_descriptive | true | Accepted-core family composition only. | Do not infer model performance, family difficulty, or representativeness from task-count bars. |
| `task_counts_by_bucket` | generated_descriptive | true | Release task-count composition by human-time bucket. | Do not treat author-estimated bucket counts as measured time-horizon performance. |
| `top_skills` | generated_descriptive | true | Most frequent declared skills in the release set. | Do not read skill-frequency bars as validated capability coverage or model failure frequencies. |
| `run_rows_by_model` | generated_provenance | true | Committed run-row provenance by model/source, including local QA rows. | Do not read row-count bars as pass-rate evidence or model ranking. |
| `task_minutes_by_bucket` | generated_descriptive | true | Reviewer-estimated p50 minutes by task bucket. | Do not claim calibrated human-time scaling from this figure without independent timing observations. |
| `scaffold_pass_at_k_plot` | blocked_by_evidence | false | No scaffold performance plot is generated from the undercovered smoke rows. | A mean pass@10-by-scaffold plot would imply comparisons the data do not support. |
| `bucket_success_plot` | blocked_by_evidence | false | No success-by-time-bucket plot is generated from the undercovered smoke rows. | Current rows cannot estimate success by human-time bucket. |
| `family_success_plot` | blocked_by_evidence | false | No family success plot is generated from the undercovered smoke rows. | Current rows cannot estimate success by task family. |
| `failure_taxonomy_plot` | blocked_by_evidence | false | No failure-taxonomy distribution plot is generated from the undercovered smoke rows. | The current failure taxonomy is useful for transcript QA but too small for distributional claims. |
| `problem_pass_vs_time` | blocked_by_evidence | false | No problem-level pass-rate versus human-time plot is generated yet. | Do not imply a time-horizon trend from one covered accepted-core non-infra cell and author-estimated times. |


## Committed Run Results

66 local QA rows are committed for reference solutions and plausible wrong submissions. These rows are not model performance and are excluded from benchmark pass-rate summaries.

Accepted-core provider row summary:

- accepted-core non-infra provider smoke rows: `1`
- successful smoke rows: `0`
- primary sweep coverage: `1/18` planned cells covered
- performance estimate status: `blocked_by_undercoverage`; no benchmark pass-rate or interval is reported.

All committed non-local rows:

| task | provider | model | scaffold | k | pass@k | failure | transcript |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| `lt-001` | anthropic | claude-sonnet-4-6 | one-shot | 1 | 1.0 | none | `transcripts/anthropic-claude-sonnet-4-6-one-shot-1780206109/lt-001.jsonl` |
| `lt-201` | anthropic | claude-sonnet-4-6 | one-shot | 1 | 0.0 | infra_failure | `transcripts/anthropic-claude-sonnet-4-6-one-shot-1780206126/lt-201.jsonl` |
| `lt-201` | anthropic | claude-sonnet-4-6 | one-shot | 1 | 0.0 | proof_debugging | `transcripts/anthropic-claude-sonnet-4-6-one-shot-1780206167/lt-201.jsonl` |

Model-sweep infra failures: 1. Infra-failure rows are retained in `data/run_results.csv` and transcripts, but excluded from pass-rate summaries.

No provider API credentials or runner commands are committed. To run a real smoke sweep, configure one of `OPENAI_LEAN_RUNNER`, `ANTHROPIC_LEAN_RUNNER`, `GEMINI_LEAN_RUNNER`, or `LEAN_MODEL_RUNNER` and use `scripts/run_model_sweep.py`.

## Claim Authorization Matrix

`reports/claim_authorization_matrix.md` and `data/claim_authorization_matrix.csv` turn evidence audits into explicit report wording controls. This is stricter than the claim ledger: it records what wording is allowed, what caveat must travel with it, and what stronger wording is blocked.

- authorization rows: `12`
- authorization statuses: `{"allowed": 1, "allowed_with_caveat": 6, "blocked": 5}`
- claim areas: `{"artifact_validity": 1, "benchmark_status": 1, "construct_validity": 1, "data_validity": 1, "failure_analysis": 1, "grading_validity": 1, "operational_validity": 1, "performance_claim": 2, "report_validity": 1, "statistical_validity": 1, "task_validity": 1}`

Claim authorization table:

| claim | area | status | allowed wording | required caveat | forbidden wording |
| --- | --- | --- | --- | --- | --- |
| `local_artifact_validity` | artifact_validity | allowed_with_caveat | The repo is a locally validated v0.1 research artifact with public tasks, hidden checks, Lean scoring, integrity scans, and metadata. | Say this is local validation only; hosted QA, independent timing, and full model sweeps are outside the current evidence. | Do not call the artifact a locked benchmark, final benchmark, or hosted-QA-cleared benchmark. |
| `research_report_scope` | report_validity | allowed_with_caveat | The report is a generated research review memo that makes task-quality, grading, reproducibility, and evidence-limit claims from committed artifacts. | Pair this with the limitations that broad provider sweeps, independent human timing, and hosted QA are missing. | Do not describe the report as proving frontier capability trends or benchmark-valid pass-rate effects. |
| `accepted_core_quality` | task_validity | allowed_with_caveat | The six accepted-core tasks are internally reviewed and stronger than the original candidate pool. | Say the core is small, internally reviewed, and still has caveat rows; do not generalize from family-level singletons. | Do not say the accepted set is benchmark-grade, representative, or sufficient for population-level model claims. |
| `hidden_pin_and_grader_strength` | grading_validity | allowed_with_caveat | Hidden checks provide meaningful anti-gaming probes for accepted tasks, especially mutable-definition semantic-pin tasks. | Note that proof-only fixed-statement rows mostly rely on Lean typechecking plus downstream signature guards, and all pins are finite probes. | Do not claim hidden pins prove full semantic equivalence or catch every weakened formalization. |
| `run_data_integrity` | data_validity | allowed | Committed run-result rows are internally consistent with transcripts, score vectors, failure labels, and pass@k arithmetic. | No extra caveat is needed for this narrow data-integrity wording; add the limitation before discussing model performance. | Do not infer model pass rates, scaffold effects, or failure distributions from local QA rows. |
| `time_horizon_scope` | construct_validity | allowed_with_caveat | The artifact explores a limited T2/T3-only slice of time-horizon evaluation design. | State that accepted human times are author/reviewer estimates, there is no T4 row, and no independent timing observations are committed. | Do not claim robust measurement of increasing time horizon or calibrated human-time scaling. |
| `scaffold_effects` | performance_claim | blocked | The scaffold ladder and execution plan are implemented; empirical scaffold-effect conclusions are not yet supported. | Only describe planned scaffold comparisons and the fact that current provider rows do not cover lookup or iterative debug cells. | Do not claim lookup helps, iterative compile/debug helps, or scaffold effects are measured from committed rows. |
| `frontier_model_performance` | performance_claim | blocked | No frontier-performance conclusion is authorized from the committed provider smoke rows. | It is acceptable to state that provider adapters and smoke transcripts exist, but they are not benchmark results. | Do not report committed smoke rows as characterizing frontier capability or model rankings. |
| `failure_taxonomy_results` | failure_analysis | allowed_with_caveat | The repo has a failure-label schema, transcript links, a transcript review queue, and a single-review audit for the committed smoke rows. | Current adjudication is single-review smoke evidence only: reviewed rows 3/3, raw queue rows still marked unreviewed in run_results 3, audit failures 0. | Do not claim dominant failure modes, distributional failure analysis, or adjudicated taxonomy results. |
| `statistical_performance_reporting` | statistical_validity | blocked | Statistical reporting checks exist and currently block recommended performance plots. | Describe the statistical audit as a guardrail for future sweeps, not as performance evidence. | Do not publish pass@10-by-scaffold plots, family means, or confidence intervals as substantive results yet. |
| `hosted_qa_status` | operational_validity | blocked | Hosted/Taiga QA readiness has been audited, and the hosted QA evidence is currently absent. | State only that local validation is ready for a hosted QA loop; do not imply hosted checks have run. | Do not claim Full Env QA passed, Env Linter findings are settled, or hosted problem versions are frozen. |
| `locked_benchmark_status` | benchmark_status | blocked | v0.1 is not a locked benchmark; it is a local v0.1 research artifact with explicit blockers. | Every report summary should preserve this boundary until all locked-benchmark gates are satisfied. | Do not call v0.1 final, locked, population-valid, or suitable for benchmark headline claims. |


## Remaining Blockers

| requirement | status | evidence | next step |
| --- | --- | --- | --- |
| `portfolio_accepted_count` | not_met | 6 accepted_v0 tasks; 8 calibration-only tasks; 12 rejected archive tasks. | Add and hard-review more high-quality T2/T3/T4 tasks before claiming a full benchmark. |
| `time_horizon_spread` | partial | Accepted bucket counts: {"T2": 5, "T3": 1}; release bucket counts: {"T1": 8, "T2": 5, "T3": 1}. | Add more accepted T3/T4 tasks, including a T4 stretch row, and independently review human times. |
| `scaffold_result_comparison` | partial | Non-infra model rows: 2; scaffolds observed: ["one-shot"]; planned rows: 18. | Run real pass@10 or comparable sweeps across one-shot, lookup, and lookup_unlimited before performance claims. |
| `frontier_model_evidence` | partial | Non-infra model rows: 2 over 6 accepted tasks; total model rows including infra failures: 3. | Run broader provider sweeps only after local and hosted QA are stable. |
| `independent_human_time_review` | partial | Accepted tasks with manual_review_complete: 6/6; accepted tasks with successful independent timing observations: 0/6; observation rows: 0. | Collect independent Lean-human timed solves or second-reviewer timing notes before freeze. |
| `hosted_qa_env_linter` | not_met | Hosted QA artifacts present: 0/2; hosted readiness report exists: True; blocked hosted-readiness checks: 9. | Run hosted Full Env QA and record findings/rebuttals before claiming a locked benchmark. |

## Report And Evidence Files

The long generated evidence tables are intentionally outside this main report:

- `reports/evidence_appendix.md`: full generated report appendix with row-level audit tables and validation manifest details.
- `reports/concise_metr_report.md`: shortest reviewer-facing METR-style narrative.
- `reports/requirement_coverage.md`: requirement-by-requirement evidence.
- `reports/report_source_traceability.md`: section-by-section source map for this main report.
- `reports/data_schema_manifest.md`: schema/data-dictionary boundary audit for core datasets and generated CSVs.
- `reports/reviewer_reproduction_packet.md`: ordered local replay workflow, expected artifacts, failure interpretations, and external-evidence boundaries.
- `reports/clean_workspace_replay.md`: bounded temporary-workspace replay of dependency materialization, Lean build, grader pass/fail behavior, and public export validation.
- `reports/construct_validity_matrix.md`: task-level construct-validity trace for accepted rows.
- `reports/claim_authorization_matrix.md`: allowed, caveated, and blocked claim wording.
- `reports/research_claim_gap_matrix.md`: evidence packages needed before stronger claims are allowed.
- `reports/freeze_readiness_roadmap.md`: locked-benchmark gates.
- `reports/failure_label_review_audit.md`: single-review smoke transcript adjudication audit.
- `reports/statistical_analysis_plan.md`: claim-tier evidence thresholds and Wilson precision ledger for future model-result reporting.
- `reports/figure_manifest.md`: source-data and claim-boundary ledger for generated figures and blocked performance plots.

## Reproducibility Checklist

`reports/reviewer_reproduction_packet.md` and `data/reviewer_reproduction_steps.csv` turn the local replay and external-evidence surface into an ordered reviewer workflow.

- reproduction steps: `15`
- phase counts: `{"external_evidence": 3, "local_replay": 12}`
- status counts: `{"blocked_external_evidence": 3, "ready": 12}`
- local replay problem rows: `0`
- external-evidence rows still blocked: `3`

Reviewer reproduction ledger:

| step | phase | status | command | limitation |
| --- | --- | --- | --- | --- |
| `mathlib_cache_get` | local_replay | ready | `lake exe cache get` | This is local dependency-cache evidence; hosted environments may use a different cache path. |
| `toolchain_build` | local_replay | ready | `lake build` | This is local build evidence; it is not hosted QA or provider-sandbox evidence. |
| `task_validation` | local_replay | ready | `python scripts/validate_all.py` | This validates local hidden checks and wrong submissions; it does not prove model performance. |
| `difficulty_review` | local_replay | ready | `python scripts/audit_difficulty.py` | The audit combines static heuristics with human judgment; it is not independent human timing. |
| `local_qa_rows` | local_replay | ready | `python scripts/record_local_qa_results.py` | Local QA rows must stay excluded from model-performance estimates. |
| `run_integrity` | local_replay | ready | `python scripts/audit_run_integrity.py` | Passing integrity checks do not imply adequate provider sample size. |
| `grader_hardening` | local_replay | ready | `python scripts/audit_grader_hardening.py` | The scanner remains lexical source scanning, not a complete Lean parser. |
| `public_export` | local_replay | ready | `python scripts/export_public_tasks.py --out public_tasks` | The export is a local directory snapshot, not a hosted problem version. |
| `public_export_validation` | local_replay | ready | `python scripts/validate_public_export.py --out public_tasks` | This does not run Taiga Full Env QA or Env Linter. |
| `report_regeneration` | local_replay | ready | `python scripts/generate_report.py` | Generated report text can still overclaim unless claim-conformance checks pass. |
| `claim_and_shape_audits` | local_replay | ready | `python scripts/audit_report_claim_conformance.py; python scripts/audit_report_shape.py` | Text audits are guardrails, not substitutes for substantive external evidence. |
| `validation_manifest` | local_replay | ready | `python scripts/write_validation_manifest.py --public-export public_tasks; python scripts/audit_validation_manifest.py` | The manifest intentionally omits self-referential report hashes and is not clean-checkout proof. |
| `provider_sweep` | external_evidence | blocked_external_evidence | `python scripts/run_model_sweep.py --provider PROVIDER --model MODEL --scaffold SCAFFOLD --attempts 10 --acceptance-status accepted_v0` | Requires external provider runners and API keys kept only in environment variables. |
| `independent_human_timing` | external_evidence | blocked_external_evidence | `Fill data/human_time_observations.csv from non-author timed solves` | Must not be inferred from model pass rates or author expectations. |
| `hosted_qa` | external_evidence | blocked_external_evidence | `Run hosted Full Env QA and Env Linter on exact final problem versions` | This repository currently records readiness only, not hosted QA pass evidence. |


`reports/clean_workspace_replay.md` and `data/clean_workspace_replay.csv` record a bounded temporary-workspace replay outside the dirty working directory.

- replay rows: `7`
- phase counts: `{"replay": 6, "setup": 1}`
- status counts: `{"pass": 7}`
- failure rows: `0`

Clean workspace replay ledger:

| check | phase | status | seconds | limitation |
| --- | --- | --- | ---: | --- |
| `workspace_materialization` | setup | pass | 78.42 | This is a local clean workspace from the current working tree, not a remote clone or hosted container. |
| `mathlib_cache_get` | replay | pass | 767.85 | This uses the Mathlib cache for local dependency materialization; hosted runners need their own cache or build path. |
| `clean_lake_build` | replay | pass | 5.92 | Local toolchain and dependency resolution can differ from hosted QA. |
| `reference_validation_smoke` | replay | pass | 34.99 | This is a representative reference-validation smoke, not full validate_all coverage. |
| `wrong_submission_smoke` | replay | pass | 6.96 | This probes expected-fail behavior for one semantic-pin wrong submission only. |
| `public_export_smoke` | replay | pass | 0.83 | Local public export is not hosted problem packaging. |
| `public_export_validation_smoke` | replay | pass | 144.35 | This validates local public assets but does not run Env Linter. |


The local regeneration gate is recorded in `README.md`, `reports/validation_manifest.json`, `reports/validation_manifest_audit.md`, `reports/reviewer_reproduction_packet.md`, and `reports/clean_workspace_replay.md`. The manifest audit verifies command coverage, current artifact hashes, public-export summary, and the policy that the manifest records generation-time git state rather than a post-commit clean-checkout proof. The public export validator checks that hidden references and wrong submissions are absent from `public_tasks`, all metadata-listed public files are present, exported Lean files compile, and obvious hidden-reference path strings do not leak.

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
