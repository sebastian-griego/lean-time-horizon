# Axiom Policy

The grader audits each submitted declaration listed in task metadata with
`#print axioms`.

Allowed axioms:

- `propext`
- `Classical.choice`
- `Quot.sound`

These are the standard Lean/Std axioms permitted for ordinary work in this
benchmark. Any other axiom dependency is a grading failure unless the task
metadata and this document are updated with a specific reason.

Forbidden source-level escape hatches are scanned before Lean runs. The common
ban list is implemented in `harness/forbidden_constructs.py`; task-specific
additional bans are listed in each `metadata.json` under `extra_forbidden`.

The current accepted tasks do not require adding task-specific axiom
allowances.
