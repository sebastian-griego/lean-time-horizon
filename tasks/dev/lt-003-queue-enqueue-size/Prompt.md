# lt-003: Repair queue size proof after an enqueue API change

Edit `Task.lean` only. The queue implementation stores newly enqueued items in `back`. Repair the proof that enqueuing a list increases the queue size by the list length.

Do not change the names or statements of `size_enqueue` or `size_enqueueAll`. You may add helper lemmas in `Task.lean`, but do not change imports or the data representation.

Forbidden constructs include `sorry`, `admit`, `axiom`, `constant`, `opaque`, `unsafe`, custom syntax or macro elaboration, `run_cmd`, `run_tac`, `Lean.addDecl`, `#eval`, and `#exit`.
