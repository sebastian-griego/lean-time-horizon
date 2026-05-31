import Std

namespace LT114

def getD (default : Nat) : Option Nat -> Nat
  | none => default
  | some x => x

def mapSucc : Option Nat -> Option Nat
  | none => none
  | some x => some (x + 1)

theorem getD_none (default : Nat) :
    getD default none = default := by
  sorry

theorem getD_some (default x : Nat) :
    getD default (some x) = x := by
  sorry

theorem mapSucc_none :
    mapSucc none = none := by
  sorry

theorem getD_mapSucc_some (default x : Nat) :
    getD default (mapSucc (some x)) = x + 1 := by
  sorry

end LT114
