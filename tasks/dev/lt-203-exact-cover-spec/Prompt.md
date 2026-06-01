# lt-203: Formalize exact list coverage

Edit `Task.lean` only. Replace the placeholder body of `CoversExactly` with a meaningful formalization of:

Two lists contain exactly the same values when an arbitrary value is a member of the first list if and only if it is a member of the second list. Multiplicity is intentionally ignored.

Then prove the public reflexivity, cons congruence, symmetry, and transitivity lemmas. Do not change declaration names, theorem statements, or imports. Helper lemmas may be added.

Forbidden constructs include `sorry`, `admit`, `axiom`, `constant`, `opaque`, `unsafe`, custom syntax or macro elaboration, `run_cmd`, `run_tac`, `Lean.addDecl`, `#eval`, and `#exit`.
