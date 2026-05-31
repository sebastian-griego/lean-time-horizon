import Task

namespace LT005

#check (projectCap_le_cap : ∀ cap x : Nat, projectCap cap x ≤ cap)
#check (projectCap_idempotent : ∀ cap x : Nat,
  projectCap cap (projectCap cap x) = projectCap cap x)

example : projectCap 5 12 = 5 := by
  rfl

example : projectCap 5 3 = 3 := by
  rfl

example (cap x : Nat) : projectCap cap (projectCap cap (projectCap cap x)) = projectCap cap x := by
  rw [projectCap_idempotent, projectCap_idempotent]

end LT005
