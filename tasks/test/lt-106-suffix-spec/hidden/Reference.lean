import Std

namespace LT106

def SuffixSpec (suf xs : List Nat) : Prop :=
  ∃ pref, xs = pref ++ suf

theorem suffix_self (xs : List Nat) : SuffixSpec xs xs := by
  exact ⟨[], by simp⟩

theorem suffix_nil (xs : List Nat) : SuffixSpec [] xs := by
  exact ⟨xs, by simp⟩

end LT106
