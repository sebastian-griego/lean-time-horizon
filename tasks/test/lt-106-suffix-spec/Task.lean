import Std

namespace LT106

def SuffixSpec (suf xs : List Nat) : Prop :=
  True

theorem suffix_self (xs : List Nat) : SuffixSpec xs xs := by
  sorry

theorem suffix_nil (xs : List Nat) : SuffixSpec [] xs := by
  sorry

end LT106
