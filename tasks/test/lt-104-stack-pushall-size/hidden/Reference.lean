import Std

namespace LT104

structure Stack where
  data : List Nat
deriving Repr, DecidableEq

def Stack.size (s : Stack) : Nat :=
  s.data.length

def Stack.push (x : Nat) (s : Stack) : Stack :=
  { data := x :: s.data }

def Stack.pushAll : List Nat -> Stack -> Stack
  | [], s => s
  | x :: xs, s => Stack.pushAll xs (Stack.push x s)

theorem size_push (s : Stack) (x : Nat) :
    (Stack.push x s).size = s.size + 1 := by
  simp [Stack.push, Stack.size]

theorem size_pushAll (xs : List Nat) (s : Stack) :
    (Stack.pushAll xs s).size = s.size + xs.length := by
  induction xs generalizing s with
  | nil =>
      simp [Stack.pushAll]
  | cons x xs ih =>
      simp [Stack.pushAll, ih, size_push, Nat.add_assoc, Nat.add_left_comm, Nat.add_comm]

end LT104
