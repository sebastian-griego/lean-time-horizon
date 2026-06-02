# Data Schema Manifest

This generated audit documents the schema status of the benchmark's data inputs. It separates schema-backed external data contracts from generated report/audit CSVs whose structure is governed by producer scripts and validation-manifest hashes.

## Summary

- dataset rows: `9`
- validation statuses: `{"codebook_valid": 1, "documented_projection": 1, "empty_ready": 3, "inventory_documented": 1, "schema_valid": 3}`

## Schema Ledger

| dataset | status | rows | columns | schema | required fields present | errors | coverage note | limitation | next action |
| --- | --- | ---: | ---: | --- | --- | --- | --- | --- | --- |
| `task_metadata_json` | schema_valid | 26 | 26 | `data/task_metadata_schema.json` | true | `[]` | Per-task metadata JSON is the authoritative full metadata surface. | The aggregate CSV is a generated projection and intentionally omits some grader-only metadata fields. | Keep metadata.json as the source of truth and rerun validate_all.py after metadata edits. |
| `task_metadata_csv_projection` | documented_projection | 26 | 21 | `data/task_metadata_schema.json` | true | `[]` | CSV columns match the validate_all.py projection used by reports. | This CSV is not the full schema-bearing metadata record; use metadata.json for hidden grading declarations and task-specific bans. | If report columns change, update validate_all.py and this manifest together. |
| `run_results` | schema_valid | 71 | 19 | `data/run_results_schema.json` | true | `[]` | Run-result rows validate against required columns, enums, numeric ranges, and pass@k field types. | Schema validation does not prove sample-size adequacy or model-result representativeness. | Run scripts/audit_run_integrity.py after edits to check transcript and arithmetic semantics. |
| `failure_annotations` | empty_ready | 0 | 6 | `data/failure_label_schema.json` | true | `[]` | The adjudicated-failure table has schema-compatible headers but no broad-run rows yet. | Empty adjudication data cannot support failure-distribution claims. | Populate after broad provider sweeps and independent transcript review. |
| `failure_label_reviews` | schema_valid | 3 | 11 | `data/failure_label_review_schema.json` | true | `[]` | Committed smoke transcript reviews satisfy the review-row schema. | These are single-review smoke rows, not independent distributional adjudication. | Use the transcript review packet and adjudication fields for future broad sweeps. |
| `human_time_observations` | empty_ready | 0 | 7 | `data/human_time_observations_schema.json` | true | `[]` | The timing-observation table has schema-compatible headers but no independent observations yet. | Author/reviewer estimates remain uncalibrated by independent timed solves. | Collect non-author timing rows before strengthening time-horizon claims. |
| `independent_task_reviews` | empty_ready | 0 | 15 | `data/independent_task_review_schema.json` | true | `[]` | The independent accepted-task review table has schema-compatible headers but no non-author task-quality reviews yet. | Empty review data cannot support independent acceptance, time-bucket, hidden-pin, or wrong-submission adequacy claims. | Collect non-author review rows for every accepted_v0 task before strengthening benchmark-grade task-quality claims. |
| `failure_label_codebook` | codebook_valid | 13 | 2 | `data/failure_label_schema.json` | true | `[]` | Failure-label codebook covers the playbook taxonomy used by run and transcript audits. | The codebook is a taxonomy definition, not evidence that those failures dominate. | Update the codebook and downstream audits together if labels change. |
| `derived_reporting_csv_inventory` | inventory_documented | 64 | 0 | `` | true | `[]` | CSV files=64; schema JSON files=6; derived/reporting CSV files=57. | Most generated audit CSVs are governed by their producer scripts and manifest hashes rather than standalone JSON schemas. | Add standalone schemas only for files that become external data contracts or model-run inputs. |

## Interpretation

`schema_valid`, `documented_projection`, `empty_ready`, `codebook_valid`, and `inventory_documented` are acceptable for v0.1 research-report evidence. They do not imply that the data are sufficient for locked-benchmark or frontier-performance claims; they only document row shape, codebooks, and schema boundaries.
