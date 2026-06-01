# Taiga Packaging Scaffold

This directory is a hosted-QA packaging scaffold, not hosted QA evidence.

It provides:

- `Dockerfile`: a candidate container image that installs the Lean toolchain,
  builds the repo, exports `public_tasks`, and starts the wrapper.
- `mcp_server.py`: a small adapter exposing `setup_problem` and `grade_problem`
  functions that delegate grading to `scripts/validate_task.py`.
- `problems_metadata.template.json`: generated Taiga problems-metadata with a
  placeholder image value.

The scaffold is not hidden-material-safe by itself. The Dockerfile copies the
repo so the Lean grader can see hidden checks, and hosted filesystem tools must
not be allowed to read those files. Before upload, either split public task files
from grader-private material or enforce and test file permissions that keep
hidden references and `hidden/PinCheck.lean` inaccessible to the model tools.

Before using this as hosted evidence:

1. Build and upload an image, then replace
   `REPLACE_WITH_IMMUTABLE_TAIGA_IMAGE_DIGEST` with the immutable uploaded image
   digest. Do not use `latest`.
2. Run Taiga preflight or Stage 1 checks on the exact problem versions.
3. Prove hidden-material isolation with the hosted tool configuration and Env
   Linter. The model should only see `public_tasks` material copied into
   `/workdir/problems/<task_id>`.
4. Run Transcript Health or Full Env QA and Env Linter.
5. Commit hosted problem-version IDs, snapshot mapping, findings, dispositions,
   and any rebuttals in `data/hosted_qa_results.csv` and `reports/hosted_qa.md`.

Until those rows exist, the benchmark report must continue to say that hosted QA
is missing.
