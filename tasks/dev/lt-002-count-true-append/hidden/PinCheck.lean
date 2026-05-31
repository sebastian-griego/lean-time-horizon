import Task

namespace LT002

#check (countTrue_append : ∀ xs ys : List Bool,
  countTrue (xs ++ ys) = countTrue xs + countTrue ys)

example : countTrue ([true, false] ++ [true]) = countTrue [true, false] + countTrue [true] := by
  simpa using countTrue_append [true, false] [true]

example : countTrue [true, false, true, false] = 2 := by
  rfl

example : countTrue [false, false] = 0 := by
  rfl

example (xs ys zs : List Bool) :
    countTrue (xs ++ ys ++ zs) = countTrue xs + countTrue ys + countTrue zs := by
  rw [countTrue_append, countTrue_append]

end LT002
