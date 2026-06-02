# Grader Hardening Audit

This generated audit probes local grading controls that are easy to overstate if only source files are listed: forbidden-construct scanning, false-positive controls, task-specific bans, grader stage ordering, axiom allowlist consistency, validation-command coverage, and local QA reference/wrong outcomes.

## Summary

- checks: `9`
- statuses: `{"pass": 9}`
- areas: `{"axiom_audit": 2, "forbidden_scanner": 3, "grader_pipeline": 1, "validation_manifest": 3}`

## Check Table

| check | area | status | evidence | hardening limit | next action |
| --- | --- | --- | --- | --- | --- |
| `default_forbidden_detection` | forbidden_scanner | pass | default_terms=15; detected_terms=15; missing_terms=[] | This probes scanner token matching, not every Lean syntax context where a term can appear. | Add regression cases whenever the forbidden list changes. |
| `comment_string_false_positive_control` | forbidden_scanner | pass | ignored_context_findings=[] | The scanner strips comments and strings but remains a lexical source scanner, not a full Lean parser. | Keep false-positive controls broad enough that prompts can mention banned constructs safely. |
| `task_specific_forbidden_control` | forbidden_scanner | pass | metadata_with_extra_forbidden=1; lt115_contains_omega=True; omega_findings=[{"column": 4, "line": 1, "term": "omega"}] | Only one archived direct-theorem row currently needs task-specific bans. | Use task-specific `extra_forbidden` whenever a shortcut would trivialize a task. |
| `grader_stage_order` | grader_pipeline | pass | forbidden_before_build=True; build_before_pin=True; pin_before_axiom=True | This is a source-order audit; full behavior is also covered by validate_all and local QA transcripts. | Preserve the order: copy public assets, scan forbidden constructs, compile public files, compile hidden pins, then audit axioms. |
| `axiom_policy_allowlist_match` | axiom_audit | pass | policy_axioms=["Classical.choice", "Quot.sound", "propext"]; grader_axioms=["Classical.choice", "Quot.sound", "propext"] | Allowlist equality does not prove each theorem is axiom-free beyond allowed Lean axioms; validate_task performs per-declaration checks. | Update docs/axiom_policy.md and validate_task.py together if the policy changes. |
| `release_axiom_declaration_coverage` | axiom_audit | pass | release_tasks=14; audited_decl_counts={"lt-001": 1, "lt-002": 1, "lt-003": 2, "lt-004": 2, "lt-101": 2, "lt-105": 2, "lt-107": 2, "lt-108": 3, "lt-201": 4, "lt-202": 5, "lt-203": 4, "lt-204": 6, "lt-205": 8, "lt-206": 5}; missing=[] | The audit checks metadata coverage, while validate_task checks actual axiom output during grading. | Require nonempty `axiom_audit_declarations` for every release task. |
| `validation_command_manifest_coverage` | validation_manifest | pass | expected_commands=68; actual_commands=68; missing=[]; extra=[] | The manifest lists validation commands; it does not prove they were run unless paired with validate_all output and run_integrity. | Regenerate validation_commands.csv with validate_all.py after task set changes. |
| `local_qa_reference_wrong_outcomes` | validation_manifest | pass | local_qa_rows=68; release_local_tasks=14/14; bad_references=[]; bad_wrongs=[] | Local QA rows are validation evidence only, not model-performance evidence. | Require reference rows to pass and plausible-wrong rows to fail before report regeneration. |
| `structural_validation_controls` | validation_manifest | pass | {"accepted_not_t0_t1": true, "record_local_scrubs_tmp_paths": true, "requires_review_notes": true, "requires_two_wrongs_for_release": true} | These are static controls; task validity still depends on human review and hidden pins. | Keep structural checks in validate_all.py aligned with acceptance policy. |

## Interpretation

`pass` means the local hardening control has concrete generated evidence. This audit does not prove the grader is impossible to game; it makes the current anti-gaming checks reviewable and keeps the remaining limits explicit.
