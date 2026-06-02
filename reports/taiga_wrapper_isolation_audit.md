# Taiga Wrapper Isolation Audit

This generated audit exercises the local Taiga wrapper hidden-bundle path. It is mitigation evidence only: hosted filesystem-tool isolation, image digest pinning, preflight, Full Env QA, and Env Linter evidence are still required before hosted-QA claims can be made.

## Summary

- checks: `3`
- statuses: `{"pass": 3}`
- areas: `{"bundle_generation": 1, "static_packaging": 1, "wrapper_runtime": 1}`

## Check Table

| check | area | status | evidence | limitation | next action |
| --- | --- | --- | --- | --- | --- |
| `hidden_bundle_generation` | bundle_generation | pass | returncode=0; bundle_entries=14; bundle_contains_pincheck=True; bundle_contains_reference=False; stdout=wrote C:\Users\sebas\lean-time-horizon\tmp\taiga_wrapper_isolation\hidden_bundle.json with 14 hidden pin entries | This checks the committed local bundle generator, not a built uploaded container image. | Keep the bundle limited to hidden PinCheck text and verify count changes whenever public release tasks change. |
| `bundle_runtime_grading_smoke` | wrapper_runtime | pass | {"bundle_deleted": true, "hidden_bundle_count": 14, "public_hidden_or_wrong_count": 0, "public_hidden_or_wrong_examples": [], "reference_hidden_bundle_used": true, "reference_score": 1.0, "source_fallback_calls": [], "unedited_hidden_bundle_used": true, "unedited_score": 0.0} | This is a local subprocess smoke test. It proves the wrapper can use the bundle path without source-task fallback, but it is not hosted filesystem-tool isolation evidence. | Run Taiga preflight and Env Linter on the uploaded image to prove the model cannot inspect hidden material. |
| `docker_static_isolation_controls` | static_packaging | pass | bundle_generation_in_docker=True; task_sources_removed=True; bundle_env=True; bundle_deleted_on_import=True; bundle_validator=True | Static controls can drift from hosted runtime behavior and do not replace uploaded-image inspection. | Keep this audit passing and add hosted evidence rows after upload. |

## Interpretation

`pass` means the local wrapper mitigation is internally exercised. It does not mean hidden material is unreachable to a model in Taiga; that requires hosted preflight and Env Linter evidence on the exact uploaded image/problem versions.
