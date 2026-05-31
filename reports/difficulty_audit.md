# Difficulty Audit

The original 20 tasks are now treated as candidates, not final accepted tasks. This audit applies the playbook criterion that diagnostic validity matters more than raw difficulty.

## Summary

- Original candidate tasks audited: 20
- Reject or downgrade to smoke/calibration: 8
- T0/T1 calibration only: 9
- Borderline candidates needing stronger review: 3
- New replacement candidates present: 5

## Original Candidate Decisions

| task | recommendation | bucket | proof lines | tactic profile | simp/omega/rfl/cases dominant | hidden pins | model one-shot | notes |
| --- | --- | --- | ---: | --- | --- | --- | --- | --- |
| lt-001 | calibration | T1 | 8 | `{"induction": 1, "simp": 2}` | true | yes | likely | Short induction; mostly simp/arithmetic cleanup. |
| lt-002 | calibration | T1 | 8 | `{"cases": 1, "induction": 1, "simp": 2}` | true | yes | likely | Short induction plus Bool cases; useful smoke row. |
| lt-003 | calibration | T1 | 11 | `{"induction": 1, "simp": 3}` | true | yes | likely | Codebase-repair shape, but the proof is a small generalized induction. |
| lt-004 | calibration | T1 | 5 | `{"exact": 2, "simp": 2}` | false | yes | likely | Semantic formalization row, but the target relation is very small. |
| lt-005 | reject_or_T0 | T0 | 9 | `{"omega": 1, "simp": 1, "split": 2, "unfold": 2}` | false | yes | very_likely | Solved by unfolding conditionals and omega/simp; weak long-horizon signal. |
| lt-101 | calibration | T1 | 11 | `{"induction": 1, "simp": 2}` | true | yes | likely | Accumulator invariant gives some decomposition value but still short. |
| lt-102 | reject_or_T0 | T0 | 8 | `{"cases": 1, "induction": 1, "omega": 1, "simp": 2}` | true | yes | very_likely | Option case split with simp/omega; too easy for final set. |
| lt-103 | calibration | T1 | 8 | `{"induction": 1, "simp": 2}` | true | yes | likely | Tree induction and arithmetic normalization; good calibration only. |
| lt-104 | calibration | T1 | 11 | `{"induction": 1, "simp": 3}` | true | yes | likely | Proof-repair shape overlaps heavily with lt-003. |
| lt-105 | borderline_candidate | T1 | 11 | `{"induction": 1, "rfl": 1, "simp": 2}` | true | yes | maybe | Recursive API repair has some value but is still mainly induction+simp. |
| lt-106 | calibration | T1 | 5 | `{"exact": 2, "simp": 2}` | false | yes | likely | Suffix formalization is semantically pinned but too compact. |
| lt-107 | borderline_candidate | T1 | 10 | `{"exact": 1, "intro": 2, "simp": 1}` | false | yes | maybe | Membership implication spec has semantic value; proof still short. |
| lt-108 | borderline_candidate | T1 | 9 | `{"exact": 1}` | false | yes | maybe | Recursive predicate design is useful; public lemmas are constructor-level. |
| lt-109 | reject_or_T0 | T0 | 13 | `{"omega": 2, "simp": 1, "split": 2, "unfold": 3}` | false | yes | very_likely | Mostly nested if split plus omega. |
| lt-110 | reject_or_T0 | T0 | 9 | `{"exact": 1, "omega": 1, "unfold": 2}` | false | yes | very_likely | Natural subtraction invariant is one arithmetic fact and transitivity. |
| lt-111 | reject_or_T1 | T1 | 9 | `{"omega": 2, "split": 4, "unfold": 2}` | false | yes | likely | Nested branch invariant, but reference is dominated by omega. |
| lt-112 | reject_or_T0 | T0 | 15 | `{"cases": 5, "simp": 3}` | true | yes | very_likely | Structure cases and simp; not final-benchmark material. |
| lt-113 | calibration | T1 | 20 | `{"cases": 7, "simp": 4}` | true | yes | likely | Small library wrapper has multiple lemmas but proofs are cases/simp. |
| lt-114 | reject_or_T0 | T0 | 13 | `{"rfl": 4}` | true | yes | very_likely | Nearly all rfl; keep only as harness smoke if needed. |
| lt-115 | reject_or_T0 | T0 | 6 | `{"exact": 1}` | false | yes | very_likely | One obvious library lemma applied twice. |

## T0/T1 Calibration-Only Items

`lt-001`, `lt-002`, `lt-003`, `lt-004`, `lt-101`, `lt-103`, `lt-104`, `lt-106`, `lt-113`

## Reject Or Smoke-Only Items

`lt-005`, `lt-102`, `lt-109`, `lt-110`, `lt-111`, `lt-112`, `lt-114`, `lt-115`

## Borderline Items Needing Stronger Review

`lt-105`, `lt-107`, `lt-108`

## Replacement Candidate Notes

- `lt-201`: multi-file cache touchAll proof repair (proof_repair_codebase), proof lines 25, profile `{"cases": 2, "induction": 2, "simp": 6}`; library_search=false, decomposition=true, semantic_formalization=false, proof_debugging=true, codebase_navigation=true, invariant_design=false, hidden_pins=yes, one_shot=maybe. Multi-file repair requires reading Model.lean, preserving API meaning, and proving two generalized batch lemmas.
- `lt-202`: Mathlib set image/preimage package (direct_theorem_proving), proof lines 46, profile `{"constructor": 1, "exact": 9, "intro": 17, "rcases": 6, "rfl": 1, "rw": 3}`; library_search=true, decomposition=true, semantic_formalization=false, proof_debugging=false, codebase_navigation=false, invariant_design=false, hidden_pins=yes, one_shot=maybe. Mathlib set/function package requires API fluency and witness merging; lookup sensitivity should be high.
- `lt-203`: formalize exact list coverage modulo multiplicity (informal_spec_to_formal), proof lines 30, profile `{"constructor": 1, "exact": 7, "intro": 6, "rcases": 2, "rfl": 1, "simp": 2}`; library_search=false, decomposition=true, semantic_formalization=true, proof_debugging=true, codebase_navigation=false, invariant_design=false, hidden_pins=yes, one_shot=maybe. Spec-to-formalization task uses hidden semantic pins to reject vacuous or duplicate-sensitive definitions.
- `lt-204`: capped-list optimizer invariant package (invariant_verification_ml_optimization), proof lines 36, profile `{"exact": 2, "induction": 3, "omega": 2, "simp": 6, "split": 2, "unfold": 2}`; library_search=false, decomposition=true, semantic_formalization=false, proof_debugging=false, codebase_navigation=false, invariant_design=true, hidden_pins=yes, one_shot=maybe. Invariant package requires several helper lemmas before the final capped-list invariant.
- `lt-205`: count-based bag library construction (small_formal_library_construction), proof lines 42, profile `{"exact": 2, "induction": 1, "intro": 4, "omega": 1, "rfl": 2, "rw": 3, "simp": 6}`; library_search=false, decomposition=true, semantic_formalization=false, proof_debugging=false, codebase_navigation=false, invariant_design=false, hidden_pins=yes, one_shot=maybe. Small library construction requires a coherent count-based bag interface across 5-10 lemmas.

## Method

The script counts reference proof lines and tactic-token profiles mechanically, then combines those counts with manual review fields for diagnostic value, likely frontier one-shot success, and final recommendation. Rows dominated by `rfl`, `simp`, `omega`, or `cases`, or by one obvious library lemma, are downgraded unless they serve a narrow calibration purpose.
