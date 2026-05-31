import Std

namespace LT101

def revAcc : List Nat -> List Nat -> List Nat
  | [], acc => acc
  | x :: xs, acc => revAcc xs (x :: acc)

def reverseTR (xs : List Nat) : List Nat :=
  revAcc xs []

theorem revAcc_length (xs acc : List Nat) (h : acc = []) :
    (revAcc xs acc).length = xs.length + acc.length := by
  subst acc
  induction xs with
  | nil => simp [revAcc]
  | cons x xs ih => simp [revAcc, ih]

theorem reverseTR_length (xs : List Nat) :
    (reverseTR xs).length = xs.length := by
  simpa [reverseTR] using revAcc_length xs [] rfl

end LT101
