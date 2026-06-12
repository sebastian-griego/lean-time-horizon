# AGENTS.md

This repo is for building a Lean-based time-horizon evaluation benchmark.

Before doing substantive work, read the public project guidance:

- README.md
- docs/qa_checklist.md
- docs/axiom_policy.md

Treat those documents, task metadata, and generated audit reports as the source of truth. Private notes may exist locally, but they are not required to work from a fresh clone.

Optimize for a serious final benchmark, not a small demo. It is acceptable to generate many candidate tasks and prune aggressively.

The central standard is diagnostic validity. A task is valuable only if model failures are interpretable and grading is hard to game.

Do not commit secrets. Use environment variables for API keys.

Do not fake model results.

Do not expose hidden references or hidden semantic checks in public task assets.

Do not accept a task unless the reference solution passes, at least one plausible wrong solution fails, forbidden constructs are enforced, hidden checks behave correctly, metadata is complete, and the task is human-solvable in the stated time bucket.

Use docs/lean_eval_project_playbook.md for detailed task, QA, scaffold, metadata, and reporting standards.
