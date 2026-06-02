# Reviewer Reproduction Packet

This generated packet converts the local validation and report-generation surface into a reviewer workflow. It is not new model evidence; it states which commands reproduce local evidence, which external evidence is still missing, and how failures should be interpreted.

## Summary

- steps: `22`
- phases: `{"external_evidence": 3, "local_replay": 19}`
- statuses: `{"blocked_external_evidence": 3, "ready": 19}`
- local replay steps ready: `19/19`
- local replay problem rows: `0`
- external evidence rows still blocked: `3`

## Reviewer Workflow

Run the local replay steps in order after dependency setup. Treat any nonzero exit code, missing expected artifact, or local-gate coverage gap as a report-blocking finding until repaired. External-evidence rows intentionally remain blocked in v0.1; do not replace them with local smoke rows or synthetic data.

## Step Table

| step | phase | status | command | supports | limitation |
| --- | --- | --- | --- | --- | --- |
| `mathlib_cache_get` | local_replay | ready | `lake exe cache get` | Mathlib dependency artifacts can be materialized before tasks importing Mathlib are validated. | This is local dependency-cache evidence; hosted environments may use a different cache path. |
| `toolchain_build` | local_replay | ready | `lake build` | Lean project and imported task libraries build in the configured toolchain. | This is local build evidence; it is not hosted QA or provider-sandbox evidence. |
| `task_validation` | local_replay | ready | `python scripts/validate_all.py` | Reference solutions pass and plausible wrong submissions fail for every task under the local grader. | This validates local hidden checks and wrong submissions; it does not prove model performance. |
| `difficulty_review` | local_replay | ready | `python scripts/audit_difficulty.py` | Accepted and calibration rows have mechanical proof-profile evidence and manual difficulty-review fields. | The audit combines static heuristics with human judgment; it is not independent human timing. |
| `local_qa_rows` | local_replay | ready | `python scripts/record_local_qa_results.py` | Local QA rows are replayable validation evidence for references and plausible wrong submissions. | Local QA rows must stay excluded from model-performance estimates. |
| `run_integrity` | local_replay | ready | `python scripts/audit_run_integrity.py` | run_results rows are internally consistent with transcripts, pass@k arithmetic, and failure labels. | Passing integrity checks do not imply adequate provider sample size. |
| `analysis_decision_register` | local_replay | ready | `python scripts/generate_analysis_decision_register.py` | The planned model analysis has explicit preregistered inclusion, endpoint, coverage, subgroup, failure-label, timing, and freeze decisions. | The register fixes analysis rules but does not create provider rows or unlock performance claims. |
| `evidence_strength_matrix` | local_replay | ready | `python scripts/generate_evidence_strength_matrix.py` | Major report claims are graded by evidence type so local, provider-smoke, independent-review, hosted-QA, and freeze evidence are not conflated. | The matrix classifies evidence strength; it does not create independent review, exact-k provider sweeps, hosted QA, or freeze evidence. |
| `peer_review_matrix` | local_replay | ready | `python scripts/generate_peer_review_matrix.py` | Skeptical reviewer questions, defensible answers, residual risks, and upgrade evidence are synthesized from committed audits. | The matrix is a synthesis of existing evidence and does not resolve blocked external-evidence gaps. |
| `model_sweep_coverage` | local_replay | ready | `python scripts/audit_model_sweep_coverage.py` | Planned accepted-core task/scaffold/pass@k cells are mapped to committed provider rows with smoke-only cells separated from pass@k-ready cells. | This audit does not create new model evidence; it only classifies coverage of existing rows. |
| `passk_claim_boundaries` | local_replay | ready | `python scripts/audit_passk_claim_boundaries.py` | Report artifacts keep exact-k pass@k-ready cells separate from smoke-only or missing planned cells. | This audit prevents wording drift; it does not create additional provider attempts or performance evidence. |
| `grader_hardening` | local_replay | ready | `python scripts/audit_grader_hardening.py` | Forbidden-construct scanning, axiom allowlists, grader ordering, and validation-command coverage are reviewable. | The scanner remains lexical source scanning, not a complete Lean parser. |
| `public_export` | local_replay | ready | `python scripts/export_public_tasks.py --out public_tasks` | Public release assets can be exported without hidden references or wrong submissions. | The export is a local directory snapshot, not a hosted problem version. |
| `public_export_validation` | local_replay | ready | `python scripts/validate_public_export.py --out public_tasks` | The public export omits hidden/wrong directories and exported Lean files compile. | This does not run Taiga Full Env QA or Env Linter. |
| `security_leakage` | local_replay | ready | `python scripts/audit_security_leakage.py` | Committed/exported artifacts can be checked for credential patterns, hidden public-export paths, and verbatim hidden Lean content leakage. | This scans committed/exported artifacts only; it does not inspect private untracked local environment files or replace hosted QA. |
| `taiga_metadata_template` | local_replay | ready | `python scripts/generate_taiga_problem_metadata.py` | The public release task set can be rendered into a Taiga problems-metadata template. | The template uses placeholder image values; it is not a hosted problem-version record or QA result. |
| `report_regeneration` | local_replay | ready | `python scripts/generate_report.py` | The main report, appendix, and descriptive figures regenerate from committed CSV inputs. | Generated report text can still overclaim unless claim-conformance checks pass. |
| `claim_and_shape_audits` | local_replay | ready | `python scripts/audit_report_claim_conformance.py; python scripts/audit_report_shape.py` | The report keeps blocked claims blocked and answers the playbook report-shape questions where evidence allows. | Text audits are guardrails, not substitutes for substantive external evidence. |
| `validation_manifest` | local_replay | ready | `python scripts/write_validation_manifest.py --public-export public_tasks; python scripts/audit_validation_manifest.py` | The local validation gate, artifact hashes, public-export summary, and dirty-status policy are recorded. | The manifest intentionally omits self-referential report hashes and is not clean-checkout proof. |
| `provider_sweep` | external_evidence | blocked_external_evidence | `python scripts/run_model_sweep.py --provider PROVIDER --model MODEL --scaffold SCAFFOLD --attempts 10 --acceptance-status accepted_v0` | Future pass@k, scaffold-effect, and frontier/open-model claims. | Requires external provider runners and API keys kept only in environment variables. |
| `independent_human_timing` | external_evidence | blocked_external_evidence | `Fill data/human_time_observations.csv from non-author timed solves` | Future calibrated time-horizon bucket and human-time trend claims. | Must not be inferred from model pass rates or author expectations. |
| `hosted_qa` | external_evidence | blocked_external_evidence | `Run hosted Full Env QA and Env Linter on exact final problem versions` | Future hosted-QA-cleared and locked-benchmark claims. | This repository currently records readiness only, not hosted QA pass evidence. |

## Interpretation

`ready` means the command and expected committed artifacts are present and the command is covered by the local regeneration gate where applicable. `blocked_external_evidence` means the step requires real provider runs, independent human timing, or hosted QA before the corresponding stronger claim can be made.
