import Std

namespace LT113

structure Log where
  entries : List Nat
deriving Repr, DecidableEq

def Log.empty : Log :=
  { entries := [] }

def Log.singleton (x : Nat) : Log :=
  { entries := [x] }

def Log.append (a b : Log) : Log :=
  { entries := a.entries ++ b.entries }

def Log.length (l : Log) : Nat :=
  l.entries.length

theorem append_empty (l : Log) :
    Log.append l Log.empty = l := by
  cases l
  simp [Log.append, Log.empty]

theorem empty_append (l : Log) :
    Log.append Log.empty l = l := by
  cases l
  simp [Log.append, Log.empty]

theorem append_assoc (a b c : Log) :
    Log.append (Log.append a b) c = Log.append a (Log.append b c) := by
  cases a
  cases b
  cases c
  simp [Log.append, List.append_assoc]

theorem length_append (a b : Log) :
    (Log.append a b).length = a.length + b.length := by
  cases a
  cases b
  simp [Log.append, Log.length]

end LT113
