import Task

namespace LT111

#check (clip_ge_lo : ∀ lo hi x : Nat, lo ≤ hi -> lo ≤ clip lo hi x)
#check (clip_le_hi : ∀ lo hi x : Nat, lo ≤ hi -> clip lo hi x ≤ hi)

example : clip 3 8 1 = 3 := by
  rfl

example : clip 3 8 20 = 8 := by
  rfl

example : clip 3 8 5 = 5 := by
  rfl

example (lo hi x : Nat) (h : lo ≤ hi) :
    lo ≤ clip lo hi (clip lo hi x) ∧ clip lo hi (clip lo hi x) ≤ hi := by
  exact ⟨clip_ge_lo lo hi (clip lo hi x) h, clip_le_hi lo hi (clip lo hi x) h⟩

end LT111
