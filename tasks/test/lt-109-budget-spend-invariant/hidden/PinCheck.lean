import Task

namespace LT109

#check (spend_le_budget : ∀ budget cost : Nat, spend budget cost ≤ budget)
#check (spend_exact_zero : ∀ budget : Nat, spend budget budget = 0)
#check (spend_zero_budget : ∀ cost : Nat, spend 0 cost = 0)

example : spend 10 3 = 7 := by
  rfl

example : spend 4 9 = 4 := by
  rfl

example (budget c1 c2 : Nat) :
    spend (spend budget c1) c2 ≤ budget := by
  exact Nat.le_trans (spend_le_budget (spend budget c1) c2) (spend_le_budget budget c1)

end LT109
