# Hidden Pin Coverage Audit

This generated audit makes hidden-check evidence more transparent. It statically counts theorem-shape checks and examples in each `hidden/PinCheck.lean`, then uses deterministic local QA transcripts to classify whether plausible wrong submissions failed during public compilation/proof checking or after reaching hidden pins.

A public-stage wrong failure can still be useful for proof-repair tasks, but it is weaker evidence for semantic-pin coverage than a wrong submission that compiles publicly and fails in `PinCheck.lean`.

## Summary

- pin coverage grades: `{"pins_not_exercised_by_wrongs": 5, "semantic_examples_exercised": 3, "semantic_pins_exercised": 3, "signature_plus_hidden_failure": 15}`
- accepted-core tasks with at least one hidden-pin wrong failure: `4/6`
- accepted-core wrong failures at public stage: `6`
- accepted-core wrong failures at hidden-pin stage: `5`

## Accepted Core Pin Coverage

| task | grade | shape checks | pos examples | neg examples | wrongs public | wrongs hidden | note |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `lt-201` | pins_not_exercised_by_wrongs | 4 | 6 | 0 | 2 | 0 | Accepted row needs a caveat: current wrong submissions fail before hidden pins run. |
| `lt-203` | semantic_pins_exercised | 4 | 3 | 2 | 0 | 2 | Accepted row has at least one wrong submission reaching hidden pins and nontrivial examples. |
| `lt-202` | pins_not_exercised_by_wrongs | 5 | 2 | 0 | 2 | 0 | Accepted row needs a caveat: current wrong submissions fail before hidden pins run. |
| `lt-204` | signature_plus_hidden_failure | 6 | 6 | 0 | 1 | 1 | Accepted row lacks negative hidden examples; review semantic pin strength before freeze. |
| `lt-205` | semantic_pins_exercised | 8 | 4 | 1 | 1 | 1 | Accepted row has at least one wrong submission reaching hidden pins and nontrivial examples. |
| `lt-206` | semantic_pins_exercised | 5 | 4 | 2 | 0 | 1 | Accepted row has at least one wrong submission reaching hidden pins and nontrivial examples. |

## Interpretation

`semantic_pins_exercised` means the task has positive and negative examples, at least one parameterized example, and at least one plausible wrong submission that reaches hidden pins. `semantic_examples_exercised` means positive/negative examples and hidden-pin wrong failures exist, but the examples are less structurally rich by this heuristic. `pins_not_exercised_by_wrongs` means local wrong submissions fail before hidden pins run, so the semantic-pin evidence is indirect.
