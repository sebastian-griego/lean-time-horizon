# Statistical Analysis Plan

This generated plan fixes the minimum evidence thresholds for interpreting future model runs. It complements `reports/evaluation_protocol.md`: the protocol defines what to run, while this plan defines what claims the resulting sample can and cannot support.

## Current Evidence Snapshot

- accepted tasks: `6`
- planned accepted task/scaffold cells: `18`
- covered non-infra accepted task/scaffold cells: `1`
- observed scaffolds: `["one-shot"]`
- independent timing observations on accepted tasks: `0`
- non-infra provider failure rows: `1`
- failure-label review rows: `3`
- hosted-QA block rows: `6`

## Claim Tiers

- tier statuses: `{"blocked": 6, "supported": 1}`

| tier | status | minimum evidence | allowed output now | blocked overclaim |
| --- | --- | --- | --- | --- |
| `smoke_run_provenance` | supported | accepted=0; cells=1; k=1; scaffolds=1; group_n=not_applicable; timing=0; failure_reviews=all committed smoke rows reviewed or explicitly queued; hosted=false | Adapter, transcript, and run-result provenance only. | Do not treat smoke rows as benchmark performance. |
| `v0_1_primary_descriptive_performance` | blocked | accepted=6; cells=18; k=10; scaffolds=3; group_n=not_applicable; timing=0; failure_reviews=all non-success transcripts reviewed; hosted=false | Coverage table and blocked performance statement. | Do not report aggregate pass@k estimates or intervals for accepted-core performance until every planned cell is covered. |
| `scaffold_effect_comparison` | blocked | accepted=20; cells=accepted_tasks * 3 scaffold cells; k=10; scaffolds=3; group_n=not_applicable; timing=0; failure_reviews=all non-success transcripts reviewed; hosted=false | Planned scaffold comparison only. | Do not claim lookup or iterative compile/debug effects from the current smoke rows. |
| `time_horizon_bucket_trend` | blocked | accepted=20; cells=all accepted task x scaffold cells for reported model; k=10; scaffolds=3; group_n=5 per reported bucket; timing=all accepted tasks; failure_reviews=all non-success transcripts reviewed; hosted=false | Task-set time-bucket composition only. | Do not claim calibrated time-horizon scaling from author estimates or singleton T3 coverage. |
| `family_or_skill_summary` | blocked | accepted=30; cells=all accepted task x scaffold cells for reported model; k=10; scaffolds=3; group_n=5 per reported family or skill group; timing=all accepted tasks; failure_reviews=all non-success transcripts reviewed; hosted=false | Family/skill coverage table only. | Do not interpret singleton family or skill rows as stable estimates. |
| `failure_taxonomy_distribution` | blocked | accepted=20; cells=enough covered cells to produce at least 10 non-infra failures; k=10; scaffolds=2; group_n=not_applicable; timing=0; failure_reviews=at least 10 independently reviewed non-infra failures; hosted=false | Failure-label workflow and smoke transcript review only. | Do not claim dominant failure modes or failure distributions. |
| `locked_benchmark_population_claims` | blocked | accepted=20-50; cells=all accepted task x scaffold cells for reported model; k=10; scaffolds=3; group_n=5 per reported subgroup; timing=all accepted tasks; failure_reviews=all non-success transcripts independently reviewed; hosted=true | Local v0.1 research artifact only. | Do not call v0.1 locked, final, population-valid, or frontier-performance-characterizing. |

## Precision Ledger

The table below shows Wilson 95% intervals for a binary task-row endpoint under a worst-case midrange success rate. It is a precision guide, not a power guarantee. It makes visible why the current accepted-core size and smoke rows cannot support stable population-level estimates.

| n | successes at p=0.5 | Wilson low | Wilson high | width | interpretation |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 0 | 0.0000 | 0.7935 | 0.7935 | very_wide |
| 6 | 3 | 0.1876 | 0.8124 | 0.6248 | very_wide |
| 18 | 9 | 0.2903 | 0.7097 | 0.4194 | wide |
| 20 | 10 | 0.2993 | 0.7007 | 0.4014 | wide |
| 30 | 15 | 0.3315 | 0.6685 | 0.3369 | moderate |
| 50 | 25 | 0.3664 | 0.6336 | 0.2671 | moderate |

## Reporting Rules

1. Report raw numerators and denominators before percentages.
2. Report Wilson intervals for binary task-row means only when the planned cells for the stated analysis set are covered.
3. Treat subgroup summaries with fewer than five accepted tasks as coverage tables, not estimates.
4. Keep infra failures in raw data and reliability summaries, but exclude them from model-capability means.
5. Do not strengthen blocked claim tiers until the threshold row for that tier is supported by committed evidence.
