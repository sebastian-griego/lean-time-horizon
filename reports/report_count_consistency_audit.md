# Report Count Consistency Audit

This generated audit checks that repeated top-line counts in the concise report, main report, evidence appendix, and validation manifest agree with the committed CSV/JSON sources. It is a drift detector for reviewer-facing numbers, not a new source of benchmark evidence.

## Summary

- checks: `8`
- statuses: `{"pass": 8}`
- areas: `{"blocker_counts": 1, "gate_counts": 1, "manifest_counts": 2, "model_counts": 1, "portfolio_counts": 1, "report_counts": 2}`

## Check Table

| check | area | status | source value | report value | evidence | failure examples | required action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `task_status_counts` | portfolio_counts | pass | `{"acceptance_status_counts": {"accepted_v0": 6, "calibration_only": 8, "rejected_duplicate": 2, "rejected_too_easy": 10}, "accepted": 6, "calibration": 8, "pending": 0, "rejected": 12, "task_count": 26}` | `{"manifest_acceptance_status_counts": {"accepted_v0": 6, "calibration_only": 8, "rejected_duplicate": 2, "rejected_too_easy": 10}, "manifest_task_count": 26, "missing_report_needles": []}` | Task-status counts are checked against task metadata, the validation manifest, and the main/concise report top lines. | `[]` | Regenerate task metadata, validation manifest, concise report, and main report after any task-status change. |
| `requirement_status_counts` | report_counts | pass | `{"not_met": 3, "partial": 4, "supported": 63}` | `{"missing_report_needles": []}` | Requirement status counts are checked where the report summarizes supported/partial/not_met evidence. | `[]` | Regenerate requirement coverage and all report layers after requirement status changes. |
| `claim_authorization_counts` | report_counts | pass | `{"allowed": 1, "allowed_with_caveat": 6, "blocked": 5}` | `{"missing_report_needles": []}` | Claim-authorization status counts are checked against generated report summaries. | `[]` | Regenerate claim authorization, concise report, and main report after claim status changes. |
| `release_and_freeze_gate_counts` | gate_counts | pass | `{"freeze_readiness": {"block": 8, "caution": 1, "ready": 1}, "release_decision": {"block": 4, "caution": 2, "pass": 2}}` | `{"missing_report_needles": []}` | Release-decision and freeze-readiness status counts are checked wherever the report repeats them. | `[]` | Regenerate release/freeze reports and all report layers after gate-status changes. |
| `model_coverage_counts` | model_counts | pass | `{"accepted_provider_rows_noninfra": 1, "accepted_provider_rows_total": 2, "covered_primary_noninfra": 1, "planned_primary_cells": 18}` | `{"missing_report_needles": []}` | Model-sweep coverage counts are checked against the source summary and report wording that keeps performance claims blocked. | `[]` | Regenerate model-result analysis and reports after provider rows or sweep plans change. |
| `run_and_manifest_counts` | manifest_counts | pass | `{"local_qa_rows": 66, "model_rows": 3, "run_rows": 69}` | `{"manifest_run_summary": {"local_qa_row_count": 66, "local_qa_status_counts": {"expected_failure": 40, "passed": 26}, "model_failure_label_counts": {"infra_failure": 1, "none": 1, "proof_debugging": 1}, "model_sweep_row_count": 3, "row_count": 69}, "missing_report_needles": []}` | Run-result counts are checked against the validation manifest and the appendix manifest summary. | `[]` | Regenerate local QA rows, validation manifest, and report appendix after run-result changes. |
| `locked_benchmark_blocker_counts` | blocker_counts | pass | `{"locked_blocker_count": 7, "locked_blockers": ["frontier_model_evidence", "hosted_qa_env_linter", "independent_human_time_review", "independent_task_quality_review", "portfolio_accepted_count", "scaffold_result_comparison", "time_horizon_spread"]}` | `{"gap_blockers": ["portfolio_accepted_count", "time_horizon_spread", "scaffold_result_comparison", "frontier_model_evidence", "independent_human_time_review", "independent_task_quality_review", "hosted_qa_env_linter"], "missing_from_gap": [], "missing_report_needles": []}` | Locked-benchmark blocker identifiers are checked against requirement coverage, the claim-gap row, and report blocker tables. | `[]` | Regenerate requirement coverage, claim gap matrix, and reports when locked-benchmark blockers change. |
| `public_export_counts` | manifest_counts | pass | `{"exists": true, "hidden_or_wrong_path_count": 0, "task_count": 14}` | `{"manifest_public_export": {"configured": true, "exists": true, "hidden_or_wrong_path_count": 0, "path": "C:\\Users\\sebas\\lean-time-horizon\\public_tasks", "relative_path": "public_tasks", "task_count": 14}, "missing_report_needles": []}` | Public-export task and hidden/wrong-path counts are checked against the manifest and appendix summary. | `[]` | Regenerate public export, validation manifest, and report appendix after public task export changes. |

## Interpretation

`fail` rows mean a generated report or manifest has stale top-line counts relative to the source artifacts. Regenerate the upstream CSV/JSON source and report layer in the order listed by the validation manifest before using the report for review.
