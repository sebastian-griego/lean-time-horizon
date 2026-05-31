import Task

namespace LT201

#check (keyCount_touch : ∀ c : Cache, ∀ k v : Nat,
  (Cache.touch k v c).keyCount = c.keyCount + 1)
#check (entryCount_touch : ∀ c : Cache, ∀ k v : Nat,
  (Cache.touch k v c).entryCount = c.entryCount + 1)
#check (keyCount_touchAll : ∀ updates : List (Nat × Nat), ∀ c : Cache,
  (Cache.touchAll updates c).keyCount = c.keyCount + updates.length)
#check (entryCount_touchAll : ∀ updates : List (Nat × Nat), ∀ c : Cache,
  (Cache.touchAll updates c).entryCount = c.entryCount + updates.length)

example (c : Cache) :
    (Cache.touchAll [(1, 10), (2, 20), (3, 30)] c).keyCount = c.keyCount + 3 := by
  simpa using keyCount_touchAll [(1, 10), (2, 20), (3, 30)] c

example (c : Cache) :
    (Cache.touchAll [(1, 10), (2, 20), (3, 30)] c).entryCount = c.entryCount + 3 := by
  simpa using entryCount_touchAll [(1, 10), (2, 20), (3, 30)] c

example (c : Cache) :
    (Cache.touch 4 40 c).keys = 4 :: c.keys := by
  rfl

example (c : Cache) :
    (Cache.touch 4 40 c).entries = (4, 40) :: c.entries := by
  rfl

end LT201
