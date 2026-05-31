import Task

namespace LT103

#check (mirror_size : ∀ t : Tree, size (mirror t) = size t)

def sample : Tree :=
  Tree.node (Tree.node Tree.leaf 1 Tree.leaf) 2 (Tree.node Tree.leaf 3 Tree.leaf)

example : size (mirror sample) = 3 := by
  rfl

example (t : Tree) : size (mirror (mirror t)) = size t := by
  rw [mirror_size, mirror_size]

end LT103
