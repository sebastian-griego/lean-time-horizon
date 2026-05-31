import Task

namespace LT102

#check (keepSome_length_le : ∀ xs : List (Option Nat),
  (keepSome xs).length ≤ xs.length)

example : keepSome [some 1, none, some 4] = [1, 4] := by
  rfl

example (xs : List (Option Nat)) :
    (keepSome (none :: xs)).length ≤ xs.length := by
  simpa [keepSome] using keepSome_length_le xs

end LT102
