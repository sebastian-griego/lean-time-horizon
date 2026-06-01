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
| `transcript_and_run_result_evidence` | post_run | blocked | Commit run_results rows and transcript JSONL files, then rerun integrity and model-result analysis. |
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
| `transcript_provenance` | run_data | pass | provider_transcripts=3; missing_transcripts=[] | Transcript existence does not imply transcript labels have been independently adjudicated. | Keep transcript files committed or explicitly mark infra rows with enough diagnostic detail. |
| `summary_count_consistency` | analysis_data | pass | summary_rows=10; mismatches=[]; primary_planned_cells=18; primary_covered_noninfra=1 | The summary intentionally records undercoverage rather than performance conclusions. | Regenerate scripts/analyze_model_results.py after any run_results change. |
| `report_sample_size_and_version_disclosure` | report_text | pass | model_versions_in_detailed_report=1/1; missing_versions=[]; missing_main_phrases=[]; missing_model_analysis_phrases=[] | The concise report summarizes counts but leaves full model-version rows to the detailed evidence appendix. | Keep sample sizes, k, infra policy, and model versions visible in generated report text. |
| `local_qa_exclusion_boundary` | claim_boundary | pass | local_qa_rows=66; provider_rows=3 | Local QA rows validate grading behavior and must not enter model-capability summaries. | Keep local QA excluded from model_result_summary and benchmark pass-rate text. |
| `infra_policy_boundary` | claim_boundary | pass | provider_infra_rows=1; accepted_infra_rows=1 | Provider reliability claims need many more rows; this row only checks accounting policy disclosure. | Retain infra rows in raw data and report them separately from capability means. |


## Statistical Reporting Audit

`reports/statistical_reporting_audit.md` and `data/statistical_reporting_audit.csv` check whether the committed provider rows can support the playbook's recommended performance plots and claims.

- checks: `8`
- statuses: `{"block": 5, "pass": 3}`
- areas: `{"data_hygiene": 2, "planned_sweep": 1, "recommended_plot": 4, "statistical_method": 1}`
- blocked performance outputs: `5`
- failing statistical hygiene checks: `0`

Statistical reporting checks:

| check | area | status | current sample | limitation | next action |
| --- | --- | --- | --- | --- | --- |
| `primary_sweep_coverage` | planned_sweep | block | 1/18 accepted task/scaffold cells covered by non-infra provider rows | The committed provider rows cannot support accepted-core performance estimates. | Run the planned accepted_v0 x scaffold sweep before reporting benchmark performance. |
| `scaffold_pass_at_k_plot` | recommended_plot | block | 1/3 scaffolds observed; 1 non-infra accepted-core rows | A mean pass@10-by-scaffold plot would imply comparisons the data do not support. | Populate all one-shot, lookup, and lookup_unlimited cells before generating scaffold-effect plots. |
| `bucket_success_plot` | recommended_plot | block | 1 human-time buckets observed in non-infra accepted-core provider rows | Current rows cannot estimate success by human-time bucket. | Run the planned sweep and add T3/T4 accepted tasks before plotting time-horizon success curves. |
| `family_success_plot` | recommended_plot | block | 1/6 accepted families observed in non-infra provider rows | Current rows cannot estimate success by task family. | Run provider rows across the accepted core before family-level summaries. |
| `failure_taxonomy_plot` | recommended_plot | block | 1 non-infra provider failure rows | The current failure taxonomy is useful for transcript QA but too small for distributional claims. | Collect provider failures across the planned scaffold sweep and review labels before plotting. |
| `wilson_interval_reporting` | statistical_method | pass | model_result_summary rows=10 | Intervals are not a substitute for adequate coverage or independent timing. | Keep Wilson intervals in future performance summaries and report raw n. |
| `local_qa_exclusion` | data_hygiene | pass | 3 provider rows; 66 local QA rows | No benchmark performance claim should use local reference/wrong rows. | Keep local QA and provider rows separated in future analyses. |
| `infra_failure_policy` | data_hygiene | pass | Infra failures retained in run_results and counted separately. | Provider reliability claims still need more rows. | Keep infra rows in raw data and exclude them from model-capability means. |


## Provider Readiness Audit

`reports/provider_readiness_audit.md` and `data/provider_readiness_audit.csv` check model-runner readiness without using provider credentials or creating new model results. The audit separates runner contracts, adapter coverage, credential policy, transcript evidence, planned sweep commands, and smoke-only provider coverage.

- checks: `11`
- statuses: `{"block": 1, "caution": 1, "pass": 9}`
- areas: `{"credential_policy": 2, "planned_sweep": 1, "provider_adapter_surface": 2, "reporting": 1, "run_data": 3, "runner_contract": 2}`
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

- threats: `12`
- statuses: `{"block": 7, "caution": 3, "controlled": 2}`
- categories: `{"construct_validity": 2, "external_validity": 2, "internal_validity": 3, "operational_security": 2, "operational_validity": 1, "statistical_validity": 2}`
- severities: `{"high": 8, "medium": 4}`
- blocked validity threats: `7`
- caution validity threats: `3`
- locally controlled threats: `2`

Threat register:

| threat | category | severity | status | evidence | stronger evidence needed | claims limited |
| --- | --- | --- | --- | --- | --- | --- |
| `construct_time_horizon_depth` | construct_validity | high | block | accepted=6; accepted buckets={"T2": 5, "T3": 1}; diagnostic blocks=1; diagnostic cautions=3 | Add independently reviewed and timed T3/T4 tasks, including at least one T4 stretch row. | time_horizon_measurement;locked_benchmark |
| `portfolio_scale_and_balance` | external_validity | high | block | accepted=6; calibration_only=8; rejected=12; accepted families={"algorithm_correctness": 1, "direct_theorem_proving": 1, "informal_spec_to_formal": 1, "invariant_verification_ml_optimization": 1, "proof_repair_codebase": 1, "small_formal_library_construction": 1} | Reach the 20-50 accepted-task target while preserving family and capability diversity. | frontier_performance;locked_benchmark;family_level_performance |
| `author_estimated_human_time` | internal_validity | high | block | accepted timed solves=0/6; human_time_observation_rows=0 | Collect independent Lean-human timed solves or second-review timing notes for every accepted task. | time_horizon_measurement;locked_benchmark |
| `automation_dominated_retained_tasks` | construct_validity | medium | caution | automation-dominated accepted tasks=2: ["lt-201", "lt-206"] | Replace or independently validate retained caveat rows before locked benchmark status. | accepted_core_reviewed;time_horizon_measurement |
| `semantic_pin_finiteness` | internal_validity | medium | caution | accepted tasks with hidden-pin wrong failures=4/6; proof-only fixed-statement rows=2 | Have an independent reviewer inspect hidden pins and add richer same-signature hidden wrongs for future mutable tasks. | hidden_pin_strength;grading_validity |
| `scaffold_sweep_undercoverage` | statistical_validity | high | block | planned accepted-core cells=18; covered non-infra cells=1 | Run accepted_v0 x one-shot/lookup/lookup_unlimited rows with fixed k and committed transcripts. | scaffold_effects;frontier_performance |
| `frontier_performance_undercoverage` | external_validity | high | block | accepted-core non-infra provider rows=1; accepted tasks=6 | Run documented frontier/open-model sweeps across the accepted scaffold plan with model versions and transcripts. | frontier_performance;locked_benchmark |
| `statistical_power_and_plots` | statistical_validity | high | block | statistical audit rows=8; blocked outputs=5 | Populate the planned sweep and accepted task count before generating scaffold, family, and bucket performance plots. | scaffold_effects;frontier_performance;family_level_performance |
| `failure_taxonomy_forecast` | internal_validity | medium | caution | accepted-core non-infra provider rows=1; transcript review queue rows=3; high/critical review rows=1 | Label real model transcripts after the scaffold sweep, adjudicate disagreements, and compare observed failures to intended diagnostic modes. | diagnostic_failure_distribution;scaffold_effects |
| `hosted_environment_gap` | operational_validity | high | block | hosted readiness rows=11; blocked hosted-QA steps=9 | Create hosted packaging, run Full Env QA/Env Linter on exact problem versions, and commit findings/dispositions. | locked_benchmark;deployment_reliability |
| `secret_and_runner_boundary` | operational_security | medium | controlled | provider readiness failures=0; model-sweep command key-assignment leaks=0 | Repeat secret scans before every commit that touches runner or transcript files. | artifact_security;provider_run_reproducibility |
| `public_export_hidden_leakage` | operational_security | high | controlled | public_tasks exists=True; hidden/wrong paths in export=0 | Validate the public export after every task-asset or export-script change. | public_release_safety;locked_benchmark |


## Committed Run Results

66 local QA rows are committed for reference solutions and plausible wrong submissions. These rows are not model performance and are excluded from benchmark pass-rate summaries.

Local QA row status:

- `expected_failure`: 40
- `passed`: 26

Accepted-core provider row summary:

- `one-shot`: pass@k mean 0.00 (0/1 rows; Wilson 95% CI 0.00-0.79)

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
| `research_report_evidence` | report_validity | supported | high | The report is generated from committed data and includes a concise reviewer-facing METR-style report, a report-shape audit that checks the narrative against the playbook questions, research-quality caveats, task quality matrices, diagnostic-coverage checks, human-time calibration checks, a human-timing collection packet, a transcript-review packet, task-asset hashes, prompt-contract checks, pin coverage, run integrity, grader-hardening checks, statistical reporting checks, model-evidence provenance checks for sample sizes and model versions, provider-readiness checks, a model-sweep execution packet, hosted-QA readiness checks, a generated threats-to-validity register, a claim-authorization matrix with forbidden overclaim wording, a research claim gap matrix that maps stronger claims to missing evidence packages, a report claim-conformance audit that checks prose against those authorizations, scaffold-support checks, release-decision gates, a freeze-readiness roadmap, and a prospective evaluation protocol. | The report is still limited by missing broad model sweeps and independent human timing. | Run the planned scaffold sweep, collect independent timing, and add external QA artifacts. |
| `accepted_core_reviewed` | task_validity | supported | medium | The six accepted-core tasks are internally reviewed and higher quality than the original candidate pool. | This is an internal-review claim. Several accepted rows retain caveats and the core size is below the target benchmark size. | Independent Lean-human review and more accepted high-quality T2/T3/T4 rows. |
| `hidden_pin_strength` | grading_validity | supported | medium | Hidden checks provide meaningful anti-gaming evidence for accepted tasks, with semantic hidden-pin failures on mutable-definition tasks and signature/downstream guards on proof-only fixed-statement tasks. | Proof-only fixed-statement rows do not have semantic hidden wrongs because Lean compilation already certifies exact same-signature theorem proofs; hidden pins remain finite probes. | Add independent reviewer assessment of hidden pins and strengthen any future mutable accepted task until it has at least one public-compiling wrong that fails hidden pins. |
| `run_data_integrity` | data_validity | supported | high | Committed run-result rows are internally consistent with transcripts, failure labels, score vectors, and pass@k semantics. | This validates data hygiene only; it does not make the smoke rows representative. | Maintain this audit for future provider sweeps and require zero failing rows before reporting results. |
| `time_horizon_measurement` | construct_validity | partial | low | The current artifact measures model behavior across increasing time horizons. | Accepted core has only T2/T3 coverage and no T4; human times are author/reviewer estimates rather than independent solves. | Add independently timed T3/T4 tasks before claiming strong time-horizon measurement. |
| `scaffold_effects` | performance_claim | unsupported | none | The report supports conclusions about how lookup and iterative compile/debug scaffolds change model performance. | The scaffold ladder is implemented and planned, but real accepted-core provider data cover only one one-shot cell. | Run accepted-core pass@10 or equivalent rows across one-shot, lookup, and lookup_unlimited. |
| `frontier_performance` | performance_claim | unsupported | none | Committed provider rows characterize frontier-model performance on this benchmark. | Only tiny smoke evidence is committed, including an infra failure; local QA rows are not model performance. | Run the planned accepted-core scaffold sweep with documented provider versions and cost/infra notes. |
| `locked_benchmark` | benchmark_status | unsupported | none | v0.1 is a locked benchmark suitable for population-level frontier-model claims. | The artifact has 6 accepted tasks, no hosted QA, no independent timing, no T4 accepted task, and limited provider data. | Reach the 20-50 accepted-task target, run hosted QA, collect independent timing, complete scaffold sweeps, and freeze exact public task versions. |


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
| `failure_taxonomy_results` | failure_analysis | allowed_with_caveat | The repo has a failure-label schema, transcript links, and a transcript review queue for non-local rows. | Failure labels are not independently adjudicated yet; queued rows still needing review: 3. | Do not claim dominant failure modes, distributional failure analysis, or adjudicated taxonomy results. |
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
| `accepted_core_quality` | allowed_with_caveat | high | `portfolio_accepted_count;time_horizon_spread;independent_human_time_review` | 20-50 hard-reviewed accepted tasks, stronger T3/T4 coverage, independent Lean-human timing, and refreshed per-task review. | Accepted-core quality can support benchmark-level aggregates only after scale, depth, and independent review gates are supported. |
| `time_horizon_scope` | allowed_with_caveat | high | `time_horizon_spread;independent_human_time_review;portfolio_accepted_count` | Independently timed T2/T3/T4 tasks, including at least one T4 stretch row and enough accepted tasks to avoid singleton bucket claims. | The report can claim robust time-horizon measurement only after accepted tasks cover meaningful T2/T3/T4 depth with independent timing evidence. |
| `scaffold_effects` | blocked | high | `scaffold_result_comparison;frontier_model_evidence` | Non-infra pass@k rows across accepted_v0 x one-shot/lookup/lookup_unlimited cells, with fixed k, model versions, transcripts, and run-integrity checks. | Empirical scaffold-effect claims require the planned accepted-core scaffold sweep to be covered and analyzed with raw n and intervals. |
| `frontier_model_performance` | blocked | high | `frontier_model_evidence;scaffold_result_comparison;hosted_qa_env_linter` | Documented frontier/open-model provider rows with model versions, transcripts, infra notes, hosted-QA-cleared tasks, and integrity audits. | Frontier-performance wording remains blocked until broad provider rows exist on stable, locally and hosted-QA-checked task versions. |
| `statistical_performance_reporting` | blocked | high | `scaffold_result_comparison;frontier_model_evidence;portfolio_accepted_count` | Sufficiently covered accepted-core sweeps, raw task-row numerators, Wilson intervals, and regenerated statistical reporting checks. | Performance plots should stay blocked until scaffold/provider coverage and accepted-task scale support the plotted comparisons. |
| `hosted_qa_status` | blocked | high | `hosted_qa_env_linter` | Hosted/Taiga package evidence, exact problem-version mapping, Full Env QA runs, Env Linter findings, and rebuttal/fix dispositions. | Hosted-QA wording can be upgraded only after warning/error/critical findings are fixed or concretely rebutted for exact final versions. |
| `locked_benchmark_status` | blocked | highest | `portfolio_accepted_count;time_horizon_spread;scaffold_result_comparison;frontier_model_evidence;independent_human_time_review;hosted_qa_env_linter` | 20-50 accepted tasks, T2/T3/T4 depth, independent timing, completed scaffold/provider sweeps, hosted QA, settled findings, and frozen exact public versions. | The locked-benchmark claim remains blocked until every locked-benchmark requirement is supported and the release/freeze gates have no blocking rows. |


## Report Claim Conformance Audit

`reports/report_claim_conformance_audit.md` and `data/report_claim_conformance_audit.csv` check that the concise report, detailed report, and README obey the claim-authorization matrix. The audit scans for missing caveats, blocked-claim phrase contexts, and report-shape drift.

- checks: `10`
- statuses: `{"pass": 10}`
- scopes: `{"claim_authorization": 1, "concise_report": 1, "main_report": 6, "readme": 1, "reports_and_readme": 1}`

Claim-conformance checks:

| check | scope | status | evidence | required action |
| --- | --- | --- | --- | --- |
| `authorization_matrix_loaded` | claim_authorization | pass | authorization rows=12; statuses={"allowed": 1, "allowed_with_caveat": 6, "blocked": 5}; blocked=5; caveated=6 | Regenerate scripts/generate_claim_authorization_matrix.py and inspect blocked/caveated coverage. |
| `main_report_authorization_section` | main_report | pass | section_present=True; claim_ids_in_matrix=12; missing_claim_ids=[] | Regenerate reports/metr_style_report.md after claim authorization and ensure every authorization row is visible. |
| `abstract_scope_boundaries` | main_report | pass | front-matter scope phrases checked before the first task table | Keep locked-benchmark, sample-size, human-time, and provider-smoke limitations in the report abstract/front matter. |
| `run_result_boundary_wording` | main_report | pass | committed-run section checked for local-QA and smoke-row boundaries | Keep local QA and tiny provider smoke rows explicitly separated from benchmark performance claims. |
| `claim_ledger_blocks_overclaims` | main_report | pass | claim ledger checked for explicit not-supported locked-benchmark and frontier-performance rows | Keep tempting overclaims in the claim ledger as unsupported, not as conclusions. |
| `concise_report_scope_and_length` | concise_report | pass | concise report exists=True; line_count=173; missing_scope_phrases=[] | Regenerate scripts/generate_concise_report.py and keep the reviewer-facing report concise and claim-bounded. |
| `blocked_phrase_context_scan` | reports_and_readme | pass | blocked-claim phrase contexts scanned across reports\metr_style_report.md, reports\concise_metr_report.md, reports\evidence_appendix.md, and README.md; unsafe_contexts=0 | Rewrite any blocked-claim phrase so the local context clearly says it is unsupported, blocked, missing, or future work. |
| `readme_scope_boundaries` | readme | pass | README checked for locked-benchmark, model-result, and credential-scope boundaries | Keep the README top-level scope aligned with the report's claim authorization matrix. |
| `limitations_cover_blockers` | main_report | pass | limitations section checked against blocked authorization themes | Keep task-count, T4, independent-timing, provider-smoke, hosted-QA, and locked-benchmark caveats in the limitations section. |
| `report_length_and_appendix_boundary` | main_report | pass | main report line_count=224; markdown_table_rows=60; evidence_appendix_exists=True; evidence_appendix_line_count=1125 | Keep the main report skimmable and keep row-level generated tables in reports/evidence_appendix.md. |


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
| `success_changes_by_scaffold_and_bucket` | How does success change with scaffold and human-time bucket? | blocked_by_evidence | scaffold_result_comparison=partial; time_horizon_spread=partial; primary_covered_noninfra=1 | Real scaffold/time-horizon performance summaries are not supported by committed data. | Run pass@k sweeps across accepted_v0 x scaffold cells and add independently timed T3/T4 tasks. |
| `failure_modes_dominate` | What failure modes dominate? | blocked_by_evidence | concision_mentions_failure_limits=True; missing_phrases=[] | Expected failure modes are documented, but broad model transcripts are not independently adjudicated. | Use the transcript review packet after broader provider sweeps before claiming dominant failure modes. |
| `next_batch_needs` | What does the next batch need? | answered | missing_phrases=[] | Next work is a concrete blocker list, not a claim that the benchmark is locked. | Keep next-work items tied to requirement/freeze gates. |
| `skimmability` | Is the main report skimmable? | answered | concise_report_lines=173; conformance_failures=0 | The concise report is short, and row-level generated tables live in the evidence appendix instead of the main narrative. | Keep the concise and main reports short and keep long tables in generated appendices. |


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
| `accepted_core_stats_scope` | task_set | caution | Use accepted_v0 rows for artifact-level task-quality summaries only; do not use them for population-level frontier claims. | Add independently reviewed T2/T3/T4 rows before treating accepted-core aggregates as benchmark estimates. |
| `hidden_pin_confidence` | grading | caution | Treat hidden pins as meaningful anti-gaming probes but not exhaustive semantic equivalence checks. | Add same-signature hidden-pin failures where realistic and expand negative examples for retained caveat rows. |
| `time_horizon_claim` | construct_validity | block | Do not claim strong time-horizon measurement yet. | Add independently timed T3/T4 tasks, including at least one T4 row, before claiming robust time-horizon coverage. |
| `scaffold_effect_claim` | performance | block | Do not report scaffold-effect conclusions from committed data. | Run the planned accepted_v0 x scaffold sweep with fixed k before comparing scaffold effects. |
| `frontier_performance_claim` | performance | block | Do not use committed provider rows to characterize frontier-model capability. | Run documented provider sweeps after local and hosted QA are stable. |
| `locked_benchmark_freeze` | benchmark_status | block | Do not call v0.1 a locked benchmark. | Reach the 20-50 accepted-task target, complete hosted QA, independent timing, and scaffold sweeps, then freeze exact task versions. |


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
| `independent_human_timing` | calibration | block | Every accepted task should have at least one independent Lean-human solve or second-review timing note; T3/T4 rows should get extra scrutiny. | Run timed solves with non-authors and append rows to data/human_time_observations.csv before freeze. | `time_horizon_measurement, locked_benchmark` |
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
- accepted-core wrong failures at hidden-pin stage: `5`
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
| `lt-206` | semantic_pins_exercised | mutable_definitions_plus_theorems | semantic_positive_negative_guard | feasible_via_definition_semantics | 0 | 1 | Accepted row has at least one wrong submission reaching hidden pins and nontrivial examples. |


## Requirement Coverage Audit

`reports/requirement_coverage.md` and `data/requirement_coverage.csv` map the repository to the committed checklist in `data/benchmark_requirements.csv`. This is a stricter evidence index than the narrative claim ledger.

Status counts:

- `supported`: 49
- `partial`: 4
- `not_met`: 2

Freeze relevance counts:

- `required_for_locked_benchmark`: supported 2, partial 4, not_met 2
- `required_for_release_artifact`: supported 15
- `required_for_research_report`: supported 32

Partial or unmet requirements:

| id | area | freeze relevance | status | evidence | next step |
| --- | --- | --- | --- | --- | --- |
| `portfolio_accepted_count` | portfolio | required_for_locked_benchmark | not_met | 6 accepted_v0 tasks; 8 calibration-only tasks; 12 rejected archive tasks. | Add and hard-review more high-quality T2/T3/T4 tasks before claiming a full benchmark. |
| `time_horizon_spread` | portfolio | required_for_locked_benchmark | partial | Accepted bucket counts: {"T2": 5, "T3": 1}; release bucket counts: {"T1": 8, "T2": 5, "T3": 1}. | Add more accepted T3/T4 tasks, including a T4 stretch row, and independently review human times. |
| `scaffold_result_comparison` | scaffolds | required_for_locked_benchmark | partial | Non-infra model rows: 2; scaffolds observed: ["one-shot"]; planned rows: 18. | Run real pass@10 or comparable sweeps across one-shot, lookup, and lookup_unlimited before performance claims. |
| `frontier_model_evidence` | runs | required_for_locked_benchmark | partial | Non-infra model rows: 2 over 6 accepted tasks; total model rows including infra failures: 3. | Run broader provider sweeps only after local and hosted QA are stable. |
| `independent_human_time_review` | calibration | required_for_locked_benchmark | partial | Accepted tasks with manual_review_complete: 6/6; accepted tasks with successful independent timing observations: 0/6; observation rows: 0. | Collect independent Lean-human timed solves or second-reviewer timing notes before freeze. |
| `hosted_qa_env_linter` | qa | required_for_locked_benchmark | not_met | Hosted QA artifacts present: 0/2; hosted readiness report exists: True; blocked hosted-readiness checks: 9. | Run hosted Full Env QA and record findings/rebuttals before claiming a locked benchmark. |


## Reproducibility Checklist

The intended local regeneration gate is:

```powershell
lake build
python scripts/validate_all.py
python scripts/audit_difficulty.py
python scripts/generate_task_quality_matrix.py
python scripts/audit_diagnostic_coverage.py
python scripts/audit_human_time_calibration.py
python scripts/generate_human_timing_packet.py
python scripts/record_local_qa_results.py
python scripts/generate_transcript_review_packet.py
python scripts/audit_pin_coverage.py
python scripts/audit_run_integrity.py
python scripts/audit_grader_hardening.py
python scripts/generate_evaluation_protocol.py
python scripts/generate_model_sweep_packet.py
python scripts/analyze_model_results.py
python scripts/audit_model_evidence_provenance.py
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
python scripts/generate_threats_to_validity.py
python scripts/audit_requirement_coverage.py --public-export public_tasks
python scripts/audit_claim_evidence.py
python scripts/generate_claim_authorization_matrix.py
python scripts/generate_research_claim_gap_matrix.py
python scripts/generate_concise_report.py
python scripts/audit_report_claim_conformance.py
python scripts/audit_report_shape.py
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
python scripts/generate_release_decision_log.py
python scripts/generate_freeze_readiness_roadmap.py
python scripts/write_validation_manifest.py --public-export public_tasks
python scripts/generate_report.py
```

The public export validator checks that hidden references and wrong submissions are absent from `public_tasks`, all metadata-listed public files are present, exported Lean files compile, and obvious hidden-reference path strings do not leak.

## Validation Manifest

`reports/validation_manifest.json` records the local toolchain, task/run counts, public-export summary, expected regeneration commands, and artifact hashes. The main report itself is intentionally omitted from the hash list to avoid a self-referential report hash.

Generated at UTC: `2026-06-01T11:45:14.853436+00:00`

Git branch/head at generation: `main` / `ca92adba484f`. Worktree status at generation: `23 pre-commit path(s) recorded`. The exact status lines are kept in the JSON manifest because this file is generated before the final commit.

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

1. `lake build`
2. `python scripts/validate_all.py`
3. `python scripts/audit_difficulty.py`
4. `python scripts/generate_task_quality_matrix.py`
5. `python scripts/audit_diagnostic_coverage.py`
6. `python scripts/audit_human_time_calibration.py`
7. `python scripts/generate_human_timing_packet.py`
8. `python scripts/record_local_qa_results.py`
9. `python scripts/generate_transcript_review_packet.py`
10. `python scripts/audit_pin_coverage.py`
11. `python scripts/audit_run_integrity.py`
12. `python scripts/audit_grader_hardening.py`
13. `python scripts/generate_evaluation_protocol.py`
14. `python scripts/generate_model_sweep_packet.py`
15. `python scripts/analyze_model_results.py`
16. `python scripts/audit_model_evidence_provenance.py`
17. `python scripts/generate_report.py`
18. `python scripts/audit_statistical_reporting.py`
19. `python scripts/audit_provider_readiness.py`
20. `python scripts/generate_report.py`
21. `python scripts/export_public_tasks.py --out public_tasks`
22. `python scripts/validate_public_export.py --out public_tasks`
23. `python scripts/audit_hosted_qa_readiness.py`
24. `python scripts/generate_task_asset_manifest.py --public-export public_tasks`
25. `python scripts/audit_prompt_contracts.py`
26. `python scripts/audit_scaffold_support.py`
27. `python scripts/generate_threats_to_validity.py`
28. `python scripts/audit_requirement_coverage.py --public-export public_tasks`
29. `python scripts/audit_claim_evidence.py`
30. `python scripts/generate_claim_authorization_matrix.py`
31. `python scripts/generate_research_claim_gap_matrix.py`
32. `python scripts/generate_concise_report.py`
33. `python scripts/audit_report_claim_conformance.py`
34. `python scripts/audit_report_shape.py`
35. `python scripts/generate_release_decision_log.py`
36. `python scripts/generate_freeze_readiness_roadmap.py`
37. `python scripts/audit_scaffold_support.py`
38. `python scripts/audit_requirement_coverage.py --public-export public_tasks`
39. `python scripts/audit_claim_evidence.py`
40. `python scripts/generate_claim_authorization_matrix.py`
41. `python scripts/generate_research_claim_gap_matrix.py`
42. `python scripts/generate_concise_report.py`
43. `python scripts/audit_report_claim_conformance.py`
44. `python scripts/audit_report_shape.py`
45. `python scripts/generate_release_decision_log.py`
46. `python scripts/generate_freeze_readiness_roadmap.py`
47. `python scripts/audit_scaffold_support.py`
48. `python scripts/audit_requirement_coverage.py --public-export public_tasks`
49. `python scripts/audit_claim_evidence.py`
50. `python scripts/generate_claim_authorization_matrix.py`
51. `python scripts/generate_research_claim_gap_matrix.py`
52. `python scripts/generate_concise_report.py`
53. `python scripts/audit_report_claim_conformance.py`
54. `python scripts/audit_report_shape.py`
55. `python scripts/generate_release_decision_log.py`
56. `python scripts/generate_freeze_readiness_roadmap.py`
57. `python scripts/write_validation_manifest.py --public-export public_tasks`
58. `python scripts/generate_report.py`

Key artifact hashes:

| artifact | sha256 prefix | rows | bytes |
| --- | --- | ---: | ---: |
| `lean-toolchain` | `db7bb24b756d` |  | 25 |
| `lakefile.lean` | `1d842f6b4179` |  | 284 |
| `lake-manifest.json` | `601ea0517a05` |  | 3110 |
| `README.md` | `dbe07091016a` |  | 15033 |
| `docs/axiom_policy.md` | `0adf66f9085a` |  | 712 |
| `data/benchmark_requirements.csv` | `7090920d60ad` | 55 | 13034 |
| `data/task_metadata.csv` | `2916f8cc78cc` | 26 | 19482 |
| `data/task_metadata_schema.json` | `a662bc8fb8e8` |  | 2317 |
| `data/run_results.csv` | `196d9de4ada4` | 69 | 15691 |
| `data/run_results_schema.json` | `5b41a198997f` |  | 1799 |
| `data/failure_label_schema.json` | `ae06ab834c14` |  | 481 |
| `data/scaffold_variants.csv` | `6ddd3f4fb586` | 3 | 379 |
| `data/model_sweep_plan.csv` | `c162dd19fb35` | 18 | 4099 |
| `data/model_sweep_execution_commands.csv` | `01916bfc1a7c` | 12 | 16361 |
| `data/model_sweep_execution_checklist.csv` | `73f34b7e239e` | 7 | 1778 |
| `data/model_result_summary.csv` | `2cfee9603a36` | 10 | 1682 |
| `data/model_evidence_provenance_audit.csv` | `dbe42a11404b` | 7 | 2680 |
| `data/statistical_reporting_audit.csv` | `0bedcd3ab24b` | 8 | 4201 |
| `data/provider_readiness_audit.csv` | `c9ff1910a432` | 11 | 4912 |
| `data/hosted_qa_readiness_audit.csv` | `aeba27f89c26` | 11 | 3290 |
| `data/threats_to_validity.csv` | `c79df0f5d094` | 12 | 5896 |
| `data/transcript_review_queue.csv` | `ae3cbf568c1e` | 3 | 1347 |
| `data/failure_label_review_template.csv` | `737dcc43903c` | 3 | 373 |
| `data/validation_commands.csv` | `747620524702` | 66 | 12164 |
| `data/difficulty_audit.csv` | `46f1487950e4` | 26 | 13428 |
| `data/task_quality_matrix.csv` | `65b778c0ae0c` | 26 | 16869 |
| `data/diagnostic_coverage_audit.csv` | `56194ecdf676` | 15 | 6702 |
| `data/human_time_observations.csv` | `b742021c8ae3` | 0 | 79 |
| `data/human_time_observations_schema.json` | `5e06e5804dbc` |  | 740 |
| `data/human_time_calibration_audit.csv` | `d4174f9ef97b` | 26 | 7512 |
| `data/human_timing_collection_plan.csv` | `b0f91d18ccbd` | 6 | 4409 |
| `data/human_time_observations_template.csv` | `b2af36e038f6` | 6 | 277 |
| `data/task_asset_manifest.csv` | `11a7904fb684` | 171 | 37297 |
| `data/prompt_contract_audit.csv` | `8ac0cc6ea492` | 14 | 3106 |
| `data/pin_coverage_audit.csv` | `8ab31ee39037` | 26 | 9391 |
| `data/run_integrity_audit.csv` | `905d30f62a8c` | 69 | 14540 |
| `data/grader_hardening_audit.csv` | `b66f1f8fc357` | 9 | 3187 |
| `data/claim_evidence_audit.csv` | `feeed7243ef2` | 9 | 16811 |
| `data/claim_authorization_matrix.csv` | `c75656b19f67` | 12 | 13255 |
| `data/research_claim_gap_matrix.csv` | `b105240323a1` | 12 | 14614 |
| `data/report_claim_conformance_audit.csv` | `fd4a05264161` | 10 | 3180 |
| `data/report_shape_audit.csv` | `c65a23e0d5e3` | 7 | 3008 |
| `data/release_decision_log.csv` | `aec743f974c5` | 8 | 9174 |
| `data/freeze_readiness_roadmap.csv` | `63655e5719ba` | 10 | 10068 |
| `data/scaffold_support_audit.csv` | `5c97c5fb587a` | 11 | 3994 |
| `data/requirement_coverage.csv` | `5021cb024c27` | 55 | 20473 |
| `reports/difficulty_audit.md` | `4864ad083e8a` |  | 6942 |
| `reports/task_quality_matrix.md` | `652739777820` |  | 4990 |
| `reports/diagnostic_coverage_audit.md` | `e9f7fe4e65a1` |  | 7206 |
| `reports/human_time_calibration_audit.md` | `0297a19d85fd` |  | 1578 |
| `reports/human_timing_collection_packet.md` | `c70a24e043b6` |  | 4578 |
| `reports/task_asset_manifest.md` | `95480e1da7cf` |  | 1377 |
| `reports/prompt_contract_audit.md` | `9d7e7dd7a857` |  | 2659 |
| `reports/pin_coverage_audit.md` | `64fea7fef8db` |  | 4145 |
| `reports/run_integrity_audit.md` | `75abcf6d7652` |  | 2213 |
| `reports/grader_hardening_audit.md` | `b543474dd490` |  | 4073 |
| `reports/claim_evidence_audit.md` | `4043ee7755ff` |  | 5639 |
| `reports/claim_authorization_matrix.md` | `3b5b24f76913` |  | 7637 |
| `reports/research_claim_gap_matrix.md` | `91f64432525a` |  | 10748 |
| `reports/report_claim_conformance_audit.md` | `954b1589f01b` |  | 3507 |
| `reports/report_shape_audit.md` | `048b35fa6718` |  | 3267 |
| `reports/concise_metr_report.md` | `a6a7db8ab54b` |  | 14037 |
| `reports/release_decision_log.md` | `a201f3efc4e5` |  | 9787 |
| `reports/freeze_readiness_roadmap.md` | `22579b7ee040` |  | 5793 |
| `reports/scaffold_support_audit.md` | `a4e45ef0d556` |  | 4916 |
| `reports/accepted_task_review.md` | `7ea531dc5f6e` |  | 13332 |
| `reports/evaluation_protocol.md` | `76d8ab27330f` |  | 6771 |
| `reports/model_sweep_execution_packet.md` | `fe29ac8c159e` |  | 7263 |
| `reports/model_run_analysis.md` | `7ea88a7de75f` |  | 1965 |
| `reports/model_evidence_provenance_audit.md` | `60134ce02013` |  | 3093 |
| `reports/statistical_reporting_audit.md` | `76bc109a408c` |  | 3415 |
| `reports/provider_readiness_audit.md` | `20047ec923ac` |  | 5876 |
| `reports/hosted_qa_readiness_audit.md` | `7c9d07aad947` |  | 3483 |
| `reports/threats_to_validity.md` | `edb07ecaac97` |  | 6070 |
| `reports/transcript_review_packet.md` | `bbe5c9b1901c` |  | 3334 |
| `reports/requirement_coverage.md` | `50a0489ed2df` |  | 18818 |
| `reports/figures/task_counts_by_family.svg` | `5833212738d0` |  | 2523 |
| `reports/figures/task_counts_by_bucket.svg` | `2ce3c13b007f` |  | 1479 |
| `reports/figures/top_skills.svg` | `27fb2a82febe` |  | 3806 |
| `reports/figures/run_rows_by_model.svg` | `50b22c3771fd` |  | 13402 |
| `reports/figures/task_minutes_by_bucket.svg` | `afef6d3c788f` |  | 3192 |
| `scripts/validate_all.py` | `1a9f7f73a567` |  | 6446 |
| `scripts/validate_task.py` | `99451d91d763` |  | 9611 |
| `scripts/audit_difficulty.py` | `0bebfeb74ec4` |  | 10134 |
| `scripts/generate_task_quality_matrix.py` | `129d2715090b` |  | 13165 |
| `scripts/audit_diagnostic_coverage.py` | `d3f26a1fb7f7` |  | 13537 |
| `scripts/audit_human_time_calibration.py` | `9aa994547bbe` |  | 9107 |
| `scripts/generate_human_timing_packet.py` | `1927518b9beb` |  | 9316 |
| `scripts/generate_task_asset_manifest.py` | `39b723c68b45` |  | 8843 |
| `scripts/audit_prompt_contracts.py` | `327ee834ce2d` |  | 9251 |
| `scripts/audit_pin_coverage.py` | `aaa6a5abbf28` |  | 15593 |
| `scripts/audit_run_integrity.py` | `0d57a7faa416` |  | 13598 |
| `scripts/audit_grader_hardening.py` | `7bcba063dd41` |  | 14898 |
| `scripts/audit_claim_evidence.py` | `680596afa1d5` |  | 16925 |
| `scripts/generate_claim_authorization_matrix.py` | `e5c3a17407ba` |  | 20250 |
| `scripts/generate_research_claim_gap_matrix.py` | `0e46d4962ec2` |  | 16408 |
| `scripts/audit_report_claim_conformance.py` | `5471202f2940` |  | 15958 |
| `scripts/generate_concise_report.py` | `95aeaa6afeaa` |  | 14353 |
| `scripts/audit_report_shape.py` | `51e9f56d0835` |  | 10558 |
| `scripts/generate_release_decision_log.py` | `b12b4ce2f80e` |  | 15421 |
| `scripts/generate_freeze_readiness_roadmap.py` | `c53382c2ae66` |  | 18317 |
| `scripts/audit_scaffold_support.py` | `4e8cab1a8f2b` |  | 15866 |
| `scripts/audit_requirement_coverage.py` | `1ac82ea59841` |  | 92048 |
| `scripts/generate_evaluation_protocol.py` | `335e77481a6e` |  | 9710 |
| `scripts/generate_model_sweep_packet.py` | `757fb25bce01` |  | 14079 |
| `scripts/analyze_model_results.py` | `eb7385902402` |  | 11969 |
| `scripts/audit_model_evidence_provenance.py` | `942724b593f4` |  | 13964 |
| `scripts/audit_statistical_reporting.py` | `f9616d16268c` |  | 12921 |
| `scripts/audit_provider_readiness.py` | `ad8b36f25ea7` |  | 18802 |
| `scripts/audit_hosted_qa_readiness.py` | `b9a4b5dc34d4` |  | 13338 |
| `scripts/generate_threats_to_validity.py` | `9b093b4ef49c` |  | 18058 |
| `scripts/generate_transcript_review_packet.py` | `2ca67bab325b` |  | 9458 |
| `scripts/record_local_qa_results.py` | `e65fa7831bc3` |  | 5303 |
| `scripts/generate_report.py` | `772a42bf3c4a` |  | 96722 |
| `scripts/export_public_tasks.py` | `ad45c6bdcdf2` |  | 2471 |
| `scripts/validate_public_export.py` | `586940302ff3` |  | 3575 |
| `scripts/run_model_sweep.py` | `d5f981674ad3` |  | 10138 |
| `scripts/lean_lookup.py` | `5941c1285ef9` |  | 2425 |
| `scripts/write_validation_manifest.py` | `1b627e428368` |  | 14447 |


## Threats To Validity

The generated register in `reports/threats_to_validity.md` is the authoritative limitations table for this report. It currently keeps the strongest benchmark claims blocked where evidence is missing, including task-count scale, T3/T4 time-horizon depth, independent human timing, scaffold-sweep coverage, frontier/open-model coverage, statistical power, and hosted QA.

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
