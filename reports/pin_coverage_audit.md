# Hidden Pin Coverage Audit

This generated audit makes hidden-check evidence more transparent. It statically counts theorem-shape checks and examples in each `hidden/PinCheck.lean`, then uses deterministic local QA transcripts to classify whether plausible wrong submissions failed during public compilation/proof checking or after reaching hidden pins.

A public-stage wrong failure can still be useful for proof-repair tasks, but it is weaker evidence for semantic-pin coverage than a wrong submission that compiles publicly and fails in `PinCheck.lean`.

The audit now also classifies the submission surface. For proof-only fixed-statement tasks, a same-signature wrong proof that compiles publicly is structurally infeasible without forbidden constructs or disallowed axioms: Lean has already certified the fixed theorem. In those rows, hidden pins mainly guard theorem signatures and downstream usability rather than catching semantically wrong definitions.

## Summary

- pin coverage grades: `{"pins_not_exercised_by_wrongs": 5, "semantic_examples_exercised": 3, "semantic_pins_exercised": 4, "signature_plus_hidden_failure": 14}`
- accepted-core tasks with at least one hidden-pin wrong failure: `4/6`
- accepted-core wrong failures at public stage: `6`
- accepted-core wrong failures at hidden-pin stage: `6`
- accepted-core same-signature hidden-wrong feasibility: `{"feasible_via_definition_semantics": 4, "structurally_infeasible_for_same_signature_proof_wrongs": 2}`
- accepted-core hidden-pin roles: `{"semantic_positive_negative_guard": 4, "signature_and_downstream_use_guard": 2}`

## Accepted Core Pin Coverage

| task | grade | surface | feasibility | role | wrongs public | wrongs hidden | note |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| `lt-201` | pins_not_exercised_by_wrongs | proof_only_fixed_statements | structurally_infeasible_for_same_signature_proof_wrongs | signature_and_downstream_use_guard | 2 | 0 | Accepted proof-only row: same-signature semantic wrong proofs are structurally infeasible once Lean accepts the fixed theorem; hidden pins guard signatures and downstream use. |
| `lt-203` | semantic_pins_exercised | mutable_definitions_plus_theorems | feasible_via_definition_semantics | semantic_positive_negative_guard | 0 | 2 | Accepted row has at least one wrong submission reaching hidden pins and nontrivial examples. |
| `lt-202` | pins_not_exercised_by_wrongs | proof_only_fixed_statements | structurally_infeasible_for_same_signature_proof_wrongs | signature_and_downstream_use_guard | 2 | 0 | Accepted proof-only row: same-signature semantic wrong proofs are structurally infeasible once Lean accepts the fixed theorem; hidden pins guard signatures and downstream use. |
| `lt-204` | semantic_pins_exercised | mutable_definitions_plus_theorems | feasible_via_definition_semantics | semantic_positive_negative_guard | 1 | 1 | Accepted row has at least one wrong submission reaching hidden pins and nontrivial examples. |
| `lt-205` | semantic_pins_exercised | mutable_definitions_plus_theorems | feasible_via_definition_semantics | semantic_positive_negative_guard | 1 | 1 | Accepted row has at least one wrong submission reaching hidden pins and nontrivial examples. |
| `lt-206` | semantic_pins_exercised | mutable_definitions_plus_theorems | feasible_via_definition_semantics | semantic_positive_negative_guard | 0 | 2 | Accepted row has at least one wrong submission reaching hidden pins and nontrivial examples. |

## Interpretation

`semantic_pins_exercised` means the task has positive and negative examples, at least one parameterized example, and at least one plausible wrong submission that reaches hidden pins. `semantic_examples_exercised` means positive/negative examples and hidden-pin wrong failures exist, but the examples are less structurally rich by this heuristic. `pins_not_exercised_by_wrongs` means local wrong submissions fail before hidden pins run. That is a stronger concern for mutable-definition/formalization rows than for proof-only fixed-statement rows, where same-signature semantic wrong proofs are not a meaningful target.
