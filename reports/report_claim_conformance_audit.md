# Report Claim Conformance Audit

This generated audit checks whether the main report and README obey the claim-authorization matrix. It is intentionally textual and conservative: it catches unsupported claim wording, missing front-matter caveats, and report-shape drift.

## Summary

- checks: `11`
- statuses: `{"pass": 11}`
- scopes: `{"claim_authorization": 1, "claim_gap_matrix": 1, "concise_report": 1, "main_report": 6, "readme": 1, "reports_and_readme": 1}`

## Check Table

| check | scope | status | evidence | failure examples | required action |
| --- | --- | --- | --- | --- | --- |
| `authorization_matrix_loaded` | claim_authorization | pass | authorization rows=12; statuses={"allowed": 1, "allowed_with_caveat": 6, "blocked": 5}; blocked=5; caveated=6; non_allowed=11 | `[]` | Regenerate scripts/generate_claim_authorization_matrix.py and inspect blocked/caveated coverage. |
| `main_report_authorization_section` | main_report | pass | section_present=True; claim_ids_in_matrix=12; missing_claim_ids=[] | `[]` | Regenerate reports/metr_style_report.md after claim authorization and ensure every authorization row is visible. |
| `abstract_scope_boundaries` | main_report | pass | front-matter scope phrases checked before the first task table | `[]` | Keep locked-benchmark, sample-size, human-time, and provider-smoke limitations in the report abstract/front matter. |
| `run_result_boundary_wording` | main_report | pass | committed-run section checked for local-QA and smoke-row boundaries | `[]` | Keep local QA and tiny provider smoke rows explicitly separated from benchmark performance claims. |
| `claim_ledger_blocks_overclaims` | main_report | pass | claim ledger checked for explicit not-supported locked-benchmark and frontier-performance rows | `[]` | Keep tempting overclaims in the claim ledger as unsupported, not as conclusions. |
| `concise_report_scope_and_length` | concise_report | pass | concise report exists=True; line_count=219; missing_scope_phrases=[] | `[]` | Regenerate scripts/generate_concise_report.py and keep the reviewer-facing report concise and claim-bounded. |
| `locked_benchmark_blocker_consistency` | claim_gap_matrix | pass | locked_blockers=["frontier_model_evidence", "hosted_qa_env_linter", "independent_human_time_review", "independent_task_quality_review", "portfolio_accepted_count", "scaffold_result_comparison", "time_horizon_spread"]; gap_row_count=1; gap_blockers=["portfolio_accepted_count", "time_horizon_spread", "scaffold_result_comparison", "frontier_model_evidence", "independent_human_time_review", "independent_task_quality_review", "hosted_qa_env_linter"]; gap_missing=[]; concise_missing=[] | `[]` | Regenerate the research claim gap matrix and concise report whenever locked-benchmark requirement coverage changes. |
| `blocked_phrase_context_scan` | reports_and_readme | pass | blocked-claim phrase contexts scanned across reports\metr_style_report.md, reports\concise_metr_report.md, reports\evidence_appendix.md, reports\report_source_traceability.md, and README.md; unsafe_contexts=0 | `[]` | Rewrite any blocked-claim phrase so the local context clearly says it is unsupported, blocked, missing, or future work. |
| `readme_scope_boundaries` | readme | pass | README checked for locked-benchmark, model-result, and credential-scope boundaries | `[]` | Keep the README top-level scope aligned with the report's claim authorization matrix. |
| `limitations_cover_blockers` | main_report | pass | limitations section checked against blocked authorization themes | `[]` | Keep task-count, T4, independent-timing, provider-smoke, hosted-QA, and locked-benchmark caveats in the limitations section. |
| `report_length_and_appendix_boundary` | main_report | pass | main report line_count=589; markdown_table_rows=209; evidence_appendix_exists=True; evidence_appendix_line_count=1718 | `[]` | Keep the main report skimmable and keep row-level generated tables in reports/evidence_appendix.md. |

## Interpretation

`fail` rows mean the report or README may be overclaiming or missing a required caveat. `caution` rows do not block local report use, but they mark places where the report is less skimmable or less mature than the playbook's final-report target.
