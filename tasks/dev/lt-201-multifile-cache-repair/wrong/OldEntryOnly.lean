import Model

namespace LT201

theorem keyCount_touch (c : Cache) (k v : Nat) :
    (Cache.touch k v c).keyCount = c.keyCount + 1 := by
  simp [Cache.touch, Cache.keyCount]

theorem entryCount_touch (c : Cache) (k v : Nat) :
    (Cache.touch k v c).entryCount = c.entryCount + 1 := by
  simp [Cache.touch, Cache.entryCount]

theorem entryCount_touchAll (updates : List (Nat × Nat)) (c : Cache) :
    (Cache.touchAll updates c).entryCount = c.entryCount + updates.length := by
  induction updates generalizing c with
  | nil => simp [Cache.touchAll]
  | cons update rest ih =>
      cases update with
      | mk k v =>
          simp [Cache.touchAll, ih, entryCount_touch, Nat.add_assoc, Nat.add_left_comm, Nat.add_comm]

theorem keyCount_touchAll (updates : List (Nat × Nat)) (c : Cache) :
    (Cache.touchAll updates c).keyCount = c.keyCount + updates.length := by
  -- Plausible old-representation repair: tries to reuse the entry-count proof
  -- for key counts. The theorem statement is unchanged, but the proof gets the
  -- wrong field.
  exact entryCount_touchAll updates c

end LT201
