import Task

namespace LT110

#check (stepDown_le : ∀ x grad : Nat, stepDown x grad ≤ x)
#check (repeatTwo_le : ∀ x g1 g2 : Nat, repeatTwo x g1 g2 ≤ x)

example : stepDown 10 3 = 7 := by
  rfl

example : stepDown 2 5 = 0 := by
  rfl

example (x g1 g2 g3 : Nat) :
    stepDown (repeatTwo x g1 g2) g3 ≤ x := by
  exact Nat.le_trans (stepDown_le (repeatTwo x g1 g2) g3) (repeatTwo_le x g1 g2)

end LT110
