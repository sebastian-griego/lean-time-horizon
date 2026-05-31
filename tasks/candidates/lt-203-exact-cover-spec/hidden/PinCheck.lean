import Task

namespace LT203

#check (covers_refl : ∀ xs : List Nat, CoversExactly xs xs)
#check (covers_cons : ∀ x : Nat, ∀ xs ys : List Nat,
  CoversExactly xs ys -> CoversExactly (x :: xs) (x :: ys))
#check (covers_symm : ∀ xs ys : List Nat, CoversExactly xs ys -> CoversExactly ys xs)
#check (covers_trans : ∀ xs ys zs : List Nat,
  CoversExactly xs ys -> CoversExactly ys zs -> CoversExactly xs zs)

example : CoversExactly [1, 2, 1] [2, 1] := by
  intro z
  simp
  omega

example : ¬ CoversExactly [1, 2] [1, 3] := by
  intro h
  have h2 := (h 2).mp (by simp)
  simp at h2

example (xs ys : List Nat) (h : CoversExactly xs ys) :
    CoversExactly (7 :: 7 :: xs) (7 :: ys) := by
  apply covers_trans (7 :: 7 :: xs) (7 :: 7 :: ys)
  · exact covers_cons 7 (7 :: xs) (7 :: ys) (covers_cons 7 xs ys h)
  · intro z
    simp

end LT203
