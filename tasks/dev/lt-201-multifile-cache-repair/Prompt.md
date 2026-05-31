# lt-201: Multi-file cache repair after `touchAll` API change

Edit `Task.lean` only. `Model.lean` is read-only public context.

The cache API now records both a key history and an entry history. Repair the proofs in `Task.lean` showing that a single touch and a batch touch update both lengths correctly.

Do not change theorem names or theorem statements. Do not edit `Model.lean` or imports. Helper lemmas may be added to `Task.lean`.

Forbidden constructs include `sorry`, `admit`, `axiom`, `constant`, `opaque`, `unsafe`, custom syntax or macro elaboration, `run_cmd`, `run_tac`, `Lean.addDecl`, `#eval`, and `#exit`.
