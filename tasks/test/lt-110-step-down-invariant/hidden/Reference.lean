import Std

namespace LT110

def stepDown (x grad : Nat) : Nat :=
  x - grad

def repeatTwo (x g1 g2 : Nat) : Nat :=
  stepDown (stepDown x g1) g2

theorem stepDown_le (x grad : Nat) :
    stepDown x grad ≤ x := by
  unfold stepDown
  omega

theorem repeatTwo_le (x g1 g2 : Nat) :
    repeatTwo x g1 g2 ≤ x := by
  unfold repeatTwo
  exact Nat.le_trans (stepDown_le (stepDown x g1) g2) (stepDown_le x g1)

end LT110
