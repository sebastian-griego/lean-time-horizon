import Std

namespace LT108

def AdjacentLeSpec (xs : List Nat) : Prop :=
  True

theorem adjacent_nil : AdjacentLeSpec [] := by
  sorry

theorem adjacent_singleton (x : Nat) : AdjacentLeSpec [x] := by
  sorry

theorem adjacent_cons (a b : Nat) (xs : List Nat)
    (hab : a ≤ b) (h : AdjacentLeSpec (b :: xs)) :
    AdjacentLeSpec (a :: b :: xs) := by
  sorry

end LT108
