import Std

namespace LT115

theorem add_right_cancel_twice (a b c d : Nat)
    (h : (a + c) + d = (b + c) + d) (hc : c = 0) :
    a = b := by
  subst c
  have h1 : a + d = b + d := by simpa using h
  exact Nat.add_right_cancel h1

end LT115
