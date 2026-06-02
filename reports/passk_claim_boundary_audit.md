# Pass@k Claim-Boundary Audit

This generated audit checks that report artifacts keep strict pass@k-ready evidence separate from smoke-only or missing planned cells. It does not create model results or judge model quality; it prevents wording drift after provider smoke rows are committed.

## Summary

- checks: `7`
- statuses: `{"pass": 7}`
- areas: `{"claim_controls": 1, "legacy_phrase_scan": 1, "release_gates": 1, "report_text": 2, "source_data": 1, "statistical_reporting": 1}`

## Check Table

| check | area | status | evidence | bad matches | required action |
| --- | --- | --- | --- | --- | --- |
| `strict_coverage_ledger_counts` | source_data | pass | planned_cells=18; plan_rows=18; pass_at_k_ready=0; aggregate_noninfra_smoke=1; statuses={"missing": 17, "smoke_only": 1} | `[]` | Regenerate scripts/audit_model_sweep_coverage.py and inspect planned-cell coverage mismatches. |
| `main_report_passk_boundary` | report_text | pass | expected_ready=0/18; expected_smoke=1/18; missing_required=0; legacy_bad_matches=0 | `[]` | Regenerate reports and keep pass@k-ready and smoke-covered counts separate in the main report. |
| `concise_report_passk_boundary` | report_text | pass | expected_ready=0; expected_smoke=1; missing_required=0; legacy_bad_matches=0 | `[]` | Regenerate the concise report and keep smoke rows out of pass@k-ready wording. |
| `release_and_freeze_passk_boundary` | release_gates | pass | ready=0/18; statuses={"missing": 17, "smoke_only": 1}; missing_required=0; legacy_bad_matches=0 | `[]` | Regenerate release/freeze reports after model-sweep coverage changes. |
| `statistical_and_plot_passk_boundary` | statistical_reporting | pass | ready=0/18; aggregate_smoke=1; missing_required=0; legacy_bad_matches=0 | `[]` | Keep performance plots and statistical claims blocked until exact-k planned cells are covered. |
| `claim_and_requirement_passk_boundary` | claim_controls | pass | ready=0/18; statuses={"missing": 17, "smoke_only": 1}; missing_required=0; legacy_bad_matches=0 | `[]` | Keep claim and requirement reports tied to the strict coverage audit before upgrading scaffold or frontier claims. |
| `legacy_aggregate_phrase_scan` | legacy_phrase_scan | pass | files_scanned=10; forbidden_phrases=4; matches=0 | `[]` | Remove stale aggregate-coverage language that could make smoke rows look like pass@k evidence. |

## Interpretation

`pass` means the audited reports use the strict `data/model_sweep_coverage_audit.csv` categories consistently. A passing row is not performance evidence: `covered_pass` and `covered_fail` only indicate exact-k row-shape readiness, while `smoke_only`, `infra_only`, and `missing` remain excluded from pass@k estimates.
