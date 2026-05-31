import Mathlib.Data.Set.Image

namespace LT202

theorem subset_preimage_image {alpha beta : Type} (f : alpha -> beta) (s : Set alpha) :
    Set.Subset s (Set.preimage f (Set.image f s)) := by
  sorry

theorem image_preimage_subset {alpha beta : Type} (f : alpha -> beta) (t : Set beta) :
    Set.Subset (Set.image f (Set.preimage f t)) t := by
  sorry

theorem preimage_image_eq_of_injective {alpha beta : Type} (f : alpha -> beta) (s : Set alpha)
    (hf : Function.Injective f) :
    Set.preimage f (Set.image f s) = s := by
  sorry

theorem image_inter_eq_of_injective {alpha beta : Type} (f : alpha -> beta) (s t : Set alpha)
    (hf : Function.Injective f) :
    Set.image f (Set.inter s t) = Set.inter (Set.image f s) (Set.image f t) := by
  sorry

theorem image_preimage_eq_of_surjective {alpha beta : Type} (f : alpha -> beta) (t : Set beta)
    (hf : Function.Surjective f) :
    Set.image f (Set.preimage f t) = t := by
  sorry

end LT202
