# lt-104: Repair stack size proofs after pushAll changes

Edit `Task.lean` only. `Stack.pushAll` pushes each element of the input list onto the stack through the current `push` API.

Repair the size proofs without changing declaration names, theorem statements, imports, or the stack representation.

Forbidden constructs include `sorry`, `admit`, `axiom`, `constant`, `opaque`, `unsafe`, custom syntax or macro elaboration, `run_cmd`, `run_tac`, `Lean.addDecl`, `#eval`, and `#exit`.
