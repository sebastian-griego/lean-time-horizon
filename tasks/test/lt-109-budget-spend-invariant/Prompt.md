# lt-109: Verify a bounded budget spend operation

Edit `Task.lean` only. `spend budget cost` subtracts `cost` when the budget is large enough and otherwise leaves the budget unchanged.

Prove that spending never increases the budget, that spending the exact budget leaves zero, and that a zero budget remains zero. Do not change declaration names, theorem statements, or imports.

Forbidden constructs include `sorry`, `admit`, `axiom`, `constant`, `opaque`, `unsafe`, custom syntax or macro elaboration, `run_cmd`, `run_tac`, `Lean.addDecl`, `#eval`, and `#exit`.
