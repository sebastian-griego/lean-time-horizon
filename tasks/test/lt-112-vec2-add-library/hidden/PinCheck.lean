import Task

namespace LT112

#check (add_zero : ∀ v : Vec2, Vec2.add v Vec2.zero = v)
#check (zero_add : ∀ v : Vec2, Vec2.add Vec2.zero v = v)
#check (add_assoc : ∀ a b c : Vec2,
  Vec2.add (Vec2.add a b) c = Vec2.add a (Vec2.add b c))

example : Vec2.add { x := 1, y := 2 } { x := 3, y := 4 } = { x := 4, y := 6 } := by
  rfl

example (a b : Vec2) :
    Vec2.add a b = Vec2.add (Vec2.add Vec2.zero a) (Vec2.add b Vec2.zero) := by
  rw [zero_add, add_zero]

end LT112
