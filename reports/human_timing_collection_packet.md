# Human Timing Collection Packet

This generated packet tells independent Lean reviewers how to collect timing evidence for accepted tasks. It does not contain measured human timings and must not be used as a substitute for `data/human_time_observations.csv` rows from real solves.

## Summary

- accepted tasks requiring timing: `6`
- bucket counts: `{"T2": 5, "T3": 1}`
- family counts: `{"algorithm_correctness": 1, "direct_theorem_proving": 1, "informal_spec_to_formal": 1, "invariant_verification_ml_optimization": 1, "proof_repair_codebase": 1, "small_formal_library_construction": 1}`
- minimum timing requirement before freeze: `one independent successful solve or second-review timing note per accepted task`
- observation data file: `data/human_time_observations.csv`
- blank reviewer template: `data/human_time_observations_template.csv`

## Collection Rules

1. Use a reviewer who did not author, repair, or manually tune the task.
2. Start timing after the reviewer opens the public prompt and public scaffold; stop timing at the first submission that passes local validation, or at timeout/abandonment.
3. Record active working minutes. For long tasks, exclude breaks but note split sessions in `notes`.
4. Record scaffold condition exactly: `one-shot`, `lookup`, or `lookup_unlimited`; also record whether lookup or compile/debug feedback was actually used.
5. Validate the final solution with the task-specific validation command before recording `validation_passed=true`.
6. Record prompt ambiguity, missing-context concerns, and any reason the metadata p50/p90 should change.

## Accepted Task Timing Plan

| task | bucket | p50/p90 | reviewer profile | condition | session cap | validation command |
| --- | --- | ---: | --- | --- | --- | --- |
| `lt-201` | T2 | 75/150 | Lean user who did not author or repair this task; record relevant Mathlib/verification background in notes | public prompt plus public scaffold; use one consistent condition per reviewer and record lookup/compile feedback use | 180 | `python scripts/validate_task.py tasks/dev/lt-201-multifile-cache-repair --submission <reviewer-solution.lean> --expect pass` |
| `lt-203` | T2 | 90/180 | Lean user who did not author or repair this task; record relevant Mathlib/verification background in notes | public prompt plus public scaffold; use one consistent condition per reviewer and record lookup/compile feedback use | 210 | `python scripts/validate_task.py tasks/dev/lt-203-exact-cover-spec --submission <reviewer-solution.lean> --expect pass` |
| `lt-202` | T2 | 90/180 | Lean user who did not author or repair this task; record relevant Mathlib/verification background in notes | public prompt plus public scaffold; use one consistent condition per reviewer and record lookup/compile feedback use | 210 | `python scripts/validate_task.py tasks/test/lt-202-mathlib-image-preimage --submission <reviewer-solution.lean> --expect pass` |
| `lt-204` | T2 | 100/200 | Lean user who did not author or repair this task; record relevant Mathlib/verification background in notes | public prompt plus public scaffold; use one consistent condition per reviewer and record lookup/compile feedback use | 230 | `python scripts/validate_task.py tasks/test/lt-204-caplist-sum-invariant --submission <reviewer-solution.lean> --expect pass` |
| `lt-205` | T3 | 150/300 | Lean user who did not author or repair this task; record relevant Mathlib/verification background in notes | public prompt plus public scaffold; read-only lookup allowed only if recorded; compile/debug feedback allowed only if recorded | 330 | `python scripts/validate_task.py tasks/test/lt-205-bag-count-library --submission <reviewer-solution.lean> --expect pass` |
| `lt-206` | T2 | 100/210 | Lean user who did not author or repair this task; record relevant Mathlib/verification background in notes | public prompt plus public scaffold; use one consistent condition per reviewer and record lookup/compile feedback use | 240 | `python scripts/validate_task.py tasks/test/lt-206-partition-count-correctness --submission <reviewer-solution.lean> --expect pass` |

## Observation Row Guidance

`reviewer_id_hash` should be a stable pseudonymous hash, not a name or email. `outcome` should use the values allowed by `data/human_time_observations_schema.json`: `solved`, `completed`, `pass`, `partial`, `unsolved`, `timeout`, or `abandoned`. The additional template fields are collection aids; the canonical audit currently reads the schema-required columns and preserves the rest as reviewer notes.
