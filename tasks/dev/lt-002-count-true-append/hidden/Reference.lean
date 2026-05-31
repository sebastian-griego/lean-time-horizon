import Std

namespace LT002

def countTrue : List Bool -> Nat
  | [] => 0
  | b :: xs => (if b then 1 else 0) + countTrue xs

theorem countTrue_append (xs ys : List Bool) :
    countTrue (xs ++ ys) = countTrue xs + countTrue ys := by
  induction xs with
  | nil =>
      simp [countTrue]
  | cons b xs ih =>
      cases b <;> simp [countTrue, ih, Nat.add_assoc, Nat.add_left_comm, Nat.add_comm]

end LT002
