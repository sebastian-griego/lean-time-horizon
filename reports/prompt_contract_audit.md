# Prompt Contract Audit

This generated audit checks release task prompts against the playbook's public prompt standards. It evaluates the model-facing prompt as `Prompt.md` plus the runner scaffold wrapper, because the wrapper supplies scaffold-specific tool and attempt information.

## Summary

- release tasks audited: `14`
- statuses: `{"caution": 14}`
- families: `{"algorithm_correctness": 4, "direct_theorem_proving": 1, "informal_spec_to_formal": 4, "invariant_verification_ml_optimization": 1, "proof_repair_codebase": 3, "small_formal_library_construction": 1}`
- runner-supplied field counts: `{"attempt_limit": 14, "submission_format": 11, "tool_affordance": 14}`
- missing/caution field counts: `{}`
- prompt leak rows: `0`

## Task Table

| task | status | checks | runner-supplied fields | missing/caution fields | leaks |
| --- | --- | ---: | --- | --- | --- |
| `lt-001` | caution | 11/11 | `["attempt_limit", "tool_affordance"]` | `[]` | `[]` |
| `lt-002` | caution | 11/11 | `["attempt_limit", "tool_affordance"]` | `[]` | `[]` |
| `lt-003` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-004` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-201` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-203` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-101` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-105` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-107` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-108` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-202` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-204` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-205` | caution | 11/11 | `["attempt_limit", "submission_format", "tool_affordance"]` | `[]` | `[]` |
| `lt-206` | caution | 11/11 | `["attempt_limit", "tool_affordance"]` | `[]` | `[]` |

## Interpretation

`pass` means Prompt.md itself covers the checked contract fields and no leak pattern was found. `caution` usually means the runner wrapper supplies tool, attempt, or submission-format fields, or the prompt lacks an explicit import policy. `fail` means a required field or leak check failed.
