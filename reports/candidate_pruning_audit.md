# Candidate Pruning Audit

This generated audit makes the v0.1 pruning decision visible for every tracked task. It joins metadata, difficulty-audit signals, and the task-quality matrix so the small accepted core is explained by task-quality review rather than by directory placement or model performance.

The audit is not a new acceptance decision. `metadata.json`, `reports/accepted_task_review.md`, and the validation scripts remain authoritative.

## Summary

- acceptance statuses: `{"accepted_v0": 6, "calibration_only": 8, "rejected_duplicate": 2, "rejected_too_easy": 10}`
- pruning decisions: `{"accepted_core": 6, "rejected_archive": 12, "retained_calibration_only": 8}`
- accepted-core rate: `6/26`
- calibration-only rows: `8`
- rejected archive rows: `12`
- rejected rows flagged too easy or automation dominated: `11/12`

## Family By Status

| family | accepted_v0 | calibration_only | rejected_duplicate | rejected_too_easy |
| --- | ---: | ---: | ---: | ---: |
| `algorithm_correctness` | 1 | 3 | 0 | 2 |
| `direct_theorem_proving` | 1 | 0 | 0 | 1 |
| `informal_spec_to_formal` | 1 | 3 | 1 | 0 |
| `invariant_verification_ml_optimization` | 1 | 0 | 0 | 4 |
| `proof_repair_codebase` | 1 | 2 | 1 | 0 |
| `small_formal_library_construction` | 1 | 0 | 0 | 3 |

## Decision Ledger

| task | status | bucket | proof lines | automation | one-shot | pins | wrongs | core decision basis |
| --- | --- | --- | ---: | --- | --- | --- | ---: | --- |
| `lt-001` | calibration_only | T1 | 8 | true | likely | semantic | 2 | Excluded from accepted-core performance claims and retained only for lower-bound calibration, harness regression, or simple semantic-pin checks. |
| `lt-002` | calibration_only | T1 | 8 | true | likely | semantic | 2 | Excluded from accepted-core performance claims and retained only for lower-bound calibration, harness regression, or simple semantic-pin checks. |
| `lt-003` | calibration_only | T1 | 11 | true | likely | semantic | 2 | Excluded from accepted-core performance claims and retained only for lower-bound calibration, harness regression, or simple semantic-pin checks. |
| `lt-004` | calibration_only | T1 | 5 | false | likely | semantic | 2 | Excluded from accepted-core performance claims and retained only for lower-bound calibration, harness regression, or simple semantic-pin checks. |
| `lt-005` | rejected_too_easy | T1 | 9 | false | very_likely | semantic | 1 | Excluded from release/core claims because the proof surface is too short, too local, automation dominated, or likely one-shot solvable. |
| `lt-201` | accepted_v0 | T2 | 25 | true | maybe | semantic | 2 | Counts toward accepted-core v0.1 task set, with any caveat recorded in the review note. |
| `lt-203` | accepted_v0 | T2 | 30 | false | maybe | semantic | 2 | Counts toward accepted-core v0.1 task set, with any caveat recorded in the review note. |
| `lt-101` | calibration_only | T1 | 11 | true | likely | semantic | 2 | Excluded from accepted-core performance claims and retained only for lower-bound calibration, harness regression, or simple semantic-pin checks. |
| `lt-102` | rejected_too_easy | T1 | 8 | true | very_likely | mixed | 1 | Excluded from release/core claims because the proof surface is too short, too local, automation dominated, or likely one-shot solvable. |
| `lt-103` | rejected_too_easy | T1 | 8 | true | likely | mixed | 1 | Excluded from release/core claims because the proof surface is too short, too local, automation dominated, or likely one-shot solvable. |
| `lt-104` | rejected_duplicate | T1 | 11 | true | likely | mixed | 1 | Excluded from release/core claims because it duplicates an already retained calibration or capability role. |
| `lt-105` | calibration_only | T1 | 11 | true | likely | semantic | 2 | Excluded from accepted-core performance claims and retained only for lower-bound calibration, harness regression, or simple semantic-pin checks. |
| `lt-106` | rejected_duplicate | T1 | 5 | false | likely | mixed | 1 | Excluded from release/core claims because it duplicates an already retained calibration or capability role. |
| `lt-107` | calibration_only | T1 | 10 | false | likely | semantic | 2 | Excluded from accepted-core performance claims and retained only for lower-bound calibration, harness regression, or simple semantic-pin checks. |
| `lt-108` | calibration_only | T1 | 9 | false | likely | semantic | 2 | Excluded from accepted-core performance claims and retained only for lower-bound calibration, harness regression, or simple semantic-pin checks. |
| `lt-109` | rejected_too_easy | T1 | 13 | false | very_likely | semantic | 1 | Excluded from release/core claims because the proof surface is too short, too local, automation dominated, or likely one-shot solvable. |
| `lt-110` | rejected_too_easy | T1 | 9 | false | very_likely | semantic | 1 | Excluded from release/core claims because the proof surface is too short, too local, automation dominated, or likely one-shot solvable. |
| `lt-111` | rejected_too_easy | T2 | 9 | false | likely | semantic | 1 | Excluded from release/core claims because the proof surface is too short, too local, automation dominated, or likely one-shot solvable. |
| `lt-112` | rejected_too_easy | T1 | 15 | true | very_likely | mixed | 1 | Excluded from release/core claims because the proof surface is too short, too local, automation dominated, or likely one-shot solvable. |
| `lt-113` | rejected_too_easy | T2 | 20 | true | likely | mixed | 1 | Excluded from release/core claims because the proof surface is too short, too local, automation dominated, or likely one-shot solvable. |
| `lt-114` | rejected_too_easy | T1 | 13 | true | very_likely | mixed | 1 | Excluded from release/core claims because the proof surface is too short, too local, automation dominated, or likely one-shot solvable. |
| `lt-115` | rejected_too_easy | T1 | 6 | false | very_likely | mixed | 1 | Excluded from release/core claims because the proof surface is too short, too local, automation dominated, or likely one-shot solvable. |
| `lt-202` | accepted_v0 | T2 | 46 | false | maybe | mixed | 2 | Counts toward accepted-core v0.1 task set, with any caveat recorded in the review note. |
| `lt-204` | accepted_v0 | T2 | 36 | false | maybe | semantic | 2 | Counts toward accepted-core v0.1 task set, with any caveat recorded in the review note. |
| `lt-205` | accepted_v0 | T3 | 42 | false | unlikely | semantic | 2 | Counts toward accepted-core v0.1 task set, with any caveat recorded in the review note. |
| `lt-206` | accepted_v0 | T2 | 60 | true | maybe | semantic | 2 | Counts toward accepted-core v0.1 task set, with any caveat recorded in the review note. |

## Interpretation

Accepted rows are the only rows eligible for accepted-core task-quality summaries. Calibration rows may be exported for lower-bound and harness checks but stay out of accepted-core performance claims. Rejected rows are retained in the repository only as pruning evidence and are not exported as public release tasks. The current accepted core remains below the target benchmark size because many candidates were too short, duplicated another role, or were likely to be solved one-shot.
