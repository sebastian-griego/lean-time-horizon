/-!
Shared namespace marker for the Lean Time-Horizon benchmark.

Individual task submissions are validated in isolated temporary directories.
The package target exists so `lake env lean` has a pinned, reproducible Lean
environment for local validation scripts.
-/

namespace LeanTimeHorizon

def benchmarkName : String := "lean-time-horizon"

end LeanTimeHorizon
