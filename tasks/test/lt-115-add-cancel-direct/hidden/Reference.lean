import Std

namespace LT115

theorem add_right_cancel_twice (a b c d : Nat)
    (h : (a + c) + d = (b + c) + d) :
    a = b := by
  have h1 : a + c = b + c := Nat.add_right_cancel h
  exact Nat.add_right_cancel h1

end LT115
