import Lake
open Lake DSL

package «LeanTimeHorizon» where
  version := v!"0.1.0"
  keywords := #["Lean", "evaluation", "benchmark"]

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.28.0"

@[default_target]
lean_lib «LeanTimeHorizon» where
