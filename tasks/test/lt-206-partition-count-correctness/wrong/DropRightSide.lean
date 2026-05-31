import Std

namespace LT206

def allLe (pivot : Nat) : List Nat -> Prop
  | [] => True
  | x :: xs => x <= pivot ∧ allLe pivot xs

def allGt (pivot : Nat) : List Nat -> Prop
  | [] => True
  | x :: xs => pivot < x ∧ allGt pivot xs

def count (a : Nat) : List Nat -> Nat
  | [] => 0
  | x :: xs => (if x = a then 1 else 0) + count a xs

def partitionLE (pivot : Nat) : List Nat -> List Nat × List Nat
  | [] => ([], [])
  | x :: xs =>
      let p := partitionLE pivot xs
      if x <= pivot then (x :: p.1, p.2) else (p.1, p.2)

theorem partition_length (pivot : Nat) (xs : List Nat) :
    let p := partitionLE pivot xs
    p.1.length + p.2.length <= xs.length := by
  induction xs with
  | nil => simp [partitionLE]
  | cons x xs ih =>
      by_cases hx : x <= pivot <;> simp [partitionLE, hx, ih]

theorem partition_left_allLe (pivot : Nat) (xs : List Nat) :
    let p := partitionLE pivot xs
    allLe pivot p.1 := by
  induction xs with
  | nil => simp [partitionLE, allLe]
  | cons x xs ih =>
      by_cases hx : x <= pivot <;> simp [partitionLE, hx, allLe, ih]

theorem partition_right_allGt (pivot : Nat) (xs : List Nat) :
    let p := partitionLE pivot xs
    allGt pivot p.2 := by
  induction xs with
  | nil => simp [partitionLE, allGt]
  | cons x xs ih =>
      by_cases hx : x <= pivot <;> simp [partitionLE, hx, ih]

theorem partition_count (pivot a : Nat) (xs : List Nat) :
    let p := partitionLE pivot xs
    count a p.1 + count a p.2 <= count a xs := by
  induction xs with
  | nil => simp [partitionLE, count]
  | cons x xs ih =>
      by_cases hx : x <= pivot <;> by_cases hxa : x = a <;>
        simp [partitionLE, hx, count, hxa, ih]

theorem partition_spec (pivot : Nat) (xs : List Nat) :
    let p := partitionLE pivot xs
    And (p.1.length + p.2.length <= xs.length)
      (And (allLe pivot p.1)
        (And (allGt pivot p.2)
          ((a : Nat) -> count a p.1 + count a p.2 <= count a xs))) := by
  exact ⟨partition_length pivot xs, partition_left_allLe pivot xs,
    partition_right_allGt pivot xs, partition_count pivot⟩

end LT206
