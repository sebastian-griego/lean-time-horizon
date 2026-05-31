import Std

namespace LT003

structure Queue where
  front : List Nat
  back : List Nat
deriving Repr, DecidableEq

def Queue.size (q : Queue) : Nat :=
  q.front.length + q.back.length

def Queue.enqueue (x : Nat) (q : Queue) : Queue :=
  { q with back := x :: q.back }

def Queue.enqueueAll : List Nat -> Queue -> Queue
  | [], q => q
  | x :: xs, q => Queue.enqueueAll xs (Queue.enqueue x q)

theorem size_enqueue (q : Queue) (x : Nat) :
    (Queue.enqueue x q).size = q.size + 1 := by
  sorry

theorem size_enqueueAll (xs : List Nat) (q : Queue) :
    (Queue.enqueueAll xs q).size = q.size + xs.length := by
  sorry

end LT003
