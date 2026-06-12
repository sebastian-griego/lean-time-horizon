# Benchmark Package Audit

This generated audit checks that source task metadata, required task assets, the committed metadata CSV, and the public export agree. It is intentionally lighter than full Lean validation, so it can run in PR CI as a packaging and release-integrity gate.

## Summary

- checks: `4`
- statuses: `{"pass": 4}`
- failed checks: `0`

## Check Table

| check | area | status | evidence | problems | required action |
| --- | --- | --- | --- | --- | --- |
| `task_inventory` | source_tasks | pass | tasks=26; statuses={"accepted_v0": 6, "calibration_only": 8, "rejected_duplicate": 2, "rejected_too_easy": 10}; duplicate_task_ids=0 | `[]` | Keep one unique task_id per tracked task metadata file. |
| `task_source_structure` | source_tasks | pass | tasks_checked=26; release_statuses=["accepted_v0", "calibration_only", "candidate_review_pending"] | `[]` | Fix task metadata, public files, hidden checks, and wrong submissions before promoting or exporting a task. |
| `task_metadata_csv_projection` | generated_data | pass | expected_rows=26; projection_fields=21; csv_path=data/task_metadata.csv | `[]` | Rerun scripts/validate_all.py after metadata edits and commit the regenerated CSV. |
| `public_export_bundle` | public_export | pass | public_export=public_tasks; expected_release_tasks=14 | `[]` | Regenerate the public export and remove any hidden, wrong, stale, or unexpected public assets. |

## Interpretation

`pass` means the source bundle and exported public task package satisfy structural release invariants. This does not replace `validate_all.py`, hidden semantic pins, axiom audits, or independent task-quality review; it prevents stale metadata, missing assets, public-export drift, and accidental hidden-material exposure from passing unnoticed.
