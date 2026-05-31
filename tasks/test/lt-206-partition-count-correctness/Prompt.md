# Task lt-206: partition/count correctness package

Complete `Task.lean`.

You may add helper lemmas, but do not change the public theorem names or weaken
their statements. The intended implementation partitions a list around a pivot:
values `<= pivot` go to the left output and values `> pivot` go to the right
output, preserving multiplicities.

Forbidden constructs include `sorry`, `admit`, `axiom`, `constant`, `opaque`,
`unsafe`, custom syntax/elaboration, `run_cmd`, `run_tac`, `Lean.addDecl`,
and `#eval`.

The submission is the complete contents of `Task.lean`.
