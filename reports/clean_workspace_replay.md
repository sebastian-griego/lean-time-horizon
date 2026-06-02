# Clean Workspace Replay

This generated replay creates a temporary workspace from the current tracked plus unignored working-tree files, excluding local build output, ignored secrets, temporary directories, and the existing public export. It then runs a bounded local replay that exercises the Lean toolchain, grader pass/fail behavior, and public export validation.

It is stronger than a manifest-only command list, but still weaker than a remote clean clone, CI run, hosted Taiga QA, or full provider sweep.

## Summary

- replay checks: `7`
- phase counts: `{"replay": 6, "setup": 1}`
- statuses: `{"pass": 7}`
- failure rows: `0`
- workspace: `tmp/clean_workspace_replay/workspace`

## Replay Table

| check | phase | status | seconds | command | limitation |
| --- | --- | --- | ---: | --- | --- |
| `workspace_materialization` | setup | pass | 28.60 | `materialize tracked and unignored working-tree files into tmp/clean_workspace_replay/workspace` | This is a local clean workspace from the current working tree, not a remote clone or hosted container. |
| `mathlib_cache_get` | replay | pass | 511.86 | `lake exe cache get` | This uses the Mathlib cache for local dependency materialization; hosted runners need their own cache or build path. |
| `clean_lake_build` | replay | pass | 5.04 | `lake build` | Local toolchain and dependency resolution can differ from hosted QA. |
| `reference_validation_smoke` | replay | pass | 24.95 | `python scripts/validate_task.py tasks/dev/lt-201-multifile-cache-repair --submission tasks/dev/lt-201-multifile-cache-repair/hidden/Reference.lean --expect pass` | This is a representative reference-validation smoke, not full validate_all coverage. |
| `wrong_submission_smoke` | replay | pass | 6.06 | `python scripts/validate_task.py tasks/dev/lt-203-exact-cover-spec --submission tasks/dev/lt-203-exact-cover-spec/wrong/Vacuous.lean --expect fail` | This probes expected-fail behavior for one semantic-pin wrong submission only. |
| `public_export_smoke` | replay | pass | 0.72 | `python scripts/export_public_tasks.py --out public_tasks` | Local public export is not hosted problem packaging. |
| `public_export_validation_smoke` | replay | pass | 82.89 | `python scripts/validate_public_export.py --out public_tasks` | This validates local public assets but does not run Env Linter. |

## Interpretation

`pass` means the bounded replay step completed in the temporary clean workspace. This should be treated as local reproducibility smoke evidence only: exhaustive task validation still comes from `validate_all.py`, model-performance evidence still requires real provider sweeps, and locked-benchmark claims still require hosted QA plus independent timing.
