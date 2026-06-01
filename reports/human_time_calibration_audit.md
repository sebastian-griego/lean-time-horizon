# Human-Time Calibration Audit

This generated audit checks whether metadata human-time estimates are internally consistent and whether independent timing evidence exists. It does not convert author estimates into measured human times.

## Summary

- tasks audited: `26`
- observation rows: `0`
- calibration statuses: `{"caution": 6, "pass": 20}`
- task buckets: `{"T1": 18, "T2": 7, "T3": 1}`
- issue counts: `{"accepted_without_independent_timing": 6}`
- accepted tasks without successful independent timing: `6/6`

## Accepted-Core Timing Rows

| task | bucket | p50/p90 | range | status | successful timings | issues |
| --- | --- | ---: | --- | --- | ---: | --- |
| `lt-201` | T2 | 75/150 | 45-120 | caution | 0 | `["accepted_without_independent_timing"]` |
| `lt-203` | T2 | 90/180 | 45-120 | caution | 0 | `["accepted_without_independent_timing"]` |
| `lt-202` | T2 | 90/180 | 45-120 | caution | 0 | `["accepted_without_independent_timing"]` |
| `lt-204` | T2 | 100/200 | 45-120 | caution | 0 | `["accepted_without_independent_timing"]` |
| `lt-205` | T3 | 150/300 | 120-360 | caution | 0 | `["accepted_without_independent_timing"]` |
| `lt-206` | T2 | 100/210 | 45-120 | caution | 0 | `["accepted_without_independent_timing"]` |

## Interpretation

`pass` means the metadata estimate is internally consistent and any required timing evidence exists. `caution` means metadata is internally consistent but an accepted task lacks independent timing evidence. `fail` means a metadata inconsistency needs correction before the row should be used.
