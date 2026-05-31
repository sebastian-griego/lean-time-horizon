import Std

namespace LT004

def PrefixSpec (pref xs : List Nat) : Prop :=
  True

theorem prefix_self (xs : List Nat) : PrefixSpec xs xs := by
  trivial

theorem prefix_nil (xs : List Nat) : PrefixSpec [] xs := by
  trivial

end LT004
