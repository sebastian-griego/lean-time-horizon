import Task

namespace LT114

#check (getD_none : ∀ default : Nat, getD default none = default)
#check (getD_some : ∀ default x : Nat, getD default (some x) = x)
#check (mapSucc_none : mapSucc none = none)
#check (getD_mapSucc_some : ∀ default x : Nat,
  getD default (mapSucc (some x)) = x + 1)

example : mapSucc (some 4) = some 5 := by
  rfl

example : getD 99 (mapSucc none) = 99 := by
  rw [mapSucc_none, getD_none]

end LT114
