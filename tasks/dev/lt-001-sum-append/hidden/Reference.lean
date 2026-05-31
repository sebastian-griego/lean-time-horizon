import Std

namespace LT001

def sumList : List Nat -> Nat
  | [] => 0
  | x :: xs => x + sumList xs

theorem sumList_append (xs ys : List Nat) :
    sumList (xs ++ ys) = sumList xs + sumList ys := by
  induction xs with
  | nil =>
      simp [sumList]
  | cons x xs ih =>
      simp [sumList, ih, Nat.add_assoc, Nat.add_left_comm, Nat.add_comm]

end LT001
