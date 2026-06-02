# Final Delivery Checklist Audit

This generated audit maps the `docs/lean_eval_project_playbook.md` final-delivery checklist to committed evidence. It is intentionally strict: a `block` means the final-delivery condition is not proven by current artifacts, while a `caution` means local evidence exists but hosted or execution evidence is still missing.

## Summary

- checklist rows: `10`
- statuses: `{"block": 5, "caution": 2, "pass": 3}`

## Checklist Table

| check | status | playbook item | evidence | limitation | next action |
| --- | --- | --- | --- | --- | --- |
| `final_versions_have_pass_at_k` | block | all exact final problem versions have pass@10 or the agreed pass@k | planned_primary_cells=18; covered_noninfra_cells=1; noninfra_provider_rows=2; nonlocal_rows=3 | The plan specifies pass@10 cells, but committed provider rows do not cover the accepted task/scaffold plan. | Run the planned accepted-core pass@10 sweep on exact final problem versions and commit transcripts/results. |
| `scaffolds_use_same_task_set` | caution | every scaffold uses the same task set unless explicitly documented | planned_scaffolds=["lookup", "lookup_unlimited", "one-shot"]; planned_same_accepted_set=True; observed_noninfra_scaffolds=["one-shot"] | The planned sweep uses the same accepted task set, but observed committed provider evidence has not yet covered the scaffold ladder. | Keep the same accepted task IDs across one-shot, lookup, and lookup_unlimited runs; document any exclusion before running. |
| `env_linter_findings_resolved` | block | no unresolved warning/error/critical Env Linter findings | env_linter_status=block; hosted_status_counts={"block": 6, "caution": 3, "pass": 3} | No Env Linter result rows are committed, so absence of unresolved findings is unproven. | Run Env Linter on exact hosted problem versions and record each warning/error/critical finding disposition. |
| `full_env_qa_10_attempts` | block | final QA used Full Env QA on 10 attempts | full_env_status=block; evidence=transcript_health_or_full_env_rows=0 | No Full Env QA result rows on final exact problem versions are committed. | Run Full Env QA on 10 attempts after hosted smoke stability and commit result IDs/findings. |
| `late_qa_findings_settled` | block | late QA findings have settled | qa_resolution_status=block; evidence=hosted_result_rows=0; unresolved_warning_or_higher=0 | There are no hosted QA rows or late-finding timestamps to prove the 30-45 minute settling window has elapsed. | Record hosted QA completion times and final finding dispositions after the settling window. |
| `repo_matches_uploaded_environment` | block | repo source matches the uploaded environment | problem_version_status=block; freeze_mapping_status=block | The local Taiga package scaffold exists, but no immutable uploaded image digest or hosted problem-version mapping is committed. | Commit image digest, environment/problem-version IDs, and snapshot/tag mapping for the exact uploaded package. |
| `plots_regenerate_from_committed_csv` | pass | plots regenerate from committed CSV files | generated_figures=5; generated_figures_ok=True; figure_status_counts={"blocked_by_evidence": 5, "generated_descriptive": 4, "generated_provenance": 1}; report_count_failures=0 | Generated descriptive/provenance plots are covered; blocked performance plots intentionally remain absent. | Keep performance plots blocked until provider/scaffold coverage satisfies the statistical plan. |
| `report_states_sample_sizes_and_model_versions` | pass | report text states sample sizes and model versions | provider_versions_phrase=True; sample_sizes_phrase=True; report_count_ok=True; claim_conformance_ok=True | The report states sample sizes and model versions for smoke rows, but performance conclusions remain blocked by undercoverage. | After broad sweeps, regenerate model provenance, count consistency, and claim-conformance audits before interpreting pass rates. |
| `dev_test_split_marked` | pass | dev/test split is clearly marked | release_split_counts={"dev": 6, "test": 8}; release_task_count=14 | Split labels are local metadata/export evidence, not evidence of hosted problem-version mapping. | Preserve split labels in metadata and hosted problem metadata when uploading exact versions. |
| `hidden_references_not_public_runtime_assets` | caution | hidden references are not in public runtime assets | public_export={"exists": true, "hidden_or_wrong_path_count": 0, "task_count": 14}; validation_manifest_exists=True; hidden_asset_rows=52; hidden_assets_with_public_export_path=0; taiga_wrapper_isolation_ok=True | Local public export and wrapper mitigation pass, but hosted filesystem-tool isolation on uploaded images is still unproven. | Run hosted preflight/Env Linter and record proof that tools cannot read hidden references, hidden pins, wrong submissions, or transient bundles. |

## Interpretation

`pass` rows are supported by committed local artifacts. `caution` rows have useful local evidence but still need hosted or execution proof before final delivery. `block` rows are missing required final-delivery evidence and must remain blockers for locked-benchmark wording.
