# Independent Review Status Audit

This generated audit checks whether the independent task-review packet is ready and whether any real non-author task reviews have been committed. It intentionally treats an empty review file as collection-ready but not as independent validation evidence.

## Summary

- checks: `5`
- statuses: `{"block": 1, "empty_ready": 1, "pass": 3}`

## Check Table

| check | area | status | evidence | limitation | next action |
| --- | --- | --- | --- | --- | --- |
| `review_plan_coverage` | packet | pass | accepted=6; plan_rows=6; template_rows=6; missing_plan=[]; missing_template=[] | The plan and template make review collection operational but do not prove reviews happened. | Regenerate scripts/generate_independent_review_packet.py after accepted task metadata changes. |
| `review_schema_and_template` | schema | pass | schema_required_fields=15; template_fields_ok=True; review_fields_ok=True; plan_fields=18 | Schema/template validity checks row shape, not review quality. | Keep schema, template, and audit in sync if review categories change. |
| `review_row_validity` | observations | pass | review_rows=0; validation_errors=0; examples=[] | Zero review rows is a valid empty-ready state; it does not satisfy independent review coverage. | Append real non-author review rows, then rerun this audit. |
| `accepted_review_coverage` | coverage | block | accepted reviewed=0/6; missing=["lt-201", "lt-202", "lt-203", "lt-204", "lt-205", "lt-206"]; review_rows=0 | Independent review coverage is absent until real non-author rows are committed. | Collect at least one non-author review row for every accepted_v0 task before freeze. |
| `review_recommendation_distribution` | observations | empty_ready | recommendations={}; review_rows=0 | No distributional review claim is supported without real rows and reviewer provenance. | Use recommendations only after rows are collected and checked against task evidence. |

## Interpretation

`pass` on packet checks means the collection workflow is ready. `block` on accepted-review coverage means the current repository still lacks independent non-author review evidence and should not upgrade accepted-task quality claims beyond internal review.
