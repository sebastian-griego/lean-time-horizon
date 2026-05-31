import Std

namespace LT107

def ContainsAllSpec (needles haystack : List Nat) : Prop :=
  True

theorem containsAll_refl (xs : List Nat) :
    ContainsAllSpec xs xs := by
  sorry

theorem containsAll_cons_right (x : Nat) (needles haystack : List Nat)
    (h : ContainsAllSpec needles haystack) :
    ContainsAllSpec needles (x :: haystack) := by
  sorry

end LT107
