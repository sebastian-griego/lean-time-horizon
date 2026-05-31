import Task

namespace LT004

#check (prefix_self : ∀ xs : List Nat, PrefixSpec xs xs)
#check (prefix_nil : ∀ xs : List Nat, PrefixSpec [] xs)

example : PrefixSpec [1, 2] [1, 2, 3] := by
  unfold PrefixSpec
  exact ⟨[3], rfl⟩

example : ¬ PrefixSpec [1, 3] [1, 2, 3] := by
  intro h
  unfold PrefixSpec at h
  rcases h with ⟨suffix, hs⟩
  cases suffix with
  | nil =>
      simp at hs
  | cons a rest =>
      cases rest <;> simp at hs

example : PrefixSpec [] [4, 5] := by
  exact prefix_nil [4, 5]

example : PrefixSpec [4, 5] [4, 5] := by
  exact prefix_self [4, 5]

end LT004
