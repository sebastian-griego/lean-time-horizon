import Std

namespace LT001

def sumList (xs : List Nat) : Nat :=
  xs.length

theorem sumList_append (xs ys : List Nat) :
    sumList (xs ++ ys) = sumList xs + sumList ys := by
  simp [sumList]

end LT001
