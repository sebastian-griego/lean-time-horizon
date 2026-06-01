# Statistical Reporting Audit

This generated audit checks whether the committed run data can support the METR-style performance plots and claims recommended by the playbook. `block` rows are not script failures; they are explicit evidence that the current data should not be used for that claim.

## Summary

- checks: `8`
- statuses: `{"block": 5, "pass": 3}`
- areas: `{"data_hygiene": 2, "planned_sweep": 1, "recommended_plot": 4, "statistical_method": 1}`

## Check Table

| check | area | status | current sample | supported output | limitation | next action |
| --- | --- | --- | --- | --- | --- | --- |
| `primary_sweep_coverage` | planned_sweep | block | 1/18 accepted task/scaffold cells covered by non-infra provider rows | Coverage table only. | The committed provider rows cannot support accepted-core performance estimates. | Run the planned accepted_v0 x scaffold sweep before reporting benchmark performance. |
| `scaffold_pass_at_k_plot` | recommended_plot | block | 1/3 scaffolds observed; 1 non-infra accepted-core rows | Scaffold coverage audit and planned sweep table. | A mean pass@10-by-scaffold plot would imply comparisons the data do not support. | Populate all one-shot, lookup, and lookup_unlimited cells before generating scaffold-effect plots. |
| `bucket_success_plot` | recommended_plot | block | 1 human-time buckets observed in non-infra accepted-core provider rows | Human-time distribution and planned sweep table. | Current rows cannot estimate success by human-time bucket. | Run the planned sweep and add T3/T4 accepted tasks before plotting time-horizon success curves. |
| `family_success_plot` | recommended_plot | block | 1/6 accepted families observed in non-infra provider rows | Accepted family composition only. | Current rows cannot estimate success by task family. | Run provider rows across the accepted core before family-level summaries. |
| `failure_taxonomy_plot` | recommended_plot | block | 1 non-infra provider failure rows | Failure-label counts table only. | The current failure taxonomy is useful for transcript QA but too small for distributional claims. | Collect provider failures across the planned scaffold sweep and review labels before plotting. |
| `wilson_interval_reporting` | statistical_method | pass | model_result_summary rows=10 | Wilson interval fields are generated even when sample sizes are too small for claims. | Intervals are not a substitute for adequate coverage or independent timing. | Keep Wilson intervals in future performance summaries and report raw n. |
| `local_qa_exclusion` | data_hygiene | pass | 3 provider rows; 66 local QA rows | Local QA is retained as validation evidence. | No benchmark performance claim should use local reference/wrong rows. | Keep local QA and provider rows separated in future analyses. |
| `infra_failure_policy` | data_hygiene | pass | Infra failures retained in run_results and counted separately. | Infra-failure accounting is implemented. | Provider reliability claims still need more rows. | Keep infra rows in raw data and exclude them from model-capability means. |

## Interpretation

The current artifact supports local validation, smoke-run analysis, and planned-sweep readiness checks. It does not support scaffold-effect, human-time-bucket, family-level, or failure-distribution performance claims until broader non-infra provider sweeps are committed.
