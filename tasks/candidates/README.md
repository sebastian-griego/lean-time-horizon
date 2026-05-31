# Candidate Tasks

This directory is reserved for tasks whose metadata status is
`candidate_review_pending`. Accepted v0.1 tasks have been promoted into
`tasks/dev` or `tasks/test`; rejected implemented tasks remain in their original
split with an explicit rejected status in metadata.

Candidate designs rejected before Lean implementation are tracked in
`data/discarded_candidates.csv`.

Do not treat a task as accepted unless it has:

- `Prompt.md`
- `Task.lean`
- `metadata.json`
- `hidden/Reference.lean` or hidden semantic checks
- at least two wrong submissions if the task is promoted to `accepted_v0`
- successful `python scripts/validate_all.py`
- manual difficulty review recorded in metadata and `data/difficulty_audit.csv`
