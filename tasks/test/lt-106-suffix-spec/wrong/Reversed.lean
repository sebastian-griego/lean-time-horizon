import Std

namespace LT106

def SuffixSpec (suf xs : List Nat) : Prop :=
  ∃ rest, suf = xs ++ rest

theorem suffix_self (xs : List Nat) : SuffixSpec xs xs := by
  exact ⟨[], by simp⟩

theorem suffix_nil (xs : List Nat) : SuffixSpec [] xs := by
  exact ⟨[], by cases xs <;> simp⟩

end LT106
