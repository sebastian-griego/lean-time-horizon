# Threats To Validity Register

This generated register turns the report limitations into reviewable evidence rows. `block` and `caution` statuses are research limitations, not script failures; they identify claims that must remain scoped until stronger evidence is committed.

## Summary

- threats: `12`
- statuses: `{"block": 7, "caution": 3, "controlled": 2}`
- categories: `{"construct_validity": 2, "external_validity": 2, "internal_validity": 3, "operational_security": 2, "operational_validity": 1, "statistical_validity": 2}`
- severities: `{"high": 8, "medium": 4}`

## Register

| threat | category | severity | status | evidence | mitigation in repo | stronger evidence needed | claims limited |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `construct_time_horizon_depth` | construct_validity | high | block | accepted=6; accepted buckets={"T2": 5, "T3": 1}; diagnostic blocks=1; diagnostic cautions=3 | The report and freeze roadmap explicitly block strong time-horizon claims. | Add independently reviewed and timed T3/T4 tasks, including at least one T4 stretch row. | time_horizon_measurement;locked_benchmark |
| `portfolio_scale_and_balance` | external_validity | high | block | accepted=6; calibration_only=8; rejected=12; accepted families={"algorithm_correctness": 1, "direct_theorem_proving": 1, "informal_spec_to_formal": 1, "invariant_verification_ml_optimization": 1, "proof_repair_codebase": 1, "small_formal_library_construction": 1} | Accepted, calibration, and rejected rows are separated so small-core claims are visible. | Reach the 20-50 accepted-task target while preserving family and capability diversity. | frontier_performance;locked_benchmark;family_level_performance |
| `author_estimated_human_time` | internal_validity | high | block | accepted timed solves=0/6; human_time_observation_rows=0 | Human-time calibration audit and timing collection packet make missing observations explicit. | Collect independent Lean-human timed solves or second-review timing notes for every accepted task. | time_horizon_measurement;locked_benchmark |
| `automation_dominated_retained_tasks` | construct_validity | medium | caution | automation-dominated accepted tasks=2: ["lt-201", "lt-206"] | Automation-dominated accepted rows are marked with caveats and excluded from claims of standalone proof-depth difficulty. | Replace or independently validate retained caveat rows before locked benchmark status. | accepted_core_reviewed;time_horizon_measurement |
| `semantic_pin_finiteness` | internal_validity | medium | caution | accepted tasks with hidden-pin wrong failures=4/6; proof-only fixed-statement rows=2 | Pin coverage audit distinguishes semantic hidden-pin failures from public-stage and fixed-statement proof checks. | Have an independent reviewer inspect hidden pins and add richer same-signature hidden wrongs for future mutable tasks. | hidden_pin_strength;grading_validity |
| `scaffold_sweep_undercoverage` | statistical_validity | high | block | planned accepted-core cells=18; covered non-infra cells=1 | Evaluation protocol and model-sweep execution packet define the missing sweep before broad model runs. | Run accepted_v0 x one-shot/lookup/lookup_unlimited rows with fixed k and committed transcripts. | scaffold_effects;frontier_performance |
| `frontier_performance_undercoverage` | external_validity | high | block | accepted-core non-infra provider rows=1; accepted tasks=6 | Committed smoke rows are separated from local QA and kept out of population-level performance claims. | Run documented frontier/open-model sweeps across the accepted scaffold plan with model versions and transcripts. | frontier_performance;locked_benchmark |
| `statistical_power_and_plots` | statistical_validity | high | block | statistical audit rows=9; blocked outputs=5 | Statistical reporting audit blocks unsupported pass-rate plots and requires raw n plus Wilson intervals. | Populate the planned sweep and accepted task count before generating scaffold, family, and bucket performance plots. | scaffold_effects;frontier_performance;family_level_performance |
| `failure_taxonomy_forecast` | internal_validity | medium | caution | accepted-core non-infra provider rows=1; transcript review queue rows=3; single-review rows=3; review-audit failures=0; high/critical queue rows=1 | Failure labels, transcript workflow, a blank review template, and single-review smoke adjudications exist, but distributions are not interpreted until broad provider rows are independently reviewed. | Label real model transcripts after the scaffold sweep, use independent adjudication for disagreements, and compare observed failures to intended diagnostic modes. | diagnostic_failure_distribution;scaffold_effects |
| `hosted_environment_gap` | operational_validity | high | block | hosted readiness rows=11; blocked hosted-QA steps=9 | Hosted QA readiness audit separates local readiness from missing Taiga packaging and Env Linter evidence. | Create hosted packaging, run Full Env QA/Env Linter on exact problem versions, and commit findings/dispositions. | locked_benchmark;deployment_reliability |
| `secret_and_runner_boundary` | operational_security | medium | controlled | provider readiness failures=0; model-sweep command key-assignment leaks=0 | Provider commands require external runner env vars and keep provider keys out of committed commands. | Repeat secret scans before every commit that touches runner or transcript files. | artifact_security;provider_run_reproducibility |
| `public_export_hidden_leakage` | operational_security | high | controlled | public_tasks exists=True; hidden/wrong paths in export=0 | Public-export validation checks that hidden references and wrong submissions are absent. | Validate the public export after every task-asset or export-script change. | public_release_safety;locked_benchmark |

## Interpretation

`controlled` means the threat is currently mitigated for local v0.1 claims. `caution` means the report may discuss the artifact but must keep the limitation visible. `block` means the stronger claims in `claims_limited` should not be made from the current evidence.
