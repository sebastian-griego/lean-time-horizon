import Std

namespace LT105

structure Counter where
  value : Nat
deriving Repr, DecidableEq

def sumList : List Nat -> Nat
  | [] => 0
  | x :: xs => x + sumList xs

def Counter.incBy (n : Nat) (c : Counter) : Counter :=
  { value := c.value + n }

def Counter.incAll : List Nat -> Counter -> Counter
  | [], c => c
  | n :: ns, c => Counter.incAll ns (Counter.incBy n c)

theorem value_incBy (c : Counter) (n : Nat) :
    (Counter.incBy n c).value = c.value + n := by
  rfl

theorem value_incAll (ns : List Nat) (c : Counter) :
    (Counter.incAll ns c).value = c.value + sumList ns := by
  induction ns generalizing c with
  | nil =>
      simp [Counter.incAll, sumList]
  | cons n ns ih =>
      simp [Counter.incAll, ih, value_incBy, sumList, Nat.add_assoc, Nat.add_left_comm, Nat.add_comm]

end LT105
