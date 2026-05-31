import Std

namespace LT107

def ContainsAllSpec (needles haystack : List Nat) : Prop :=
  ∀ x, x ∈ needles -> x ∈ haystack

theorem containsAll_refl (xs : List Nat) :
    ContainsAllSpec xs xs := by
  intro x hx
  exact hx

theorem containsAll_cons_right (x : Nat) (needles haystack : List Nat)
    (h : ContainsAllSpec needles haystack) :
    ContainsAllSpec needles (x :: haystack) := by
  intro y hy
  simp [h y hy]

end LT107
