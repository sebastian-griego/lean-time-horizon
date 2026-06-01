# Concise METR-Style Report

## Bottom Line

This repository is a locally validated v0.1 Lean time-horizon evaluation artifact, not a locked benchmark. It has enough local task, grading, reporting, and anti-overclaim evidence to support review, but not enough accepted-task scale, independent human timing, provider/scaffold coverage, or hosted QA to support population-level frontier-model claims.

- accepted core tasks: `6`
- calibration-only tasks: `8`
- rejected archive tasks: `12`
- requirement statuses: `{"not_met": 2, "partial": 4, "supported": 54}`
- claim authorizations: `{"allowed": 1, "allowed_with_caveat": 6, "blocked": 5}`
- release-decision gates: `{"block": 4, "caution": 3, "pass": 1}`
- freeze-readiness gates: `{"block": 8, "caution": 1, "ready": 1}`

## Research Questions

1. Can a model recover the intended Lean proof or formalization from the public prompt and scaffold?
2. Which failures are diagnostic of formalization, theorem decomposition, proof debugging, codebase navigation, invariant design, or library/API search?
3. How do lookup and iterative compile/debug scaffolds change outcomes once real sweeps are run?

The current artifact can evaluate local task/grader validity and prepare the scaffold sweep. It cannot yet answer the third question empirically because committed provider data cover only a tiny smoke sample.

## Task Set

Accepted core tasks are mixed across six families, with T2/T3 coverage but no accepted T4 task.

Accepted families:

- `algorithm_correctness`: 1
- `direct_theorem_proving`: 1
- `informal_spec_to_formal`: 1
- `invariant_verification_ml_optimization`: 1
- `proof_repair_codebase`: 1
- `small_formal_library_construction`: 1

Release time buckets:

- `T1`: 8
- `T2`: 5
- `T3`: 1

Accepted core rows:

| task | split | family | bucket | p50/p90 | review note |
| --- | --- | --- | --- | --- | --- |
| `lt-201` | dev | proof_repair_codebase | T2 | 75/150 | accepted_v0_keep_with_caveat: reference proof is automation-dominated, but the task is retained for multi-file navigation, fixed API semantics, and generalized batch repair; needs independent review before any locked benchmark claim. |
| `lt-203` | dev | informal_spec_to_formal | T2 | 90/180 | accepted_v0: spec-to-formal task with hidden pins rejecting vacuous, equality-only, and duplicate-sensitive interpretations. |
| `lt-202` | test | direct_theorem_proving | T2 | 90/180 | accepted_v0_keep_with_caveat: Mathlib-adjacent theorem package requiring image/preimage API lookup, premise selection, and witness decomposition; hidden checks mostly protect fixed theorem signatures rather than semantic formalization choices. |
| `lt-204` | test | invariant_verification_ml_optimization | T2 | 100/200 | accepted_v0: optimizer-style invariant package with helper lemmas for cap bounds, list preservation, and sum monotonicity. |
| `lt-205` | test | small_formal_library_construction | T3 | 150/300 | accepted_v0: T3 small library construction with dependent count lemmas and downstream BagEq reuse; expected to be hard one-shot. |
| `lt-206` | test | algorithm_correctness | T2 | 100/210 | accepted_v0_keep_with_caveat: reference proof uses substantial simp/omega automation, but the task is retained for the multi-lemma partition invariant, side predicates, and duplicate-sensitive count preservation; needs independent review before any locked benchmark claim. |

## Capabilities And Expected Failures

The accepted set is meant to test diagnostic capabilities, not just theorem-proving difficulty. Singleton capability rows are visible limitations rather than hidden assumptions.

| capability | status | accepted tasks | limit |
| --- | --- | --- | --- |
| `library_search` | caution | 1 | Capability is represented by a singleton accepted task, so task-specific quirks can dominate. |
| `theorem_decomposition` | pass | 6 | Capability is represented by more than one accepted task. |
| `semantic_formalization` | caution | 1 | Capability is represented by a singleton accepted task, so task-specific quirks can dominate. |
| `proof_debugging` | pass | 2 | Capability is represented by more than one accepted task. |
| `codebase_navigation` | caution | 1 | Capability is represented by a singleton accepted task, so task-specific quirks can dominate. |
| `invariant_design` | pass | 2 | Capability is represented by more than one accepted task. |
| `long_horizon_construction` | pass | 3 | Capability is represented by more than one accepted task. |

Construct-validity matrix:

- accepted task rows traced: `6`
- support levels: `{"task_level_internal_review": 2, "task_level_internal_review_singleton_capability": 1, "task_level_with_caveat": 3}`
- rows with singleton-covered capabilities: `3/6`
- this is task-level construct evidence, not capability-level performance evidence.

Most common accepted-task skills:

- `arithmetic normalization`: 1
- `codebase navigation`: 1
- `generalized induction`: 1
- `helper lemma decomposition`: 2
- `invariant design`: 2
- `list induction`: 2
- `proof repair`: 1
- `theorem decomposition`: 2

Expected failure modes are author/reviewer forecasts until broader model transcripts are independently labeled. Common expected modes include:

- `fails to generalize cache in induction`: 1
- `forgets surjectivity direction`: 1
- `keeps multiplicity accidentally`: 1
- `misses key history API change`: 1
- `proves only length preservation`: 2
- `repairs only entry count`: 1
- `uses equality instead of membership equivalence`: 1
- `vacuous relation`: 1

Committed single-review smoke adjudications: `3` rows; failure-label review-audit failures: `0`. These rows are transcript provenance evidence, not failure-distribution evidence.

## Grading And Integrity

The grader is Lean-first: submissions must pass forbidden-construct scanning, public compilation, hidden `PinCheck.lean`, and axiom auditing. Local QA rows validate reference solutions and wrong submissions; they are not model performance.

- run-integrity failures: `0`
- grader-hardening failures: `0`
- public export validator checks hidden/wrong files are absent from `public_tasks`.
- hidden pins are meaningful finite probes, not proof of full semantic equivalence.

## Model Evidence

Committed provider rows are smoke evidence only. They show the runner and transcript path can work, but they do not characterize frontier performance, scaffold effects, family-level performance, or failure distributions.

- planned accepted-core task/scaffold cells: `18`
- covered non-infra primary cells: `1`
- accepted-core provider rows: `2` total, `1` non-infra
- provider/model versions in committed smoke rows: `["anthropic:claude-sonnet-4-6"]`
- statistical claim-tier statuses: `{"blocked": 6, "supported": 1}`
- Wilson precision ledger rows for assumed p=0.5: `6`
- the statistical analysis plan treats current provider rows as smoke provenance only; performance estimates and scaffold effects stay blocked by threshold rows.

## Claim Boundaries

The report now has explicit claim authorization and a prose conformance audit. Blocked claims may appear only as limitations or future work.

- `reports/report_claim_conformance_audit.md` checks this narrative, the detailed report, and README for blocked-claim wording.
- `reports/report_shape_audit.md` checks whether this narrative answers the playbook report-shape questions or explicitly blocks unsupported analyses.
- `reports/research_claim_gap_matrix.md` records the evidence packages needed before stronger claims are allowed.
- `reports/statistical_analysis_plan.md` records minimum evidence thresholds, blocked overclaim wording, and Wilson precision limits before broader model sweeps.

| claim | authorization | allowed wording | required caveat |
| --- | --- | --- | --- |
| `local_artifact_validity` | allowed_with_caveat | The repo is a locally validated v0.1 research artifact with public tasks, hidden checks, Lean scoring, integrity scans, and metadata. | Say this is local validation only; hosted QA, independent timing, and full model sweeps are outside the current evidence. |
| `research_report_scope` | allowed_with_caveat | The report is a generated research review memo that makes task-quality, grading, reproducibility, and evidence-limit claims from committed artifacts. | Pair this with the limitations that broad provider sweeps, independent human timing, and hosted QA are missing. |
| `accepted_core_quality` | allowed_with_caveat | The six accepted-core tasks are internally reviewed and stronger than the original candidate pool. | Say the core is small, internally reviewed, and still has caveat rows; do not generalize from family-level singletons. |
| `hidden_pin_and_grader_strength` | allowed_with_caveat | Hidden checks provide meaningful anti-gaming probes for accepted tasks, especially mutable-definition semantic-pin tasks. | Note that proof-only fixed-statement rows mostly rely on Lean typechecking plus downstream signature guards, and all pins are finite probes. |
| `time_horizon_scope` | allowed_with_caveat | The artifact explores a limited T2/T3-only slice of time-horizon evaluation design. | State that accepted human times are author/reviewer estimates, there is no T4 row, and no independent timing observations are committed. |
| `scaffold_effects` | blocked | The scaffold ladder and execution plan are implemented; empirical scaffold-effect conclusions are not yet supported. | Only describe planned scaffold comparisons and the fact that current provider rows do not cover lookup or iterative debug cells. |
| `frontier_model_performance` | blocked | No frontier-performance conclusion is authorized from the committed provider smoke rows. | It is acceptable to state that provider adapters and smoke transcripts exist, but they are not benchmark results. |
| `failure_taxonomy_results` | allowed_with_caveat | The repo has a failure-label schema, transcript links, a transcript review queue, and a single-review audit for the committed smoke rows. | Current adjudication is single-review smoke evidence only: reviewed rows 3/3, raw queue rows still marked unreviewed in run_results 3, audit failures 0. |
| `statistical_performance_reporting` | blocked | Statistical reporting checks exist and currently block recommended performance plots. | Describe the statistical audit as a guardrail for future sweeps, not as performance evidence. |
| `hosted_qa_status` | blocked | Hosted/Taiga QA readiness has been audited, and the hosted QA evidence is currently absent. | State only that local validation is ready for a hosted QA loop; do not imply hosted checks have run. |
| `locked_benchmark_status` | blocked | v0.1 is not a locked benchmark; it is a local v0.1 research artifact with explicit blockers. | Every report summary should preserve this boundary until all locked-benchmark gates are satisfied. |

## Evidence Upgrade Path

Upgrade priorities: `{"high": 6, "highest": 1, "maintain": 1, "medium": 4}`. High-priority rows are not ready; they are a checklist for evidence that must exist before stronger wording is permitted.

| claim | priority | current status | blocking requirements |
| --- | --- | --- | --- |
| `accepted_core_quality` | high | allowed_with_caveat | portfolio_accepted_count;time_horizon_spread;independent_human_time_review |
| `time_horizon_scope` | high | allowed_with_caveat | time_horizon_spread;independent_human_time_review;portfolio_accepted_count |
| `scaffold_effects` | high | blocked | scaffold_result_comparison;frontier_model_evidence |
| `frontier_model_performance` | high | blocked | frontier_model_evidence;scaffold_result_comparison;hosted_qa_env_linter |
| `statistical_performance_reporting` | high | blocked | scaffold_result_comparison;frontier_model_evidence;portfolio_accepted_count |
| `hosted_qa_status` | high | blocked | hosted_qa_env_linter |
| `locked_benchmark_status` | highest | blocked | portfolio_accepted_count;time_horizon_spread;scaffold_result_comparison;frontier_model_evidence;independent_human_time_review;hosted_qa_env_linter |

## Remaining Blockers

| requirement | status | current evidence | next step |
| --- | --- | --- | --- |
| `portfolio_accepted_count` | not_met | 6 accepted_v0 tasks; 8 calibration-only tasks; 12 rejected archive tasks. | Add and hard-review more high-quality T2/T3/T4 tasks before claiming a full benchmark. |
| `time_horizon_spread` | partial | Accepted bucket counts: {"T2": 5, "T3": 1}; release bucket counts: {"T1": 8, "T2": 5, "T3": 1}. | Add more accepted T3/T4 tasks, including a T4 stretch row, and independently review human times. |
| `scaffold_result_comparison` | partial | Non-infra model rows: 2; scaffolds observed: ["one-shot"]; planned rows: 18. | Run real pass@10 or comparable sweeps across one-shot, lookup, and lookup_unlimited before performance claims. |
| `frontier_model_evidence` | partial | Non-infra model rows: 2 over 6 accepted tasks; total model rows including infra failures: 3. | Run broader provider sweeps only after local and hosted QA are stable. |
| `independent_human_time_review` | partial | Accepted tasks with manual_review_complete: 6/6; accepted tasks with successful independent timing observations: 0/6; observation rows: 0. | Collect independent Lean-human timed solves or second-reviewer timing notes before freeze. |
| `hosted_qa_env_linter` | not_met | Hosted QA artifacts present: 0/2; hosted readiness report exists: True; blocked hosted-readiness checks: 9. | Run hosted Full Env QA and record findings/rebuttals before claiming a locked benchmark. |

## Validity Notes

- accepted tasks without independent timing observations: `6/6`
- task-count target remains 20-50 accepted tasks; v0.1 has 6 accepted core tasks.
- accepted human-time coverage is T2/T3 only; there is no T4 accepted stretch task.
- capability-level claims remain weak where a capability is represented by a singleton accepted task.
- hosted Taiga/Env Linter QA artifacts are absent.
- the detailed evidence report remains appendix-heavy by design; this concise report is the reviewer-facing narrative.

## Next Work

1. Collect independent Lean-human timing observations for every accepted task.
2. Add a small number of hard-reviewed T3/T4 tasks only if they meet the existing diagnostic bar.
3. Run the accepted-core scaffold sweep across one-shot, lookup, and lookup_unlimited with documented provider versions.
4. Run hosted QA and commit Env Linter findings or rebuttals for exact public task versions.
5. Regenerate this report and keep blocked claims blocked until the corresponding evidence is committed.

## Evidence Appendix

Detailed evidence is in `reports/metr_style_report.md`, `reports/evidence_appendix.md`, `reports/report_source_traceability.md`, `reports/requirement_coverage.md`, `reports/claim_authorization_matrix.md`, `reports/research_claim_gap_matrix.md`, `reports/statistical_analysis_plan.md`, `reports/report_claim_conformance_audit.md`, `reports/report_shape_audit.md`, and the committed CSVs under `data/`.
