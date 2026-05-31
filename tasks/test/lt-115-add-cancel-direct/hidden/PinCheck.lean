import Task

namespace LT115

#check (add_right_cancel_twice : ∀ a b c d : Nat,
  (a + c) + d = (b + c) + d -> a = b)

example (a b : Nat) (h : (a + 2) + 3 = (b + 2) + 3) : a = b := by
  exact add_right_cancel_twice a b 2 3 h

end LT115
