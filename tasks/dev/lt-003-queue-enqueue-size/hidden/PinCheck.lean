import Task

namespace LT003

#check (size_enqueue : ∀ q : Queue, ∀ x : Nat,
  (Queue.enqueue x q).size = q.size + 1)

#check (size_enqueueAll : ∀ xs : List Nat, ∀ q : Queue,
  (Queue.enqueueAll xs q).size = q.size + xs.length)

example (q : Queue) : (Queue.enqueueAll [10, 20, 30] q).size = q.size + 3 := by
  simpa using size_enqueueAll [10, 20, 30] q

example (q : Queue) (x y : Nat) :
    (Queue.enqueue y (Queue.enqueue x q)).size = q.size + 2 := by
  rw [size_enqueue, size_enqueue]

end LT003
