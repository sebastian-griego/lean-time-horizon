import Std

namespace LT109

def spend (budget cost : Nat) : Nat :=
  if cost ≤ budget then budget - cost else budget

theorem spend_le_budget (budget cost : Nat) :
    spend budget cost ≤ budget := by
  sorry

theorem spend_exact_zero (budget : Nat) :
    spend budget budget = 0 := by
  sorry

theorem spend_zero_budget (cost : Nat) :
    spend 0 cost = 0 := by
  sorry

end LT109
