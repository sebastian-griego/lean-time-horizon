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
  -- Same theorem statement, but only the empty and singleton cases are
  -- repaired. The batched recursive case is left to a brittle simplification.
  cases ns with
  | nil => simp [Counter.incAll, sumList]
  | cons n ns =>
      cases ns with
      | nil => simp [Counter.incAll, sumList, value_incBy]
      | cons m rest => simp [Counter.incAll, sumList, value_incBy]

end LT105
