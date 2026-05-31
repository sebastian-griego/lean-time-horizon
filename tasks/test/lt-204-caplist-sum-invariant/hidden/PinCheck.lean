import Task

namespace LT204

#check (capOne_le_cap : ∀ cap x : Nat, capOne cap x ≤ cap)
#check (capOne_le_self : ∀ cap x : Nat, capOne cap x ≤ x)
#check (capList_invariant : ∀ cap : Nat, ∀ xs : List Nat,
  (capList cap xs).length = xs.length ∧ allLe cap (capList cap xs) ∧ sumList (capList cap xs) ≤ sumList xs)

example : capList 3 [0, 4, 2, 9] = [0, 3, 2, 3] := by
  rfl

example : sumList (capList 3 [0, 4, 2, 9]) = 8 := by
  rfl

example (cap : Nat) (xs : List Nat) :
    allLe cap (capList cap (capList cap xs)) := by
  exact capList_allLe cap (capList cap xs)

example : capOne 3 9 = 3 := by
  rfl

example : capOne 3 2 = 2 := by
  rfl

end LT204
