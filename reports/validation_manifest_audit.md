# Validation Manifest Audit

This generated audit checks `reports/validation_manifest.json` as reproducibility evidence. It verifies schema fields, command coverage, current artifact hashes, public-export summary, and the policy that the manifest records generation-time git state rather than a post-commit clean-checkout proof.

## Summary

- checks: `8`
- statuses: `{"pass": 8}`
- areas: `{"artifact_hashes": 3, "commands": 1, "counts": 1, "git_state": 1, "manifest_schema": 1, "public_export": 1}`

## Check Table

| check | area | status | evidence | limitation | next action |
| --- | --- | --- | --- | --- | --- |
| `schema_and_policy_note` | manifest_schema | pass | schema_version=1; generated_at_present=True; tool_versions_present=True; policy_note_present=True | The manifest records generation-time state and intentionally omits self-referential main-report hashes. | Regenerate reports/validation_manifest.json with scripts/write_validation_manifest.py and keep the policy note explicit. |
| `regeneration_command_coverage` | commands | pass | commands=82; required=36; missing=[] | Command coverage proves the intended local gate is listed, not that it was run on a clean hosted environment. | Keep the README, manifest, and full validation command list in sync. |
| `artifact_hash_integrity` | artifact_hashes | pass | artifacts=184; checked_hashes=184; hash_mismatches=0; missing_recorded_paths=0; examples=[] | The manifest hashes generated local artifacts but intentionally avoids self-referential report hashes. | Regenerate the full local gate if any hash mismatch appears. |
| `artifact_inventory_coverage` | artifact_hashes | pass | inventory_candidates=168; recorded_artifacts=184; allowed_unhashed=5; missing_inventory=0; examples=[] | The inventory check covers data CSVs, report markdown, and scripts. It intentionally excludes self-referential final reports, the validation-manifest audit output, and the progress log. | Add omitted evidence files to HASHED_ARTIFACTS or document them in ALLOWED_UNHASHED_ARTIFACTS. |
| `self_reference_boundary` | artifact_hashes | pass | main_report_omitted=True; evidence_appendix_omitted=True; policy_note_mentions_omission=True | The main report and appendix are regenerated after manifest writing and therefore cannot be hashed by the manifest without circularity. | Use git history plus report-source traceability for those final rendered reports. |
| `public_export_snapshot` | public_export | pass | configured=True; exists=True; task_count=14; hidden_or_wrong_path_count=0 | This is a local public-export snapshot, not hosted QA evidence. | Run hosted QA before treating the public export as a locked problem set. |
| `git_snapshot_policy` | git_state | pass | dirty=True; status_entries=25; policy_note_present=True | A dirty generation-time snapshot is expected for committed report updates; this is not a clean-checkout proof. | For a release tag, run the full gate from a clean checkout or CI and record that evidence separately. |
| `summary_count_snapshot` | counts | pass | task_count=26; acceptance_status_counts={"accepted_v0": 6, "calibration_only": 8, "rejected_duplicate": 2, "rejected_too_easy": 10}; run_rows=69; local_qa_rows=66; model_rows=3 | Count snapshots are local evidence and do not imply benchmark-scale sufficiency. | Keep count snapshots aligned with requirement coverage and release-decision gates. |

## Interpretation

`pass` means the manifest is internally consistent for the local reproducibility role it claims. It does not mean the benchmark has been validated from a clean checkout, hosted environment, or final release tag.
