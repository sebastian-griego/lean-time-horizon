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
      if x <= pivot then (x :: p.1, p.2) else (p.1, x :: p.2)

theorem partition_length (pivot : Nat) (xs : List Nat) :
    let p := partitionLE pivot xs
    p.1.length + p.2.length = xs.length := by
  sorry

theorem partition_left_allLe (pivot : Nat) (xs : List Nat) :
    let p := partitionLE pivot xs
    allLe pivot p.1 := by
  sorry

theorem partition_right_allGt (pivot : Nat) (xs : List Nat) :
    let p := partitionLE pivot xs
    allGt pivot p.2 := by
  sorry

theorem partition_count (pivot a : Nat) (xs : List Nat) :
    let p := partitionLE pivot xs
    count a p.1 + count a p.2 = count a xs := by
  sorry

theorem partition_spec (pivot : Nat) (xs : List Nat) :
    let p := partitionLE pivot xs
    And (p.1.length + p.2.length = xs.length)
      (And (allLe pivot p.1)
        (And (allGt pivot p.2)
          ((a : Nat) -> count a p.1 + count a p.2 = count a xs))) := by
  sorry

end LT206
