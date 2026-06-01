# Lean Time-Horizon Benchmark v0.1 Evidence Appendix

## Abstract

This repository is a v0.1 Lean time-horizon evaluation artifact for studying how far models get on realistic formalization and verification tasks as task horizon increases. It is not a locked benchmark. The release set contains 6 accepted core tasks and 8 calibration-only tasks. The remaining 12 tasks are retained as a rejected archive, and 0 tasks remain pending review.

The accepted core set is intentionally smaller than the original target of 20. The original task batch was downgraded because many rows were dominated by `rfl`, `simp`, `omega`, `cases`, or one obvious library lemma. A stricter accepted-task review is maintained in `reports/accepted_task_review.md`; v0.1 keeps downgraded rows out of benchmark statistics unless they serve a calibration role.

## Reader Guide

`reports/concise_metr_report.md` is the reviewer-facing concise narrative. This file is the detailed generated evidence appendix: it intentionally includes long tables, hashes, and audit rows that should not be read as a locked-benchmark claim.

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
| `run_results` | schema_valid | 69 | `data/run_results_schema.json` | Schema validation does not prove sample-size adequacy or model-result representativeness. | Run scripts/audit_run_integrity.py after edits to check transcript and arithmetic semantics. |
| `failure_annotations` | empty_ready | 0 | `data/failure_label_schema.json` | Empty adjudication data cannot support failure-distribution claims. | Populate after broad provider sweeps and independent transcript review. |
| `failure_label_reviews` | schema_valid | 3 | `data/failure_label_review_schema.json` | These are single-review smoke rows, not independent distributional adjudication. | Use the transcript review packet and adjudication fields for future broad sweeps. |
| `human_time_observations` | empty_ready | 0 | `data/human_time_observations_schema.json` | Author/reviewer estimates remain uncalibrated by independent timed solves. | Collect non-author timing rows before strengthening time-horizon claims. |
| `independent_task_reviews` | empty_ready | 0 | `data/independent_task_review_schema.json` | Empty review data cannot support independent acceptance, time-bucket, hidden-pin, or wrong-submission adequacy claims. | Collect non-author review rows for every accepted_v0 task before strengthening benchmark-grade task-quality claims. |
| `failure_label_codebook` | codebook_valid | 13 | `data/failure_label_schema.json` | The codebook is a taxonomy definition, not evidence that those failures dominate. | Update the codebook and downstream audits together if labels change. |
| `derived_reporting_csv_inventory` | inventory_documented | 61 | `` | Most generated audit CSVs are governed by their producer scripts and manifest hashes rather than standalone JSON schemas. | Add standalone schemas only for files that become external data contracts or model-run inputs. |


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
| `lt-204` | 36 | false | semantic | 2 | maybe | high |
| `lt-205` | 42 | false | semantic | 2 | unlikely | high |
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
| `lt-204` | keep | 36 lines; automation=false; one-shot=maybe | semantic_pins_exercised; stages `{"hidden_pin": 1, "public_stage": 1}` | `{"expected_failure": 2, "passed": 1}` | Collect independent timing, hosted QA, and accepted-core scaffold/model evidence before benchmark freeze. independent human timing; accepted-core scaffold sweep; hosted QA evidence Mutable definitions have public-comp... |
| `lt-205` | keep | 42 lines; automation=false; one-shot=unlikely | semantic_pins_exercised; stages `{"hidden_pin": 1, "public_stage": 1}` | `{"expected_failure": 2, "passed": 1}` | Independently time at least one human solve and run the planned scaffold sweep before using this as long-horizon evidence. independent human timing; accepted-core scaffold sweep; hosted QA evidence; extra timing revie... |
| `lt-206` | keep_with_caveat | 60 lines; automation=true; one-shot=maybe | semantic_pins_exercised; stages `{"hidden_pin": 2, "unknown": 2}` | `{"expected_failure": 2, "passed": 1}` | Retain in v0.1 only with the recorded caveat; collect independent human timing, full scaffold sweep evidence, and external QA before freeze. independent human timing; accepted-core scaffold sweep; hosted QA evidence M... |


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

## Diagnostic Coverage Audit

`reports/diagnostic_coverage_audit.md` and `data/diagnostic_coverage_audit.csv` map accepted_v0 tasks to playbook task families, diagnostic capabilities, failure-label coverage, automation caveats, one-shot solvability balance, and construct-validity gaps.

- checks: `15`
- statuses: `{"block": 1, "caution": 3, "pass": 11}`
- areas: `{"construct_validity": 1, "data_integrity": 1, "diagnostic_capability": 7, "diagnostic_metadata": 1, "failure_taxonomy": 1, "portfolio_shape": 2, "task_validity": 2}`
- caution rows: `3`
- blocked construct-validity rows: `1`
- failing data-integrity rows: `0`

Diagnostic coverage checks:

| check | area | status | accepted tasks | diagnostic limit | next action |
| --- | --- | --- | ---: | --- | --- |
| `family_mix` | portfolio_shape | pass | 6 | Family diversity is represented, but most families have only one accepted task. | Add more accepted rows per family before using family-level performance summaries. |
| `direct_theorem_balance` | portfolio_shape | pass | 1 | Direct theorem proving is present but does not dominate accepted_v0. | Keep direct theorem proving as one slice of the portfolio rather than the main task type. |
| `capability_library_search` | diagnostic_capability | caution | 1 | Capability is represented by a singleton accepted task, so task-specific quirks can dominate. | Add at least two independently reviewed accepted tasks for each core diagnostic capability before making capability-level claims. |
| `capability_theorem_decomposition` | diagnostic_capability | pass | 6 | Capability is represented by more than one accepted task. | Add at least two independently reviewed accepted tasks for each core diagnostic capability before making capability-level claims. |
| `capability_semantic_formalization` | diagnostic_capability | caution | 1 | Capability is represented by a singleton accepted task, so task-specific quirks can dominate. | Add at least two independently reviewed accepted tasks for each core diagnostic capability before making capability-level claims. |
| `capability_proof_debugging` | diagnostic_capability | pass | 2 | Capability is represented by more than one accepted task. | Add at least two independently reviewed accepted tasks for each core diagnostic capability before making capability-level claims. |
| `capability_codebase_navigation` | diagnostic_capability | caution | 1 | Capability is represented by a singleton accepted task, so task-specific quirks can dominate. | Add at least two independently reviewed accepted tasks for each core diagnostic capability before making capability-level claims. |
| `capability_invariant_design` | diagnostic_capability | pass | 2 | Capability is represented by more than one accepted task. | Add at least two independently reviewed accepted tasks for each core diagnostic capability before making capability-level claims. |
| `capability_long_horizon_construction` | diagnostic_capability | pass | 3 | Capability is represented by more than one accepted task. | Add at least two independently reviewed accepted tasks for each core diagnostic capability before making capability-level claims. |
| `failure_mode_metadata_density` | diagnostic_metadata | pass | 6 | Expected failure modes are documented, but they are author forecasts until provider transcripts accumulate. | Compare predicted failure modes to independently labeled model transcripts after the full scaffold sweep. |
| `capability_failure_label_alignment` | failure_taxonomy | pass | 6 | Failure labels can describe the intended capabilities, but committed provider transcripts are too sparse for distributional analysis. | Use the mapped labels during transcript review and revisit the taxonomy after broad model sweeps. |
| `automation_caveat_coverage` | task_validity | pass | 2 | Automation-dominated retained tasks are visible caveat rows, not hidden as benchmark-grade proof difficulty. | Keep automation caveats in task metadata and do not use these rows as standalone evidence of long-horizon proof difficulty. |
| `one_shot_solvability_balance` | task_validity | pass | 0 | The accepted core is not dominated by rows expected to be easy one-shot, but estimates are internal judgments. | Replace internal solvability estimates with measured scaffold runs before performance claims. |
| `time_horizon_construct_limit` | construct_validity | block | 6 | Accepted_v0 has no T4 task and only one T3 task; the current set cannot support strong time-horizon claims. | Add independently timed T3/T4 tasks, including a T4 stretch row, before claiming robust time-horizon measurement. |
| `quality_matrix_join_integrity` | data_integrity | pass | 6 | Diagnostic coverage depends on the task quality matrix joining metadata and difficulty audit rows correctly. | Regenerate difficulty audit and task quality matrix before this audit whenever task metadata changes. |


## Construct Validity Matrix

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

Human-time buckets follow the project playbook:

- `T0`: 5-15 minutes.
- `T1`: 15-45 minutes.
- `T2`: 45-120 minutes.
- `T3`: 2-6 hours.
- `T4`: 6+ hours.

The p50/p90 estimates in metadata are reviewer estimates, not measured independent solves. The hard review downgraded three rows from accepted core to calibration-only because their proof surface and likely one-shot solvability did not justify accepted T2 status.

## Human-Time Calibration Audit

`reports/human_time_calibration_audit.md` and `data/human_time_calibration_audit.csv` check that metadata p50 estimates fall inside their assigned bucket, p90 is not below p50, manual review status is recorded, and independent human timing observations are explicitly counted.

- tasks audited: `26`
- calibration statuses: `{"caution": 6, "pass": 20}`
- task buckets: `{"T1": 18, "T2": 7, "T3": 1}`
- issue counts: `{"accepted_without_independent_timing": 6}`
- accepted-core tasks without successful independent timing: `6/6`

Accepted-core human-time rows:

| task | bucket | p50/p90 | bucket range | status | timings | issues |
| --- | --- | ---: | --- | --- | ---: | --- |
| `lt-201` | T2 | 75/150 | 45-120 | caution | 0 | `["accepted_without_independent_timing"]` |
| `lt-203` | T2 | 90/180 | 45-120 | caution | 0 | `["accepted_without_independent_timing"]` |
| `lt-202` | T2 | 90/180 | 45-120 | caution | 0 | `["accepted_without_independent_timing"]` |
| `lt-204` | T2 | 100/200 | 45-120 | caution | 0 | `["accepted_without_independent_timing"]` |
| `lt-205` | T3 | 150/300 | 120-360 | caution | 0 | `["accepted_without_independent_timing"]` |
| `lt-206` | T2 | 100/210 | 45-120 | caution | 0 | `["accepted_without_independent_timing"]` |


## Human Timing Collection Packet

`reports/human_timing_collection_packet.md`, `data/human_timing_collection_plan.csv`, and `data/human_time_observations_template.csv` make independent timing collection operational without fabricating observations.

- accepted tasks in timing plan: `6`
- bucket counts: `{"T2": 5, "T3": 1}`
- family counts: `{"algorithm_correctness": 1, "direct_theorem_proving": 1, "informal_spec_to_formal": 1, "invariant_verification_ml_optimization": 1, "proof_repair_codebase": 1, "small_formal_library_construction": 1}`
- validation commands containing hidden-reference paths: `0`

Accepted-task timing collection plan:

| task | bucket | p50/p90 | condition | validation command |
| --- | --- | ---: | --- | --- |
| `lt-201` | T2 | 75/150 | public prompt plus public scaffold; use one consistent condition per reviewer and record lookup/compile feedback use | `python scripts/validate_task.py tasks/dev/lt-201-multifile-cache-repair --submission <reviewer-solution.lean> --expect pass` |
| `lt-203` | T2 | 90/180 | public prompt plus public scaffold; use one consistent condition per reviewer and record lookup/compile feedback use | `python scripts/validate_task.py tasks/dev/lt-203-exact-cover-spec --submission <reviewer-solution.lean> --expect pass` |
| `lt-202` | T2 | 90/180 | public prompt plus public scaffold; use one consistent condition per reviewer and record lookup/compile feedback use | `python scripts/validate_task.py tasks/test/lt-202-mathlib-image-preimage --submission <reviewer-solution.lean> --expect pass` |
| `lt-204` | T2 | 100/200 | public prompt plus public scaffold; use one consistent condition per reviewer and record lookup/compile feedback use | `python scripts/validate_task.py tasks/test/lt-204-caplist-sum-invariant --submission <reviewer-solution.lean> --expect pass` |
| `lt-205` | T3 | 150/300 | public prompt plus public scaffold; read-only lookup allowed only if recorded; compile/debug feedback allowed only if recorded | `python scripts/validate_task.py tasks/test/lt-205-bag-count-library --submission <reviewer-solution.lean> --expect pass` |
| `lt-206` | T2 | 100/210 | public prompt plus public scaffold; use one consistent condition per reviewer and record lookup/compile feedback use | `python scripts/validate_task.py tasks/test/lt-206-partition-count-correctness --submission <reviewer-solution.lean> --expect pass` |


## Transcript Review Packet

`reports/transcript_review_packet.md`, `data/transcript_review_queue.csv`, and `data/failure_label_review_template.csv` make failure-label review operational without fabricating adjudicated labels.

- queued non-local rows: `3`
- review priorities: `{"high": 1, "low": 1, "medium": 1}`
- current failure labels: `{"infra_failure": 1, "none": 1, "proof_debugging": 1}`
- QA finding statuses: `{"unreviewed": 3}`
- missing transcript files in queue: `0`
- high/critical review rows: `1`

Transcript review queue:

| priority | run id | task | scaffold | pass@k | current label | action |
| --- | --- | --- | --- | ---: | --- | --- |
| high | `anthropic-claude-sonnet-4-6-one-shot-1780206167:lt-201` | `lt-201` | one-shot | 0.0 | `proof_debugging` | Review failed non-infra model row and record rationale. |
| medium | `anthropic-claude-sonnet-4-6-one-shot-1780206126:lt-201` | `lt-201` | one-shot | 0.0 | `infra_failure` | Confirm this is an infrastructure failure and record whether the row should be rerun. |
| low | `anthropic-claude-sonnet-4-6-one-shot-1780206109:lt-001` | `lt-001` | one-shot | 1.0 | `none` | Confirm success transcript and keep primary label `none`. |


## Failure Label Review Audit

`reports/failure_label_review_audit.md`, `data/failure_label_review_audit.csv`, and `data/failure_label_reviews.csv` check that committed single-review smoke adjudications cite transcript evidence and preserve the no-distributional-claims boundary.

- checks: `6`
- statuses: `{"pass": 6}`
- areas: `{"claim_boundary": 1, "coverage": 1, "evidence": 1, "labels": 1, "review_process": 1, "schema": 1}`
- failures: `0`

Failure-label review audit rows:

| check | area | status | evidence | limitation |
| --- | --- | --- | --- | --- |
| `review_schema` | schema | pass | review rows=3; required_fields_covered=11/11; duplicates=[]; schema_exists=True | The schema records review metadata; it does not imply independent adjudication. |
| `queue_coverage` | coverage | pass | queue_rows=3; review_rows=3; missing_reviews=[]; extra_reviews=[]; model_rows_missing_queue=[] | Coverage is over the tiny committed smoke queue only. |
| `label_validity` | labels | pass | valid_labels=14; invalid_labels=[]; none_on_failure=[]; run_result_label_mismatches=[] | The review currently agrees with the run-record label; it has not been independently double-coded. |
| `transcript_evidence` | evidence | pass | evidence_excerpt_missing_or_not_in_transcript=[]; short_rationales=[] | Evidence excerpts are short anchors, not a substitute for full transcript inspection. |
| `review_metadata` | review_process | pass | reviewers={"codex_internal_review": 3}; bad_confidence=[]; bad_adjudication_flags=[]; adjudication_needed=[] | All current rows are single internal reviews; this is weaker than independent adjudication. |
| `claim_boundary` | claim_boundary | pass | transcript_packet_mentions_distribution_boundary=True | A reviewed smoke queue can support transcript-provenance claims only, not model-failure prevalence claims. |


## Grader And Integrity Controls

The grader is Lean-first. For each submission it copies the public files listed in `metadata.json`, replaces the submission file, scans forbidden constructs, compiles public Lean files, compiles hidden semantic pins, and audits axioms on declared targets. Accepted and calibration tasks must have at least two wrong submissions.

Hidden pins check more than type signatures where possible: semantic formalization tasks include positive and negative examples; invariant tasks include edge cases and downstream bundled consequences; library tasks include downstream reuse through public lemmas. The grader still cannot prove that a task measures every intended cognitive skill, and it cannot replace human review of whether a task is too automation-dominated.

The axiom policy allows only the standard Lean axioms documented in `docs/axiom_policy.md`. Source-level escape hatches such as `sorry`, `admit`, `axiom`, `constant`, `unsafe`, custom elaboration, and command execution are rejected by the forbidden-construct scanner before Lean grading.

## Grader Hardening Audit

`reports/grader_hardening_audit.md` and `data/grader_hardening_audit.csv` probe local anti-gaming controls: forbidden-construct scanner coverage, comment/string false-positive controls, task-specific bans, grader stage ordering, axiom allowlist consistency, validation-command coverage, and local QA reference/wrong outcomes.

- checks: `9`
- statuses: `{"pass": 9}`
- areas: `{"axiom_audit": 2, "forbidden_scanner": 3, "grader_pipeline": 1, "validation_manifest": 3}`
- failing hardening checks: `0`

Grader hardening checks:

| check | area | status | hardening limit | next action |
| --- | --- | --- | --- | --- |
| `default_forbidden_detection` | forbidden_scanner | pass | This probes scanner token matching, not every Lean syntax context where a term can appear. | Add regression cases whenever the forbidden list changes. |
| `comment_string_false_positive_control` | forbidden_scanner | pass | The scanner strips comments and strings but remains a lexical source scanner, not a full Lean parser. | Keep false-positive controls broad enough that prompts can mention banned constructs safely. |
| `task_specific_forbidden_control` | forbidden_scanner | pass | Only one archived direct-theorem row currently needs task-specific bans. | Use task-specific `extra_forbidden` whenever a shortcut would trivialize a task. |
| `grader_stage_order` | grader_pipeline | pass | This is a source-order audit; full behavior is also covered by validate_all and local QA transcripts. | Preserve the order: copy public assets, scan forbidden constructs, compile public files, compile hidden pins, then audit axioms. |
| `axiom_policy_allowlist_match` | axiom_audit | pass | Allowlist equality does not prove each theorem is axiom-free beyond allowed Lean axioms; validate_task performs per-declaration checks. | Update docs/axiom_policy.md and validate_task.py together if the policy changes. |
| `release_axiom_declaration_coverage` | axiom_audit | pass | The audit checks metadata coverage, while validate_task checks actual axiom output during grading. | Require nonempty `axiom_audit_declarations` for every release task. |
| `validation_command_manifest_coverage` | validation_manifest | pass | The manifest lists validation commands; it does not prove they were run unless paired with validate_all output and run_integrity. | Regenerate validation_commands.csv with validate_all.py after task set changes. |
| `local_qa_reference_wrong_outcomes` | validation_manifest | pass | Local QA rows are validation evidence only, not model-performance evidence. | Require reference rows to pass and plausible-wrong rows to fail before report regeneration. |
| `structural_validation_controls` | validation_manifest | pass | These are static controls; task validity still depends on human review and hidden pins. | Keep structural checks in validate_all.py aligned with acceptance policy. |


## Public Export

`scripts/export_public_tasks.py` exports the release set by default: `accepted_v0`, `calibration_only`, and pending candidates if any. It copies every file listed in metadata `public_files` plus `Prompt.md` and `metadata.json`. `scripts/validate_public_export.py` checks that hidden and wrong directories are absent, all public files are present, exported Lean files compile, and obvious hidden-reference path strings do not leak.

## Prompt Contract Audit

`reports/prompt_contract_audit.md` and `data/prompt_contract_audit.csv` audit release prompts against public prompt standards. The audit evaluates `Prompt.md` plus the runner wrapper because the wrapper supplies scaffold-specific lookup, attempt-limit, and submission-format instructions.

- prompt rows: `14`
- statuses: `{"caution": 14}`
- failing rows: `0`
- hidden-material leak rows: `0`
- runner-supplied field counts: `{"attempt_limit": 14, "submission_format": 11, "tool_affordance": 14}`
- missing/caution field counts: `{}`

Prompt contract rows:

| task | status | checks | runner-supplied fields | missing/caution fields | leaks |
| --- | --- | ---: | --- | --- | --- |
| `lt-001` | caution | 11/11 | `["attempt_limit", "tool_affordance"]` | `[]` | `[]` |
| `lt-002` | caution | 11/11 | `["attempt_limit", "tool_affordance"]` | `[]` | `[]` |
| `lt-003` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-004` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-201` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-203` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-101` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-105` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-107` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-108` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-202` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-204` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-205` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-206` | caution | 11/11 | `["attempt_limit", "tool_affordance"]` | `[]` | `[]` |


## Scaffold And Model-Run Support

The supported scaffold ladder is `one-shot`, `lookup`, and `lookup_unlimited`. Lookup is a real read-only command, `python scripts/lean_lookup.py QUERY`, which searches metadata-listed public Lean task files and installed Std/Mathlib files when available. External model runners receive `PROMPT_PATH`, `MODEL`, `TASK_ID`, `ATTEMPT_INDEX`, `SCAFFOLD`, `LEAN_LOOKUP_COMMAND`, `TASK_PUBLIC_DIR`, and `TASK_PUBLIC_FILES`.

## Scaffold Support Audit

`reports/scaffold_support_audit.md` and `data/scaffold_support_audit.csv` audit the scaffold ladder itself: prompt affordances, runner environment contract, attempt-count semantics, lookup safety, planned sweep coverage, observed provider coverage, and the boundary around scaffold-effect claims.

- checks: `11`
- statuses: `{"caution": 1, "pass": 10}`
- areas: `{"evaluation_protocol": 2, "lookup_integrity": 3, "reporting": 1, "runner_contract": 3, "scaffold_contract": 2}`
- failing checks: `0`
- caution checks: `1`

Scaffold audit table:

| check | area | status | evidence | next action |
| --- | --- | --- | --- | --- |
| `scaffold_catalog_complete` | scaffold_contract | pass | scaffold rows=3; names=["lookup", "lookup_unlimited", "one-shot"]; mismatches=[]; extras=[]. | Keep data/scaffold_variants.csv aligned with runner and protocol semantics. |
| `prompt_affordance_contract` | scaffold_contract | pass | {"lookup_mentions_lookup_command": true, "lookup_no_feedback_section": true, "one_shot_no_lookup": true, "sample_task": "lt-201", "unlimited_mentions_feedback": true, "unlimited_mentions_lookup": true} | Keep scaffold-specific prompt text explicit whenever runner semantics change. |
| `runner_env_contract` | runner_contract | pass | missing env keys=[]; provider env map complete=True. | Keep runner environment variables stable for provider adapters and transcripts. |
| `iterative_feedback_gate` | runner_contract | pass | lookup_unlimited-only feedback gate present=True. | Preserve feedback only for lookup_unlimited so lookup remains one-submission. |
| `attempt_count_semantics` | runner_contract | pass | attempt loop and k/success fields present=True. | Keep k, attempts_completed, successes_out_of_k, and pass_at_k tied to the same attempt budget. |
| `lookup_roots_public_only` | lookup_integrity | pass | lookup roots=29; public task lean files=27; mathlib/std roots=1; hidden_or_wrong_roots=0. | Never add tasks/ as a whole-tree root; include only metadata-listed public Lean files. |
| `lookup_command_smoke` | lookup_integrity | pass | {"hidden_or_wrong_line_count": 0, "line_count": 26, "query": "Set.image", "returncode": 0, "sample": ["C:\\Users\\sebas\\lean-time-horizon\\tasks\\test\\lt-202-mathlib-image-preimage\\Task.lean:6:    Set.Subset s (Set.preimage f (Set.image f s)) := by", "C:\\Users\\sebas\\lean-time-horizon\\tasks\\test\\lt-202-mathlib-image-preimage\\Task.lean:10:    Set.Subset (Set.image f (Set.preimage f t)) t := by", "C:\\Users\\sebas\\lean-time-horizon\\tasks\\test\\lt-202-mathlib-image-preimage\\Task.lean:15:    Set.preimage f (Set.image f s) = s := by"]} | Keep lookup command read-only and runnable without provider credentials. |
| `lookup_hidden_leak_scan` | lookup_integrity | pass | [{"hidden_or_wrong_line_count": 0, "line_count": 101, "query": "Set.image", "returncode": 0}, {"hidden_or_wrong_line_count": 0, "line_count": 0, "query": "PinCheck", "returncode": 0}] | Keep hidden and wrong directories out of lookup roots and public exports. |
| `planned_sweep_coverage` | evaluation_protocol | pass | expected pairs=18; planned pairs=18; missing=[]; planned_k_values=["10"]. | Regenerate the evaluation protocol whenever accepted tasks or scaffold variants change. |
| `observed_scaffold_data_coverage` | evaluation_protocol | caution | non-infra accepted-provider rows=1; observed pairs=1/18; observed scaffolds=["one-shot"]. | Run accepted-core provider rows across one-shot, lookup, and lookup_unlimited before scaffold-effect claims. |
| `scaffold_claim_boundary` | reporting | pass | claim scaffold_effects=unsupported; decision scaffold_effect_claim=block. | Keep scaffold-effect claims blocked until observed scaffold coverage reaches the planned sweep. |


## Evaluation Protocol

`reports/evaluation_protocol.md` defines the planned primary analysis before broad model sweeps are run. The primary plan is accepted-core tasks crossed with the scaffold ladder at fixed `k`.

- planned task count: `6`
- planned rows in `data/model_sweep_plan.csv`: `18`
- planned k values: `10`
- scaffold row counts: `{"lookup": 6, "lookup_unlimited": 6, "one-shot": 6}`

The protocol specifies that headline capability claims use accepted-core rows only, local QA is validation evidence only, infra failures are retained but excluded from capability means, and binary task-row means should report numerators, denominators, and Wilson intervals.


## Model Sweep Execution Packet

`reports/model_sweep_execution_packet.md`, `data/model_sweep_execution_commands.csv`, and `data/model_sweep_execution_checklist.csv` turn the prospective scaffold sweep into concrete provider-route commands and post-run evidence checks without calling APIs or creating model results.

- command rows: `12`
- scaffold command counts: `{"lookup": 4, "lookup_unlimited": 4, "one-shot": 4}`
- provider routes: `{"anthropic": 3, "command": 3, "gemini": 3, "openai": 3}`
- checklist statuses: `{"blocked": 3, "planned": 1, "ready": 3}`
- command rows with direct API-key assignments: `0`

Model-sweep evidence checklist:

| check | phase | status | next action |
| --- | --- | --- | --- |
| `local_validation_before_sweep` | pre_run | ready | Run lake build, validate_all, public export validation, and run_integrity immediately before provider sweeps. |
| `provider_runner_contract` | pre_run | ready | Set the relevant runner env var and provider API key in the shell only; run a one-task smoke command first. |
| `scaffold_ladder_contract` | pre_run | ready | Keep one-shot, lookup, and lookup_unlimited prompt semantics fixed across provider runs. |
| `planned_primary_cells` | run | planned | Run exactly the accepted_v0 x scaffold commands for each provider/model being reported. |
| `transcript_and_run_result_evidence` | post_run | blocked | Commit run_results rows and transcript JSONL files, regenerate the transcript queue, complete failure-label review rows, then rerun integrity and model-result analysis. |
| `frontier_claim_boundary` | post_run | blocked | Keep frontier and scaffold-effect claims unsupported until non-infra accepted-core coverage is broad enough. |
| `statistical_report_refresh` | post_run | blocked | Rerun statistical reporting after provider rows are committed; report raw n and Wilson intervals. |


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

`reports/model_evidence_provenance_audit.md` and `data/model_evidence_provenance_audit.csv` check that model evidence in the report is traceable to committed run rows with model versions, k values, transcripts, sample sizes, infra accounting, and local-QA exclusion.

- checks: `7`
- statuses: `{"pass": 7}`
- areas: `{"analysis_data": 1, "claim_boundary": 2, "report_text": 1, "run_data": 3}`

Model-evidence provenance checks:

| check | area | status | evidence | limitation | required action |
| --- | --- | --- | --- | --- | --- |
| `provider_row_inventory` | run_data | pass | provider_rows=3; noninfra_provider_rows=2; accepted_provider_rows=2; accepted_noninfra_rows=1; calibration_provider_rows=1; local_qa_rows=66 | Provider rows are smoke evidence only and are underpowered for benchmark claims. | Keep provider rows separate from local QA rows and rerun this audit after every sweep. |
| `model_version_and_k_completeness` | run_data | pass | model_versions=["anthropic:claude-sonnet-4-6"]; k_values=["1"]; scaffolds={"one-shot": 3}; missing_required_rows=[]; duplicate_jobs=[] | Current model-version rows are tiny smoke rows, not a model-comparison dataset. | Require model, model_version, job_id, k, and transcript_link on every future non-local row. |
| `transcript_provenance` | run_data | pass | provider_transcripts=3; missing_transcripts=[] | Transcript existence plus single-review labels does not imply independent adjudication or representative failure-mode coverage. | Keep transcript files committed, audit review rows against transcript evidence, and require independent adjudication before failure-distribution claims. |
| `summary_count_consistency` | analysis_data | pass | summary_rows=0; mismatches=[]; primary_planned_cells=missing; primary_covered_noninfra=missing | The summary intentionally records undercoverage rather than performance conclusions. | Regenerate scripts/analyze_model_results.py after any run_results change. |
| `report_sample_size_and_version_disclosure` | report_text | pass | model_versions_in_detailed_report=1/1; missing_versions=[]; missing_main_phrases=[]; missing_model_analysis_phrases=[] | The concise report summarizes counts but leaves full model-version rows to the detailed evidence appendix. | Keep sample sizes, k, infra policy, and model versions visible in generated report text. |
| `local_qa_exclusion_boundary` | claim_boundary | pass | local_qa_rows=66; provider_rows=3 | Local QA rows validate grading behavior and must not enter model-capability summaries. | Keep local QA excluded from model_result_summary and benchmark pass-rate text. |
| `infra_policy_boundary` | claim_boundary | pass | provider_infra_rows=1; accepted_infra_rows=1 | Provider reliability claims need many more rows; this row only checks accounting policy disclosure. | Retain infra rows in raw data and report them separately from capability means. |


## Statistical Analysis Plan

`reports/statistical_analysis_plan.md`, `data/statistical_design_thresholds.csv`, and `data/wilson_precision_table.csv` define minimum evidence thresholds before stronger model-result claims are allowed. This is a precision and claim-tier ledger, not new model evidence.

- claim tiers: `7`
- tier statuses: `{"blocked": 6, "supported": 1}`
- claim types: `{"benchmark_status": 1, "descriptive_performance": 1, "failure_analysis": 1, "performance_comparison": 1, "run_provenance": 1, "subgroup_performance": 1, "time_horizon_performance": 1}`
- blocked tiers: `6`
- Wilson precision rows: `15`

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


## Statistical Reporting Audit

`reports/statistical_reporting_audit.md` and `data/statistical_reporting_audit.csv` check whether the committed provider rows can support the playbook's recommended performance plots and claims.

- checks: `9`
- statuses: `{"block": 5, "pass": 4}`
- areas: `{"data_hygiene": 2, "planned_sweep": 1, "recommended_plot": 4, "report_text": 1, "statistical_method": 1}`
- blocked performance outputs: `5`
- failing statistical hygiene checks: `0`

Statistical reporting checks:

| check | area | status | current sample | limitation | next action |
| --- | --- | --- | --- | --- | --- |
| `primary_sweep_coverage` | planned_sweep | block | 1/18 accepted task/scaffold cells covered by non-infra provider rows | The committed provider rows cannot support accepted-core performance estimates. | Run the planned accepted_v0 x scaffold sweep before reporting benchmark performance. |
| `main_report_performance_estimate_suppression` | report_text | pass | 1/18 accepted task/scaffold cells covered by non-infra provider rows | The main report should not display performance-style estimates when primary sweep coverage is blocked. | Suppress mean/interval wording in the main report until the planned accepted-core sweep is covered. |
| `scaffold_pass_at_k_plot` | recommended_plot | block | 1/3 scaffolds observed; 1 non-infra accepted-core rows | A mean pass@10-by-scaffold plot would imply comparisons the data do not support. | Populate all one-shot, lookup, and lookup_unlimited cells before generating scaffold-effect plots. |
| `bucket_success_plot` | recommended_plot | block | 1 human-time buckets observed in non-infra accepted-core provider rows | Current rows cannot estimate success by human-time bucket. | Run the planned sweep and add T3/T4 accepted tasks before plotting time-horizon success curves. |
| `family_success_plot` | recommended_plot | block | 1/6 accepted families observed in non-infra provider rows | Current rows cannot estimate success by task family. | Run provider rows across the accepted core before family-level summaries. |
| `failure_taxonomy_plot` | recommended_plot | block | 1 non-infra provider failure rows | The current failure taxonomy is useful for transcript QA but too small for distributional claims. | Collect provider failures across the planned scaffold sweep and review labels before plotting. |
| `wilson_interval_reporting` | statistical_method | pass | model_result_summary rows=10 | Intervals are not a substitute for adequate coverage or independent timing. | Keep Wilson intervals in future performance summaries and report raw n. |
| `local_qa_exclusion` | data_hygiene | pass | 3 provider rows; 66 local QA rows | No benchmark performance claim should use local reference/wrong rows. | Keep local QA and provider rows separated in future analyses. |
| `infra_failure_policy` | data_hygiene | pass | Infra failures retained in run_results and counted separately. | Provider reliability claims still need more rows. | Keep infra rows in raw data and exclude them from model-capability means. |


## Provider Readiness Audit

`reports/provider_readiness_audit.md` and `data/provider_readiness_audit.csv` check model-runner readiness without using provider credentials or creating new model results. The audit separates runner contracts, adapter coverage, credential policy, transcript evidence, planned sweep commands, and smoke-only provider coverage.

- checks: `12`
- statuses: `{"block": 1, "caution": 1, "pass": 10}`
- areas: `{"credential_policy": 2, "planned_sweep": 1, "provider_adapter_surface": 3, "reporting": 1, "run_data": 3, "runner_contract": 2}`
- failing readiness checks: `0`
- caution rows: `1`
- blocked provider-evidence rows: `1`

Provider readiness checks:

| check | area | status | current state | limitation | next action |
| --- | --- | --- | --- | --- | --- |
| `provider_catalog_contract` | runner_contract | pass | Runner exposes local_reference plus command/openai/anthropic/gemini provider routes. | OpenAI and Gemini currently rely on the generic environment-command adapter contract. | Keep provider choices and PROVIDER_COMMAND_ENV synchronized with README and sweep plans. |
| `external_runner_env_contract` | runner_contract | pass | External runner commands receive prompt path, task identity, scaffold, lookup command, and public-file metadata. | Static source checks do not prove a third-party adapter honors those variables. | Keep this contract stable and update adapter docs when adding runner-supplied fields. |
| `bundled_provider_adapters` | provider_adapter_surface | caution | Anthropic has a minimal bundled adapter; OpenAI and Gemini are supported through external command env vars, not dedicated committed adapters. | Missing dedicated adapters are acceptable for local report readiness but limit turnkey provider comparability. | Add dedicated OpenAI and Gemini adapters or document external runner commands before a broad frontier sweep. |
| `anthropic_adapter_static_safety` | provider_adapter_surface | pass | The bundled Anthropic adapter reads credentials from the environment and emits Lean text. | This is a static audit; it does not call the provider API or validate current model availability. | Run a fresh smoke job with explicit cost/version notes before claiming provider performance. |
| `anthropic_adapter_utf8_stdout` | provider_adapter_surface | pass | The bundled Anthropic adapter configures UTF-8 stdout before printing extracted Lean text, guarding against Windows console encoding failures in Unicode Lean output. | This is a static regression guard for adapter output encoding; it does not call the provider API. | Keep UTF-8 stdout handling covered whenever provider adapters are edited. |
| `tracked_secret_scan` | credential_policy | pass | Tracked files contain no high-confidence API key patterns or direct API-key assignments. | Pattern scanning can miss unknown key formats and should not replace careful review. | Keep credentials in environment variables only and rerun this audit before publishing. |
| `credential_and_no_fake_policy_text` | credential_policy | pass | The public documentation states the no-fake-results and env-var credential policy. | Policy text is not evidence that future provider rows are externally reproduced. | Require transcripts, run-result integrity, and provider-version notes for every future model run. |
| `primary_sweep_command_plan` | planned_sweep | pass | The committed model-sweep plan encodes accepted_v0 x scaffold pass@10 command templates. | The plan is prospective and does not mean the rows have been run. | Instantiate MODEL and runner env vars only when running real provider sweeps. |
| `provider_transcript_evidence` | run_data | pass | Committed provider smoke rows have parseable transcript files. | Transcript presence does not make the tiny smoke set representative. | Keep transcript links mandatory and parse-check future provider sweeps. |
| `local_qa_provider_separation` | run_data | pass | Local reference/wrong rows are separated from provider model_sweep rows. | This is hygiene evidence only; it does not validate provider capability. | Keep local QA rows excluded from model-performance summaries. |
| `provider_sweep_coverage` | run_data | block | Provider evidence is smoke-only and covers one accepted non-infra cell. | This blocks frontier/scaffold-effect claims but does not block local report readiness. | Run the full accepted_v0 x scaffold sweep after hosted QA and runner readiness checks are stable. |
| `provider_claim_boundary` | reporting | pass | Model analysis separates smoke evidence from benchmark performance claims. | Future reports still need broader provider data before performance conclusions. | Keep unsupported frontier and scaffold claims blocked until planned coverage is real. |


## Hosted QA Readiness Audit

`reports/hosted_qa_readiness_audit.md` and `data/hosted_qa_readiness_audit.csv` distinguish local readiness from missing Taiga/hosted QA evidence.

- checks: `11`
- statuses: `{"block": 9, "pass": 2}`
- areas: `{"hosted_evidence": 6, "hosted_packaging": 3, "local_prerequisite": 2}`
- blocked hosted-QA steps: `9`
- failing local readiness checks: `0`

`block` rows are expected before upload and do not count as generated-script failures. They are evidence that hosted packaging, problem-version records, Full Env QA, Env Linter rows, and finding dispositions have not happened and must not be claimed.

Hosted QA readiness checks:

| check | area | status | current state | next action |
| --- | --- | --- | --- | --- |
| `local_validation_gate` | local_prerequisite | pass | Local validation evidence is present and passing. | Keep local validation passing before any hosted upload. |
| `public_export_ready` | local_prerequisite | pass | Public export evidence is present in the validation manifest. | Regenerate and validate public export immediately before hosted packaging. |
| `taiga_container_artifact` | hosted_packaging | block | No committed Taiga container artifact was found. | Create a Taiga-compatible container or document use of a managed preset before hosted QA. |
| `taiga_problem_metadata` | hosted_packaging | block | No committed Taiga problems-metadata JSON was found. | Generate a Taiga problems-metadata file for the exact accepted/calibration public versions. |
| `mcp_hooks` | hosted_packaging | block | No committed MCP hook implementation was found. | Implement or document the MCP wrapper that calls the Lean grader. |
| `problem_version_evidence` | hosted_evidence | block | No hosted problem-version evidence is committed. | After upload, record environment, problem, problem-version, image digest, and snapshot IDs. |
| `hosted_preflight_or_stage1` | hosted_evidence | block | No hosted preflight or Stage 1 rows are committed. | Run Taiga preflight/Stage 1 checks and record warning/error/critical findings. |
| `transcript_health_or_full_env_qa` | hosted_evidence | block | No Transcript Health or Full Env QA result rows are committed. | Run Full Env QA after hosted smoke runs and record result IDs and findings. |
| `env_linter` | hosted_evidence | block | No Env Linter rows are committed. | Run Env Linter on the hosted environment/snapshot and record dispositions. |
| `qa_findings_resolution` | hosted_evidence | block | No finding-resolution evidence is committed. | Record each finding with severity, disposition, fix/rebuttal, and affected problem version. |
| `exact_version_freeze_mapping` | hosted_evidence | block | No hosted freeze mapping is committed. | After hosted QA, commit the exact version/snapshot mapping and tag policy. |


## Threats To Validity Register

`reports/threats_to_validity.md` and `data/threats_to_validity.csv` convert the limitations section into a generated evidence register. `block` and `caution` rows are limitations on claims, not validation failures.

- threats: `13`
- statuses: `{"block": 8, "caution": 3, "controlled": 2}`
- categories: `{"construct_validity": 2, "external_validity": 2, "internal_validity": 4, "operational_security": 2, "operational_validity": 1, "statistical_validity": 2}`
- severities: `{"high": 9, "medium": 4}`
- blocked validity threats: `8`
- caution validity threats: `3`
- locally controlled threats: `2`

Threat register:

| threat | category | severity | status | evidence | stronger evidence needed | claims limited |
| --- | --- | --- | --- | --- | --- | --- |
| `construct_time_horizon_depth` | construct_validity | high | block | accepted=6; accepted buckets={"T2": 5, "T3": 1}; diagnostic blocks=1; diagnostic cautions=3 | Add independently reviewed and timed T3/T4 tasks, including at least one T4 stretch row. | time_horizon_measurement;locked_benchmark |
| `portfolio_scale_and_balance` | external_validity | high | block | accepted=6; calibration_only=8; rejected=12; accepted families={"algorithm_correctness": 1, "direct_theorem_proving": 1, "informal_spec_to_formal": 1, "invariant_verification_ml_optimization": 1, "proof_repair_codebase": 1, "small_formal_library_construction": 1} | Reach the 20-50 accepted-task target while preserving family and capability diversity. | frontier_performance;locked_benchmark;family_level_performance |
| `author_estimated_human_time` | internal_validity | high | block | accepted timed solves=0/6; human_time_observation_rows=0 | Collect independent Lean-human timed solves or second-review timing notes for every accepted task. | time_horizon_measurement;locked_benchmark |
| `missing_independent_task_quality_review` | internal_validity | high | block | independent task-review rows=0/6; review-status checks=5 | Collect non-author task-quality reviews covering prompt clarity, time bucket, diagnostic value, hidden pins, wrong submissions, and benchmark-grade recommendation for every accepted task. | accepted_core_reviewed;locked_benchmark |
| `automation_dominated_retained_tasks` | construct_validity | medium | caution | automation-dominated accepted tasks=2: ["lt-201", "lt-206"] | Replace or independently validate retained caveat rows before locked benchmark status. | accepted_core_reviewed;time_horizon_measurement |
| `semantic_pin_finiteness` | internal_validity | medium | caution | accepted tasks with hidden-pin wrong failures=4/6; proof-only fixed-statement rows=2 | Have an independent reviewer inspect hidden pins and add richer same-signature hidden wrongs for future mutable tasks. | hidden_pin_strength;grading_validity |
| `scaffold_sweep_undercoverage` | statistical_validity | high | block | planned accepted-core cells=18; covered non-infra cells=1 | Run accepted_v0 x one-shot/lookup/lookup_unlimited rows with fixed k and committed transcripts. | scaffold_effects;frontier_performance |
| `frontier_performance_undercoverage` | external_validity | high | block | accepted-core non-infra provider rows=1; accepted tasks=6 | Run documented frontier/open-model sweeps across the accepted scaffold plan with model versions and transcripts. | frontier_performance;locked_benchmark |
| `statistical_power_and_plots` | statistical_validity | high | block | statistical audit rows=9; blocked outputs=5 | Populate the planned sweep and accepted task count before generating scaffold, family, and bucket performance plots. | scaffold_effects;frontier_performance;family_level_performance |
| `failure_taxonomy_forecast` | internal_validity | medium | caution | accepted-core non-infra provider rows=1; transcript review queue rows=3; single-review rows=3; review-audit failures=0; high/critical queue rows=1 | Label real model transcripts after the scaffold sweep, use independent adjudication for disagreements, and compare observed failures to intended diagnostic modes. | diagnostic_failure_distribution;scaffold_effects |
| `hosted_environment_gap` | operational_validity | high | block | hosted readiness rows=11; blocked hosted-QA steps=9 | Create hosted packaging, run Full Env QA/Env Linter on exact problem versions, and commit findings/dispositions. | locked_benchmark;deployment_reliability |
| `secret_and_runner_boundary` | operational_security | medium | controlled | provider readiness failures=0; model-sweep command key-assignment leaks=0 | Repeat secret scans before every commit that touches runner or transcript files. | artifact_security;provider_run_reproducibility |
| `public_export_hidden_leakage` | operational_security | high | controlled | public_tasks exists=True; hidden/wrong paths in export=0 | Validate the public export after every task-asset or export-script change. | public_release_safety;locked_benchmark |


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


## Committed Run Results

66 local QA rows are committed for reference solutions and plausible wrong submissions. These rows are not model performance and are excluded from benchmark pass-rate summaries.

Local QA row status:

- `expected_failure`: 40
- `passed`: 26

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

Observed model-sweep failure labels:

- `infra_failure`: 1
- `proof_debugging`: 1

## Run Result Integrity Audit

`reports/run_integrity_audit.md` and `data/run_integrity_audit.csv` verify that committed run rows are internally consistent with task metadata, known failure labels, score vectors, pass@k semantics, and JSONL transcript files.

- rows checked: `69`
- integrity statuses: `{"pass": 69}`
- qa stages: `{"local_qa": 66, "model_sweep": 3}`
- missing transcript files: `0`
- transcript parse failures: `0`
- pass@k arithmetic failures: `0`
- transcript consistency failures: `0`

Failing integrity rows:

_None._


## Claim Evidence Audit

`reports/claim_evidence_audit.md` and `data/claim_evidence_audit.csv` map report claims to evidence strength and limits. This keeps local artifact-validity claims separate from performance and locked-benchmark claims.

- claims audited: `9`
- support statuses: `{"partial": 1, "supported": 5, "unsupported": 3}`
- claim types: `{"artifact_validity": 1, "benchmark_status": 1, "construct_validity": 1, "data_validity": 1, "grading_validity": 1, "performance_claim": 2, "report_validity": 1, "task_validity": 1}`

Claim support table:

| claim | type | support | strength | claim text | limit | stronger claim requires |
| --- | --- | --- | --- | --- | --- | --- |
| `local_release_artifact` | artifact_validity | supported | high | The repository is a locally validated v0.1 release artifact with public scaffolds, hidden checks, Lean scoring, integrity controls, and complete metadata. | This is a local artifact claim, not a hosted/frozen benchmark claim. | Hosted QA, independent review, and broader accepted task count are still required for a locked benchmark. |
| `research_report_evidence` | report_validity | supported | high | The report is generated from committed data and includes a concise reviewer-facing METR-style report, a data schema manifest for schema-backed datasets and generated CSV boundaries, a reviewer reproduction packet with local replay steps and external-evidence boundaries, a clean-workspace replay of dependency materialization, Lean build, grader pass/fail behavior, and public export validation, a figure manifest that ties SVGs to source data and blocked plot claims, a main-report/evidence-appendix boundary, a source-traceability audit mapping report sections to committed artifacts, a report-shape audit that checks the narrative against the playbook questions, a count-consistency audit that checks repeated top-line numbers against committed CSV/JSON sources, a regeneration-command consistency audit that checks README/manifest/reviewer replay synchronization, research-quality caveats, task quality matrices, accepted-task cards, diagnostic-coverage checks, a construct-validity matrix, human-time calibration checks, a human-timing collection packet, an independent task-review packet plus status audit, a transcript-review packet, a failure-label review audit for committed smoke transcripts, task-asset hashes, prompt-contract checks, pin coverage, run integrity, grader-hardening checks, a statistical analysis plan with precision thresholds, statistical reporting checks, model-evidence provenance checks for sample sizes and model versions, provider-readiness checks, a model-sweep execution packet, hosted-QA readiness checks, a generated threats-to-validity register plus blocker/claim threat-coverage audit, a claim-authorization matrix with forbidden overclaim wording, a research claim gap matrix that maps stronger claims to missing evidence packages, a report claim-conformance audit that checks prose against those authorizations, scaffold-support checks, release-decision gates, a freeze-readiness roadmap, and a prospective evaluation protocol. | The report is still limited by missing broad model sweeps, independent human timing, and completed independent task reviews. | Run the planned scaffold sweep, collect independent timing and task-quality reviews, and add external QA artifacts. |
| `accepted_core_reviewed` | task_validity | supported | medium | The six accepted-core tasks are internally reviewed and higher quality than the original candidate pool. | This is an internal-review claim. The independent task-review workflow is present, but no completed non-author review rows are committed. | Collect independent Lean-human task-quality reviews and more accepted high-quality T2/T3/T4 rows. |
| `hidden_pin_strength` | grading_validity | supported | medium | Hidden checks provide meaningful anti-gaming evidence for accepted tasks, with semantic hidden-pin failures on mutable-definition tasks and signature/downstream guards on proof-only fixed-statement tasks. | Proof-only fixed-statement rows do not have semantic hidden wrongs because Lean compilation already certifies exact same-signature theorem proofs; hidden pins remain finite probes. | Add independent reviewer assessment of hidden pins and strengthen any future mutable accepted task until it has at least one public-compiling wrong that fails hidden pins. |
| `run_data_integrity` | data_validity | supported | high | Committed run-result rows are internally consistent with transcripts, failure labels, score vectors, and pass@k semantics. | This validates data hygiene only; it does not make the smoke rows representative. | Maintain this audit for future provider sweeps and require zero failing rows before reporting results. |
| `time_horizon_measurement` | construct_validity | partial | low | The current artifact measures model behavior across increasing time horizons. | Accepted core has only T2/T3 coverage and no T4; human times are author/reviewer estimates rather than independent solves. | Add independently timed T3/T4 tasks before claiming strong time-horizon measurement. |
| `scaffold_effects` | performance_claim | unsupported | none | The report supports conclusions about how lookup and iterative compile/debug scaffolds change model performance. | The scaffold ladder is implemented and planned, but real accepted-core provider data cover only one one-shot cell. | Run accepted-core pass@10 or equivalent rows across one-shot, lookup, and lookup_unlimited. |
| `frontier_performance` | performance_claim | unsupported | none | Committed provider rows characterize frontier-model performance on this benchmark. | Only tiny smoke evidence is committed, including an infra failure; local QA rows are not model performance. | Run the planned accepted-core scaffold sweep with documented provider versions and cost/infra notes. |
| `locked_benchmark` | benchmark_status | unsupported | none | v0.1 is a locked benchmark suitable for population-level frontier-model claims. | The artifact has 6 accepted tasks, no hosted QA, no independent timing or completed non-author task reviews, no T4 accepted task, and limited provider data. | Reach the 20-50 accepted-task target, run hosted QA, collect independent timing and task reviews, complete scaffold sweeps, and freeze exact public task versions. |


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


## Research Claim Gap Matrix

`reports/research_claim_gap_matrix.md` and `data/research_claim_gap_matrix.csv` map caveated and blocked claims to the evidence packages required before stronger report wording is allowed. This is an upgrade plan, not evidence that the gaps have been filled.

- tracked claims: `12`
- authorization statuses: `{"allowed": 1, "allowed_with_caveat": 6, "blocked": 5}`
- upgrade priorities: `{"high": 6, "highest": 1, "maintain": 1, "medium": 4}`
- high-or-blocked rows: `7`

High-priority claim gaps:

| claim | authorization | priority | blocking requirements | minimum evidence package | exit criteria |
| --- | --- | --- | --- | --- | --- |
| `accepted_core_quality` | allowed_with_caveat | high | `portfolio_accepted_count;time_horizon_spread;independent_human_time_review;independent_task_quality_review` | 20-50 hard-reviewed accepted tasks, stronger T3/T4 coverage, independent Lean-human timing, completed non-author task-quality reviews, and refreshed per-task review. | Accepted-core quality can support benchmark-level aggregates only after scale, depth, independent timing, and completed independent task-review evidence are supported. |
| `time_horizon_scope` | allowed_with_caveat | high | `time_horizon_spread;independent_human_time_review;portfolio_accepted_count` | Independently timed T2/T3/T4 tasks, including at least one T4 stretch row and enough accepted tasks to avoid singleton bucket claims. | The report can claim robust time-horizon measurement only after accepted tasks cover meaningful T2/T3/T4 depth with independent timing evidence. |
| `scaffold_effects` | blocked | high | `scaffold_result_comparison;frontier_model_evidence` | Non-infra pass@k rows across accepted_v0 x one-shot/lookup/lookup_unlimited cells, with fixed k, model versions, transcripts, and run-integrity checks. | Empirical scaffold-effect claims require the planned accepted-core scaffold sweep to be covered and analyzed with raw n and intervals. |
| `frontier_model_performance` | blocked | high | `frontier_model_evidence;scaffold_result_comparison;hosted_qa_env_linter` | Documented frontier/open-model provider rows with model versions, transcripts, infra notes, hosted-QA-cleared tasks, and integrity audits. | Frontier-performance wording remains blocked until broad provider rows exist on stable, locally and hosted-QA-checked task versions. |
| `statistical_performance_reporting` | blocked | high | `scaffold_result_comparison;frontier_model_evidence;portfolio_accepted_count` | Sufficiently covered accepted-core sweeps, raw task-row numerators, Wilson intervals, claim-tier threshold checks, and regenerated statistical reporting checks. | Performance plots should stay blocked until scaffold/provider coverage and accepted-task scale support the plotted comparisons. |
| `hosted_qa_status` | blocked | high | `hosted_qa_env_linter` | Hosted/Taiga package evidence, exact problem-version mapping, Full Env QA runs, Env Linter findings, and rebuttal/fix dispositions. | Hosted-QA wording can be upgraded only after warning/error/critical findings are fixed or concretely rebutted for exact final versions. |
| `locked_benchmark_status` | blocked | highest | `portfolio_accepted_count;time_horizon_spread;scaffold_result_comparison;frontier_model_evidence;independent_human_time_review;independent_task_quality_review;hosted_qa_env_linter` | 20-50 accepted tasks, T2/T3/T4 depth, independent timing, completed non-author task-quality reviews, completed scaffold/provider sweeps, hosted QA, settled findings, and frozen exact public versions. | The locked-benchmark claim remains blocked until every locked-benchmark requirement is supported and the release/freeze gates have no blocking rows. |


## Report Claim Conformance Audit

`reports/report_claim_conformance_audit.md` and `data/report_claim_conformance_audit.csv` check that the concise report, detailed report, and README obey the claim-authorization matrix. The audit scans for missing caveats, blocked-claim phrase contexts, and report-shape drift.

- checks: `11`
- statuses: `{"pass": 11}`
- scopes: `{"claim_authorization": 1, "claim_gap_matrix": 1, "concise_report": 1, "main_report": 6, "readme": 1, "reports_and_readme": 1}`

Claim-conformance checks:

| check | scope | status | evidence | required action |
| --- | --- | --- | --- | --- |
| `authorization_matrix_loaded` | claim_authorization | pass | authorization rows=12; statuses={"allowed": 1, "allowed_with_caveat": 6, "blocked": 5}; blocked=5; caveated=6; non_allowed=11 | Regenerate scripts/generate_claim_authorization_matrix.py and inspect blocked/caveated coverage. |
| `main_report_authorization_section` | main_report | pass | section_present=True; claim_ids_in_matrix=12; missing_claim_ids=[] | Regenerate reports/metr_style_report.md after claim authorization and ensure every authorization row is visible. |
| `abstract_scope_boundaries` | main_report | pass | front-matter scope phrases checked before the first task table | Keep locked-benchmark, sample-size, human-time, and provider-smoke limitations in the report abstract/front matter. |
| `run_result_boundary_wording` | main_report | pass | committed-run section checked for local-QA and smoke-row boundaries | Keep local QA and tiny provider smoke rows explicitly separated from benchmark performance claims. |
| `claim_ledger_blocks_overclaims` | main_report | pass | claim ledger checked for explicit not-supported locked-benchmark and frontier-performance rows | Keep tempting overclaims in the claim ledger as unsupported, not as conclusions. |
| `concise_report_scope_and_length` | concise_report | pass | concise report exists=True; line_count=217; missing_scope_phrases=[] | Regenerate scripts/generate_concise_report.py and keep the reviewer-facing report concise and claim-bounded. |
| `locked_benchmark_blocker_consistency` | claim_gap_matrix | pass | locked_blockers=["frontier_model_evidence", "hosted_qa_env_linter", "independent_human_time_review", "independent_task_quality_review", "portfolio_accepted_count", "scaffold_result_comparison", "time_horizon_spread"]; gap_row_count=1; gap_blockers=["portfolio_accepted_count", "time_horizon_spread", "scaffold_result_comparison", "frontier_model_evidence", "independent_human_time_review", "independent_task_quality_review", "hosted_qa_env_linter"]; gap_missing=[]; concise_missing=[] | Regenerate the research claim gap matrix and concise report whenever locked-benchmark requirement coverage changes. |
| `blocked_phrase_context_scan` | reports_and_readme | pass | blocked-claim phrase contexts scanned across reports\metr_style_report.md, reports\concise_metr_report.md, reports\evidence_appendix.md, reports\report_source_traceability.md, and README.md; unsafe_contexts=0 | Rewrite any blocked-claim phrase so the local context clearly says it is unsupported, blocked, missing, or future work. |
| `readme_scope_boundaries` | readme | pass | README checked for locked-benchmark, model-result, and credential-scope boundaries | Keep the README top-level scope aligned with the report's claim authorization matrix. |
| `limitations_cover_blockers` | main_report | pass | limitations section checked against blocked authorization themes | Keep task-count, T4, independent-timing, provider-smoke, hosted-QA, and locked-benchmark caveats in the limitations section. |
| `report_length_and_appendix_boundary` | main_report | pass | main report line_count=507; markdown_table_rows=173; evidence_appendix_exists=True; evidence_appendix_line_count=1590 | Keep the main report skimmable and keep row-level generated tables in reports/evidence_appendix.md. |


## Report Shape Audit

`reports/report_shape_audit.md` and `data/report_shape_audit.csv` check whether the concise METR-style report answers the playbook's main report-shape questions. `blocked_by_evidence` rows are expected in v0.1 when the report explicitly says the current data cannot support a scaffold, time-horizon, or failure-distribution analysis.

- checks: `7`
- answer statuses: `{"answered": 3, "answered_with_blocker": 1, "answered_with_caveat": 1, "blocked_by_evidence": 2}`

Report-shape checks:

| check | playbook question | answer status | evidence | limitation | next action |
| --- | --- | --- | --- | --- | --- |
| `tasks_built` | What tasks were built? | answered | accepted=6; calibration=8; missing_phrases=[] | The accepted set is below the final 20-50 task target. | Keep accepted/calibration/rejected status visible and expand only with hard-reviewed tasks. |
| `capabilities_tested` | What capabilities do the tasks test? | answered_with_caveat | capability_rows=7; singleton_capabilities=["library_search", "semantic_formalization", "codebase_navigation"]; missing_phrases=[] | Some capabilities are represented by only one accepted task, so capability-level claims remain weak. | Add independently reviewed tasks for singleton capabilities before making capability-level performance claims. |
| `scaffolds_compared` | What scaffolds were compared? | answered_with_blocker | planned_cells=18; covered_noninfra=1; missing_phrases=[] | The scaffold ladder is planned and implemented, but committed provider evidence covers only a tiny one-shot smoke sample. | Run the accepted-core scaffold sweep before interpreting scaffold effects. |
| `success_changes_by_scaffold_and_bucket` | How does success change with scaffold and human-time bucket? | blocked_by_evidence | scaffold_result_comparison=partial; time_horizon_spread=partial; statistical_analysis_plan=supported; primary_covered_noninfra=1 | Real scaffold/time-horizon performance summaries are not supported by committed data. | Run pass@k sweeps across accepted_v0 x scaffold cells, meet the statistical threshold rows, and add independently timed T3/T4 tasks. |
| `failure_modes_dominate` | What failure modes dominate? | blocked_by_evidence | concision_mentions_failure_limits=True; missing_phrases=[] | Expected failure modes are documented, but broad model transcripts are not independently adjudicated. | Use the transcript review packet and failure-label review audit after broader provider sweeps before claiming dominant failure modes. |
| `next_batch_needs` | What does the next batch need? | answered | missing_phrases=[] | Next work is a concrete blocker list, not a claim that the benchmark is locked. | Keep next-work items tied to requirement/freeze gates. |
| `skimmability` | Is the main report skimmable? | answered | concise_report_lines=217; conformance_failures=0 | The concise report is short, and row-level generated tables live in the evidence appendix instead of the main narrative. | Keep the concise and main reports short and keep long tables in generated appendices. |


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


## Release Decision Log

`reports/release_decision_log.md` and `data/release_decision_log.csv` translate the evidence audits into explicit gate decisions. This is the report's operational conclusion: what can be used now, what requires caveats, and what is blocked.

- gates: `8`
- gate statuses: `{"block": 4, "caution": 2, "pass": 2}`
- blocked stronger claims: `4`
- caution gates: `2`

Decision table:

| gate | scope | status | decision | next action |
| --- | --- | --- | --- | --- |
| `local_release_artifact` | artifact_release | pass | OK to treat v0.1 as a locally validated research artifact, not as a locked benchmark. | Keep artifact claims scoped to local reproducibility and local grading evidence. |
| `research_report_readiness` | reporting | pass | OK to use the report as a research review memo if caveats and unsupported claims stay visible. | Update the decision log whenever a requirement, claim audit, or provider sweep changes. |
| `accepted_core_stats_scope` | task_set | caution | Use accepted_v0 rows for artifact-level task-quality summaries only; do not use them for population-level frontier claims. | Add completed non-author task reviews and more independently reviewed T2/T3/T4 rows before treating accepted-core aggregates as benchmark estimates. |
| `hidden_pin_confidence` | grading | caution | Treat hidden pins as meaningful anti-gaming probes but not exhaustive semantic equivalence checks. | Add same-signature hidden-pin failures where realistic and expand negative examples for retained caveat rows. |
| `time_horizon_claim` | construct_validity | block | Do not claim strong time-horizon measurement yet. | Add independently timed T3/T4 tasks, including at least one T4 row, before claiming robust time-horizon coverage. |
| `scaffold_effect_claim` | performance | block | Do not report scaffold-effect conclusions from committed data. | Run the planned accepted_v0 x scaffold sweep with fixed k before comparing scaffold effects. |
| `frontier_performance_claim` | performance | block | Do not use committed provider rows to characterize frontier-model capability. | Run documented provider sweeps after local and hosted QA are stable. |
| `locked_benchmark_freeze` | benchmark_status | block | Do not call v0.1 a locked benchmark. | Reach the 20-50 accepted-task target, complete hosted QA, independent timing, task reviews, and scaffold sweeps, then freeze exact task versions. |


## Freeze Readiness Roadmap

`reports/freeze_readiness_roadmap.md` and `data/freeze_readiness_roadmap.csv` synthesize the requirement, claim, release-decision, hosted-QA, statistical, model-run, and metadata audits into concrete gates for turning the local v0.1 artifact into a locked benchmark. It is a planning ledger, not evidence that blocked gates are complete.

- gates: `10`
- roadmap statuses: `{"block": 8, "caution": 1, "ready": 1}`
- categories: `{"analysis": 1, "calibration": 1, "hosted_qa": 1, "local_release": 1, "model_sweeps": 2, "release_management": 1, "task_portfolio": 3}`
- blocking gates before locked benchmark: `8`

Freeze-readiness gates:

| gate | category | status | exit criteria | next action | blocks claims |
| --- | --- | --- | --- | --- | --- |
| `local_artifact_validation` | local_release | ready | Keep zero failing local validation, public-export, run-integrity, and grader-hardening rows immediately before any release tag. | Rerun the README validation gate after every task, grader, or report change. | `local_release_artifact` |
| `accepted_portfolio_scale` | task_portfolio | block | Reach 20-50 accepted_v0 tasks after hard review, with candidate/rejected rows retained for pruning evidence. | Author a small batch of high-quality T2/T3/T4 candidates, then apply the existing hard review before accepting any row. | `locked_benchmark, frontier_performance` |
| `time_horizon_depth` | task_portfolio | block | Accepted core should include a meaningful T2/T3/T4 spread, including at least one independently reviewed T4 stretch task. | Design one T4 candidate and several T3 candidates only after the current v0.1 core remains stable under review. | `time_horizon_measurement, locked_benchmark` |
| `family_balance_and_diagnostics` | task_portfolio | caution | Maintain family coverage while expanding; do not let direct theorem proving or simple list tasks dominate accepted rows. | For each new accepted task, record the intended diagnostic failure mode and reject rows that are automation-dominated. | `accepted_core_reviewed, locked_benchmark` |
| `independent_human_timing` | calibration | block | Every accepted task should have at least one independent Lean-human solve or second-review timing note and one non-author task-quality review; T3/T4 rows should get extra scrutiny. | Run timed solves and task-quality reviews with non-authors, then append rows to data/human_time_observations.csv and data/independent_task_reviews.csv before freeze. | `time_horizon_measurement, locked_benchmark` |
| `scaffold_sweep_coverage` | model_sweeps | block | Accepted_v0 x {one-shot, lookup, lookup_unlimited} cells should have non-infra pass@k rows for each reported model. | Run the planned sweep commands from reports/evaluation_protocol.md with fixed k and committed transcripts. | `scaffold_effects, frontier_performance, locked_benchmark` |
| `frontier_and_open_model_evidence` | model_sweeps | block | Commit documented provider/model-version rows across the accepted scaffold plan before any frontier or open-model capability claim. | After hosted/local QA are stable, run provider adapters for the selected frontier/open models and retain transcripts plus infra notes. | `frontier_performance, scaffold_effects, locked_benchmark` |
| `hosted_qa_and_env_linter` | hosted_qa | block | Taiga/hosted package, problem metadata, Full Env QA, Env Linter, and finding dispositions must be committed for exact problem versions. | Create hosted packaging artifacts, upload exact public versions, run hosted QA, and commit finding dispositions. | `locked_benchmark` |
| `statistical_reporting_readiness` | analysis | block | Recommended performance plots should have adequate task/scaffold coverage and report raw n plus Wilson intervals. | Keep performance plots blocked until the planned accepted-core sweep and larger accepted set exist. | `scaffold_effects, frontier_performance, locked_benchmark` |
| `freeze_versioning` | release_management | block | Freeze only after local validation, hosted QA, independent timing, accepted-count, scaffold-sweep, and provider-evidence gates are satisfied. | Tag the exact commit/export hash and hosted problem-version mapping only after all block gates are cleared. Current authorization statuses={"allowed": 1, "allowed_with_caveat": 6, "blocked": 5}; claim-conformance failures=0; claim-conformance cautions=0; report-shape blocked_by_evidence=2; blocked authorizations=["scaffold_effects", "frontier_model_performance", "statistical_performance_reporting", "hosted_qa_status", "locked_benchmark_status"]. | `locked_benchmark` |


## Difficulty Audit Summary

The regenerated difficulty audit separates mechanical signals from manual judgments. Mechanical signals include reference proof lines, declaration count, public file count, public lemma count, tactic profile, automation dominance, Mathlib use, multi-file context, hidden pin strength, and wrong-submission count. Manual fields include frontier one-shot solvability estimates, p50/p90 human time, scaffold sensitivity, diagnostic value, and final accept/reject rationale.

## Accepted Task Review

`reports/accepted_task_review.md` records the per-task reviewer judgment for every row that was marked `accepted_v0` at the start of the hardening pass. It explicitly distinguishes keep, downgrade, and keep-with-caveat recommendations; checks whether buckets are deserved; audits hidden pins and wrong submissions; and lists what must change before each task can be treated as benchmark-grade.

## Task Quality Matrix

`reports/task_quality_matrix.md` and `data/task_quality_matrix.csv` provide a generated one-row-per-task quality ledger joining metadata with difficulty-audit signals. This is meant for reviewer navigation; acceptance still comes from task metadata, validation, and `reports/accepted_task_review.md`.

- release roles: `{"accepted_core": 6, "calibration_release": 8, "rejected_archive": 12}`
- benchmark-grade statuses: `{"accepted_core_retained": 3, "accepted_core_with_caveat": 3, "calibration_only": 8, "rejected_archive": 12}`
- accepted-core caveat rows: `3/6`
- accepted-core automation-dominated rows: `2/6`
- accepted-core likely/very-likely one-shot rows: `0/6`

Accepted-core quality rows:

| task | grade | bucket | proof lines | automation | pins | wrongs | one-shot | next action |
| --- | --- | --- | ---: | --- | --- | ---: | --- | --- |
| `lt-201` | accepted_core_with_caveat | T2 | 25 | true | semantic | 2 | maybe | Retain in v0.1 only with the recorded caveat; collect independent human timing, full scaffold sweep evidence, and external QA before freeze. |
| `lt-203` | accepted_core_retained | T2 | 30 | false | semantic | 2 | maybe | Collect independent timing, hosted QA, and accepted-core scaffold/model evidence before benchmark freeze. |
| `lt-202` | accepted_core_with_caveat | T2 | 46 | false | mixed | 2 | maybe | Retain in v0.1 only with the recorded caveat; collect independent human timing, full scaffold sweep evidence, and external QA before freeze. |
| `lt-204` | accepted_core_retained | T2 | 36 | false | semantic | 2 | maybe | Collect independent timing, hosted QA, and accepted-core scaffold/model evidence before benchmark freeze. |
| `lt-205` | accepted_core_retained | T3 | 42 | false | semantic | 2 | unlikely | Independently time at least one human solve and run the planned scaffold sweep before using this as long-horizon evidence. |
| `lt-206` | accepted_core_with_caveat | T2 | 60 | true | semantic | 2 | maybe | Retain in v0.1 only with the recorded caveat; collect independent human timing, full scaffold sweep evidence, and external QA before freeze. |


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
| `lt-204` | keep | 36 lines; automation=false; one-shot=maybe | semantic_pins_exercised; stages `{"hidden_pin": 1, "public_stage": 1}` | `{"expected_failure": 2, "passed": 1}` | Collect independent timing, hosted QA, and accepted-core scaffold/model evidence before benchmark freeze. independent human timing; accepted-core scaffold sweep; hosted QA evidence Mutable definitions have public-comp... |
| `lt-205` | keep | 42 lines; automation=false; one-shot=unlikely | semantic_pins_exercised; stages `{"hidden_pin": 1, "public_stage": 1}` | `{"expected_failure": 2, "passed": 1}` | Independently time at least one human solve and run the planned scaffold sweep before using this as long-horizon evidence. independent human timing; accepted-core scaffold sweep; hosted QA evidence; extra timing revie... |
| `lt-206` | keep_with_caveat | 60 lines; automation=true; one-shot=maybe | semantic_pins_exercised; stages `{"hidden_pin": 2, "unknown": 2}` | `{"expected_failure": 2, "passed": 1}` | Retain in v0.1 only with the recorded caveat; collect independent human timing, full scaffold sweep evidence, and external QA before freeze. independent human timing; accepted-core scaffold sweep; hosted QA evidence M... |


## Task Asset Manifest

`reports/task_asset_manifest.md` and `data/task_asset_manifest.csv` provide a task-file-level hash ledger for prompts, metadata, public Lean files, hidden references, hidden pins, and wrong submissions. The report summarizes coverage without copying hidden proof contents.

- task count: `26`
- asset rows: `171`
- task statuses: `{"accepted_v0": 6, "calibration_only": 8, "rejected_duplicate": 2, "rejected_too_easy": 10}`
- asset roles: `{"hidden_pincheck": 26, "hidden_reference": 26, "metadata": 26, "prompt": 26, "public": 27, "wrong_submission": 40}`
- missing task assets: `0`
- release public assets missing from public export: `0`
- hidden/wrong assets present in public export: `0`

Accepted task asset coverage:

| task | public assets | wrong submissions | hidden ref | pincheck |
| --- | ---: | ---: | --- | --- |
| `lt-201` | 4 | 2 | true | true |
| `lt-202` | 3 | 2 | true | true |
| `lt-203` | 3 | 2 | true | true |
| `lt-204` | 3 | 2 | true | true |
| `lt-205` | 3 | 2 | true | true |
| `lt-206` | 3 | 2 | true | true |


## Hidden Pin Coverage Audit

`reports/pin_coverage_audit.md` and `data/pin_coverage_audit.csv` make hidden-check evidence inspectable by separating public-stage wrong failures from wrong submissions that actually reach `PinCheck.lean`. It also classifies whether same-signature hidden wrongs are meaningful for the task surface: proof-only fixed-statement rows are already semantically certified by Lean if the fixed theorem compiles, while mutable-definition rows can have public-compiling semantic wrongs that hidden pins should catch.

- pin coverage grades: `{"pins_not_exercised_by_wrongs": 5, "semantic_examples_exercised": 3, "semantic_pins_exercised": 4, "signature_plus_hidden_failure": 14}`
- accepted-core tasks with at least one hidden-pin wrong failure: `4/6`
- accepted-core wrong failures at public stage: `6`
- accepted-core wrong failures at hidden-pin stage: `6`
- accepted-core same-signature hidden-wrong feasibility: `{"feasible_via_definition_semantics": 4, "structurally_infeasible_for_same_signature_proof_wrongs": 2}`
- accepted-core hidden-pin roles: `{"semantic_positive_negative_guard": 4, "signature_and_downstream_use_guard": 2}`

Accepted-core hidden-pin coverage:

| task | grade | surface | hidden-pin role | same-signature hidden-wrong feasibility | public-stage wrongs | hidden-pin wrongs | note |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| `lt-201` | pins_not_exercised_by_wrongs | proof_only_fixed_statements | signature_and_downstream_use_guard | structurally_infeasible_for_same_signature_proof_wrongs | 2 | 0 | Accepted proof-only row: same-signature semantic wrong proofs are structurally infeasible once Lean accepts the fixed theorem; hidden pins guard signatures and downstream use. |
| `lt-203` | semantic_pins_exercised | mutable_definitions_plus_theorems | semantic_positive_negative_guard | feasible_via_definition_semantics | 0 | 2 | Accepted row has at least one wrong submission reaching hidden pins and nontrivial examples. |
| `lt-202` | pins_not_exercised_by_wrongs | proof_only_fixed_statements | signature_and_downstream_use_guard | structurally_infeasible_for_same_signature_proof_wrongs | 2 | 0 | Accepted proof-only row: same-signature semantic wrong proofs are structurally infeasible once Lean accepts the fixed theorem; hidden pins guard signatures and downstream use. |
| `lt-204` | semantic_pins_exercised | mutable_definitions_plus_theorems | semantic_positive_negative_guard | feasible_via_definition_semantics | 1 | 1 | Accepted row has at least one wrong submission reaching hidden pins and nontrivial examples. |
| `lt-205` | semantic_pins_exercised | mutable_definitions_plus_theorems | semantic_positive_negative_guard | feasible_via_definition_semantics | 1 | 1 | Accepted row has at least one wrong submission reaching hidden pins and nontrivial examples. |
| `lt-206` | semantic_pins_exercised | mutable_definitions_plus_theorems | semantic_positive_negative_guard | feasible_via_definition_semantics | 0 | 2 | Accepted row has at least one wrong submission reaching hidden pins and nontrivial examples. |


## Requirement Coverage Audit

`reports/requirement_coverage.md` and `data/requirement_coverage.csv` map the repository to the committed checklist in `data/benchmark_requirements.csv`. This is a stricter evidence index than the narrative claim ledger.

Status counts:

- `supported`: 64
- `partial`: 4
- `not_met`: 3

Freeze relevance counts:

- `required_for_locked_benchmark`: supported 2, partial 4, not_met 3
- `required_for_release_artifact`: supported 15
- `required_for_research_report`: supported 47

Partial or unmet requirements:

| id | area | freeze relevance | status | evidence | next step |
| --- | --- | --- | --- | --- | --- |
| `portfolio_accepted_count` | portfolio | required_for_locked_benchmark | not_met | 6 accepted_v0 tasks; 8 calibration-only tasks; 12 rejected archive tasks. | Add and hard-review more high-quality T2/T3/T4 tasks before claiming a full benchmark. |
| `time_horizon_spread` | portfolio | required_for_locked_benchmark | partial | Accepted bucket counts: {"T2": 5, "T3": 1}; release bucket counts: {"T1": 8, "T2": 5, "T3": 1}. | Add more accepted T3/T4 tasks, including a T4 stretch row, and independently review human times. |
| `scaffold_result_comparison` | scaffolds | required_for_locked_benchmark | partial | Non-infra model rows: 2; scaffolds observed: ["one-shot"]; planned rows: 18. | Run real pass@10 or comparable sweeps across one-shot, lookup, and lookup_unlimited before performance claims. |
| `frontier_model_evidence` | runs | required_for_locked_benchmark | partial | Non-infra model rows: 2 over 6 accepted tasks; total model rows including infra failures: 3. | Run broader provider sweeps only after local and hosted QA are stable. |
| `independent_human_time_review` | calibration | required_for_locked_benchmark | partial | Accepted tasks with manual_review_complete: 6/6; accepted tasks with successful independent timing observations: 0/6; observation rows: 0. | Collect independent Lean-human timed solves or second-reviewer timing notes before freeze. |
| `independent_task_quality_review` | calibration | required_for_locked_benchmark | not_met | Accepted tasks with completed independent task reviews: 0/6; review rows: 0; status-audit rows: 5. | Collect non-author task-quality reviews for every accepted_v0 task before freeze. |
| `hosted_qa_env_linter` | qa | required_for_locked_benchmark | not_met | Hosted QA artifacts present: 0/2; hosted readiness report exists: True; blocked hosted-readiness checks: 9. | Run hosted Full Env QA and record findings/rebuttals before claiming a locked benchmark. |


## Reproducibility Checklist

The intended local regeneration gate is:

```powershell
lake exe cache get
lake build
python scripts/validate_all.py
python scripts/audit_difficulty.py
python scripts/generate_task_quality_matrix.py
python scripts/generate_candidate_pruning_audit.py
python scripts/audit_diagnostic_coverage.py
python scripts/generate_construct_validity_matrix.py
python scripts/audit_human_time_calibration.py
python scripts/generate_human_timing_packet.py
python scripts/generate_independent_review_packet.py
python scripts/audit_independent_review_status.py
python scripts/record_local_qa_results.py
python scripts/generate_transcript_review_packet.py
python scripts/audit_failure_label_reviews.py
python scripts/audit_pin_coverage.py
python scripts/audit_run_integrity.py
python scripts/audit_grader_hardening.py
python scripts/generate_evaluation_protocol.py
python scripts/generate_statistical_analysis_plan.py
python scripts/generate_model_sweep_packet.py
python scripts/analyze_model_results.py
python scripts/audit_model_evidence_provenance.py
python scripts/generate_report.py
python scripts/audit_statistical_reporting.py
python scripts/audit_figure_manifest.py
python scripts/audit_data_schema_manifest.py
python scripts/generate_reviewer_reproduction_packet.py
python scripts/run_clean_workspace_replay.py
python scripts/audit_provider_readiness.py
python scripts/generate_report.py
python scripts/audit_report_source_traceability.py
python scripts/export_public_tasks.py --out public_tasks
python scripts/validate_public_export.py --out public_tasks
python scripts/audit_hosted_qa_readiness.py
python scripts/generate_task_asset_manifest.py --public-export public_tasks
python scripts/generate_accepted_task_cards.py
python scripts/audit_prompt_contracts.py
python scripts/audit_scaffold_support.py
python scripts/generate_threats_to_validity.py
python scripts/audit_threat_coverage.py
python scripts/audit_requirement_coverage.py --public-export public_tasks
python scripts/audit_claim_evidence.py
python scripts/generate_claim_authorization_matrix.py
python scripts/generate_research_claim_gap_matrix.py
python scripts/generate_concise_report.py
python scripts/audit_report_claim_conformance.py
python scripts/audit_report_shape.py
python scripts/audit_report_count_consistency.py
python scripts/generate_release_decision_log.py
python scripts/generate_freeze_readiness_roadmap.py
python scripts/audit_scaffold_support.py
python scripts/audit_requirement_coverage.py --public-export public_tasks
python scripts/audit_claim_evidence.py
python scripts/generate_claim_authorization_matrix.py
python scripts/generate_research_claim_gap_matrix.py
python scripts/generate_concise_report.py
python scripts/audit_report_claim_conformance.py
python scripts/audit_report_shape.py
python scripts/audit_report_count_consistency.py
python scripts/generate_release_decision_log.py
python scripts/generate_freeze_readiness_roadmap.py
python scripts/audit_scaffold_support.py
python scripts/audit_requirement_coverage.py --public-export public_tasks
python scripts/audit_claim_evidence.py
python scripts/generate_claim_authorization_matrix.py
python scripts/generate_research_claim_gap_matrix.py
python scripts/generate_concise_report.py
python scripts/audit_report_claim_conformance.py
python scripts/audit_report_shape.py
python scripts/audit_report_count_consistency.py
python scripts/generate_release_decision_log.py
python scripts/generate_freeze_readiness_roadmap.py
python scripts/write_validation_manifest.py --public-export public_tasks
python scripts/audit_validation_manifest.py
python scripts/generate_report.py
python scripts/audit_report_source_traceability.py
python scripts/audit_regeneration_commands.py
python scripts/write_validation_manifest.py --public-export public_tasks
python scripts/audit_validation_manifest.py
python scripts/generate_report.py
```

The public export validator checks that hidden references and wrong submissions are absent from `public_tasks`, all metadata-listed public files are present, exported Lean files compile, and obvious hidden-reference path strings do not leak.

## Reviewer Reproduction Packet

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


## Clean Workspace Replay

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


## Validation Manifest

`reports/validation_manifest.json` records the local toolchain, task/run counts, public-export summary, expected regeneration commands, and artifact hashes. The main report itself is intentionally omitted from the hash list to avoid a self-referential report hash.

Generated at UTC: `2026-06-01T22:46:19.890548+00:00`

Git branch/head at generation: `main` / `96b908d36e3f`. Worktree status at generation: `clean`. The exact status lines are kept in the JSON manifest because this file is generated before the final commit.

Toolchain:

- Lean: `Lean (version 4.28.0, x86_64-w64-windows-gnu, commit 7e01a1bf5c70fc6167d49c345d3bf80596e9a79b, Release)`
- Lake: `Lake version 5.0.0-src+7e01a1b (Lean version 4.28.0)`
- Python: `3.11.9`
- Platform: `Windows-10-10.0.26200-SP0`

Task summary:

- total tasks in metadata: `26`
- acceptance statuses: `{"accepted_v0": 6, "calibration_only": 8, "rejected_duplicate": 2, "rejected_too_easy": 10}`
- run-result rows: `69` total, `66` local QA, `3` model-sweep
- public export: `14` tasks at `public_tasks`, hidden/wrong paths found: `0`

Regeneration commands:

1. `lake exe cache get`
2. `lake build`
3. `python scripts/validate_all.py`
4. `python scripts/audit_difficulty.py`
5. `python scripts/generate_task_quality_matrix.py`
6. `python scripts/generate_candidate_pruning_audit.py`
7. `python scripts/audit_diagnostic_coverage.py`
8. `python scripts/generate_construct_validity_matrix.py`
9. `python scripts/audit_human_time_calibration.py`
10. `python scripts/generate_human_timing_packet.py`
11. `python scripts/generate_independent_review_packet.py`
12. `python scripts/audit_independent_review_status.py`
13. `python scripts/record_local_qa_results.py`
14. `python scripts/generate_transcript_review_packet.py`
15. `python scripts/audit_failure_label_reviews.py`
16. `python scripts/audit_pin_coverage.py`
17. `python scripts/audit_run_integrity.py`
18. `python scripts/audit_grader_hardening.py`
19. `python scripts/generate_evaluation_protocol.py`
20. `python scripts/generate_statistical_analysis_plan.py`
21. `python scripts/generate_model_sweep_packet.py`
22. `python scripts/analyze_model_results.py`
23. `python scripts/audit_model_evidence_provenance.py`
24. `python scripts/generate_report.py`
25. `python scripts/audit_statistical_reporting.py`
26. `python scripts/audit_figure_manifest.py`
27. `python scripts/audit_data_schema_manifest.py`
28. `python scripts/generate_reviewer_reproduction_packet.py`
29. `python scripts/run_clean_workspace_replay.py`
30. `python scripts/audit_provider_readiness.py`
31. `python scripts/generate_report.py`
32. `python scripts/audit_report_source_traceability.py`
33. `python scripts/export_public_tasks.py --out public_tasks`
34. `python scripts/validate_public_export.py --out public_tasks`
35. `python scripts/audit_hosted_qa_readiness.py`
36. `python scripts/generate_task_asset_manifest.py --public-export public_tasks`
37. `python scripts/generate_accepted_task_cards.py`
38. `python scripts/audit_prompt_contracts.py`
39. `python scripts/audit_scaffold_support.py`
40. `python scripts/generate_threats_to_validity.py`
41. `python scripts/audit_threat_coverage.py`
42. `python scripts/audit_requirement_coverage.py --public-export public_tasks`
43. `python scripts/audit_claim_evidence.py`
44. `python scripts/generate_claim_authorization_matrix.py`
45. `python scripts/generate_research_claim_gap_matrix.py`
46. `python scripts/generate_concise_report.py`
47. `python scripts/audit_report_claim_conformance.py`
48. `python scripts/audit_report_shape.py`
49. `python scripts/audit_report_count_consistency.py`
50. `python scripts/generate_release_decision_log.py`
51. `python scripts/generate_freeze_readiness_roadmap.py`
52. `python scripts/audit_scaffold_support.py`
53. `python scripts/audit_requirement_coverage.py --public-export public_tasks`
54. `python scripts/audit_claim_evidence.py`
55. `python scripts/generate_claim_authorization_matrix.py`
56. `python scripts/generate_research_claim_gap_matrix.py`
57. `python scripts/generate_concise_report.py`
58. `python scripts/audit_report_claim_conformance.py`
59. `python scripts/audit_report_shape.py`
60. `python scripts/audit_report_count_consistency.py`
61. `python scripts/generate_release_decision_log.py`
62. `python scripts/generate_freeze_readiness_roadmap.py`
63. `python scripts/audit_scaffold_support.py`
64. `python scripts/audit_requirement_coverage.py --public-export public_tasks`
65. `python scripts/audit_claim_evidence.py`
66. `python scripts/generate_claim_authorization_matrix.py`
67. `python scripts/generate_research_claim_gap_matrix.py`
68. `python scripts/generate_concise_report.py`
69. `python scripts/audit_report_claim_conformance.py`
70. `python scripts/audit_report_shape.py`
71. `python scripts/audit_report_count_consistency.py`
72. `python scripts/generate_release_decision_log.py`
73. `python scripts/generate_freeze_readiness_roadmap.py`
74. `python scripts/write_validation_manifest.py --public-export public_tasks`
75. `python scripts/audit_validation_manifest.py`
76. `python scripts/generate_report.py`
77. `python scripts/audit_report_source_traceability.py`
78. `python scripts/audit_regeneration_commands.py`
79. `python scripts/write_validation_manifest.py --public-export public_tasks`
80. `python scripts/audit_validation_manifest.py`
81. `python scripts/generate_report.py`

Key artifact hashes:

| artifact | sha256 prefix | rows | bytes |
| --- | --- | ---: | ---: |
| `lean-toolchain` | `db7bb24b756d` |  | 25 |
| `lakefile.lean` | `1d842f6b4179` |  | 284 |
| `lake-manifest.json` | `601ea0517a05` |  | 3110 |
| `README.md` | `52e637a23717` |  | 20285 |
| `docs/axiom_policy.md` | `0adf66f9085a` |  | 712 |
| `data/benchmark_requirements.csv` | `9d56d361b3d1` | 71 | 17839 |
| `data/task_metadata.csv` | `2916f8cc78cc` | 26 | 19482 |
| `data/task_metadata_schema.json` | `a662bc8fb8e8` |  | 2317 |
| `data/run_results.csv` | `196d9de4ada4` | 69 | 15691 |
| `data/run_results_schema.json` | `5b41a198997f` |  | 1799 |
| `data/failure_annotations.csv` | `84e736888241` | 0 | 72 |
| `data/failure_labels.csv` | `96dd4a7de0fb` | 13 | 852 |
| `data/failure_label_schema.json` | `ae06ab834c14` |  | 481 |
| `data/scaffold_variants.csv` | `6ddd3f4fb586` | 3 | 379 |
| `data/model_sweep_plan.csv` | `c162dd19fb35` | 18 | 4099 |
| `data/model_sweep_execution_commands.csv` | `2559082a46e7` | 12 | 18653 |
| `data/model_sweep_execution_checklist.csv` | `d82ce46d70e6` | 7 | 1847 |
| `data/model_result_summary.csv` | `2cfee9603a36` | 10 | 1682 |
| `data/model_evidence_provenance_audit.csv` | `b6df2d6e0c50` | 7 | 2858 |
| `data/statistical_design_thresholds.csv` | `513aaa59e26f` | 7 | 4814 |
| `data/wilson_precision_table.csv` | `37ea4c8f4ca5` | 15 | 712 |
| `data/statistical_reporting_audit.csv` | `dbafbce2a5ad` | 9 | 4740 |
| `data/provider_readiness_audit.csv` | `391398d0edb7` | 12 | 5378 |
| `data/hosted_qa_readiness_audit.csv` | `aeba27f89c26` | 11 | 3290 |
| `data/threats_to_validity.csv` | `649cf81bb658` | 13 | 6777 |
| `data/threat_coverage_audit.csv` | `babdabd5070c` | 4 | 2834 |
| `data/transcript_review_queue.csv` | `ae3cbf568c1e` | 3 | 1347 |
| `data/failure_label_review_template.csv` | `737dcc43903c` | 3 | 373 |
| `data/failure_label_reviews.csv` | `94e458beda6b` | 3 | 1537 |
| `data/failure_label_review_schema.json` | `0ec0d05f9514` |  | 891 |
| `data/failure_label_review_audit.csv` | `70fbdec8c6b4` | 6 | 1871 |
| `data/validation_commands.csv` | `747620524702` | 66 | 12164 |
| `data/difficulty_audit.csv` | `46f1487950e4` | 26 | 13428 |
| `data/task_quality_matrix.csv` | `65b778c0ae0c` | 26 | 16869 |
| `data/candidate_pruning_audit.csv` | `3dad7f962b9f` | 26 | 19662 |
| `data/discarded_candidates.csv` | `d35af84cbc65` | 8 | 1334 |
| `data/hidden_check_inventory.csv` | `54e69574dfa8` | 20 | 2754 |
| `data/accepted_task_cards.csv` | `474af55b635d` | 6 | 9824 |
| `data/diagnostic_coverage_audit.csv` | `56194ecdf676` | 15 | 6702 |
| `data/construct_validity_matrix.csv` | `aa0ffef15c0e` | 6 | 3976 |
| `data/human_time_observations.csv` | `b742021c8ae3` | 0 | 79 |
| `data/human_time_observations_schema.json` | `5e06e5804dbc` |  | 740 |
| `data/human_time_calibration_audit.csv` | `d4174f9ef97b` | 26 | 7512 |
| `data/human_timing_collection_plan.csv` | `b0f91d18ccbd` | 6 | 4409 |
| `data/human_time_observations_template.csv` | `b2af36e038f6` | 6 | 277 |
| `data/independent_task_review_schema.json` | `6952eba4483e` |  | 2029 |
| `data/independent_task_reviews.csv` | `39665f7cb633` | 0 | 320 |
| `data/independent_task_review_plan.csv` | `80efa445e7d6` | 6 | 6513 |
| `data/independent_task_review_template.csv` | `da3950c0d22f` | 6 | 453 |
| `data/independent_review_status_audit.csv` | `534e997f2138` | 5 | 1459 |
| `data/task_asset_manifest.csv` | `11a7904fb684` | 171 | 37297 |
| `data/prompt_contract_audit.csv` | `8ac0cc6ea492` | 14 | 3106 |
| `data/pin_coverage_audit.csv` | `3e6fd3f10e92` | 26 | 9391 |
| `data/run_integrity_audit.csv` | `905d30f62a8c` | 69 | 14540 |
| `data/grader_hardening_audit.csv` | `b66f1f8fc357` | 9 | 3187 |
| `data/claim_evidence_audit.csv` | `2ec216f64e93` | 9 | 22244 |
| `data/claim_authorization_matrix.csv` | `306723eb220d` | 12 | 16546 |
| `data/research_claim_gap_matrix.csv` | `afdef5e23a7c` | 12 | 16565 |
| `data/report_claim_conformance_audit.csv` | `957a936c6167` | 11 | 4101 |
| `data/report_source_traceability.csv` | `f68cdd76dbef` | 33 | 14906 |
| `data/regeneration_command_consistency.csv` | `c8f4555256b9` | 4 | 1537 |
| `data/report_shape_audit.csv` | `162dd3825949` | 7 | 3350 |
| `data/report_count_consistency_audit.csv` | `b7f40ea404fc` | 8 | 5271 |
| `data/figure_manifest.csv` | `41b703492d89` | 10 | 5376 |
| `data/data_schema_manifest.csv` | `706683d1f73c` | 9 | 3823 |
| `data/reviewer_reproduction_steps.csv` | `0be804f614cf` | 15 | 8678 |
| `data/clean_workspace_replay.csv` | `be2899712c87` | 7 | 3641 |
| `data/release_decision_log.csv` | `b8c0d4720ecf` | 8 | 11525 |
| `data/freeze_readiness_roadmap.csv` | `9009f883ec82` | 10 | 12704 |
| `data/scaffold_support_audit.csv` | `5c97c5fb587a` | 11 | 3994 |
| `data/requirement_coverage.csv` | `d70409e92af4` | 71 | 27700 |
| `reports/difficulty_audit.md` | `4864ad083e8a` |  | 6942 |
| `reports/task_quality_matrix.md` | `652739777820` |  | 4990 |
| `reports/candidate_pruning_audit.md` | `07b1cb1ed464` |  | 7227 |
| `reports/accepted_task_cards.md` | `363beeaa16a9` |  | 12764 |
| `reports/diagnostic_coverage_audit.md` | `e9f7fe4e65a1` |  | 7206 |
| `reports/construct_validity_matrix.md` | `adc0a1b56429` |  | 4329 |
| `reports/human_time_calibration_audit.md` | `0297a19d85fd` |  | 1578 |
| `reports/human_timing_collection_packet.md` | `c70a24e043b6` |  | 4578 |
| `reports/independent_task_review_packet.md` | `b36997d5d15d` |  | 3984 |
| `reports/independent_review_status_audit.md` | `d7a1a8b8e6bd` |  | 2250 |
| `reports/task_asset_manifest.md` | `95480e1da7cf` |  | 1377 |
| `reports/prompt_contract_audit.md` | `9d7e7dd7a857` |  | 2659 |
| `reports/pin_coverage_audit.md` | `9dc62771263a` |  | 4145 |
| `reports/run_integrity_audit.md` | `75abcf6d7652` |  | 2213 |
| `reports/grader_hardening_audit.md` | `b543474dd490` |  | 4073 |
| `reports/claim_evidence_audit.md` | `5cd2c5a4f8b4` |  | 6738 |
| `reports/claim_authorization_matrix.md` | `f2efb00e0b08` |  | 7893 |
| `reports/research_claim_gap_matrix.md` | `1ca79f308321` |  | 11700 |
| `reports/report_claim_conformance_audit.md` | `b869f098efcd` |  | 4268 |
| `reports/report_source_traceability.md` | `eb3fdfb4c846` |  | 15667 |
| `reports/regeneration_command_consistency.md` | `420420054e6c` |  | 2166 |
| `reports/report_shape_audit.md` | `c5a11554e4ae` |  | 3373 |
| `reports/report_count_consistency_audit.md` | `466f232e24d5` |  | 5190 |
| `reports/figure_manifest.md` | `b39eb8a92c4c` |  | 6198 |
| `reports/data_schema_manifest.md` | `a23c90d22ad4` |  | 4381 |
| `reports/reviewer_reproduction_packet.md` | `f48c501206ea` |  | 5634 |
| `reports/clean_workspace_replay.md` | `a7727d6727df` |  | 2739 |
| `reports/concise_metr_report.md` | `c72b5a99811e` |  | 18905 |
| `reports/release_decision_log.md` | `11b6af90c6bc` |  | 12114 |
| `reports/freeze_readiness_roadmap.md` | `6b3e1cef3203` |  | 6032 |
| `reports/scaffold_support_audit.md` | `a4e45ef0d556` |  | 4916 |
| `reports/accepted_task_review.md` | `7ea531dc5f6e` |  | 13332 |
| `reports/evaluation_protocol.md` | `76d8ab27330f` |  | 6771 |
| `reports/model_sweep_execution_packet.md` | `7d7ee7f886c1` |  | 7332 |
| `reports/model_run_analysis.md` | `7ea88a7de75f` |  | 1965 |
| `reports/model_evidence_provenance_audit.md` | `ec82bbbab321` |  | 3200 |
| `reports/statistical_analysis_plan.md` | `759131325902` |  | 4662 |
| `reports/statistical_reporting_audit.md` | `16c69a8d8e03` |  | 3813 |
| `reports/provider_readiness_audit.md` | `01f5dc9a1da2` |  | 6359 |
| `reports/hosted_qa_readiness_audit.md` | `7c9d07aad947` |  | 3483 |
| `reports/threats_to_validity.md` | `43116dfa76d2` |  | 6684 |
| `reports/threat_coverage_audit.md` | `9354eebeb039` |  | 3415 |
| `reports/transcript_review_packet.md` | `58c5e52bf1b5` |  | 4276 |
| `reports/failure_label_review_audit.md` | `b8aa8b111870` |  | 2775 |
| `reports/requirement_coverage.md` | `78f005bf2730` |  | 24930 |
| `reports/figures/task_counts_by_family.svg` | `5833212738d0` |  | 2523 |
| `reports/figures/task_counts_by_bucket.svg` | `2ce3c13b007f` |  | 1479 |
| `reports/figures/top_skills.svg` | `27fb2a82febe` |  | 3806 |
| `reports/figures/run_rows_by_model.svg` | `50b22c3771fd` |  | 13402 |
| `reports/figures/task_minutes_by_bucket.svg` | `afef6d3c788f` |  | 3192 |
| `scripts/validate_all.py` | `1a9f7f73a567` |  | 6446 |
| `scripts/validate_task.py` | `1235a228d571` |  | 9683 |
| `scripts/audit_difficulty.py` | `0bebfeb74ec4` |  | 10134 |
| `scripts/generate_task_quality_matrix.py` | `129d2715090b` |  | 13165 |
| `scripts/generate_candidate_pruning_audit.py` | `320b553c34f4` |  | 13187 |
| `scripts/generate_accepted_task_cards.py` | `00c9c434eeee` |  | 13899 |
| `scripts/audit_diagnostic_coverage.py` | `d3f26a1fb7f7` |  | 13537 |
| `scripts/generate_construct_validity_matrix.py` | `c28dd2ce4c4b` |  | 11164 |
| `scripts/audit_human_time_calibration.py` | `9aa994547bbe` |  | 9107 |
| `scripts/generate_human_timing_packet.py` | `1927518b9beb` |  | 9316 |
| `scripts/generate_independent_review_packet.py` | `c8cbea1516d7` |  | 10710 |
| `scripts/audit_independent_review_status.py` | `9cc52ff163cd` |  | 8804 |
| `scripts/generate_task_asset_manifest.py` | `39b723c68b45` |  | 8843 |
| `scripts/audit_prompt_contracts.py` | `327ee834ce2d` |  | 9251 |
| `scripts/audit_pin_coverage.py` | `aaa6a5abbf28` |  | 15593 |
| `scripts/audit_run_integrity.py` | `0d57a7faa416` |  | 13598 |
| `scripts/audit_grader_hardening.py` | `7bcba063dd41` |  | 14898 |
| `scripts/audit_claim_evidence.py` | `d7788043c305` |  | 19034 |
| `scripts/generate_claim_authorization_matrix.py` | `96d55e2df744` |  | 22884 |
| `scripts/generate_research_claim_gap_matrix.py` | `53e3bdfcd86c` |  | 17966 |
| `scripts/audit_report_claim_conformance.py` | `b77d0684f1f2` |  | 18920 |
| `scripts/audit_report_source_traceability.py` | `588254e8f46e` |  | 30946 |
| `scripts/audit_report_count_consistency.py` | `c166095dc595` |  | 20053 |
| `scripts/audit_regeneration_commands.py` | `2059803ba297` |  | 11105 |
| `scripts/audit_figure_manifest.py` | `9d1717d9a6ff` |  | 11955 |
| `scripts/audit_data_schema_manifest.py` | `42a7e152571a` |  | 18608 |
| `scripts/generate_reviewer_reproduction_packet.py` | `f5460e7ddf25` |  | 18537 |
| `scripts/run_clean_workspace_replay.py` | `7df9aa349ef9` |  | 11361 |
| `scripts/generate_concise_report.py` | `16eca2b0032f` |  | 22749 |
| `scripts/audit_report_shape.py` | `c05401fcd5b5` |  | 11123 |
| `scripts/generate_release_decision_log.py` | `3e3c631059fa` |  | 16375 |
| `scripts/generate_freeze_readiness_roadmap.py` | `26ffefe8ecd1` |  | 20676 |
| `scripts/audit_scaffold_support.py` | `4e8cab1a8f2b` |  | 15866 |
| `scripts/audit_requirement_coverage.py` | `123cbe0a0d8d` |  | 132035 |
| `scripts/generate_evaluation_protocol.py` | `335e77481a6e` |  | 9710 |
| `scripts/generate_statistical_analysis_plan.py` | `fc6d38797a90` |  | 18559 |
| `scripts/generate_model_sweep_packet.py` | `338ab30af454` |  | 14347 |
| `scripts/analyze_model_results.py` | `eb7385902402` |  | 11969 |
| `scripts/audit_model_evidence_provenance.py` | `f97a3d01f536` |  | 14136 |
| `scripts/audit_statistical_reporting.py` | `62d3992d0214` |  | 14208 |
| `scripts/audit_provider_readiness.py` | `721efbd15df9` |  | 19841 |
| `scripts/audit_hosted_qa_readiness.py` | `b9a4b5dc34d4` |  | 13338 |
| `scripts/generate_threats_to_validity.py` | `da5b3121a97b` |  | 20033 |
| `scripts/audit_threat_coverage.py` | `e67a9460521e` |  | 11521 |
| `scripts/generate_transcript_review_packet.py` | `d65df15a3994` |  | 10925 |
| `scripts/audit_failure_label_reviews.py` | `03af6cabc1b3` |  | 11811 |
| `scripts/record_local_qa_results.py` | `e65fa7831bc3` |  | 5303 |
| `scripts/generate_report.py` | `c8c2e8de4f23` |  | 128444 |
| `scripts/export_public_tasks.py` | `ad45c6bdcdf2` |  | 2471 |
| `scripts/validate_public_export.py` | `586940302ff3` |  | 3575 |
| `scripts/anthropic_runner.py` | `4f940f91986e` |  | 2095 |
| `scripts/run_local_smoke.py` | `e885d0996d2f` |  | 1038 |
| `scripts/run_model_sweep.py` | `d5f981674ad3` |  | 10138 |
| `scripts/lean_lookup.py` | `5941c1285ef9` |  | 2425 |
| `scripts/audit_validation_manifest.py` | `a7dd1bb1be4b` |  | 14612 |
| `scripts/write_validation_manifest.py` | `cef391c2b263` |  | 18392 |


## Validation Manifest Audit

`reports/validation_manifest_audit.md` and `data/validation_manifest_audit.csv` check the validation manifest's schema, command coverage, artifact hashes, public-export snapshot, and dirty-status policy. This keeps the manifest from being overread as clean-checkout or hosted-QA evidence.

- checks: `8`
- statuses: `{"pass": 8}`
- areas: `{"artifact_hashes": 3, "commands": 1, "counts": 1, "git_state": 1, "manifest_schema": 1, "public_export": 1}`
- failures: `0`

Validation manifest audit rows:

| check | area | status | evidence | limitation |
| --- | --- | --- | --- | --- |
| `schema_and_policy_note` | manifest_schema | pass | schema_version=1; generated_at_present=True; tool_versions_present=True; policy_note_present=True | The manifest records generation-time state and intentionally omits self-referential main-report hashes. |
| `regeneration_command_coverage` | commands | pass | commands=81; required=35; missing=[] | Command coverage proves the intended local gate is listed, not that it was run on a clean hosted environment. |
| `artifact_hash_integrity` | artifact_hashes | pass | artifacts=177; checked_hashes=177; hash_mismatches=0; missing_recorded_paths=0; examples=[] | The manifest hashes generated local artifacts but intentionally avoids self-referential report hashes. |
| `artifact_inventory_coverage` | artifact_hashes | pass | inventory_candidates=166; recorded_artifacts=177; allowed_unhashed=5; missing_inventory=0; examples=[] | The inventory check covers data CSVs, report markdown, and scripts. It intentionally excludes self-referential final reports, the validation-manifest audit output, and the progress log. |
| `self_reference_boundary` | artifact_hashes | pass | main_report_omitted=True; evidence_appendix_omitted=True; policy_note_mentions_omission=True | The main report and appendix are regenerated after manifest writing and therefore cannot be hashed by the manifest without circularity. |
| `public_export_snapshot` | public_export | pass | configured=True; exists=True; task_count=14; hidden_or_wrong_path_count=0 | This is a local public-export snapshot, not hosted QA evidence. |
| `git_snapshot_policy` | git_state | pass | dirty=False; status_entries=0; policy_note_present=True | A dirty generation-time snapshot is expected for committed report updates; this is not a clean-checkout proof. |
| `summary_count_snapshot` | counts | pass | task_count=26; acceptance_status_counts={"accepted_v0": 6, "calibration_only": 8, "rejected_duplicate": 2, "rejected_too_easy": 10}; run_rows=69; local_qa_rows=66; model_rows=3 | Count snapshots are local evidence and do not imply benchmark-scale sufficiency. |


## Regeneration Command Consistency Audit

`reports/regeneration_command_consistency.md` and `data/regeneration_command_consistency.csv` check that README validation commands, manifest-source commands, committed manifest commands, and reviewer local-replay commands stay synchronized. This is a replay-instruction consistency guard, not evidence that hosted QA or provider sweeps have run.

- checks: `4`
- statuses: `{"pass": 4}`
- areas: `{"command_sequence": 2, "required_command_coverage": 1, "reviewer_reproduction": 1}`
- failures: `0`

Regeneration-command checks:

| check | area | status | evidence | required action |
| --- | --- | --- | --- | --- |
| `readme_matches_manifest_source` | command_sequence | pass | readme_commands=81; source_commands=81; first_readme=['lake exe cache get', 'lake build', 'python scripts/validate_all.py']; last_readme=['python scripts/write_validation_manifest.py --public-export public_tasks', 'python scripts/audit_validation_manifest.py', 'python scripts/generate_report.py'] | Update README.md and scripts/write_validation_manifest.py together whenever the local gate changes. |
| `json_manifest_matches_source` | command_sequence | pass | manifest_commands=81; source_commands=81; manifest_present=True | Run scripts/write_validation_manifest.py after editing the regeneration command list. |
| `required_commands_in_public_gate` | required_command_coverage | pass | required=35; missing_readme=0; missing_source=0; missing_manifest=0 | Keep the required-command set visible in both the README gate and validation manifest command list. |
| `reviewer_packet_local_subset` | reviewer_reproduction | pass | reviewer_rows=15; local_reviewer_commands=14; missing_from_full_gate=0 | Keep reviewer local-replay commands as a subset of the full local regeneration gate. |


## Threats To Validity

The generated register in `reports/threats_to_validity.md` is the authoritative limitations table for this report. It currently keeps the strongest benchmark claims blocked where evidence is missing, including task-count scale, T3/T4 time-horizon depth, independent human timing, scaffold-sweep coverage, frontier/open-model coverage, statistical power, and hosted QA.

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
