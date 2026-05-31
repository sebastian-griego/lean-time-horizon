import Std

namespace LT004

def PrefixSpec (pref xs : List Nat) : Prop :=
  pref = [] \/ pref = xs

theorem prefix_self (xs : List Nat) : PrefixSpec xs xs := by
  exact Or.inr rfl

theorem prefix_nil (xs : List Nat) : PrefixSpec [] xs := by
  exact Or.inl rfl

end LT004
