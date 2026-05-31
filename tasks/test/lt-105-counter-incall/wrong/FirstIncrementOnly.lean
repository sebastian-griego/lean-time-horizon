import Std

namespace LT105

structure Counter where
  value : Nat
deriving Repr, DecidableEq

def sumList : List Nat -> Nat
  | [] => 0
  | x :: _ => x

def Counter.incBy (n : Nat) (c : Counter) : Counter :=
  { value := c.value + n }

def Counter.incAll : List Nat -> Counter -> Counter
  | [], c => c
  | n :: _, c => Counter.incBy n c

theorem value_incBy (c : Counter) (n : Nat) :
    (Counter.incBy n c).value = c.value + n := by
  rfl

theorem value_incAll (ns : List Nat) (c : Counter) :
    (Counter.incAll ns c).value = c.value + sumList ns := by
  cases ns <;> simp [Counter.incAll, sumList, value_incBy]

end LT105
