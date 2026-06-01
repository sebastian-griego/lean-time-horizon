# Hosted QA Readiness Audit

This generated audit checks the local artifact against the Taiga/hosted QA flow described in the playbook and Taiga wiki. `block` rows are expected before upload; they are evidence that hosted QA has not happened and should not be claimed.

## Summary

- checks: `11`
- statuses: `{"block": 9, "pass": 2}`
- areas: `{"hosted_evidence": 6, "hosted_packaging": 3, "local_prerequisite": 2}`

## Check Table

| check | area | status | evidence | current state | next action |
| --- | --- | --- | --- | --- | --- |
| `local_validation_gate` | local_prerequisite | pass | run_integrity_audit_exists=True; validation_commands_exists=True; run_integrity_failures=0 | Local validation evidence is present and passing. | Keep local validation passing before any hosted upload. |
| `public_export_ready` | local_prerequisite | pass | public_export={"exists": true, "hidden_or_wrong_path_count": 0, "task_count": 14}; expected_public_task_count=14 | Public export evidence is present in the validation manifest. | Regenerate and validate public export immediately before hosted packaging. |
| `taiga_container_artifact` | hosted_packaging | block | container_artifacts=[] | No committed Taiga container artifact was found. | Create a Taiga-compatible container or document use of a managed preset before hosted QA. |
| `taiga_problem_metadata` | hosted_packaging | block | problem_metadata_files=[] | No committed Taiga problems-metadata JSON was found. | Generate a Taiga problems-metadata file for the exact accepted/calibration public versions. |
| `mcp_hooks` | hosted_packaging | block | mcp_hook_files=[] | No committed MCP hook implementation was found. | Implement or document the MCP wrapper that calls the Lean grader. |
| `problem_version_evidence` | hosted_evidence | block | hosted_result_rows=0; hosted_report_exists=False | No hosted problem-version evidence is committed. | After upload, record environment, problem, problem-version, image digest, and snapshot IDs. |
| `hosted_preflight_or_stage1` | hosted_evidence | block | stage1_rows=0 | No hosted preflight or Stage 1 rows are committed. | Run Taiga preflight/Stage 1 checks and record warning/error/critical findings. |
| `transcript_health_or_full_env_qa` | hosted_evidence | block | transcript_health_or_full_env_rows=0 | No Transcript Health or Full Env QA result rows are committed. | Run Full Env QA after hosted smoke runs and record result IDs and findings. |
| `env_linter` | hosted_evidence | block | env_linter_rows=0 | No Env Linter rows are committed. | Run Env Linter on the hosted environment/snapshot and record dispositions. |
| `qa_findings_resolution` | hosted_evidence | block | hosted_result_rows=0; unresolved_warning_or_higher=0 | No finding-resolution evidence is committed. | Record each finding with severity, disposition, fix/rebuttal, and affected problem version. |
| `exact_version_freeze_mapping` | hosted_evidence | block | hosted_report_exists=False; freeze_mapping_terms_present=False | No hosted freeze mapping is committed. | After hosted QA, commit the exact version/snapshot mapping and tag policy. |

## Interpretation

The repo is locally validated, but it does not yet include Taiga container/problem metadata, hosted problem-version IDs, preflight/Stage 1 evidence, Full Env QA, Env Linter rows, or finding dispositions. The locked-benchmark hosted-QA gate must remain not met until those artifacts are real and committed.
