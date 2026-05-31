import Std

namespace LT102

def keepSome : List (Option Nat) -> List Nat
  | [] => []
  | none :: xs => keepSome xs
  | some x :: xs => x :: keepSome xs

theorem keepSome_length_le (xs : List (Option Nat)) (h : ∀ x ∈ xs, x.isSome) :
    (keepSome xs).length ≤ xs.length := by
  induction xs with
  | nil => simp [keepSome]
  | cons x xs ih =>
      cases x <;> simp [keepSome]

end LT102
