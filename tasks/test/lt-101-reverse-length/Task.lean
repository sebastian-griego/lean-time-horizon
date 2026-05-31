import Std

namespace LT101

def revAcc : List Nat -> List Nat -> List Nat
  | [], acc => acc
  | x :: xs, acc => revAcc xs (x :: acc)

def reverseTR (xs : List Nat) : List Nat :=
  revAcc xs []

theorem revAcc_length (xs acc : List Nat) :
    (revAcc xs acc).length = xs.length + acc.length := by
  sorry

theorem reverseTR_length (xs : List Nat) :
    (reverseTR xs).length = xs.length := by
  sorry

end LT101
