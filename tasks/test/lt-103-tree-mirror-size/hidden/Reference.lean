import Std

namespace LT103

inductive Tree where
  | leaf : Tree
  | node : Tree -> Nat -> Tree -> Tree
deriving Repr, DecidableEq

def size : Tree -> Nat
  | Tree.leaf => 0
  | Tree.node left _ right => 1 + size left + size right

def mirror : Tree -> Tree
  | Tree.leaf => Tree.leaf
  | Tree.node left x right => Tree.node (mirror right) x (mirror left)

theorem mirror_size (t : Tree) :
    size (mirror t) = size t := by
  induction t with
  | leaf =>
      simp [mirror, size]
  | node left x right ihLeft ihRight =>
      simp [mirror, size, ihLeft, ihRight, Nat.add_assoc, Nat.add_left_comm, Nat.add_comm]

end LT103
