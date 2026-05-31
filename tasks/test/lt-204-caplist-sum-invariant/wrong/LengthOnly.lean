import Std

namespace LT204

def capOne (cap x : Nat) : Nat := x

def capList (cap : Nat) : List Nat -> List Nat
  | [] => []
  | x :: xs => capOne cap x :: capList cap xs

def allLe (cap : Nat) : List Nat -> Prop
  | [] => True
  | x :: xs => x ≤ cap ∧ allLe cap xs

def sumList : List Nat -> Nat
  | [] => 0
  | x :: xs => x + sumList xs

theorem capOne_le_cap (cap x : Nat) (h : x ≤ cap) :
    capOne cap x ≤ cap := by
  exact h

theorem capOne_le_self (cap x : Nat) :
    capOne cap x ≤ x := by
  rfl

theorem capList_length (cap : Nat) (xs : List Nat) :
    (capList cap xs).length = xs.length := by
  induction xs <;> simp [capList, *]

theorem capList_allLe (cap : Nat) (xs : List Nat) (h : allLe cap xs) :
    allLe cap (capList cap xs) := by
  simpa [capList] using h

theorem sum_capList_le_sum (cap : Nat) (xs : List Nat) :
    sumList (capList cap xs) ≤ sumList xs := by
  induction xs <;> simp [capList, sumList, *]

theorem capList_invariant (cap : Nat) (xs : List Nat) (h : allLe cap xs) :
    (capList cap xs).length = xs.length ∧
    allLe cap (capList cap xs) ∧
    sumList (capList cap xs) ≤ sumList xs := by
  exact ⟨capList_length cap xs, capList_allLe cap xs h, sum_capList_le_sum cap xs⟩

end LT204
