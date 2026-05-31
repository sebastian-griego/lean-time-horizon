import Std

namespace LT005

def projectCap (cap x : Nat) : Nat :=
  if x ≤ cap then x else cap

theorem projectCap_le_cap (cap x : Nat) :
    projectCap cap x ≤ cap := by
  sorry

theorem projectCap_idempotent (cap x : Nat) :
    projectCap cap (projectCap cap x) = projectCap cap x := by
  sorry

end LT005
