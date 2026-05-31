import Std

namespace LT112

structure Vec2 where
  x : Nat
  y : Nat
deriving Repr, DecidableEq

def Vec2.zero : Vec2 :=
  { x := 0, y := 0 }

def Vec2.add (a b : Vec2) : Vec2 :=
  { x := a.x + b.x, y := a.y + b.y }

theorem add_zero (v : Vec2) :
    Vec2.add v Vec2.zero = v := by
  cases v
  simp [Vec2.add, Vec2.zero]

theorem zero_add (v : Vec2) :
    Vec2.add Vec2.zero v = v := by
  cases v
  simp [Vec2.add, Vec2.zero]

theorem add_assoc (a b c : Vec2) :
    Vec2.add (Vec2.add a b) c = Vec2.add a (Vec2.add b c) := by
  cases a
  cases b
  cases c
  simp [Vec2.add, Nat.add_assoc]

end LT112
