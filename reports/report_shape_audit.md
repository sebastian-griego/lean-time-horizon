# Report Shape Audit

This generated audit checks the concise METR-style report against the report-shape questions in `docs/lean_eval_project_playbook.md`. `blocked_by_evidence` is an honest answer, not an audit failure: it means the report explicitly says the current data cannot support that analysis yet.

## Summary

- checks: `7`
- answer statuses: `{"answered": 3, "answered_with_blocker": 1, "answered_with_caveat": 1, "blocked_by_evidence": 2}`

## Check Table

| check | playbook question | answer status | evidence | limitation | next action |
| --- | --- | --- | --- | --- | --- |
| `tasks_built` | What tasks were built? | answered | accepted=6; calibration=8; missing_phrases=[] | The accepted set is below the final 20-50 task target. | Keep accepted/calibration/rejected status visible and expand only with hard-reviewed tasks. |
| `capabilities_tested` | What capabilities do the tasks test? | answered_with_caveat | capability_rows=7; singleton_capabilities=["library_search", "semantic_formalization", "codebase_navigation"]; missing_phrases=[] | Some capabilities are represented by only one accepted task, so capability-level claims remain weak. | Add independently reviewed tasks for singleton capabilities before making capability-level performance claims. |
| `scaffolds_compared` | What scaffolds were compared? | answered_with_blocker | planned_cells=18; covered_noninfra=1; missing_phrases=[] | The scaffold ladder is planned and implemented, but committed provider evidence covers only a tiny one-shot smoke sample. | Run the accepted-core scaffold sweep before interpreting scaffold effects. |
| `success_changes_by_scaffold_and_bucket` | How does success change with scaffold and human-time bucket? | blocked_by_evidence | scaffold_result_comparison=partial; time_horizon_spread=partial; statistical_analysis_plan=supported; primary_covered_noninfra=1 | Real scaffold/time-horizon performance summaries are not supported by committed data. | Run pass@k sweeps across accepted_v0 x scaffold cells, meet the statistical threshold rows, and add independently timed T3/T4 tasks. |
| `failure_modes_dominate` | What failure modes dominate? | blocked_by_evidence | concision_mentions_failure_limits=True; missing_phrases=[] | Expected failure modes are documented, but broad model transcripts are not independently adjudicated. | Use the transcript review packet and failure-label review audit after broader provider sweeps before claiming dominant failure modes. |
| `next_batch_needs` | What does the next batch need? | answered | missing_phrases=[] | Next work is a concrete blocker list, not a claim that the benchmark is locked. | Keep next-work items tied to requirement/freeze gates. |
| `skimmability` | Is the main report skimmable? | answered | concise_report_lines=186; conformance_failures=0 | The concise report is short, and row-level generated tables live in the evidence appendix instead of the main narrative. | Keep the concise and main reports short and keep long tables in generated appendices. |

## Interpretation

`answered` rows are directly handled by the concise report. `answered_with_caveat` rows are handled but have construct-validity limits. `answered_with_blocker` and `blocked_by_evidence` rows are acceptable only because the report states the missing evidence rather than implying a result.
