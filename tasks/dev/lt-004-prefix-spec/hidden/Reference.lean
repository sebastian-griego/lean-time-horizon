import Std

namespace LT004

def PrefixSpec (pref xs : List Nat) : Prop :=
  ∃ suffix, xs = pref ++ suffix

theorem prefix_self (xs : List Nat) : PrefixSpec xs xs := by
  exact ⟨[], by simp⟩

theorem prefix_nil (xs : List Nat) : PrefixSpec [] xs := by
  exact ⟨xs, by simp⟩

end LT004
