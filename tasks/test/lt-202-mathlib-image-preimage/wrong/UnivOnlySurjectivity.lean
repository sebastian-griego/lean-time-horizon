import Mathlib.Data.Set.Image

namespace LT202

theorem subset_preimage_image {alpha beta : Type} (f : alpha -> beta) (s : Set alpha) :
    Set.Subset s (Set.preimage f (Set.image f s)) := by
  intro x hx
  exact Exists.intro x (And.intro hx rfl)

theorem image_preimage_subset {alpha beta : Type} (f : alpha -> beta) (t : Set beta) :
    Set.Subset (Set.image f (Set.preimage f t)) t := by
  intro y hy
  rcases hy with ⟨x, hx, hxy⟩
  rw [← hxy]
  exact hx

theorem preimage_image_eq_of_injective {alpha beta : Type} (f : alpha -> beta) (s : Set alpha)
    (hf : Function.Injective f) :
    Set.preimage f (Set.image f s) = s := by
  apply Set.Subset.antisymm
  · intro x hx
    rcases hx with ⟨y, hy, hxy⟩
    have hyx : y = x := hf hxy
    rwa [hyx] at hy
  · exact subset_preimage_image f s

theorem image_inter_eq_of_injective {alpha beta : Type} (f : alpha -> beta) (s t : Set alpha)
    (hf : Function.Injective f) :
    Set.image f (Set.inter s t) = Set.inter (Set.image f s) (Set.image f t) := by
  apply Set.Subset.antisymm
  · intro y hy
    rcases hy with ⟨x, hx, hxy⟩
    constructor
    · exact Exists.intro x (And.intro hx.left hxy)
    · exact Exists.intro x (And.intro hx.right hxy)
  · intro y hy
    rcases hy.left with ⟨x, hxs, hxy⟩
    rcases hy.right with ⟨x', hxt, hx'y⟩
    rw [← hxy] at hx'y
    have hx'x : x' = x := hf hx'y
    exact Exists.intro x (And.intro (And.intro hxs (by rwa [hx'x] at hxt)) hxy)

theorem image_preimage_eq_of_surjective {alpha beta : Type} (f : alpha -> beta) (t : Set beta)
    (hf : Function.Surjective f) (ht : t = Set.univ) :
    Set.image f (Set.preimage f t) = t := by
  subst t
  ext y
  constructor
  · intro hy
    trivial
  · intro hy
    rcases hf y with ⟨x, hxy⟩
    exact ⟨x, by trivial, hxy⟩

end LT202
