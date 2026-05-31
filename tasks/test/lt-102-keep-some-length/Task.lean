import Std

namespace LT102

def keepSome : List (Option Nat) -> List Nat
  | [] => []
  | none :: xs => keepSome xs
  | some x :: xs => x :: keepSome xs

theorem keepSome_length_le (xs : List (Option Nat)) :
    (keepSome xs).length ≤ xs.length := by
  sorry

end LT102
