import Model

namespace LT201

theorem keyCount_touch (c : Cache) (k v : Nat) :
    (Cache.touch k v c).keyCount = c.keyCount + 1 := by
  sorry

theorem entryCount_touch (c : Cache) (k v : Nat) :
    (Cache.touch k v c).entryCount = c.entryCount + 1 := by
  sorry

theorem keyCount_touchAll (updates : List (Nat × Nat)) (c : Cache) :
    (Cache.touchAll updates c).keyCount = c.keyCount + updates.length := by
  sorry

theorem entryCount_touchAll (updates : List (Nat × Nat)) (c : Cache) :
    (Cache.touchAll updates c).entryCount = c.entryCount + updates.length := by
  sorry

end LT201
