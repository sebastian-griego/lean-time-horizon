import Std

namespace LT005

def projectCap (cap x : Nat) : Nat :=
  if x ≤ cap then x else cap

theorem projectCap_le_cap (cap x : Nat) :
    projectCap cap x ≤ cap := by
  unfold projectCap
  split <;> omega

theorem projectCap_idempotent (cap x : Nat) :
    projectCap cap (projectCap cap x) = projectCap cap x := by
  unfold projectCap
  split <;> simp [projectCap]

end LT005
