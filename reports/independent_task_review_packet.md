# Independent Task Review Packet

This generated packet gives non-author Lean reviewers a structured way to review accepted_v0 task quality. It does not contain completed independent reviews and must not be cited as independent validation evidence.

## Summary

- accepted tasks requiring independent review: `6`
- family counts: `{"algorithm_correctness": 1, "direct_theorem_proving": 1, "informal_spec_to_formal": 1, "invariant_verification_ml_optimization": 1, "proof_repair_codebase": 1, "small_formal_library_construction": 1}`
- bucket counts: `{"T2": 5, "T3": 1}`
- accepted rows already carrying caveats: `3/6`
- automation-dominated accepted rows: `2/6`
- observation data file: `data/independent_task_reviews.csv`
- blank reviewer template: `data/independent_task_review_template.csv`
- review schema: `data/independent_task_review_schema.json`

## Review Rules

1. Use a reviewer who did not author, repair, or manually tune the task.
2. Review only public task assets, metadata, generated review cards, and generated summaries unless the reviewer is explicitly doing a hidden-grader audit.
3. Do not paste hidden reference proofs or hidden PinCheck contents into review notes.
4. Record whether hidden grader files were inspected. A public-only review and a hidden-grader audit support different claims.
5. Record whether the validation command was run and whether the reviewer actually solved the task.
6. Treat `keep_with_caveat`, `revise`, `downgrade`, and `reject` as useful outcomes, not failures of the review process.

Allowed template values:

- `prompt_clarity`: `clear`, `minor_ambiguity`, `major_ambiguity`, `uncertain`
- `time_bucket_assessment`: `too_low`, `plausible`, `too_high`, `uncertain`
- `diagnostic_value_assessment`: `high`, `medium`, `low`, `uncertain`
- `hidden_pin_assessment`: `adequate`, `needs_strengthening`, `not_applicable`, `uncertain`
- `wrong_submission_assessment`: `meaningful`, `too_signature_based`, `insufficient`, `uncertain`
- `benchmark_grade_recommendation`: `keep`, `keep_with_caveat`, `revise`, `downgrade`, `reject`

## Review Plan

| task | family | bucket | caveat | automation | pins | wrongs | one-shot | validation command |
| --- | --- | --- | --- | --- | --- | ---: | --- | --- |
| `lt-201` | proof_repair_codebase | T2 | accepted_core_with_caveat | true | semantic | 2 | maybe | `python scripts/validate_task.py tasks/dev/lt-201-multifile-cache-repair --submission <reviewer-solution.lean> --expect pass` |
| `lt-203` | informal_spec_to_formal | T2 | accepted_core_retained | false | semantic | 2 | maybe | `python scripts/validate_task.py tasks/dev/lt-203-exact-cover-spec --submission <reviewer-solution.lean> --expect pass` |
| `lt-202` | direct_theorem_proving | T2 | accepted_core_with_caveat | false | mixed | 2 | maybe | `python scripts/validate_task.py tasks/test/lt-202-mathlib-image-preimage --submission <reviewer-solution.lean> --expect pass` |
| `lt-204` | invariant_verification_ml_optimization | T2 | accepted_core_retained | false | semantic | 2 | maybe | `python scripts/validate_task.py tasks/test/lt-204-caplist-sum-invariant --submission <reviewer-solution.lean> --expect pass` |
| `lt-205` | small_formal_library_construction | T3 | accepted_core_retained | false | semantic | 2 | unlikely | `python scripts/validate_task.py tasks/test/lt-205-bag-count-library --submission <reviewer-solution.lean> --expect pass` |
| `lt-206` | algorithm_correctness | T2 | accepted_core_with_caveat | true | semantic | 2 | maybe | `python scripts/validate_task.py tasks/test/lt-206-partition-count-correctness --submission <reviewer-solution.lean> --expect pass` |

## Interpretation

This packet makes independent review collection operational, but the committed observation file is the authority for whether independent review has actually happened. Until real rows are committed and audited, accepted-task quality remains an internal-review claim with caveats.
