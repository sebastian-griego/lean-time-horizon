# Task Quality Matrix

This generated matrix joins task metadata with the difficulty audit so reviewers can inspect one row per task without treating directory placement as acceptance. It is not an acceptance decision by itself; `metadata.json`, `reports/accepted_task_review.md`, and the validation scripts remain authoritative.

## Status Counts

- release roles: `{"accepted_core": 6, "calibration_release": 8, "rejected_archive": 12}`
- benchmark-grade statuses: `{"accepted_core_retained": 3, "accepted_core_with_caveat": 3, "calibration_only": 8, "rejected_archive": 12}`
- accepted-core caveat rows: `3/6`
- accepted-core automation-dominated rows: `2/6`
- accepted-core likely/very-likely one-shot rows: `0/6`

## Accepted Core Matrix

| task | grade | family | bucket | proof lines | automation | pins | wrongs | one-shot | diagnostic | next review action |
| --- | --- | --- | --- | ---: | --- | --- | ---: | --- | --- | --- |
| `lt-201` | accepted_core_with_caveat | proof_repair_codebase | T2 | 25 | yes | semantic | 2 | maybe | high | Retain in v0.1 only with the recorded caveat; collect independent human timing, full scaffold sweep evidence, and external QA before freeze. |
| `lt-203` | accepted_core_retained | informal_spec_to_formal | T2 | 30 | no | semantic | 2 | maybe | high | Collect independent timing, hosted QA, and accepted-core scaffold/model evidence before benchmark freeze. |
| `lt-202` | accepted_core_with_caveat | direct_theorem_proving | T2 | 46 | no | mixed | 2 | maybe | medium_high | Retain in v0.1 only with the recorded caveat; collect independent human timing, full scaffold sweep evidence, and external QA before freeze. |
| `lt-204` | accepted_core_retained | invariant_verification_ml_optimization | T2 | 36 | no | semantic | 2 | maybe | high | Collect independent timing, hosted QA, and accepted-core scaffold/model evidence before benchmark freeze. |
| `lt-205` | accepted_core_retained | small_formal_library_construction | T3 | 42 | no | semantic | 2 | unlikely | high | Independently time at least one human solve and run the planned scaffold sweep before using this as long-horizon evidence. |
| `lt-206` | accepted_core_with_caveat | algorithm_correctness | T2 | 60 | yes | semantic | 2 | maybe | high | Retain in v0.1 only with the recorded caveat; collect independent human timing, full scaffold sweep evidence, and external QA before freeze. |

## Calibration Matrix

| task | family | bucket | proof lines | automation | pins | wrongs | one-shot | diagnostic role |
| --- | --- | --- | ---: | --- | --- | ---: | --- | --- |
| `lt-001` | algorithm_correctness | T1 | 8 | yes | semantic | 2 | likely | calibration_only: T1 list induction smoke row; retained to verify harness behavior, not counted as core benchmark difficulty. |
| `lt-002` | algorithm_correctness | T1 | 8 | yes | semantic | 2 | likely | calibration_only: T1 Bool/list induction row; useful for lower-bound calibration and wrong-definition pins. |
| `lt-003` | proof_repair_codebase | T1 | 11 | yes | semantic | 2 | likely | calibration_only: small proof-repair shape retained as a codebase-navigation smoke row; too short for core benchmark status. |
| `lt-004` | informal_spec_to_formal | T1 | 5 | no | semantic | 2 | likely | calibration_only: compact semantic-formalization row retained to test vacuity and endpoint-only wrong specs. |
| `lt-101` | algorithm_correctness | T1 | 11 | yes | semantic | 2 | likely | calibration_only: tail-recursive accumulator proof retained as a T1 calibration row; not core long-horizon material. |
| `lt-105` | proof_repair_codebase | T1 | 11 | yes | semantic | 2 | likely | calibration_only: same-signature semantic wrongs are useful, but the reference proof is short and automation-dominated; T2/core status was too generous. |
| `lt-107` | informal_spec_to_formal | T1 | 10 | no | semantic | 2 | likely | calibration_only: hidden pins catch vacuous and nonempty-only specs, but the formalization surface is too compact for accepted core status. |
| `lt-108` | informal_spec_to_formal | T1 | 9 | no | semantic | 2 | likely | calibration_only: good semantic pins for dropped-tail and first-pair-only definitions, but the proof surface is too small for core benchmark status. |

## Rejected Archive Summary

- rejected rows: `12`
- rejection statuses: `{"rejected_duplicate": 2, "rejected_too_easy": 10}`
- rejected families: `{"algorithm_correctness": 2, "direct_theorem_proving": 1, "informal_spec_to_formal": 1, "invariant_verification_ml_optimization": 4, "proof_repair_codebase": 1, "small_formal_library_construction": 3}`
- automation-dominated rejected rows: `6`

## Interpretation

Rows marked `accepted_core_with_caveat` are retained in v0.1 only because their task context still gives diagnostic signal despite automation or finite-pin limitations. Calibration rows should not enter benchmark performance claims. Rejected rows are kept to make pruning decisions auditable.
