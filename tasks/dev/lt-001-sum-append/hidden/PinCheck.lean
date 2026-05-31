import Task

namespace LT001

#check (sumList_append : ∀ xs ys : List Nat,
  sumList (xs ++ ys) = sumList xs + sumList ys)

example : sumList ([2, 3] ++ [5]) = sumList [2, 3] + sumList [5] := by
  simpa using sumList_append [2, 3] [5]

example : sumList [2, 3, 5] = 10 := by
  rfl

example : sumList [] = 0 := by
  rfl

example (xs ys zs : List Nat) :
    sumList ((xs ++ ys) ++ zs) = sumList xs + sumList ys + sumList zs := by
  rw [sumList_append, sumList_append]

end LT001
