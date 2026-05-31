/-!
Template used by the Python grader for axiom auditing.

The actual audit file is generated in a temporary directory because each task
has a different module and declaration list:

```
import Task
#print axioms Namespace.target_theorem
```

`scripts/validate_task.py` parses the resulting axiom list and checks it
against `docs/axiom_policy.md`.
-/
