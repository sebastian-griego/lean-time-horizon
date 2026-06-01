# Model Evidence Provenance Audit

This generated audit checks whether committed non-local run rows have enough provenance for a research report: model versions, k, transcripts, sample sizes, infra accounting, and a clear boundary between smoke rows and benchmark claims.

## Summary

- checks: `7`
- statuses: `{"pass": 7}`
- areas: `{"analysis_data": 1, "claim_boundary": 2, "report_text": 1, "run_data": 3}`

## Check Table

| check | area | status | evidence | limitation | required action |
| --- | --- | --- | --- | --- | --- |
| `provider_row_inventory` | run_data | pass | provider_rows=3; noninfra_provider_rows=2; accepted_provider_rows=2; accepted_noninfra_rows=1; calibration_provider_rows=1; local_qa_rows=66 | Provider rows are smoke evidence only and are underpowered for benchmark claims. | Keep provider rows separate from local QA rows and rerun this audit after every sweep. |
| `model_version_and_k_completeness` | run_data | pass | model_versions=["anthropic:claude-sonnet-4-6"]; k_values=["1"]; scaffolds={"one-shot": 3}; missing_required_rows=[]; duplicate_jobs=[] | Current model-version rows are tiny smoke rows, not a model-comparison dataset. | Require model, model_version, job_id, k, and transcript_link on every future non-local row. |
| `transcript_provenance` | run_data | pass | provider_transcripts=3; missing_transcripts=[] | Transcript existence plus single-review labels does not imply independent adjudication or representative failure-mode coverage. | Keep transcript files committed, audit review rows against transcript evidence, and require independent adjudication before failure-distribution claims. |
| `summary_count_consistency` | analysis_data | pass | summary_rows=10; mismatches=[]; primary_planned_cells=18; primary_covered_noninfra=1 | The summary intentionally records undercoverage rather than performance conclusions. | Regenerate scripts/analyze_model_results.py after any run_results change. |
| `report_sample_size_and_version_disclosure` | report_text | pass | model_versions_in_detailed_report=1/1; missing_versions=[]; missing_main_phrases=[]; missing_model_analysis_phrases=[] | The concise report summarizes counts but leaves full model-version rows to the detailed evidence appendix. | Keep sample sizes, k, infra policy, and model versions visible in generated report text. |
| `local_qa_exclusion_boundary` | claim_boundary | pass | local_qa_rows=66; provider_rows=3 | Local QA rows validate grading behavior and must not enter model-capability summaries. | Keep local QA excluded from model_result_summary and benchmark pass-rate text. |
| `infra_policy_boundary` | claim_boundary | pass | provider_infra_rows=1; accepted_infra_rows=1 | Provider reliability claims need many more rows; this row only checks accounting policy disclosure. | Retain infra rows in raw data and report them separately from capability means. |

## Interpretation

`pass` means the current smoke-run evidence is traceable and correctly caveated. It does not mean the sample is large enough for performance claims. `fail` means a report reader could not audit model/version/sample-size provenance from committed artifacts.
