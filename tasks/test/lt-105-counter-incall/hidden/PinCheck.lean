import Task

namespace LT105

#check (value_incBy : ∀ c : Counter, ∀ n : Nat,
  (Counter.incBy n c).value = c.value + n)

#check (value_incAll : ∀ ns : List Nat, ∀ c : Counter,
  (Counter.incAll ns c).value = c.value + sumList ns)

example : (Counter.incAll [2, 0, 5] { value := 10 }).value = 17 := by
  rfl

example : sumList [2, 0, 5] = 7 := by
  rfl

example : (Counter.incAll [4, 1] { value := 3 }).value = 8 := by
  rfl

example (c : Counter) (xs ys : List Nat) :
    (Counter.incAll ys (Counter.incAll xs c)).value =
      c.value + sumList xs + sumList ys := by
  rw [value_incAll, value_incAll]

end LT105
