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

example : ¬ AdjacentLeSpec [1, 3, 2] := by
  intro h
  simp [AdjacentLeSpec] at h

example : AdjacentLeSpec [0, 1, 1, 4] := by
  simp [AdjacentLeSpec]

end LT108
