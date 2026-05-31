# lt-105: Repair counter increment proofs after batched increments

Edit `Task.lean` only. The counter API now supports incrementing by each amount in a list. Repair the proof that the final counter value increases by the sum of the requested increments.

Do not change declaration names, theorem statements, imports, or the counter representation. You may add helper lemmas in `Task.lean`.

Forbidden constructs include `sorry`, `admit`, `axiom`, `constant`, `opaque`, `unsafe`, custom syntax or macro elaboration, `run_cmd`, `run_tac`, `Lean.addDecl`, `#eval`, and `#exit`.
