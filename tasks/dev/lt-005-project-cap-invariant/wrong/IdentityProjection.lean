import Std

namespace LT005

def projectCap (cap x : Nat) : Nat :=
  x

theorem projectCap_le_cap (cap x : Nat) (h : x ≤ cap) :
    projectCap cap x ≤ cap := by
  exact h

theorem projectCap_idempotent (cap x : Nat) :
    projectCap cap (projectCap cap x) = projectCap cap x := by
  rfl

end LT005
