import Std

namespace LT111

def clip (lo hi x : Nat) : Nat :=
  if x < lo then lo else if hi < x then hi else x

theorem clip_ge_lo (lo hi x : Nat) (h : lo ≤ hi) :
    lo ≤ clip lo hi x := by
  sorry

theorem clip_le_hi (lo hi x : Nat) (h : lo ≤ hi) :
    clip lo hi x ≤ hi := by
  sorry

end LT111
