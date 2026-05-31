import Std

namespace LT110

def stepDown (x grad : Nat) : Nat :=
  x - grad

def repeatTwo (x g1 g2 : Nat) : Nat :=
  stepDown (stepDown x g1) g2

theorem stepDown_le (x grad : Nat) :
    stepDown x grad ≤ x := by
  sorry

theorem repeatTwo_le (x g1 g2 : Nat) :
    repeatTwo x g1 g2 ≤ x := by
  sorry

end LT110
