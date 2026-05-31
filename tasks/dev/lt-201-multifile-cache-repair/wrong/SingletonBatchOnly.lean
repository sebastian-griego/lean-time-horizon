import Model

namespace LT201

theorem keyCount_touch (c : Cache) (k v : Nat) :
    (Cache.touch k v c).keyCount = c.keyCount + 1 := by
  simp [Cache.touch, Cache.keyCount]

theorem entryCount_touch (c : Cache) (k v : Nat) :
    (Cache.touch k v c).entryCount = c.entryCount + 1 := by
  simp [Cache.touch, Cache.entryCount]

theorem keyCount_touchAll (updates : List (Nat × Nat)) (c : Cache) (h : updates.length <= 1) :
    (Cache.touchAll updates c).keyCount = c.keyCount + updates.length := by
  cases updates with
  | nil => simp [Cache.touchAll]
  | cons update rest =>
      cases rest with
      | nil =>
          cases update
          simp [Cache.touchAll, keyCount_touch]
      | cons update2 rest2 =>
          simp at h

theorem entryCount_touchAll (updates : List (Nat × Nat)) (c : Cache) (h : updates.length <= 1) :
    (Cache.touchAll updates c).entryCount = c.entryCount + updates.length := by
  cases updates with
  | nil => simp [Cache.touchAll]
  | cons update rest =>
      cases rest with
      | nil =>
          cases update
          simp [Cache.touchAll, entryCount_touch]
      | cons update2 rest2 =>
          simp at h

end LT201
