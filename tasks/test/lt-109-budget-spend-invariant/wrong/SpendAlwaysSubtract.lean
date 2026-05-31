import Std

namespace LT109

def spend (budget cost : Nat) : Nat :=
  budget - cost

theorem spend_le_budget (budget cost : Nat) :
    spend budget cost ≤ budget := by
  unfold spend
  omega

theorem spend_exact_zero (budget : Nat) :
    spend budget budget = 0 := by
  unfold spend
  omega

theorem spend_zero_budget (cost : Nat) :
    spend 0 cost = 0 := by
  unfold spend
  omega

end LT109
