# Transcript Review Packet

This generated packet turns committed non-local transcripts into a review queue for failure-label adjudication. It does not create new model results and does not change `data/run_results.csv`; reviewers should fill `data/failure_label_review_template.csv` after inspecting transcripts. A separate `data/failure_label_reviews.csv` file may record completed single-review adjudications, but the current smoke queue does not support distributional failure-mode claims.

## Summary

- queued non-local rows: `3`
- queue rows with committed single-review adjudication: `3/3`
- review rows needing adjudication: `0`
- review priorities: `{"high": 1, "low": 1, "medium": 1}`
- current failure labels: `{"infra_failure": 1, "none": 1, "proof_debugging": 1}`
- QA finding statuses: `{"unreviewed": 3}`

## Label Codebook

| label | description |
| --- | --- |
| `none` | attempt succeeded; no failure label applies |
| `library_search` | could not find the right Lean/Std/API lemma |
| `premise_selection` | found relevant lemmas but chose the wrong ones |
| `theorem_decomposition` | failed to split the proof into viable subgoals |
| `semantic_formalization` | formal statement or definition does not match the spec |
| `hidden_pin_failure` | visible build passes but hidden semantic check fails |
| `proof_debugging` | close proof but unresolved Lean errors remain |
| `codebase_navigation` | edited wrong file or missed required local context |
| `invariant_design` | wrong or insufficient invariant |
| `termination` | failed to prove termination or chose bad recursion structure |
| `timeout` | ran out of time with plausible progress |
| `reward_hack_attempt` | attempted a shortcut or used a banned construct |
| `grader_false_negative` | grader rejected a valid solution |
| `infra_failure` | container or tooling failure unrelated to the task |

## Review Rules

1. Review failed non-infra model rows before using failure-label distributions.
2. Mark `infra_failure`, `timeout`, or `reward_hack_attempt` before cognitive labels when applicable.
3. Use one primary label for the dominant failure and secondary labels only when the transcript has separable causes.
4. Record a short evidence excerpt and rationale; do not infer a label from task metadata alone.
5. If two reviewers disagree, set `adjudication_needed=true` in the template and resolve before reporting distributions.

## Review Queue

| priority | run id | task | scaffold | pass@k | current label | transcript | action |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| high | `anthropic-claude-sonnet-4-6-one-shot-1780206167:lt-201` | `lt-201` | one-shot | 0.0 | `proof_debugging` | `transcripts/anthropic-claude-sonnet-4-6-one-shot-1780206167/lt-201.jsonl` | Review failed non-infra model row and record rationale. |
| medium | `anthropic-claude-sonnet-4-6-one-shot-1780206126:lt-201` | `lt-201` | one-shot | 0.0 | `infra_failure` | `transcripts/anthropic-claude-sonnet-4-6-one-shot-1780206126/lt-201.jsonl` | Confirm this is an infrastructure failure and record whether the row should be rerun. |
| low | `anthropic-claude-sonnet-4-6-one-shot-1780206109:lt-001` | `lt-001` | one-shot | 1.0 | `none` | `transcripts/anthropic-claude-sonnet-4-6-one-shot-1780206109/lt-001.jsonl` | Confirm success transcript and keep primary label `none`. |

## Output Template

`data/failure_label_review_template.csv` contains one blank review row for each queued non-local run. It is intentionally blank so that committed review labels are not fabricated from existing run metadata.

## Completed Single-Review Rows

`data/failure_label_reviews.csv` records any completed single-review adjudication rows. These rows can be audited for transcript-evidence consistency, but they are not independent adjudication and should not be summarized as failure-mode prevalence.

| run id | primary label | confidence | adjudication needed |
| --- | --- | --- | --- |
| `anthropic-claude-sonnet-4-6-one-shot-1780206167:lt-201` | `proof_debugging` | high | false |
| `anthropic-claude-sonnet-4-6-one-shot-1780206126:lt-201` | `infra_failure` | high | false |
| `anthropic-claude-sonnet-4-6-one-shot-1780206109:lt-001` | `none` | high | false |
