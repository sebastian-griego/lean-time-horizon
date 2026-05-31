import Task

namespace LT107

#check (containsAll_refl : ∀ xs : List Nat, ContainsAllSpec xs xs)

#check (containsAll_cons_right : ∀ x : Nat, ∀ needles haystack : List Nat,
  ContainsAllSpec needles haystack -> ContainsAllSpec needles (x :: haystack))

example : ContainsAllSpec [1, 2] [0, 1, 2] := by
  intro x hx
  simp at hx ⊢
  omega

example : ¬ ContainsAllSpec [2] [1, 3] := by
  intro h
  have hx := h 2 (by simp)
  simp at hx

example : ContainsAllSpec [] [1, 3] := by
  intro x hx
  simp at hx

example : ContainsAllSpec [1, 1, 2] [2, 1] := by
  intro x hx
  simp at hx ⊢
  omega

example : ¬ ContainsAllSpec [4] [] := by
  intro h
  have hx := h 4 (by simp)
  simp at hx

end LT107
