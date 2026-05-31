import Std

namespace LT002

def countTrue (xs : List Bool) : Nat :=
  xs.length

theorem countTrue_append (xs ys : List Bool) :
    countTrue (xs ++ ys) = countTrue xs + countTrue ys := by
  simp [countTrue]

end LT002
