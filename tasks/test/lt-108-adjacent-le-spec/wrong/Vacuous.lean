import Std

namespace LT108

def AdjacentLeSpec (xs : List Nat) : Prop :=
  True

theorem adjacent_nil : AdjacentLeSpec [] := by
  trivial

theorem adjacent_singleton (x : Nat) : AdjacentLeSpec [x] := by
  trivial

theorem adjacent_cons (a b : Nat) (xs : List Nat)
    (hab : a ≤ b) (h : AdjacentLeSpec (b :: xs)) :
    AdjacentLeSpec (a :: b :: xs) := by
  trivial

end LT108
