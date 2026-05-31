import Std

namespace LT201

structure Cache where
  keys : List Nat
  entries : List (Nat × Nat)
deriving Repr, DecidableEq

def Cache.keyCount (c : Cache) : Nat :=
  c.keys.length

def Cache.entryCount (c : Cache) : Nat :=
  c.entries.length

def Cache.touch (k v : Nat) (c : Cache) : Cache :=
  { keys := k :: c.keys, entries := (k, v) :: c.entries }

def Cache.touchAll : List (Nat × Nat) -> Cache -> Cache
  | [], c => c
  | (k, v) :: rest, c => Cache.touchAll rest (Cache.touch k v c)

end LT201
