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
  sorry

theorem capOne_le_self (cap x : Nat) :
    capOne cap x ≤ x := by
  sorry

theorem capList_length (cap : Nat) (xs : List Nat) :
    (capList cap xs).length = xs.length := by
  sorry

theorem capList_allLe (cap : Nat) (xs : List Nat) :
    allLe cap (capList cap xs) := by
  sorry

theorem sum_capList_le_sum (cap : Nat) (xs : List Nat) :
    sumList (capList cap xs) ≤ sumList xs := by
  sorry

theorem capList_invariant (cap : Nat) (xs : List Nat) :
    (capList cap xs).length = xs.length ∧
    allLe cap (capList cap xs) ∧
    sumList (capList cap xs) ≤ sumList xs := by
  sorry

end LT204
