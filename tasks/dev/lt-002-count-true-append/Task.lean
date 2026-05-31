import Std

namespace LT002

def countTrue : List Bool -> Nat
  | [] => 0
  | b :: xs => (if b then 1 else 0) + countTrue xs

theorem countTrue_append (xs ys : List Bool) :
    countTrue (xs ++ ys) = countTrue xs + countTrue ys := by
  sorry

end LT002
