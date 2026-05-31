import Std

namespace LT111

def clip (lo hi x : Nat) : Nat :=
  if x < lo then lo else x

theorem clip_ge_lo (lo hi x : Nat) (h : lo ≤ hi) :
    lo ≤ clip lo hi x := by
  unfold clip
  split <;> omega

theorem clip_le_hi (lo hi x : Nat) (h : lo ≤ hi) (hx : x ≤ hi) :
    clip lo hi x ≤ hi := by
  unfold clip
  split <;> omega

end LT111
