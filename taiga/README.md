# Taiga Packaging Scaffold

This directory is a hosted-QA packaging scaffold, not hosted QA evidence.

It provides:

- `Dockerfile`: a candidate container image that installs the Lean toolchain,
  builds the repo, exports `public_tasks`, and starts the wrapper.
- `mcp_server.py`: a small adapter exposing `setup_problem` and `grade_problem`
  functions. In hosted mode it grades against public task files plus an
  in-memory hidden-pin bundle generated at image build time.
- `problems_metadata.template.json`: generated Taiga problems-metadata with a
  placeholder image value.

The scaffold mitigates, but does not by itself prove, hidden-material isolation.
During image build the Dockerfile generates a private hidden-pin bundle, removes
`tasks/` from the final filesystem, and the MCP server deletes the bundle file
after loading it into memory. Hosted filesystem tools still need preflight/Env
Linter evidence showing that the model can only read the public workdir and not
grader-private state.

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
