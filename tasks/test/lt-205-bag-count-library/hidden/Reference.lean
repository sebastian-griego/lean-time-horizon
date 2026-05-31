import Std

namespace LT205

def count (a : Nat) : List Nat -> Nat
  | [] => 0
  | x :: xs => (if x = a then 1 else 0) + count a xs

def insert (a : Nat) (xs : List Nat) : List Nat :=
  a :: xs

def union (xs ys : List Nat) : List Nat :=
  xs ++ ys

def BagEq (xs ys : List Nat) : Prop :=
  ∀ a, count a xs = count a ys

theorem count_nil (a : Nat) :
    count a [] = 0 := by
  rfl

theorem count_insert_same (a : Nat) (xs : List Nat) :
    count a (insert a xs) = count a xs + 1 := by
  simp [insert, count, Nat.add_comm]

theorem count_insert_ne (a b : Nat) (xs : List Nat) (h : b ≠ a) :
    count a (insert b xs) = count a xs := by
  simp [insert, count, h]

theorem count_union (a : Nat) (xs ys : List Nat) :
    count a (union xs ys) = count a xs + count a ys := by
  induction xs with
  | nil =>
      simp [union, count]
  | cons x xs ih =>
      simp [union] at ih
      by_cases hx : x = a
      ·
        simp [union, count, hx]
        rw [ih]
        omega
      ·
        simp [union, count, hx]
        rw [ih]

theorem bageq_refl (xs : List Nat) :
    BagEq xs xs := by
  intro a
  rfl

theorem bageq_symm (xs ys : List Nat) :
    BagEq xs ys -> BagEq ys xs := by
  intro h a
  exact (h a).symm

theorem bageq_trans (xs ys zs : List Nat) :
    BagEq xs ys -> BagEq ys zs -> BagEq xs zs := by
  intro hxy hyz a
  exact Eq.trans (hxy a) (hyz a)

theorem bageq_union_congr (xs ys zs : List Nat)
    (h : BagEq xs ys) :
    BagEq (union xs zs) (union ys zs) := by
  intro a
  rw [count_union, count_union, h a]

end LT205
