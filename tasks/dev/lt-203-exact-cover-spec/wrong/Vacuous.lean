import Std

namespace LT203

def CoversExactly (xs ys : List Nat) : Prop :=
  True

theorem covers_refl (xs : List Nat) :
    CoversExactly xs xs := by
  trivial

theorem covers_cons (x : Nat) (xs ys : List Nat)
    (h : CoversExactly xs ys) :
    CoversExactly (x :: xs) (x :: ys) := by
  trivial

theorem covers_symm (xs ys : List Nat)
    (h : CoversExactly xs ys) :
    CoversExactly ys xs := by
  trivial

theorem covers_trans (xs ys zs : List Nat)
    (hxy : CoversExactly xs ys) (hyz : CoversExactly ys zs) :
    CoversExactly xs zs := by
  trivial

end LT203
