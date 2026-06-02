# Model Sweep Coverage Audit

This generated audit maps each planned accepted-core `(task, scaffold, k)` cell in `data/model_sweep_plan.csv` to committed non-local rows in `data/run_results.csv`. It is deliberately stricter than the smoke-run summary: a cell is covered only when a non-infra provider row reaches the planned `k` and has at least `k` completed attempts.

## Summary

- planned cells: `18`
- coverage statuses: `{"missing": 17, "smoke_only": 1}`
- cells not ready for pass@k analysis: `18`

## Coverage By Scaffold

| scaffold | status | cells |
| --- | --- | ---: |
| `lookup` | missing | 6 |
| `lookup_unlimited` | missing | 6 |
| `one-shot` | missing | 5 |
| `one-shot` | smoke_only | 1 |

## Planned Cell Ledger

| cell | planned k | provider rows | non-infra rows | exact-k rows | status | evidence | next action |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| `lt-201:one-shot` | 10 | 2 | 1 | 0 | smoke_only | 1 non-infra row(s), but max_k=1 and max_attempts_completed=1 are below planned_k=10. | Run this task/scaffold with the planned k and commit the full score vector and transcript. |
| `lt-201:lookup` | 10 | 0 | 0 | 0 | missing | No committed non-local row matches this planned task/scaffold cell. | Run the planned sweep command for this task/scaffold and commit transcripts/results. |
| `lt-201:lookup_unlimited` | 10 | 0 | 0 | 0 | missing | No committed non-local row matches this planned task/scaffold cell. | Run the planned sweep command for this task/scaffold and commit transcripts/results. |
| `lt-203:one-shot` | 10 | 0 | 0 | 0 | missing | No committed non-local row matches this planned task/scaffold cell. | Run the planned sweep command for this task/scaffold and commit transcripts/results. |
| `lt-203:lookup` | 10 | 0 | 0 | 0 | missing | No committed non-local row matches this planned task/scaffold cell. | Run the planned sweep command for this task/scaffold and commit transcripts/results. |
| `lt-203:lookup_unlimited` | 10 | 0 | 0 | 0 | missing | No committed non-local row matches this planned task/scaffold cell. | Run the planned sweep command for this task/scaffold and commit transcripts/results. |
| `lt-202:one-shot` | 10 | 0 | 0 | 0 | missing | No committed non-local row matches this planned task/scaffold cell. | Run the planned sweep command for this task/scaffold and commit transcripts/results. |
| `lt-202:lookup` | 10 | 0 | 0 | 0 | missing | No committed non-local row matches this planned task/scaffold cell. | Run the planned sweep command for this task/scaffold and commit transcripts/results. |
| `lt-202:lookup_unlimited` | 10 | 0 | 0 | 0 | missing | No committed non-local row matches this planned task/scaffold cell. | Run the planned sweep command for this task/scaffold and commit transcripts/results. |
| `lt-204:one-shot` | 10 | 0 | 0 | 0 | missing | No committed non-local row matches this planned task/scaffold cell. | Run the planned sweep command for this task/scaffold and commit transcripts/results. |
| `lt-204:lookup` | 10 | 0 | 0 | 0 | missing | No committed non-local row matches this planned task/scaffold cell. | Run the planned sweep command for this task/scaffold and commit transcripts/results. |
| `lt-204:lookup_unlimited` | 10 | 0 | 0 | 0 | missing | No committed non-local row matches this planned task/scaffold cell. | Run the planned sweep command for this task/scaffold and commit transcripts/results. |
| `lt-205:one-shot` | 10 | 0 | 0 | 0 | missing | No committed non-local row matches this planned task/scaffold cell. | Run the planned sweep command for this task/scaffold and commit transcripts/results. |
| `lt-205:lookup` | 10 | 0 | 0 | 0 | missing | No committed non-local row matches this planned task/scaffold cell. | Run the planned sweep command for this task/scaffold and commit transcripts/results. |
| `lt-205:lookup_unlimited` | 10 | 0 | 0 | 0 | missing | No committed non-local row matches this planned task/scaffold cell. | Run the planned sweep command for this task/scaffold and commit transcripts/results. |
| `lt-206:one-shot` | 10 | 0 | 0 | 0 | missing | No committed non-local row matches this planned task/scaffold cell. | Run the planned sweep command for this task/scaffold and commit transcripts/results. |
| `lt-206:lookup` | 10 | 0 | 0 | 0 | missing | No committed non-local row matches this planned task/scaffold cell. | Run the planned sweep command for this task/scaffold and commit transcripts/results. |
| `lt-206:lookup_unlimited` | 10 | 0 | 0 | 0 | missing | No committed non-local row matches this planned task/scaffold cell. | Run the planned sweep command for this task/scaffold and commit transcripts/results. |

## Interpretation

`covered_pass` and `covered_fail` are row-shape readiness states, not standalone benchmark validity: hosted QA, model/provider coverage, and claim-tier sample-size gates still apply. `smoke_only`, `infra_only`, and `missing` cells must stay out of scaffold-effect or frontier-performance estimates.
