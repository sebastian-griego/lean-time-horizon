import Std

namespace LT204

def capOne (cap x : Nat) : Nat :=
  if x ≤ cap then x else cap

def capList (cap : Nat) : List Nat -> List Nat
  | [] => []
  | x :: xs => capOne cap x :: capList cap xs

def allLe (cap : Nat) : List Nat -> Prop
  | [] => True
  | x :: xs => x ≤ cap ∧ allLe cap xs

def sumList : List Nat -> Nat
  | [] => 0
  | x :: xs => x + sumList xs

theorem capOne_le_cap (cap x : Nat) :
    capOne cap x ≤ cap := by
  unfold capOne
  split <;> omega

theorem capOne_le_self (cap x : Nat) :
    capOne cap x ≤ x := by
  unfold capOne
  split <;> omega

theorem capList_length (cap : Nat) (xs : List Nat) :
    (capList cap xs).length = xs.length := by
  induction xs with
  | nil =>
      simp [capList]
  | cons x xs ih =>
      simp [capList, ih]

theorem capList_allLe (cap : Nat) (xs : List Nat) :
    allLe cap (capList cap xs) := by
  induction xs with
  | nil =>
      simp [capList, allLe]
  | cons x xs ih =>
      simp [capList, allLe, capOne_le_cap, ih]

theorem sum_capList_le_sum (cap : Nat) (xs : List Nat) :
    sumList (capList cap xs) ≤ sumList xs := by
  induction xs with
  | nil =>
      simp [capList, sumList]
  | cons x xs ih =>
      simp [capList, sumList]
      exact Nat.add_le_add (capOne_le_self cap x) ih

theorem capList_invariant (cap : Nat) (xs : List Nat) :
    (capList cap xs).length = xs.length ∧
    allLe cap (capList cap xs) ∧
    sumList (capList cap xs) ≤ sumList xs := by
  exact ⟨capList_length cap xs, capList_allLe cap xs, sum_capList_le_sum cap xs⟩

end LT204
