# lt-204: Verify capped-list optimizer invariants

Edit `Task.lean` only. `capList cap xs` applies a one-dimensional projection to every coordinate of a simplified optimizer state.

Prove the helper lemmas and final invariant theorem. The final theorem says the capped state has the same length, every coordinate is within the cap, and the total sum cannot increase.

Do not change declaration names, theorem statements, or imports. Helper lemmas may be added.

Forbidden constructs include `sorry`, `admit`, `axiom`, `constant`, `opaque`, `unsafe`, custom syntax or macro elaboration, `run_cmd`, `run_tac`, `Lean.addDecl`, `#eval`, and `#exit`.
