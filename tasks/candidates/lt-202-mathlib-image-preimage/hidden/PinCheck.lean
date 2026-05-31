import Task

namespace LT202

#check (subset_preimage_image : ∀ {alpha beta : Type} (f : alpha -> beta) (s : Set alpha),
  Set.Subset s (Set.preimage f (Set.image f s)))
#check (image_preimage_subset : ∀ {alpha beta : Type} (f : alpha -> beta) (t : Set beta),
  Set.Subset (Set.image f (Set.preimage f t)) t)
#check (preimage_image_eq_of_injective : ∀ {alpha beta : Type} (f : alpha -> beta) (s : Set alpha),
  Function.Injective f -> Set.preimage f (Set.image f s) = s)
#check (image_inter_eq_of_injective : ∀ {alpha beta : Type} (f : alpha -> beta) (s t : Set alpha),
  Function.Injective f -> Set.image f (Set.inter s t) = Set.inter (Set.image f s) (Set.image f t))
#check (image_preimage_eq_of_surjective : ∀ {alpha beta : Type} (f : alpha -> beta) (t : Set beta),
  Function.Surjective f -> Set.image f (Set.preimage f t) = t)

example :
    Set.image (fun p : Nat × Nat => p.1)
        (Set.preimage (fun p : Nat × Nat => p.1) ({2} : Set Nat)) = ({2} : Set Nat) := by
  apply image_preimage_eq_of_surjective
  intro n
  exact ⟨(n, 0), rfl⟩

example :
    Set.image (fun n : Nat => n) (Set.inter ({1, 2} : Set Nat) ({2, 3} : Set Nat))
      = Set.inter (Set.image (fun n : Nat => n) ({1, 2} : Set Nat))
          (Set.image (fun n : Nat => n) ({2, 3} : Set Nat)) := by
  apply image_inter_eq_of_injective
  intro a b h
  exact h

end LT202
