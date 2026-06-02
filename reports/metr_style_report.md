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

- dataset rows: `9`
- validation statuses: `{"codebook_valid": 1, "documented_projection": 1, "empty_ready": 3, "inventory_documented": 1, "schema_valid": 3}`
- problem rows: `0`

Data schema ledger:

| dataset | status | rows | schema | limitation | next action |
| --- | --- | ---: | --- | --- | --- |
| `task_metadata_json` | schema_valid | 26 | `data/task_metadata_schema.json` | The aggregate CSV is a generated projection and intentionally omits some grader-only metadata fields. | Keep metadata.json as the source of truth and rerun validate_all.py after metadata edits. |
| `task_metadata_csv_projection` | documented_projection | 26 | `data/task_metadata_schema.json` | This CSV is not the full schema-bearing metadata record; use metadata.json for hidden grading declarations and task-specific bans. | If report columns change, update validate_all.py and this manifest together. |
| `run_results` | schema_valid | 71 | `data/run_results_schema.json` | Schema validation does not prove sample-size adequacy or model-result representativeness. | Run scripts/audit_run_integrity.py after edits to check transcript and arithmetic semantics. |
| `failure_annotations` | empty_ready | 0 | `data/failure_label_schema.json` | Empty adjudication data cannot support failure-distribution claims. | Populate after broad provider sweeps and independent transcript review. |
| `failure_label_reviews` | schema_valid | 3 | `data/failure_label_review_schema.json` | These are single-review smoke rows, not independent distributional adjudication. | Use the transcript review packet and adjudication fields for future broad sweeps. |
| `human_time_observations` | empty_ready | 0 | `data/human_time_observations_schema.json` | Author/reviewer estimates remain uncalibrated by independent timed solves. | Collect non-author timing rows before strengthening time-horizon claims. |
| `independent_task_reviews` | empty_ready | 0 | `data/independent_task_review_schema.json` | Empty review data cannot support independent acceptance, time-bucket, hidden-pin, or wrong-submission adequacy claims. | Collect non-author review rows for every accepted_v0 task before strengthening benchmark-grade task-quality claims. |
| `failure_label_codebook` | codebook_valid | 13 | `data/failure_label_schema.json` | The codebook is a taxonomy definition, not evidence that those failures dominate. | Update the codebook and downstream audits together if labels change. |
| `derived_reporting_csv_inventory` | inventory_documented | 64 | `` | Most generated audit CSVs are governed by their producer scripts and manifest hashes rather than standalone JSON schemas. | Add standalone schemas only for files that become external data contracts or model-run inputs. |


## Task Selection Protocol

Task status is assigned by metadata, not by directory alone:

- `accepted_v0`: core task retained after manual review and local validation.
- `calibration_only`: release task retained for lower-bound calibration, harness checks, or simple semantic-pin regression tests.
- `rejected_*`: archived task retained for auditability but excluded from release claims.
- `candidate_review_pending`: generated task not yet accepted.

Acceptance requires more than a passing reference solution: wrong submissions must fail, hidden checks must test meaningful behavior where possible, metadata must include human-time and diagnostic fields, and the accepted-task review must document known limitations. Tasks can be downgraded after review even when they validate.

## Candidate Pruning Audit

`reports/candidate_pruning_audit.md` and `data/candidate_pruning_audit.csv` make the v0.1 pruning decision visible for every tracked task. The audit joins metadata, difficulty signals, and the task-quality matrix so the small accepted core is explained by task-quality review rather than directory placement. It is not model performance evidence.

- pruning rows: `26`
- acceptance statuses: `{"accepted_v0": 6, "calibration_only": 8, "rejected_duplicate": 2, "rejected_too_easy": 10}`
- pruning decisions: `{"accepted_core": 6, "rejected_archive": 12, "retained_calibration_only": 8}`
- accepted-core rate: `6/26`
- calibration-only rows: `8`
- rejected archive rows: `12`
- non-core rows with explicit core-exclusion reasons: `20/20`

Family/status pruning table:

| family | accepted_v0 | calibration_only | rejected_duplicate | rejected_too_easy |
| --- | ---: | ---: | ---: | ---: |
| `algorithm_correctness` | 1 | 3 | 0 | 2 |
| `direct_theorem_proving` | 1 | 0 | 0 | 1 |
| `informal_spec_to_formal` | 1 | 3 | 1 | 0 |
| `invariant_verification_ml_optimization` | 1 | 0 | 0 | 4 |
| `proof_repair_codebase` | 1 | 2 | 1 | 0 |
| `small_formal_library_construction` | 1 | 0 | 0 | 3 |


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
| `lt-204` | 36 | false | semantic | 3 | maybe | high |
| `lt-205` | 42 | false | semantic | 3 | unlikely | high |
| `lt-206` | 60 | true | semantic | 2 | maybe | high |

## Accepted Task Cards

`reports/accepted_task_cards.md` and `data/accepted_task_cards.csv` synthesize one reviewer card per accepted_v0 task from metadata, difficulty, task-quality, construct-validity, hidden-pin coverage, asset-manifest, validation-command, and local-QA evidence. The cards are a review navigation layer only: they do not expose hidden proof contents and are not model-performance evidence.

- accepted task cards: `6`
- recommendations: `{"keep": 3, "keep_with_caveat": 3}`
- automation-dominated rows: `2/6`
- rows whose wrong controls exercise semantic hidden pins: `4/6`
- caveated accepted rows: `3/6`

Accepted-task card summary:

| task | recommendation | proof signal | hidden-pin coverage | local QA | blocker summary |
| --- | --- | --- | --- | --- | --- |
| `lt-201` | keep_with_caveat | 25 lines; automation=true; one-shot=maybe | pins_not_exercised_by_wrongs; stages `{"public_stage": 2}` | `{"expected_failure": 2, "passed": 1}` | Retain in v0.1 only with the recorded caveat; collect independent human timing, full scaffold sweep evidence, and external QA before freeze. independent human timing; accepted-core scaffold sweep; hosted QA evidence;... |
| `lt-203` | keep | 30 lines; automation=false; one-shot=maybe | semantic_pins_exercised; stages `{"hidden_pin": 2}` | `{"expected_failure": 2, "passed": 1}` | Collect independent timing, hosted QA, and accepted-core scaffold/model evidence before benchmark freeze. independent human timing; accepted-core scaffold sweep; hosted QA evidence; at least one more accepted task for... |
| `lt-202` | keep_with_caveat | 46 lines; automation=false; one-shot=maybe | pins_not_exercised_by_wrongs; stages `{"public_stage": 2}` | `{"expected_failure": 2, "passed": 1}` | Retain in v0.1 only with the recorded caveat; collect independent human timing, full scaffold sweep evidence, and external QA before freeze. independent human timing; accepted-core scaffold sweep; hosted QA evidence;... |
| `lt-204` | keep | 36 lines; automation=false; one-shot=maybe | semantic_pins_exercised; stages `{"hidden_pin": 2, "public_stage": 1}` | `{"expected_failure": 3, "passed": 1}` | Collect independent timing, hosted QA, and accepted-core scaffold/model evidence before benchmark freeze. independent human timing; accepted-core scaffold sweep; hosted QA evidence Mutable definitions have public-comp... |
| `lt-205` | keep | 42 lines; automation=false; one-shot=unlikely | semantic_pins_exercised; stages `{"hidden_pin": 2, "public_stage": 1}` | `{"expected_failure": 3, "passed": 1}` | Independently time at least one human solve and run the planned scaffold sweep before using this as long-horizon evidence. independent human timing; accepted-core scaffold sweep; hosted QA evidence; extra timing revie... |
| `lt-206` | keep_with_caveat | 60 lines; automation=true; one-shot=maybe | semantic_pins_exercised; stages `{"hidden_pin": 1, "unknown": 1}` | `{"expected_failure": 2, "passed": 1}` | Retain in v0.1 only with the recorded caveat; collect independent human timing, full scaffold sweep evidence, and external QA before freeze. independent human timing; accepted-core scaffold sweep; hosted QA evidence M... |


## Independent Task Review Packet

`reports/independent_task_review_packet.md` and `data/independent_task_review_plan.csv` define a non-author task-quality review workflow for accepted_v0 tasks. `data/independent_task_reviews.csv` is intentionally empty until real reviewers add rows; the status audit records that packet readiness is not independent validation evidence.

- review-plan rows: `6`
- review-observation rows: `0`
- plan family counts: `{"algorithm_correctness": 1, "direct_theorem_proving": 1, "informal_spec_to_formal": 1, "invariant_verification_ml_optimization": 1, "proof_repair_codebase": 1, "small_formal_library_construction": 1}`
- plan bucket counts: `{"T2": 5, "T3": 1}`
- status-audit counts: `{"block": 1, "empty_ready": 1, "pass": 3}`
- accepted-review coverage: `accepted reviewed=0/6; missing=["lt-201", "lt-202", "lt-203", "lt-204", "lt-205", "lt-206"]; review_rows=0`
- observed recommendations: `{}`

Independent review status:

| check | status | evidence | next action |
| --- | --- | --- | --- |
| `review_plan_coverage` | pass | accepted=6; plan_rows=6; template_rows=6; missing_plan=[]; missing_template=[] | Regenerate scripts/generate_independent_review_packet.py after accepted task metadata changes. |
| `review_schema_and_template` | pass | schema_required_fields=15; template_fields_ok=True; review_fields_ok=True; plan_fields=18 | Keep schema, template, and audit in sync if review categories change. |
| `review_row_validity` | pass | review_rows=0; validation_errors=0; examples=[] | Append real non-author review rows, then rerun this audit. |
| `accepted_review_coverage` | block | accepted reviewed=0/6; missing=["lt-201", "lt-202", "lt-203", "lt-204", "lt-205", "lt-206"]; review_rows=0 | Collect at least one non-author review row for every accepted_v0 task before freeze. |
| `review_recommendation_distribution` | empty_ready | recommendations={}; review_rows=0 | Use recommendations only after rows are collected and checked against task evidence. |


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
- requirement statuses: `{"not_met": 3, "partial": 4, "supported": 67}`
- claim authorizations: `{"allowed": 1, "allowed_with_caveat": 6, "blocked": 5}`
- release-decision gates: `{"block": 4, "caution": 2, "pass": 2}`
- freeze-readiness gates: `{"block": 8, "caution": 1, "ready": 1}`

## Report Count Consistency Audit

`reports/report_count_consistency_audit.md` and `data/report_count_consistency_audit.csv` check that repeated top-line counts in the concise report, main report, evidence appendix, and validation manifest agree with committed CSV/JSON sources. This is a drift detector for reviewer-facing numbers, not a new benchmark-evidence source.

- checks: `8`
- statuses: `{"pass": 8}`
- areas: `{"blocker_counts": 1, "gate_counts": 1, "manifest_counts": 2, "model_counts": 1, "portfolio_counts": 1, "report_counts": 2}`

Count-consistency checks:

| check | area | status | evidence | required action |
| --- | --- | --- | --- | --- |
| `task_status_counts` | portfolio_counts | pass | Task-status counts are checked against task metadata, the validation manifest, and the main/concise report top lines. | Regenerate task metadata, validation manifest, concise report, and main report after any task-status change. |
| `requirement_status_counts` | report_counts | pass | Requirement status counts are checked where the report summarizes supported/partial/not_met evidence. | Regenerate requirement coverage and all report layers after requirement status changes. |
| `claim_authorization_counts` | report_counts | pass | Claim-authorization status counts are checked against generated report summaries. | Regenerate claim authorization, concise report, and main report after claim status changes. |
| `release_and_freeze_gate_counts` | gate_counts | pass | Release-decision and freeze-readiness status counts are checked wherever the report repeats them. | Regenerate release/freeze reports and all report layers after gate-status changes. |
| `model_coverage_counts` | model_counts | pass | Model-sweep coverage counts are checked against the source summary and report wording that keeps performance claims blocked. | Regenerate model-result analysis and reports after provider rows or sweep plans change. |
| `run_and_manifest_counts` | manifest_counts | pass | Run-result counts are checked against the validation manifest and the appendix manifest summary. | Regenerate local QA rows, validation manifest, and report appendix after run-result changes. |
| `locked_benchmark_blocker_counts` | blocker_counts | pass | Locked-benchmark blocker identifiers are checked against requirement coverage, the claim-gap row, and report blocker tables. | Regenerate requirement coverage, claim gap matrix, and reports when locked-benchmark blockers change. |
| `public_export_counts` | manifest_counts | pass | Public-export task and hidden/wrong-path counts are checked against the manifest and appendix summary. | Regenerate public export, validation manifest, and report appendix after public task export changes. |


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
- strict planned-cell coverage statuses: `{"missing": 17, "smoke_only": 1}`
- strict cells not ready for pass@k analysis: `18`
- scaffold/status cells: `{"lookup:missing": 6, "lookup_unlimited:missing": 6, "one-shot:missing": 5, "one-shot:smoke_only": 1}`

`reports/model_sweep_coverage_audit.md` is the stricter ledger for planned `(task, scaffold, k)` cells. It treats current k=1 provider rows as smoke evidence only; the planned primary sweep remains mostly uncovered and cannot support scaffold-effect or frontier-performance claims.


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
| `problem_pass_vs_time` | blocked_by_evidence | false | No problem-level pass-rate versus human-time plot is generated yet. | Do not imply a time-horizon trend from zero pass@k-ready accepted-core cells and author-estimated times. |


## Committed Run Results

68 local QA rows are committed for reference solutions and plausible wrong submissions. These rows are not model performance and are excluded from benchmark pass-rate summaries.

Accepted-core provider row summary:

- accepted-core non-infra provider smoke rows: `1`
- successful smoke rows: `0`
- primary sweep pass@k-ready coverage: `0/18` planned cells ready
- aggregate non-infra smoke-covered cells: `1/18`
- performance estimate status: `blocked_by_undercoverage`; no benchmark pass-rate or interval is reported.

All committed non-local rows:

| task | provider | model | scaffold | k | pass@k | failure | transcript |
| --- | --- | --- | --- | ---: | ---: | --- | --- |
| `lt-001` | anthropic | claude-sonnet-4-6 | one-shot | 1 | 1.0 | none | `transcripts/anthropic-claude-sonnet-4-6-one-shot-1780206109/lt-001.jsonl` |
| `lt-201` | anthropic | claude-sonnet-4-6 | one-shot | 1 | 0.0 | infra_failure | `transcripts/anthropic-claude-sonnet-4-6-one-shot-1780206126/lt-201.jsonl` |
| `lt-201` | anthropic | claude-sonnet-4-6 | one-shot | 1 | 0.0 | proof_debugging | `transcripts/anthropic-claude-sonnet-4-6-one-shot-1780206167/lt-201.jsonl` |

Model-sweep infra failures: 1. Infra-failure rows are retained in `data/run_results.csv` and transcripts, but excluded from pass-rate summaries.

No provider API credentials or runner commands are committed. To run a real smoke sweep, configure one of `OPENAI_LEAN_RUNNER`, `ANTHROPIC_LEAN_RUNNER`, `GEMINI_LEAN_RUNNER`, or `LEAN_MODEL_RUNNER` and use `scripts/run_model_sweep.py`.

## Threat Coverage Audit

`reports/threat_coverage_audit.md` and `data/threat_coverage_audit.csv` check that open locked-benchmark blockers and non-allowed claims are represented in the threats-to-validity register. This is a limitation-coverage audit, not evidence that the limitations have been resolved.

- checks: `4`
- statuses: `{"pass": 4}`
- areas: `{"claim_threats": 1, "freeze_alignment": 1, "locked_benchmark_threats": 1, "threat_register_integrity": 1}`
- failures: `0`

Threat-coverage checks:

| check | area | status | evidence | required action |
| --- | --- | --- | --- | --- |
| `locked_blocker_threat_mapping` | locked_benchmark_threats | pass | open_locked_requirements=7; covered={"frontier_model_evidence": ["frontier_performance_undercoverage"], "hosted_qa_env_linter": ["hosted_environment_gap"], "independent_human_time_review": ["author_estimated_human_time"], "independent_task_quality_review": ["missing_independent_task_quality_review"], "portfolio_accepted_count": ["portfolio_scale_and_balance"], "scaffold_result_comparison": ["scaffold_sweep_undercoverage", "statistical_power_and_plots"], "time_horizon_spread": ["construct_time_horizon_depth"]}; missing=[]; weak_status=[] | Add or update threat rows whenever a locked-benchmark blocker is partial or not_met. |
| `non_allowed_claim_threat_mapping` | claim_threats | pass | non_allowed_claims=11; expected_tokens={"accepted_core_quality": ["accepted_core_reviewed"], "failure_taxonomy_results": ["diagnostic_failure_distribution"], "frontier_model_performance": ["frontier_performance"], "hidden_pin_and_grader_strength": ["hidden_pin_strength", "grading_validity"], "hosted_qa_status": ["deployment_reliability", "locked_benchmark"], "local_artifact_validity": [], "locked_benchmark_status": ["locked_benchmark"], "research_report_scope": [], "scaffold_effects": ["scaffold_effects"], "statistical_performance_reporting": ["frontier_performance", "scaffold_effects", "family_level_performance"], "time_horizon_scope": ["time_horizon_measurement"]}; available_tokens=["accepted_core_reviewed", "artifact_security", "deployment_reliability", "diagnostic_failure_distribution", "family_level_performance", "frontier_performance", "grading_validity", "hidden_pin_strength", "locked_benchmark", "provider_run_reproducibility", "public_release_safety", "scaffold_effects", "time_horizon_measurement"] | Keep every caveated or blocked claim tied to at least one threat claims_limited token. |
| `threat_row_completeness` | threat_register_integrity | pass | threat_rows=13; statuses={"block": 8, "caution": 3, "controlled": 2}; incomplete=0; invalid_statuses=0; missing_source_paths=0 | Every threat row should have evidence, mitigation, stronger-evidence requirements, claim limits, and existing source artifacts. |
| `high_block_threat_freeze_alignment` | freeze_alignment | pass | high_block_threats=8; freeze_rows=10; missing_freeze_claim_tokens=[] | High-severity blocking threats should correspond to freeze-roadmap claim limits or gates. |


## Claim Authorization Matrix

`reports/claim_authorization_matrix.md` and `data/claim_authorization_matrix.csv` turn evidence audits into explicit report wording controls. This is stricter than the claim ledger: it records what wording is allowed, what caveat must travel with it, and what stronger wording is blocked.

- authorization rows: `12`
- authorization statuses: `{"allowed": 1, "allowed_with_caveat": 6, "blocked": 5}`
- claim areas: `{"artifact_validity": 1, "benchmark_status": 1, "construct_validity": 1, "data_validity": 1, "failure_analysis": 1, "grading_validity": 1, "operational_validity": 1, "performance_claim": 2, "report_validity": 1, "statistical_validity": 1, "task_validity": 1}`

Claim authorization table:

| claim | area | status | allowed wording | required caveat | forbidden wording |
| --- | --- | --- | --- | --- | --- |
| `local_artifact_validity` | artifact_validity | allowed_with_caveat | The repo is a locally validated v0.1 research artifact with public tasks, hidden checks, Lean scoring, integrity scans, and metadata. | Say this is local validation only; hosted QA, independent timing, and full model sweeps are outside the current evidence. | Do not call the artifact a locked benchmark, final benchmark, or hosted-QA-cleared benchmark. |
| `research_report_scope` | report_validity | allowed_with_caveat | The report is a generated research review memo that makes task-quality, grading, reproducibility, and evidence-limit claims from committed artifacts. | Pair this with the limitations that broad provider sweeps, independent human timing, completed independent task reviews, and hosted QA are missing. | Do not describe the report as proving frontier capability trends or benchmark-valid pass-rate effects. |
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
| `scaffold_result_comparison` | partial | Non-infra model rows: 2; smoke scaffolds observed: ["one-shot"]; pass@k-ready cells: 0/18; pass@k-ready scaffolds: []; coverage statuses: {"missing": 17, "smoke_only": 1}. | Run real pass@10 or comparable sweeps across one-shot, lookup, and lookup_unlimited before performance claims. |
| `frontier_model_evidence` | partial | Non-infra model rows: 2 over 6 accepted tasks; total model rows including infra failures: 3. | Run broader provider sweeps only after local and hosted QA are stable. |
| `independent_human_time_review` | partial | Accepted tasks with manual_review_complete: 6/6; accepted tasks with successful independent timing observations: 0/6; observation rows: 0. | Collect independent Lean-human timed solves or second-reviewer timing notes before freeze. |
| `independent_task_quality_review` | not_met | Accepted tasks with completed independent task reviews: 0/6; review rows: 0; status-audit rows: 5. | Collect non-author task-quality reviews for every accepted_v0 task before freeze. |
| `hosted_qa_env_linter` | not_met | Hosted QA artifacts present: 0/2; hosted readiness report exists: True; blocked hosted-readiness checks: 6. | Run hosted Full Env QA and record findings/rebuttals before claiming a locked benchmark. |

## Taiga Wrapper Isolation Audit

`reports/taiga_wrapper_isolation_audit.md` and `data/taiga_wrapper_isolation_audit.csv` locally exercise the hosted wrapper's hidden-bundle grading path. This is mitigation evidence only; hosted filesystem-tool isolation still requires Taiga preflight and Env Linter evidence on uploaded problem versions.

- checks: `3`
- statuses: `{"pass": 3}`
- failing local wrapper-isolation checks: `0`

Taiga wrapper isolation checks:

| check | area | status | limitation |
| --- | --- | --- | --- |
| `hidden_bundle_generation` | bundle_generation | pass | This checks the committed local bundle generator, not a built uploaded container image. |
| `bundle_runtime_grading_smoke` | wrapper_runtime | pass | This is a local subprocess smoke test. It proves the wrapper can use the bundle path without source-task fallback, but it is not hosted filesystem-tool isolation evidence. |
| `docker_static_isolation_controls` | static_packaging | pass | Static controls can drift from hosted runtime behavior and do not replace uploaded-image inspection. |


## Final Delivery Checklist Audit

`reports/final_delivery_checklist_audit.md` and `data/final_delivery_checklist_audit.csv` map the playbook final-delivery checklist to committed evidence. This is a claim-boundary audit: it keeps missing pass@10/pass@k, hosted QA, late-finding, and version-freeze proof blocked while identifying local rows that are already supported.

- checklist rows: `10`
- statuses: `{"block": 5, "caution": 2, "pass": 3}`
- blocked final-delivery rows: `5`
- caution rows: `2`

Final-delivery checklist:

| check | status | playbook item | limitation | next action |
| --- | --- | --- | --- | --- |
| `final_versions_have_pass_at_k` | block | all exact final problem versions have pass@10 or the agreed pass@k | The plan specifies pass@10 cells, but committed provider rows do not cover the accepted task/scaffold plan. | Run the planned accepted-core pass@10 sweep on exact final problem versions and commit transcripts/results. |
| `scaffolds_use_same_task_set` | caution | every scaffold uses the same task set unless explicitly documented | The planned sweep uses the same accepted task set, but observed committed provider evidence has not yet covered the scaffold ladder. | Keep the same accepted task IDs across one-shot, lookup, and lookup_unlimited runs; document any exclusion before running. |
| `env_linter_findings_resolved` | block | no unresolved warning/error/critical Env Linter findings | No Env Linter result rows are committed, so absence of unresolved findings is unproven. | Run Env Linter on exact hosted problem versions and record each warning/error/critical finding disposition. |
| `full_env_qa_10_attempts` | block | final QA used Full Env QA on 10 attempts | No Full Env QA result rows on final exact problem versions are committed. | Run Full Env QA on 10 attempts after hosted smoke stability and commit result IDs/findings. |
| `late_qa_findings_settled` | block | late QA findings have settled | There are no hosted QA rows or late-finding timestamps to prove the 30-45 minute settling window has elapsed. | Record hosted QA completion times and final finding dispositions after the settling window. |
| `repo_matches_uploaded_environment` | block | repo source matches the uploaded environment | The local Taiga package scaffold exists, but no immutable uploaded image digest or hosted problem-version mapping is committed. | Commit image digest, environment/problem-version IDs, and snapshot/tag mapping for the exact uploaded package. |
| `plots_regenerate_from_committed_csv` | pass | plots regenerate from committed CSV files | Generated descriptive/provenance plots are covered; blocked performance plots intentionally remain absent. | Keep performance plots blocked until provider/scaffold coverage satisfies the statistical plan. |
| `report_states_sample_sizes_and_model_versions` | pass | report text states sample sizes and model versions | The report states sample sizes and model versions for smoke rows, but performance conclusions remain blocked by undercoverage. | After broad sweeps, regenerate model provenance, count consistency, and claim-conformance audits before interpreting pass rates. |
| `dev_test_split_marked` | pass | dev/test split is clearly marked | Split labels are local metadata/export evidence, not evidence of hosted problem-version mapping. | Preserve split labels in metadata and hosted problem metadata when uploading exact versions. |
| `hidden_references_not_public_runtime_assets` | caution | hidden references are not in public runtime assets | Local public export and wrapper mitigation pass, but hosted filesystem-tool isolation on uploaded images is still unproven. | Run hosted preflight/Env Linter and record proof that tools cannot read hidden references, hidden pins, wrong submissions, or transient bundles. |


## Report And Evidence Files

The long generated evidence tables are intentionally outside this main report:

- `reports/evidence_appendix.md`: full generated report appendix with row-level audit tables and validation manifest details.
- `reports/concise_metr_report.md`: shortest reviewer-facing METR-style narrative.
- `reports/requirement_coverage.md`: requirement-by-requirement evidence.
- `reports/report_source_traceability.md`: section-by-section source map for this main report.
- `reports/report_count_consistency_audit.md`: top-line count drift detector across reports, manifests, and committed CSV/JSON sources.
- `reports/final_delivery_checklist_audit.md`: strict playbook final-delivery checklist mapped to committed evidence, with pass@k, hosted QA, and version-freeze blockers kept visible.
- `reports/regeneration_command_consistency.md`: synchronization check for README, manifest, manifest-source, and reviewer local-replay commands.
- `reports/taiga_wrapper_isolation_audit.md`: local hidden-bundle wrapper smoke audit; mitigation evidence only, not hosted filesystem-tool isolation evidence.
- `reports/model_sweep_coverage_audit.md`: strict planned-cell coverage ledger distinguishing pass@k-ready provider rows from smoke-only or missing cells.
- `reports/data_schema_manifest.md`: schema/data-dictionary boundary audit for core datasets and generated CSVs.
- `reports/reviewer_reproduction_packet.md`: ordered local replay workflow, expected artifacts, failure interpretations, and external-evidence boundaries.
- `reports/clean_workspace_replay.md`: bounded temporary-workspace replay of dependency materialization, Lean build, grader pass/fail behavior, and public export validation.
- `reports/candidate_pruning_audit.md`: per-task pruning ledger explaining accepted, calibration-only, and rejected decisions from metadata and difficulty signals.
- `reports/accepted_task_cards.md`: per-accepted-task synthesis of review status, proof signals, pin-stage evidence, local QA, asset counts, and benchmark-grade blockers.
- `reports/independent_task_review_packet.md`: non-author accepted-task review plan, blank template, and schema for future independent review collection.
- `reports/independent_review_status_audit.md`: packet-readiness and missing completed-review status audit.
- `reports/construct_validity_matrix.md`: task-level construct-validity trace for accepted rows.
- `reports/claim_authorization_matrix.md`: allowed, caveated, and blocked claim wording.
- `reports/research_claim_gap_matrix.md`: evidence packages needed before stronger claims are allowed.
- `reports/freeze_readiness_roadmap.md`: locked-benchmark gates.
- `reports/failure_label_review_audit.md`: single-review smoke transcript adjudication audit.
- `reports/statistical_analysis_plan.md`: claim-tier evidence thresholds and Wilson precision ledger for future model-result reporting.
- `reports/figure_manifest.md`: source-data and claim-boundary ledger for generated figures and blocked performance plots.
- `reports/threat_coverage_audit.md`: mapping from open blockers and non-allowed claims to threats-to-validity rows.

## Reproducibility Checklist

`reports/reviewer_reproduction_packet.md` and `data/reviewer_reproduction_steps.csv` turn the local replay and external-evidence surface into an ordered reviewer workflow.

- reproduction steps: `17`
- phase counts: `{"external_evidence": 3, "local_replay": 14}`
- status counts: `{"blocked_external_evidence": 3, "ready": 14}`
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
| `model_sweep_coverage` | local_replay | ready | `python scripts/audit_model_sweep_coverage.py` | This audit does not create new model evidence; it only classifies coverage of existing rows. |
| `grader_hardening` | local_replay | ready | `python scripts/audit_grader_hardening.py` | The scanner remains lexical source scanning, not a complete Lean parser. |
| `public_export` | local_replay | ready | `python scripts/export_public_tasks.py --out public_tasks` | The export is a local directory snapshot, not a hosted problem version. |
| `public_export_validation` | local_replay | ready | `python scripts/validate_public_export.py --out public_tasks` | This does not run Taiga Full Env QA or Env Linter. |
| `taiga_metadata_template` | local_replay | ready | `python scripts/generate_taiga_problem_metadata.py` | The template uses placeholder image values; it is not a hosted problem-version record or QA result. |
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
| `workspace_materialization` | setup | pass | 68.53 | This is a local clean workspace from the current working tree, not a remote clone or hosted container. |
| `mathlib_cache_get` | replay | pass | 657.98 | This uses the Mathlib cache for local dependency materialization; hosted runners need their own cache or build path. |
| `clean_lake_build` | replay | pass | 5.65 | Local toolchain and dependency resolution can differ from hosted QA. |
| `reference_validation_smoke` | replay | pass | 33.68 | This is a representative reference-validation smoke, not full validate_all coverage. |
| `wrong_submission_smoke` | replay | pass | 5.41 | This probes expected-fail behavior for one semantic-pin wrong submission only. |
| `public_export_smoke` | replay | pass | 0.74 | Local public export is not hosted problem packaging. |
| `public_export_validation_smoke` | replay | pass | 133.20 | This validates local public assets but does not run Env Linter. |


The local regeneration gate is recorded in `README.md`, `reports/validation_manifest.json`, `reports/validation_manifest_audit.md`, `reports/regeneration_command_consistency.md`, `reports/reviewer_reproduction_packet.md`, and `reports/clean_workspace_replay.md`. The manifest audit verifies command coverage, current artifact hashes, public-export summary, and the policy that the manifest records generation-time git state rather than a post-commit clean-checkout proof. The command-consistency audit checks that README, manifest-source, committed manifest, and reviewer local-replay commands stay synchronized. The public export validator checks that hidden references and wrong submissions are absent from `public_tasks`, all metadata-listed public files are present, exported Lean files compile, and obvious hidden-reference path strings do not leak.

## Claim Ledger

| claim | current evidence | status |
| --- | --- | --- |
| Local references and wrong submissions validate as expected | `python scripts/validate_all.py`; `data/run_results.csv`; local QA transcripts | supported locally |
| Public task export excludes hidden material | `python scripts/export_public_tasks.py --out public_tasks`; `python scripts/validate_public_export.py --out public_tasks` | supported locally |
| Accepted core tasks are higher quality than the original pool | `reports/accepted_task_review.md`; `reports/difficulty_audit.md`; downgraded metadata statuses | supported by internal review |
| v0.1 is a locked benchmark | independent timing, completed independent task reviews, hosted QA, broader model sweeps, and freeze review are missing | not supported |
| Reported model pass rates characterize frontier performance | only tiny smoke-sweep rows are committed | not supported |

## Limitations

- The v0.1 accepted core is below the 20-task target because the original pool did not meet the diagnostic-quality bar.
- The release has limited T3 coverage and no accepted T4 stretch task yet.
- Human-time estimates are author/reviewer estimates, not measured independent solves, and no completed non-author task-quality reviews are committed yet.
- Hidden pins are stronger than type checks, but they remain finite semantic probes.
- Only a tiny real provider smoke sweep is committed; it is adapter/proof-debugging evidence, not a benchmark performance claim.
- Hosted Taiga/Env Linter QA is not represented in this local artifact.
- The artifact is not a locked benchmark. The accepted rows still need independent human timing, broader scaffold data, and external QA before a freeze.

## Before Claiming A Locked Benchmark

The next step is to add more high-quality T2/T3/T4 tasks, collect independent human timing and task-quality reviews, execute real provider smoke sweeps across the scaffold ladder, run hosted QA, settle linter findings, and freeze exact public task versions.
