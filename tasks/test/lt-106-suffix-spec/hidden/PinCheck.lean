import Task

namespace LT106

#check (suffix_self : ∀ xs : List Nat, SuffixSpec xs xs)
#check (suffix_nil : ∀ xs : List Nat, SuffixSpec [] xs)

example : SuffixSpec [2, 3] [1, 2, 3] := by
  unfold SuffixSpec
  exact ⟨[1], rfl⟩

example : ¬ SuffixSpec [1] [] := by
  intro h
  unfold SuffixSpec at h
  rcases h with ⟨pref, hp⟩
  cases pref <;> simp at hp

end LT106
