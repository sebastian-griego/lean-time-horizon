# Requirement Coverage Audit

This generated audit maps the local repository state to playbook-level benchmark requirements. It is an evidence index, not a claim that the benchmark is frozen.

## Status Counts

- `supported`: 21
- `partial`: 4
- `not_met`: 2

## Coverage Table

| id | area | status | requirement | evidence | gap / next step |
| --- | --- | --- | --- | --- | --- |
| `portfolio_accepted_count` | portfolio | not_met | Final benchmark should contain 20-50 accepted tasks after QA and filtering. | 6 accepted_v0 tasks; 8 calibration-only tasks; 12 rejected archive tasks. | Add and hard-review more high-quality T2/T3/T4 tasks before claiming a full benchmark. |
| `dev_test_split` | portfolio | supported | Accepted tasks should preserve a dev/test split. | Accepted split counts: {"dev": 2, "test": 4}. | No gap. |
| `mixed_realistic_portfolio` | portfolio | supported | Task families should be mixed and not mostly direct theorem proving. | Accepted family counts: {"algorithm_correctness": 1, "direct_theorem_proving": 1, "informal_spec_to_formal": 1, "invariant_verification_ml_optimization": 1, "proof_repair_codebase": 1, "small_formal_library_construction": 1}. | No gap. |
| `time_horizon_spread` | portfolio | partial | Accepted tasks should span increasing human-time horizons, not only T0/T1/T2 calibration. | Accepted bucket counts: {"T2": 5, "T3": 1}; release bucket counts: {"T1": 8, "T2": 5, "T3": 1}. | Add more accepted T3/T4 tasks, including a T4 stretch row, and independently review human times. |
| `public_prompts_scaffolds` | assets | supported | Each release task should include public prompt and public Lean scaffold files. | Release assets: 14/14 prompts; 14/14 public-file sets. | No gap. |
| `hidden_references_pins` | grading | supported | Each release task should have hidden reference proof and hidden semantic PinCheck. | Release hidden assets: 14/14 references; 14/14 PinCheck files. | No gap. |
| `wrong_submission_controls` | grading | supported | Accepted tasks should include plausible wrong submissions that fail for meaningful reasons. | Accepted tasks with at least two wrong submissions: 6/6. | No gap. |
| `automatic_lean_scoring` | grading | supported | Scoring should use Lean wherever possible and provide validation commands. | validate_task.py exists: True; validation command rows: 66. | No gap. |
| `forbidden_construct_scan` | integrity | supported | Submissions should be scanned for forbidden constructs before Lean grading. | forbidden_constructs.py exists: True; validate_task calls scanner: True. | No gap. |
| `axiom_audit_policy` | integrity | supported | Axiom usage should be audited or governed by a documented policy. | docs/axiom_policy.md exists: True; validate_task uses #print axioms: True. | No gap. |
| `metadata_completeness` | data | supported | Task metadata should include family, domain, human-time, skills, scaffold sensitivity, and failure modes. | 26 task metadata rows checked; missing fields sample: []. | No gap. |
| `schemas_present` | data | supported | Task metadata, run results, and failure labels should have schemas. | Schema files present: run=True, failure=True, metadata=True. | No gap. |
| `run_result_semantics` | data | supported | run_results should represent successes_out_of_k and pass@k consistently. | 69 run-result rows checked; semantic errors sample: []. | No gap. |
| `scaffold_support` | scaffolds | supported | The repo should support one-shot, lookup, and lookup plus iterative compile/debug scaffold variants. | 3 scaffold variants configured; runner exposes lookup command: True; runner preserves requested k attempts: True. | No gap. |
| `evaluation_protocol_plan` | runs | supported | A prospective evaluation protocol should define the primary accepted-task scaffold sweep before broad model runs. | evaluation_protocol.md exists: True; model_sweep_plan rows: 18; planned scaffolds: ["lookup", "lookup_unlimited", "one-shot"]. | No gap. |
| `scaffold_result_comparison` | scaffolds | partial | The report should compare real model performance across scaffolds, ideally pass@10. | Non-infra model rows: 2; scaffolds observed: ["one-shot"]; planned rows: 18. | Run real pass@10 or comparable sweeps across one-shot, lookup, and lookup_unlimited before performance claims. |
| `transcript_failure_workflow` | runs | supported | Run rows should link transcripts and carry failure labels for review. | run_results rows: 69; local QA rows: 66; model rows: 3. | No gap for workflow; broader model sweeps are still needed. |
| `frontier_model_evidence` | runs | partial | Frontier/open-model runs should provide evidence beyond local QA. | Non-infra model rows: 2 over 6 accepted tasks; total model rows including infra failures: 3. | Run broader provider sweeps only after local and hosted QA are stable. |
| `public_export_no_hidden_leak` | integrity | supported | Public export should include public assets and exclude hidden references and wrong submissions. | Public export exists: True; exported tasks: 14; hidden/wrong paths: 0. | No gap. |
| `report_from_committed_data` | reporting | supported | The METR-style report and plots should regenerate from committed CSVs. | metr_style_report.md exists: True; generate_report reads CSV: True. | No gap. |
| `difficulty_audit_report` | reporting | supported | Difficulty audit should include proof length, tactic profile, automation dominance, hidden-pin strength, and model-solvability estimates. | difficulty_audit rows: 26; report exists: True. | No gap. |
| `manual_accepted_task_review` | reporting | supported | Accepted tasks should have hard reviewer-style notes and benchmark-grade caveats. | accepted_task_review.md exists: True. | No gap. |
| `independent_human_time_review` | calibration | partial | Human-time estimates should be separately reviewed or measured, not inferred from model pass rates. | Accepted tasks with manual_review_complete: 6/6; no independent timed solves detected in metadata. | Collect independent Lean-human timed solves or second-reviewer timing notes before freeze. |
| `hosted_qa_env_linter` | qa | not_met | Hosted Taiga/Env Linter QA should be run before delivery/freeze. | Hosted QA artifacts present: 0/2. | Run hosted Full Env QA and record findings/rebuttals before claiming a locked benchmark. |
| `reproducibility_manifest` | reproducibility | supported | A clean regeneration trail should record toolchain, commands, counts, and artifact hashes. | validation_manifest.json exists: True. | No gap. |
| `candidate_pruning_audit` | portfolio | supported | Candidate tasks should be separated from accepted tasks and pruned aggressively. | Rejected archive tasks: 12; calibration-only tasks: 8; accepted tasks: 6. | No gap. |
| `semantic_formalization_pins` | grading | supported | Formalization tasks should use semantic pins rather than brittle exact-text matching. | Accepted informal-spec rows in difficulty audit: 1; semantic pin rows: 1. | No gap. |
