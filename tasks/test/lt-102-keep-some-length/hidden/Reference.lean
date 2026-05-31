import Std

namespace LT102

def keepSome : List (Option Nat) -> List Nat
  | [] => []
  | none :: xs => keepSome xs
  | some x :: xs => x :: keepSome xs

theorem keepSome_length_le (xs : List (Option Nat)) :
    (keepSome xs).length ≤ xs.length := by
  induction xs with
  | nil =>
      simp [keepSome]
  | cons x xs ih =>
      cases x <;> simp [keepSome, ih] <;> omega

end LT102
