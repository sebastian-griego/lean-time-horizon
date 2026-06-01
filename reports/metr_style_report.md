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


## Model Result Analysis

`reports/model_run_analysis.md` and `data/model_result_summary.csv` analyze committed provider rows against the planned primary sweep.

- planned accepted-core task/scaffold cells: `18`
- planned cells with any committed accepted-core provider row: `1`
- planned cells with a non-infra accepted-core provider row: `1`
- accepted-core provider rows: `2` total, `1` non-infra
- accepted-core successes among non-infra provider rows: `0`
- all committed provider smoke rows: `3` total, `2` non-infra

The committed provider rows are smoke evidence only; the planned primary sweep remains mostly uncovered.


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
- support statuses: `{"partial": 2, "supported": 4, "unsupported": 3}`
- claim types: `{"artifact_validity": 1, "benchmark_status": 1, "construct_validity": 1, "data_validity": 1, "grading_validity": 1, "performance_claim": 2, "report_validity": 1, "task_validity": 1}`

Claim support table:

| claim | type | support | strength | claim text | limit | stronger claim requires |
| --- | --- | --- | --- | --- | --- | --- |
| `local_release_artifact` | artifact_validity | supported | high | The repository is a locally validated v0.1 release artifact with public scaffolds, hidden checks, Lean scoring, integrity controls, and complete metadata. | This is a local artifact claim, not a hosted/frozen benchmark claim. | Hosted QA, independent review, and broader accepted task count are still required for a locked benchmark. |
| `research_report_evidence` | report_validity | supported | high | The report is generated from committed data and includes research-quality caveats, task quality matrices, task-asset hashes, pin coverage, run integrity, scaffold-support checks, release-decision gates, and a prospective evaluation protocol. | The report is still limited by missing broad model sweeps and independent human timing. | Run the planned scaffold sweep, collect independent timing, and add external QA artifacts. |
| `accepted_core_reviewed` | task_validity | supported | medium | The six accepted-core tasks are internally reviewed and higher quality than the original candidate pool. | This is an internal-review claim. Several accepted rows retain caveats and the core size is below the target benchmark size. | Independent Lean-human review and more accepted high-quality T2/T3/T4 rows. |
| `hidden_pin_strength` | grading_validity | partial | medium | Hidden semantic checks provide meaningful anti-gaming evidence for accepted tasks. | Some accepted fixed-statement/proof-repair rows have wrong submissions that fail before hidden pins run; hidden pins are finite probes. | Add stronger same-signature semantic wrongs where possible and expand negative hidden examples for retained caveat rows. |
| `run_data_integrity` | data_validity | supported | high | Committed run-result rows are internally consistent with transcripts, failure labels, score vectors, and pass@k semantics. | This validates data hygiene only; it does not make the smoke rows representative. | Maintain this audit for future provider sweeps and require zero failing rows before reporting results. |
| `time_horizon_measurement` | construct_validity | partial | low | The current artifact measures model behavior across increasing time horizons. | Accepted core has only T2/T3 coverage and no T4; human times are author/reviewer estimates rather than independent solves. | Add independently timed T3/T4 tasks before claiming strong time-horizon measurement. |
| `scaffold_effects` | performance_claim | unsupported | none | The report supports conclusions about how lookup and iterative compile/debug scaffolds change model performance. | The scaffold ladder is implemented and planned, but real accepted-core provider data cover only one one-shot cell. | Run accepted-core pass@10 or equivalent rows across one-shot, lookup, and lookup_unlimited. |
| `frontier_performance` | performance_claim | unsupported | none | Committed provider rows characterize frontier-model performance on this benchmark. | Only tiny smoke evidence is committed, including an infra failure; local QA rows are not model performance. | Run the planned accepted-core scaffold sweep with documented provider versions and cost/infra notes. |
| `locked_benchmark` | benchmark_status | unsupported | none | v0.1 is a locked benchmark suitable for population-level frontier-model claims. | The artifact has 6 accepted tasks, no hosted QA, no independent timing, no T4 accepted task, and limited provider data. | Reach the 20-50 accepted-task target, run hosted QA, collect independent timing, complete scaffold sweeps, and freeze exact public task versions. |


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

`reports/pin_coverage_audit.md` and `data/pin_coverage_audit.csv` make hidden-check evidence inspectable by separating public-stage wrong failures from wrong submissions that actually reach `PinCheck.lean`.

- pin coverage grades: `{"pins_not_exercised_by_wrongs": 5, "semantic_examples_exercised": 3, "semantic_pins_exercised": 3, "signature_plus_hidden_failure": 15}`
- accepted-core tasks with at least one hidden-pin wrong failure: `4/6`
- accepted-core wrong failures at public stage: `6`
- accepted-core wrong failures at hidden-pin stage: `5`

Accepted-core hidden-pin coverage:

| task | grade | shape checks | positive examples | negative examples | public-stage wrongs | hidden-pin wrongs | note |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `lt-201` | pins_not_exercised_by_wrongs | 4 | 6 | 0 | 2 | 0 | Accepted row needs a caveat: current wrong submissions fail before hidden pins run. |
| `lt-203` | semantic_pins_exercised | 4 | 3 | 2 | 0 | 2 | Accepted row has at least one wrong submission reaching hidden pins and nontrivial examples. |
| `lt-202` | pins_not_exercised_by_wrongs | 5 | 2 | 0 | 2 | 0 | Accepted row needs a caveat: current wrong submissions fail before hidden pins run. |
| `lt-204` | signature_plus_hidden_failure | 6 | 6 | 0 | 1 | 1 | Accepted row lacks negative hidden examples; review semantic pin strength before freeze. |
| `lt-205` | semantic_pins_exercised | 8 | 4 | 1 | 1 | 1 | Accepted row has at least one wrong submission reaching hidden pins and nontrivial examples. |
| `lt-206` | semantic_pins_exercised | 5 | 4 | 2 | 0 | 1 | Accepted row has at least one wrong submission reaching hidden pins and nontrivial examples. |


## Requirement Coverage Audit

`reports/requirement_coverage.md` and `data/requirement_coverage.csv` map the repository to the committed checklist in `data/benchmark_requirements.csv`. This is a stricter evidence index than the narrative claim ledger.

Status counts:

- `supported`: 30
- `partial`: 4
- `not_met`: 2

Freeze relevance counts:

- `required_for_locked_benchmark`: supported 2, partial 4, not_met 2
- `required_for_release_artifact`: supported 15
- `required_for_research_report`: supported 13

Partial or unmet requirements:

| id | area | freeze relevance | status | evidence | next step |
| --- | --- | --- | --- | --- | --- |
| `portfolio_accepted_count` | portfolio | required_for_locked_benchmark | not_met | 6 accepted_v0 tasks; 8 calibration-only tasks; 12 rejected archive tasks. | Add and hard-review more high-quality T2/T3/T4 tasks before claiming a full benchmark. |
| `time_horizon_spread` | portfolio | required_for_locked_benchmark | partial | Accepted bucket counts: {"T2": 5, "T3": 1}; release bucket counts: {"T1": 8, "T2": 5, "T3": 1}. | Add more accepted T3/T4 tasks, including a T4 stretch row, and independently review human times. |
| `scaffold_result_comparison` | scaffolds | required_for_locked_benchmark | partial | Non-infra model rows: 2; scaffolds observed: ["one-shot"]; planned rows: 18. | Run real pass@10 or comparable sweeps across one-shot, lookup, and lookup_unlimited before performance claims. |
| `frontier_model_evidence` | runs | required_for_locked_benchmark | partial | Non-infra model rows: 2 over 6 accepted tasks; total model rows including infra failures: 3. | Run broader provider sweeps only after local and hosted QA are stable. |
| `independent_human_time_review` | calibration | required_for_locked_benchmark | partial | Accepted tasks with manual_review_complete: 6/6; no independent timed solves detected in metadata. | Collect independent Lean-human timed solves or second-reviewer timing notes before freeze. |
| `hosted_qa_env_linter` | qa | required_for_locked_benchmark | not_met | Hosted QA artifacts present: 0/2. | Run hosted Full Env QA and record findings/rebuttals before claiming a locked benchmark. |


## Reproducibility Checklist

The intended local regeneration gate is:

```powershell
lake build
python scripts/validate_all.py
python scripts/audit_difficulty.py
python scripts/generate_task_quality_matrix.py
python scripts/record_local_qa_results.py
python scripts/audit_pin_coverage.py
python scripts/audit_run_integrity.py
python scripts/generate_evaluation_protocol.py
python scripts/analyze_model_results.py
python scripts/generate_report.py
python scripts/export_public_tasks.py --out public_tasks
python scripts/validate_public_export.py --out public_tasks
python scripts/generate_task_asset_manifest.py --public-export public_tasks
python scripts/audit_scaffold_support.py
python scripts/audit_requirement_coverage.py --public-export public_tasks
python scripts/audit_claim_evidence.py
python scripts/generate_release_decision_log.py
python scripts/audit_scaffold_support.py
python scripts/audit_requirement_coverage.py --public-export public_tasks
python scripts/audit_claim_evidence.py
python scripts/generate_release_decision_log.py
python scripts/audit_scaffold_support.py
python scripts/audit_requirement_coverage.py --public-export public_tasks
python scripts/audit_claim_evidence.py
python scripts/generate_release_decision_log.py
python scripts/write_validation_manifest.py --public-export public_tasks
python scripts/generate_report.py
```

The public export validator checks that hidden references and wrong submissions are absent from `public_tasks`, all metadata-listed public files are present, exported Lean files compile, and obvious hidden-reference path strings do not leak.

## Validation Manifest

`reports/validation_manifest.json` records the local toolchain, task/run counts, public-export summary, expected regeneration commands, and artifact hashes. The main report itself is intentionally omitted from the hash list to avoid a self-referential report hash.

Generated at UTC: `2026-06-01T02:58:30.075470+00:00`

Git branch/head at generation: `main` / `2c92e720625c`. Worktree status at generation: `16 pre-commit path(s) recorded`. The exact status lines are kept in the JSON manifest because this file is generated before the final commit.

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
5. `python scripts/record_local_qa_results.py`
6. `python scripts/audit_pin_coverage.py`
7. `python scripts/audit_run_integrity.py`
8. `python scripts/generate_evaluation_protocol.py`
9. `python scripts/analyze_model_results.py`
10. `python scripts/generate_report.py`
11. `python scripts/export_public_tasks.py --out public_tasks`
12. `python scripts/validate_public_export.py --out public_tasks`
13. `python scripts/generate_task_asset_manifest.py --public-export public_tasks`
14. `python scripts/audit_scaffold_support.py`
15. `python scripts/audit_requirement_coverage.py --public-export public_tasks`
16. `python scripts/audit_claim_evidence.py`
17. `python scripts/generate_release_decision_log.py`
18. `python scripts/audit_scaffold_support.py`
19. `python scripts/audit_requirement_coverage.py --public-export public_tasks`
20. `python scripts/audit_claim_evidence.py`
21. `python scripts/generate_release_decision_log.py`
22. `python scripts/audit_scaffold_support.py`
23. `python scripts/audit_requirement_coverage.py --public-export public_tasks`
24. `python scripts/audit_claim_evidence.py`
25. `python scripts/generate_release_decision_log.py`
26. `python scripts/write_validation_manifest.py --public-export public_tasks`
27. `python scripts/generate_report.py`

Key artifact hashes:

| artifact | sha256 prefix | rows | bytes |
| --- | --- | ---: | ---: |
| `lean-toolchain` | `db7bb24b756d` |  | 25 |
| `lakefile.lean` | `1d842f6b4179` |  | 284 |
| `lake-manifest.json` | `601ea0517a05` |  | 3110 |
| `README.md` | `f613e296e311` |  | 8431 |
| `docs/axiom_policy.md` | `0adf66f9085a` |  | 712 |
| `data/benchmark_requirements.csv` | `27f828fcaeeb` | 36 | 7298 |
| `data/task_metadata.csv` | `2916f8cc78cc` | 26 | 19482 |
| `data/task_metadata_schema.json` | `a662bc8fb8e8` |  | 2317 |
| `data/run_results.csv` | `196d9de4ada4` | 69 | 15691 |
| `data/run_results_schema.json` | `5b41a198997f` |  | 1799 |
| `data/failure_label_schema.json` | `ae06ab834c14` |  | 481 |
| `data/scaffold_variants.csv` | `6ddd3f4fb586` | 3 | 379 |
| `data/model_sweep_plan.csv` | `c162dd19fb35` | 18 | 4099 |
| `data/model_result_summary.csv` | `2cfee9603a36` | 10 | 1682 |
| `data/validation_commands.csv` | `747620524702` | 66 | 12164 |
| `data/difficulty_audit.csv` | `123f2bed92f0` | 26 | 13428 |
| `data/task_quality_matrix.csv` | `5c6891423804` | 26 | 16869 |
| `data/task_asset_manifest.csv` | `59c9ec26ab2f` | 171 | 37297 |
| `data/pin_coverage_audit.csv` | `c9d78f916dae` | 26 | 6514 |
| `data/run_integrity_audit.csv` | `905d30f62a8c` | 69 | 14540 |
| `data/claim_evidence_audit.csv` | `4e52242a99c7` | 9 | 9946 |
| `data/release_decision_log.csv` | `ad5a661e7b47` | 8 | 4845 |
| `data/scaffold_support_audit.csv` | `5c97c5fb587a` | 11 | 3994 |
| `data/requirement_coverage.csv` | `364676cdf517` | 36 | 11563 |
| `reports/difficulty_audit.md` | `4864ad083e8a` |  | 6942 |
| `reports/task_quality_matrix.md` | `652739777820` |  | 4990 |
| `reports/task_asset_manifest.md` | `95480e1da7cf` |  | 1377 |
| `reports/pin_coverage_audit.md` | `26b6cb10ed91` |  | 2544 |
| `reports/run_integrity_audit.md` | `75abcf6d7652` |  | 2213 |
| `reports/claim_evidence_audit.md` | `a5eefdcb7e85` |  | 4640 |
| `reports/release_decision_log.md` | `b78b5e5bfcfb` |  | 5562 |
| `reports/scaffold_support_audit.md` | `a4e45ef0d556` |  | 4916 |
| `reports/accepted_task_review.md` | `7ea531dc5f6e` |  | 13332 |
| `reports/evaluation_protocol.md` | `76d8ab27330f` |  | 6771 |
| `reports/model_run_analysis.md` | `7ea88a7de75f` |  | 1965 |
| `reports/requirement_coverage.md` | `56f024ad73ab` |  | 11027 |
| `reports/figures/task_counts_by_family.svg` | `5833212738d0` |  | 2523 |
| `reports/figures/task_counts_by_bucket.svg` | `2ce3c13b007f` |  | 1479 |
| `reports/figures/top_skills.svg` | `27fb2a82febe` |  | 3806 |
| `reports/figures/run_rows_by_model.svg` | `50b22c3771fd` |  | 13402 |
| `reports/figures/task_minutes_by_bucket.svg` | `afef6d3c788f` |  | 3192 |
| `scripts/validate_all.py` | `1a9f7f73a567` |  | 6446 |
| `scripts/validate_task.py` | `99451d91d763` |  | 9611 |
| `scripts/audit_difficulty.py` | `0bebfeb74ec4` |  | 10134 |
| `scripts/generate_task_quality_matrix.py` | `129d2715090b` |  | 13165 |
| `scripts/generate_task_asset_manifest.py` | `39b723c68b45` |  | 8843 |
| `scripts/audit_pin_coverage.py` | `91d9de6011db` |  | 11828 |
| `scripts/audit_run_integrity.py` | `0d57a7faa416` |  | 13598 |
| `scripts/audit_claim_evidence.py` | `5185a706ec4f` |  | 13455 |
| `scripts/generate_release_decision_log.py` | `9129cbccde23` |  | 12027 |
| `scripts/audit_scaffold_support.py` | `4e8cab1a8f2b` |  | 15866 |
| `scripts/audit_requirement_coverage.py` | `89593e226a35` |  | 44304 |
| `scripts/generate_evaluation_protocol.py` | `335e77481a6e` |  | 9710 |
| `scripts/analyze_model_results.py` | `eb7385902402` |  | 11969 |
| `scripts/record_local_qa_results.py` | `e65fa7831bc3` |  | 5303 |
| `scripts/generate_report.py` | `8dd27830eca2` |  | 49581 |
| `scripts/export_public_tasks.py` | `ad45c6bdcdf2` |  | 2471 |
| `scripts/validate_public_export.py` | `586940302ff3` |  | 3575 |
| `scripts/run_model_sweep.py` | `d5f981674ad3` |  | 10138 |
| `scripts/lean_lookup.py` | `5941c1285ef9` |  | 2425 |
| `scripts/write_validation_manifest.py` | `d0aa7124e9b2` |  | 10170 |


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
