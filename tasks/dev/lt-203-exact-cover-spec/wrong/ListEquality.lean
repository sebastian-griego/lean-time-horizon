import Std

namespace LT203

def CoversExactly (xs ys : List Nat) : Prop :=
  xs = ys

theorem covers_refl (xs : List Nat) :
    CoversExactly xs xs := by
  rfl

theorem covers_cons (x : Nat) (xs ys : List Nat)
    (h : CoversExactly xs ys) :
    CoversExactly (x :: xs) (x :: ys) := by
  rw [h]

theorem covers_symm (xs ys : List Nat)
    (h : CoversExactly xs ys) :
    CoversExactly ys xs := by
  exact h.symm

theorem covers_trans (xs ys zs : List Nat)
    (hxy : CoversExactly xs ys) (hyz : CoversExactly ys zs) :
    CoversExactly xs zs := by
  exact Eq.trans hxy hyz

end LT203
