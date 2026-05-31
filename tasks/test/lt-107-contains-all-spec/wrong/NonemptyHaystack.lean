import Std

namespace LT107

def ContainsAllSpec (needles haystack : List Nat) : Prop :=
  needles = [] \/ Not (haystack = [])

theorem containsAll_refl (xs : List Nat) :
    ContainsAllSpec xs xs := by
  cases xs with
  | nil => exact Or.inl rfl
  | cons x xs =>
      exact Or.inr (by intro h; cases h)

theorem containsAll_cons_right (x : Nat) (needles haystack : List Nat)
    (h : ContainsAllSpec needles haystack) :
    ContainsAllSpec needles (x :: haystack) := by
  exact Or.inr (by intro hnil; cases hnil)

end LT107
