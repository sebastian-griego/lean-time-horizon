import Task

namespace LT206

#check (partition_length : (pivot : Nat) -> (xs : List Nat) ->
  let p := partitionLE pivot xs
  p.1.length + p.2.length = xs.length)

#check (partition_left_allLe : (pivot : Nat) -> (xs : List Nat) ->
  let p := partitionLE pivot xs
  allLe pivot p.1)

#check (partition_right_allGt : (pivot : Nat) -> (xs : List Nat) ->
  let p := partitionLE pivot xs
  allGt pivot p.2)

#check (partition_count : (pivot a : Nat) -> (xs : List Nat) ->
  let p := partitionLE pivot xs
  count a p.1 + count a p.2 = count a xs)

example : partitionLE 3 [4, 1, 3, 2, 5] = ([1, 3, 2], [4, 5]) := by
  rfl

example : count 2 (partitionLE 2 [2, 3, 2, 1]).1 + count 2 (partitionLE 2 [2, 3, 2, 1]).2 = 2 := by
  rfl

example : ¬ allLe 3 [1, 4] := by
  intro h
  simp [allLe] at h

example : ¬ allGt 3 [4, 3] := by
  intro h
  simp [allGt] at h

example (pivot : Nat) (xs : List Nat) :
    let p := partitionLE pivot xs
    And (allLe pivot p.1) (allGt pivot p.2) := by
  exact ⟨partition_left_allLe pivot xs, partition_right_allGt pivot xs⟩

end LT206
