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

theorem mirror_size (t : Tree) (h : t = Tree.leaf) :
    size (mirror t) = size t := by
  subst t
  rfl

end LT103
