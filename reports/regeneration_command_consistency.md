# Regeneration Command Consistency Audit

This generated audit checks that the README validation block, the validation-manifest command source, and the committed validation manifest describe the same local regeneration gate. It also verifies that the shorter reviewer reproduction packet is a subset of that gate for local replay commands.

## Summary

- checks: `4`
- statuses: `{"pass": 4}`
- areas: `{"command_sequence": 2, "required_command_coverage": 1, "reviewer_reproduction": 1}`

## Check Table

| check | area | status | evidence | mismatches | required action |
| --- | --- | --- | --- | --- | --- |
| `readme_matches_manifest_source` | command_sequence | pass | readme_commands=86; source_commands=86; first_readme=['lake exe cache get', 'lake build', 'python scripts/validate_all.py']; last_readme=['python scripts/write_validation_manifest.py --public-export public_tasks', 'python scripts/audit_validation_manifest.py', 'python scripts/generate_report.py'] | `[]` | Update README.md and scripts/write_validation_manifest.py together whenever the local gate changes. |
| `json_manifest_matches_source` | command_sequence | pass | manifest_commands=86; source_commands=86; manifest_present=True | `[]` | Run scripts/write_validation_manifest.py after editing the regeneration command list. |
| `required_commands_in_public_gate` | required_command_coverage | pass | required=38; missing_readme=0; missing_source=0; missing_manifest=0 | `[]` | Keep the required-command set visible in both the README gate and validation manifest command list. |
| `reviewer_packet_local_subset` | reviewer_reproduction | pass | reviewer_rows=16; local_reviewer_commands=15; missing_from_full_gate=0 | `[]` | Keep reviewer local-replay commands as a subset of the full local regeneration gate. |

## Interpretation

`pass` means the local replay instructions are synchronized across the public README, the manifest producer, the committed manifest, and the reviewer reproduction packet's local replay subset. This audit does not prove the commands were run on a clean hosted environment; it only prevents stale or contradictory replay instructions.
