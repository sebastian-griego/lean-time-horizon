# lt-101: Tail-recursive reverse preserves length

Edit `Task.lean` only. Prove the helper theorem and final theorem without changing their names or statements.

`reverseTR` is implemented through an accumulator. The task is to prove that both the accumulator helper and the public reverse function preserve the expected lengths.

You may add helper lemmas in `Task.lean`. Do not change imports.

Forbidden constructs include `sorry`, `admit`, `axiom`, `constant`, `opaque`, `unsafe`, custom syntax or macro elaboration, `run_cmd`, `run_tac`, `Lean.addDecl`, `#eval`, and `#exit`.
