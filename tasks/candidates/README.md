# Candidate Tasks

The current `tasks/dev`, `tasks/test`, and `tasks/candidates` directories are
all treated as validated candidate pools, not final accepted benchmark splits.

This directory contains harder replacement candidates that pass local
validation but still need manual difficulty review before promotion. Candidate
designs rejected before Lean implementation are tracked in
`data/discarded_candidates.csv`.

Do not treat a task as accepted unless it has:

- `Prompt.md`
- `Task.lean`
- `metadata.json`
- `hidden/Reference.lean` or hidden semantic checks
- at least one wrong submission that fails
- successful `python scripts/validate_all.py`
- manual difficulty review recorded in metadata and `data/difficulty_audit.csv`
