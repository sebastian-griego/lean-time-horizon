import Task

namespace LT108

#check (adjacent_nil : AdjacentLeSpec [])
#check (adjacent_singleton : ∀ x : Nat, AdjacentLeSpec [x])
#check (adjacent_cons : ∀ a b : Nat, ∀ xs : List Nat,
  a ≤ b -> AdjacentLeSpec (b :: xs) -> AdjacentLeSpec (a :: b :: xs))

example : AdjacentLeSpec [1, 2, 2, 5] := by
  simp [AdjacentLeSpec]

example : ¬ AdjacentLeSpec [2, 1] := by
  intro h
  simp [AdjacentLeSpec] at h

end LT108
