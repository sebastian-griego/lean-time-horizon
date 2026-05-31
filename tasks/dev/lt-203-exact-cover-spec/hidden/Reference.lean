import Std

namespace LT203

def CoversExactly (xs ys : List Nat) : Prop :=
  ∀ z, z ∈ xs ↔ z ∈ ys

theorem covers_refl (xs : List Nat) :
    CoversExactly xs xs := by
  intro z
  exact Iff.rfl

theorem covers_cons (x : Nat) (xs ys : List Nat)
    (h : CoversExactly xs ys) :
    CoversExactly (x :: xs) (x :: ys) := by
  intro z
  constructor
  · intro hz
    simp at hz ⊢
    rcases hz with hzx | hxs
    · exact Or.inl hzx
    · exact Or.inr ((h z).mp hxs)
  · intro hz
    simp at hz ⊢
    rcases hz with hzx | hys
    · exact Or.inl hzx
    · exact Or.inr ((h z).mpr hys)

theorem covers_symm (xs ys : List Nat)
    (h : CoversExactly xs ys) :
    CoversExactly ys xs := by
  intro z
  exact (h z).symm

theorem covers_trans (xs ys zs : List Nat)
    (hxy : CoversExactly xs ys) (hyz : CoversExactly ys zs) :
    CoversExactly xs zs := by
  intro z
  exact Iff.trans (hxy z) (hyz z)

end LT203
