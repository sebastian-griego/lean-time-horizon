import Task

namespace LT205

#check (count_nil : ∀ a : Nat, count a [] = 0)
#check (count_insert_same : ∀ a : Nat, ∀ xs : List Nat, count a (insert a xs) = count a xs + 1)
#check (count_insert_ne : ∀ a b : Nat, ∀ xs : List Nat, b ≠ a -> count a (insert b xs) = count a xs)
#check (count_union : ∀ a : Nat, ∀ xs ys : List Nat, count a (union xs ys) = count a xs + count a ys)
#check (bageq_union_congr : ∀ xs ys zs : List Nat, BagEq xs ys -> BagEq (union xs zs) (union ys zs))

example : count 2 (union [1, 2, 2] [2, 3]) = 3 := by
  rfl

example : BagEq [1, 2, 1] [2, 1, 1] := by
  intro a
  by_cases h1 : a = 1
  · subst a
    rfl
  · by_cases h2 : a = 2
    · subst a
      rfl
    ·
      have h1' : 1 ≠ a := by
        intro h
        exact h1 h.symm
      have h2' : 2 ≠ a := by
        intro h
        exact h2 h.symm
      simp [count, h1', h2']

example (xs ys zs ws : List Nat) (hxy : BagEq xs ys) (hzw : BagEq zs ws) :
    BagEq (union xs zs) (union ys ws) := by
  apply bageq_trans (union xs zs) (union ys zs) (union ys ws)
  · exact bageq_union_congr xs ys zs hxy
  · intro a
    rw [count_union, count_union, hzw a]

end LT205
