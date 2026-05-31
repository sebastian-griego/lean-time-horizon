import Task

namespace LT113

#check (append_empty : ∀ l : Log, Log.append l Log.empty = l)
#check (empty_append : ∀ l : Log, Log.append Log.empty l = l)
#check (append_assoc : ∀ a b c : Log,
  Log.append (Log.append a b) c = Log.append a (Log.append b c))
#check (length_append : ∀ a b : Log,
  (Log.append a b).length = a.length + b.length)

example : (Log.append (Log.singleton 1) (Log.singleton 2)).entries = [1, 2] := by
  rfl

example (a b c : Log) :
    (Log.append a (Log.append b c)).length = a.length + b.length + c.length := by
  rw [length_append, length_append]
  omega

end LT113
