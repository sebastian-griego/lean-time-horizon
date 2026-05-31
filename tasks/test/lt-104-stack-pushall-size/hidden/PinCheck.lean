import Task

namespace LT104

#check (size_push : ∀ s : Stack, ∀ x : Nat,
  (Stack.push x s).size = s.size + 1)

#check (size_pushAll : ∀ xs : List Nat, ∀ s : Stack,
  (Stack.pushAll xs s).size = s.size + xs.length)

example (s : Stack) : (Stack.pushAll [7, 8, 9, 10] s).size = s.size + 4 := by
  simpa using size_pushAll [7, 8, 9, 10] s

example (s : Stack) (x y : Nat) :
    (Stack.push y (Stack.push x s)).size = s.size + 2 := by
  rw [size_push, size_push]

end LT104
