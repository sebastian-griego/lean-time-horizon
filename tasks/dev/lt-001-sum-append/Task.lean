import Std

namespace LT001

def sumList : List Nat -> Nat
  | [] => 0
  | x :: xs => x + sumList xs

theorem sumList_append (xs ys : List Nat) :
    sumList (xs ++ ys) = sumList xs + sumList ys := by
  sorry

end LT001
