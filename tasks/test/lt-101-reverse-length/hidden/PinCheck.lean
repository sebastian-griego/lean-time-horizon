import Task

namespace LT101

#check (revAcc_length : ∀ xs acc : List Nat,
  (revAcc xs acc).length = xs.length + acc.length)

#check (reverseTR_length : ∀ xs : List Nat,
  (reverseTR xs).length = xs.length)

example : reverseTR [1, 2, 3] = [3, 2, 1] := by
  rfl

example (xs acc tail : List Nat) :
    (revAcc xs (acc ++ tail)).length = xs.length + acc.length + tail.length := by
  rw [revAcc_length, List.length_append]
  omega

end LT101
