# Difficulty Audit

This audit separates mechanical signals from manual benchmark judgments. Mechanical signals are generated from the task files and hidden references; manual judgments live in each task's `metadata.json` and are regenerated into the CSV.

## Summary

- Accepted v0 core tasks: 9
- Calibration-only release tasks: 5
- Rejected tasks retained in archive: 12
- Candidate review pending: 0
- Accepted/calibration buckets: {'T1': 5, 'T2': 8, 'T3': 1}
- Accepted core families: {'algorithm_correctness': 1, 'direct_theorem_proving': 1, 'informal_spec_to_formal': 3, 'invariant_verification_ml_optimization': 1, 'proof_repair_codebase': 2, 'small_formal_library_construction': 1}

## Accepted v0 Core Tasks

| task | status | bucket | proof lines | hidden pins | wrongs | automation dominated | diagnostic value | review note |
| --- | --- | --- | ---: | --- | ---: | --- | --- | --- |
| lt-201 | accepted_v0 | T2 | 25 | semantic | 2 | true | high | accepted_v0: multi-file cache repair requires preserving Model.lean API semantics and proving batch count lemmas. |
| lt-203 | accepted_v0 | T2 | 30 | semantic | 2 | false | high | accepted_v0: spec-to-formal task with hidden pins rejecting vacuous, equality-only, and duplicate-sensitive interpretations. |
| lt-105 | accepted_v0 | T2 | 11 | semantic | 2 | true | medium_high | accepted_v0: lower-end T2 proof-repair task requiring generalized induction over a batched API and sum accounting; strengthened with semantic pins. |
| lt-107 | accepted_v0 | T2 | 10 | semantic | 2 | false | medium_high | accepted_v0: semantic formalization task where vacuous and nonempty-only specifications pass superficial lemmas but fail hidden pins. |
| lt-108 | accepted_v0 | T2 | 9 | semantic | 2 | false | medium_high | accepted_v0: recursive predicate formalization with hidden pins for dropped tail invariants and first-pair-only specifications. |
| lt-202 | accepted_v0 | T2 | 46 | mixed | 2 | false | medium_high | accepted_v0: Mathlib-adjacent theorem package requiring image/preimage API lookup, premise selection, and witness decomposition. |
| lt-204 | accepted_v0 | T2 | 36 | semantic | 2 | false | high | accepted_v0: optimizer-style invariant package with helper lemmas for cap bounds, list preservation, and sum monotonicity. |
| lt-205 | accepted_v0 | T3 | 42 | semantic | 2 | false | high | accepted_v0: T3 small library construction with dependent count lemmas and downstream BagEq reuse; expected to be hard one-shot. |
| lt-206 | accepted_v0 | T2 | 60 | semantic | 2 | true | high | accepted_v0: algorithm-correctness package with side predicates, length, and duplicate-sensitive count preservation. |

## Calibration-Only Release Tasks

| task | status | bucket | proof lines | hidden pins | wrongs | automation dominated | diagnostic value | review note |
| --- | --- | --- | ---: | --- | ---: | --- | --- | --- |
| lt-001 | calibration_only | T1 | 8 | semantic | 2 | true | medium | calibration_only: T1 list induction smoke row; retained to verify harness behavior, not counted as core benchmark difficulty. |
| lt-002 | calibration_only | T1 | 8 | semantic | 2 | true | medium | calibration_only: T1 Bool/list induction row; useful for lower-bound calibration and wrong-definition pins. |
| lt-003 | calibration_only | T1 | 11 | semantic | 2 | true | medium | calibration_only: small proof-repair shape retained as a codebase-navigation smoke row; too short for core benchmark status. |
| lt-004 | calibration_only | T1 | 5 | semantic | 2 | false | medium | calibration_only: compact semantic-formalization row retained to test vacuity and endpoint-only wrong specs. |
| lt-101 | calibration_only | T1 | 11 | semantic | 2 | true | medium | calibration_only: tail-recursive accumulator proof retained as a T1 calibration row; not core long-horizon material. |

## Rejected Archive

| task | status | bucket | proof lines | hidden pins | wrongs | automation dominated | diagnostic value | review note |
| --- | --- | --- | ---: | --- | ---: | --- | --- | --- |
| lt-005 | rejected_too_easy | T1 | 9 | semantic | 1 | false | low | rejected_too_easy: branch proof is dominated by unfolding, simp, and omega; weak diagnostic signal. |
| lt-102 | rejected_too_easy | T1 | 8 | mixed | 1 | true | low | rejected_too_easy: option/list proof is mostly cases, induction, simp, and omega. |
| lt-103 | rejected_too_easy | T1 | 8 | mixed | 1 | true | low | rejected_too_easy: tree-size proof is a short structural induction with arithmetic simplification. |
| lt-104 | rejected_duplicate | T1 | 11 | mixed | 1 | true | low | rejected_duplicate: overlaps strongly with lt-003 queue/stack size repair and is similarly short. |
| lt-106 | rejected_duplicate | T1 | 5 | mixed | 1 | false | low | rejected_duplicate: suffix version duplicates lt-004 prefix semantic-calibration role. |
| lt-109 | rejected_too_easy | T1 | 13 | semantic | 1 | false | low | rejected_too_easy: budget invariant is mostly nested if-splitting plus omega. |
| lt-110 | rejected_too_easy | T1 | 9 | semantic | 1 | false | low | rejected_too_easy: one arithmetic monotonicity fact, too small for core benchmark use. |
| lt-111 | rejected_too_easy | T2 | 9 | semantic | 1 | false | low | rejected_too_easy: interval clipping invariant is useful as a candidate idea but reference is omega-dominated. |
| lt-112 | rejected_too_easy | T1 | 15 | mixed | 1 | true | low | rejected_too_easy: structure wrapper proofs are cases/simp dominated. |
| lt-113 | rejected_too_easy | T2 | 20 | mixed | 1 | true | medium | rejected_too_easy: small library interface is useful but cases/simp dominated; not promoted to avoid inflating accepted count. |
| lt-114 | rejected_too_easy | T1 | 13 | mixed | 1 | true | low | rejected_too_easy: nearly all rfl; harness smoke only. |
| lt-115 | rejected_too_easy | T1 | 6 | mixed | 1 | false | low | rejected_too_easy: direct proof is one obvious library cancellation lemma. |

## Pending Candidates

_None._

## Method

The script counts reference proof lines, declarations, public files, public theorem/lemma statements, tactic-token profiles, Mathlib imports, multi-file context, hidden pin shape, and wrong-submission count. Manual fields record likely frontier one-shot solvability, human p50/p90, diagnostic value, and the keep/revise/reject rationale. Tasks dominated by `rfl`, `simp`, `omega`, or `cases` are only accepted as calibration unless their metadata records a specific diagnostic role.
