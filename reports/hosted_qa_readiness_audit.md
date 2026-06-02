# Hosted QA Readiness Audit

This generated audit checks the local artifact against the Taiga/hosted QA flow described in the playbook and Taiga wiki. `block` rows are expected before upload; they are evidence that hosted QA has not happened and should not be claimed.

## Summary

- checks: `12`
- statuses: `{"block": 6, "caution": 3, "pass": 3}`
- areas: `{"hosted_evidence": 6, "hosted_packaging": 4, "local_prerequisite": 2}`

## Check Table

| check | area | status | evidence | current state | next action |
| --- | --- | --- | --- | --- | --- |
| `local_validation_gate` | local_prerequisite | pass | run_integrity_audit_exists=True; validation_commands_exists=True; run_integrity_failures=0 | Local validation evidence is present and passing. | Keep local validation passing before any hosted upload. |
| `public_export_ready` | local_prerequisite | pass | public_export={"exists": true, "hidden_or_wrong_path_count": 0, "task_count": 14}; expected_public_task_count=14 | Public export evidence is present in the validation manifest. | Regenerate and validate public export immediately before hosted packaging. |
| `taiga_container_artifact` | hosted_packaging | caution | container_artifacts=["taiga/Dockerfile"] | A candidate Dockerfile is committed, but no uploaded immutable image digest or hosted preflight result is committed. | Build and upload the container, then record the immutable image digest and hosted preflight result before upgrading this to hosted evidence. |
| `taiga_problem_metadata` | hosted_packaging | caution | problem_metadata={"expected_count": 14, "files": [{"first_ids": ["lt-001", "lt-002", "lt-003", "lt-004", "lt-201"], "path": "taiga/problems_metadata.template.json", "problem_count": 14, "valid_json": true}], "immutable_digest_images": 0, "latest_images": 0, "missing_required_fields": 0, "placeholder_images": 14, "startup_wrapper_count": 14, "total_problems": 14, "unique_problem_ids": 14} | Generated problems-metadata covers the public release task set but still uses placeholder image values. | Replace placeholder image values with immutable uploaded image digests and commit hosted problem-version IDs after upload. |
| `mcp_hooks` | hosted_packaging | pass | mcp_hook_files=["scripts/audit_taiga_wrapper_isolation.py", "taiga/mcp_server.py"]; py_compile_failures={} | A local wrapper with setup_problem and grade_problem is present and syntactically valid; Taiga preflight has not run it. | Run Taiga local tunnel/preflight against the wrapper and record exact failures or pass evidence. |
| `hidden_material_isolation` | hosted_packaging | caution | full_repo_copy=true; hidden_dirs_present=true; problem_metadata_files=1; hidden_bundle_generated=true; task_sources_removed=true; hidden_bundle_env=true; hidden_bundle_deleted=true; hidden_bundle_validation=true; isolation_documented=true | The scaffold removes task sources after creating an in-memory hidden-pin bundle path, but no hosted tool-isolation proof is committed. | Before upload, verify with hosted preflight/Env Linter that filesystem tools cannot read hidden references, hidden pins, wrong submissions, or the transient bundle. |
| `problem_version_evidence` | hosted_evidence | block | hosted_result_rows=0; hosted_report_exists=False | No hosted problem-version evidence is committed. | After upload, record environment, problem, problem-version, image digest, and snapshot IDs. |
| `hosted_preflight_or_stage1` | hosted_evidence | block | stage1_rows=0 | No hosted preflight or Stage 1 rows are committed. | Run Taiga preflight/Stage 1 checks and record warning/error/critical findings. |
| `transcript_health_or_full_env_qa` | hosted_evidence | block | transcript_health_or_full_env_rows=0 | No Transcript Health or Full Env QA result rows are committed. | Run Full Env QA after hosted smoke runs and record result IDs and findings. |
| `env_linter` | hosted_evidence | block | env_linter_rows=0 | No Env Linter rows are committed. | Run Env Linter on the hosted environment/snapshot and record dispositions. |
| `qa_findings_resolution` | hosted_evidence | block | hosted_result_rows=0; unresolved_warning_or_higher=0 | No finding-resolution evidence is committed. | Record each finding with severity, disposition, fix/rebuttal, and affected problem version. |
| `exact_version_freeze_mapping` | hosted_evidence | block | hosted_report_exists=False; freeze_mapping_terms_present=False | No hosted freeze mapping is committed. | After hosted QA, commit the exact version/snapshot mapping and tag policy. |

## Interpretation

The repo is locally validated and now includes a Taiga packaging scaffold with local hidden-material exposure mitigations, but it does not yet include hosted isolation proof, immutable uploaded image digests, hosted problem-version IDs, preflight/Stage 1 evidence, Full Env QA, Env Linter rows, or finding dispositions. The locked-benchmark hosted-QA gate must remain not met until those artifacts are real and committed.

Packaging `caution` means the repository contains a concrete local scaffold, such as a Dockerfile or generated problems-metadata template, but not immutable uploaded image digests or hosted preflight evidence. Hosted-evidence `block` rows are still the authoritative reason the benchmark is not hosted-QA-cleared.
