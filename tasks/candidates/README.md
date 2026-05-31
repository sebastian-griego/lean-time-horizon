# Candidate Tasks

Accepted tasks live under `tasks/dev` and `tasks/test`.

This directory is reserved for candidate tasks that have not passed the full
local acceptance gate. Candidate designs rejected before Lean implementation
are tracked in `data/discarded_candidates.csv`.

Do not point model runs at this directory unless the task is promoted and gets:

- `Prompt.md`
- `Task.lean`
- `metadata.json`
- `hidden/Reference.lean` or hidden semantic checks
- at least one wrong submission that fails
- successful `python scripts/validate_all.py`
