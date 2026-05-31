# Model Run Analysis

This generated analysis reads `data/run_results.csv` and `data/model_sweep_plan.csv`. It separates local QA from provider rows, accepted-core rows from calibration rows, and planned-sweep coverage from smoke evidence.

## Current Evidence Status

- planned accepted-core task/scaffold cells: `18`
- planned cells with any committed accepted-core provider row: `1`
- planned cells with a non-infra accepted-core provider row: `1`
- accepted-core provider rows: `2` total, `1` non-infra
- accepted-core successes among non-infra provider rows: `0`
- all committed provider smoke rows: `3` total, `2` non-infra

The committed provider rows are useful smoke evidence, but they are not a benchmark performance run. The planned primary sweep remains mostly uncovered.

## Planned-Sweep Coverage By Scaffold

| scaffold | planned cells | covered any | covered non-infra | successful cells |
| --- | ---: | ---: | ---: | ---: |
| `one-shot` | 6 | 1 | 1 | 0 |
| `lookup` | 6 | 0 | 0 | 0 |
| `lookup_unlimited` | 6 | 0 | 0 | 0 |

## Accepted-Core Provider Rows By Scaffold

| scaffold | rows | non-infra rows | successes | mean pass@k | Wilson 95% CI | infra rows |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| `one-shot` | 2 | 1 | 0 | 0.0000 | 0.0000-0.7935 | 1 |

## Failure Labels In Provider Rows

| label | rows | notes |
| --- | ---: | --- |
| `infra_failure` | 1 | 1 committed provider row(s) with this primary failure label. |
| `proof_debugging` | 1 | 1 committed provider row(s) with this primary failure label. |

## Interpretation

- Do not use these rows for frontier-model capability claims.
- Use the analysis to verify that future sweeps cover all planned accepted-core task/scaffold cells.
- Keep calibration-only rows separate from accepted-core estimates.
- Retain infra failures in `data/run_results.csv`, but exclude them from capability means while reporting reliability separately.
