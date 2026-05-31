import Std

namespace LT101

def revAcc (xs acc : List Nat) : List Nat :=
  xs ++ acc

def reverseTR (xs : List Nat) : List Nat :=
  revAcc xs []

theorem revAcc_length (xs acc : List Nat) :
    (revAcc xs acc).length = xs.length + acc.length := by
  simp [revAcc]

theorem reverseTR_length (xs : List Nat) :
    (reverseTR xs).length = xs.length := by
  simp [reverseTR, revAcc]

end LT101
