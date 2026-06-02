# Construct Validity Matrix

This generated matrix is a reviewer aid for construct validity. It links each accepted_v0 task to the diagnostic capabilities it is supposed to exercise, the mechanical evidence behind that claim, and the boundary on what the row can support. It is not model-performance evidence.

## Summary

- accepted task rows: `6`
- support levels: `{"task_level_internal_review": 2, "task_level_internal_review_singleton_capability": 1, "task_level_with_caveat": 3}`
- rows with singleton-covered capabilities: `3/6`
- automation-dominated accepted rows: `2/6`
- caveated accepted rows: `3/6`

## Capability Trace

| capability | accepted tasks | claim boundary |
| --- | ---: | --- |
| `library_search` | `lt-202` | singleton-covered; treat as design intent only |
| `theorem_decomposition` | `lt-201`, `lt-202`, `lt-203`, `lt-204`, `lt-205`, `lt-206` | represented by more than one accepted task, but still not a performance claim |
| `semantic_formalization` | `lt-203` | singleton-covered; treat as design intent only |
| `proof_debugging` | `lt-201`, `lt-203` | represented by more than one accepted task, but still not a performance claim |
| `codebase_navigation` | `lt-201` | singleton-covered; treat as design intent only |
| `invariant_design` | `lt-204`, `lt-206` | represented by more than one accepted task, but still not a performance claim |
| `long_horizon_construction` | `lt-204`, `lt-205`, `lt-206` | represented by more than one accepted task, but still not a performance claim |

## Accepted Task Construct Rows

| task | grade | capabilities | singleton caps | evidence | support | limit |
| --- | --- | --- | --- | --- | --- | --- |
| `lt-201` | accepted_core_with_caveat | `theorem_decomposition`, `proof_debugging`, `codebase_navigation` | `codebase_navigation` | family=proof_repair_codebase; bucket=T2; proof_lines=25; pins=semantic; wrongs=2; diagnostic=high | task_level_with_caveat | singleton capabilities cannot support capability-level generalization; accepted row carries a task-quality caveat; reference proof is automation-dominated |
| `lt-203` | accepted_core_retained | `theorem_decomposition`, `semantic_formalization`, `proof_debugging` | `semantic_formalization` | family=informal_spec_to_formal; bucket=T2; proof_lines=30; pins=semantic; wrongs=2; diagnostic=high | task_level_internal_review_singleton_capability | singleton capabilities cannot support capability-level generalization |
| `lt-202` | accepted_core_with_caveat | `library_search`, `theorem_decomposition` | `library_search` | family=direct_theorem_proving; bucket=T2; proof_lines=46; pins=mixed; wrongs=2; diagnostic=medium_high | task_level_with_caveat | singleton capabilities cannot support capability-level generalization; accepted row carries a task-quality caveat |
| `lt-204` | accepted_core_retained | `theorem_decomposition`, `invariant_design`, `long_horizon_construction` | _none_ | family=invariant_verification_ml_optimization; bucket=T2; proof_lines=36; pins=semantic; wrongs=3; diagnostic=high | task_level_internal_review | task-level evidence only; aggregate claims still require more accepted tasks and model data |
| `lt-205` | accepted_core_retained | `theorem_decomposition`, `long_horizon_construction` | _none_ | family=small_formal_library_construction; bucket=T3; proof_lines=42; pins=semantic; wrongs=3; diagnostic=high | task_level_internal_review | task-level evidence only; aggregate claims still require more accepted tasks and model data |
| `lt-206` | accepted_core_with_caveat | `theorem_decomposition`, `invariant_design`, `long_horizon_construction` | _none_ | family=algorithm_correctness; bucket=T2; proof_lines=60; pins=semantic; wrongs=2; diagnostic=high | task_level_with_caveat | accepted row carries a task-quality caveat; reference proof is automation-dominated |

## Interpretation

The matrix supports only a task-level construct-validity claim: the accepted tasks have documented intended capabilities and local evidence that those capabilities are plausibly exercised. It does not support capability-level performance claims, family-level generalization, or a robust time-horizon measurement claim. Singleton-covered capabilities, automation-dominated rows, and missing independent timing remain active limitations.
