# Scaffold Support Audit

This generated audit checks whether the scaffold ladder is implemented and reported safely. It verifies prompt/runner contracts, lookup command behavior, hidden-path exclusion, planned sweep coverage, observed provider coverage, and the report's scaffold-claim boundary.

## Summary

- checks: `11`
- statuses: `{"caution": 1, "pass": 10}`
- areas: `{"evaluation_protocol": 2, "lookup_integrity": 3, "reporting": 1, "runner_contract": 3, "scaffold_contract": 2}`

## Check Table

| check | area | status | evidence | risk or limit | next action |
| --- | --- | --- | --- | --- | --- |
| `scaffold_catalog_complete` | scaffold_contract | pass | scaffold rows=3; names=["lookup", "lookup_unlimited", "one-shot"]; mismatches=[]; extras=[]. | Catalog correctness does not by itself prove provider behavior. | Keep data/scaffold_variants.csv aligned with runner and protocol semantics. |
| `prompt_affordance_contract` | scaffold_contract | pass | {"lookup_mentions_lookup_command": true, "lookup_no_feedback_section": true, "one_shot_no_lookup": true, "sample_task": "lt-201", "unlimited_mentions_feedback": true, "unlimited_mentions_lookup": true} | This checks prompt construction, not whether a particular external model obeys the affordance. | Keep scaffold-specific prompt text explicit whenever runner semantics change. |
| `runner_env_contract` | runner_contract | pass | missing env keys=[]; provider env map complete=True. | External adapters still need provider-specific QA; this only verifies the runner contract. | Keep runner environment variables stable for provider adapters and transcripts. |
| `iterative_feedback_gate` | runner_contract | pass | lookup_unlimited-only feedback gate present=True. | Static check; it should be backed by provider smoke tests before performance claims. | Preserve feedback only for lookup_unlimited so lookup remains one-submission. |
| `attempt_count_semantics` | runner_contract | pass | attempt loop and k/success fields present=True. | This verifies runner bookkeeping structure; run_integrity_audit checks committed rows. | Keep k, attempts_completed, successes_out_of_k, and pass_at_k tied to the same attempt budget. |
| `lookup_roots_public_only` | lookup_integrity | pass | lookup roots=29; public task lean files=27; mathlib/std roots=1; hidden_or_wrong_roots=0. | Lookup still exposes public task scaffolds and installed library sources by design. | Never add tasks/ as a whole-tree root; include only metadata-listed public Lean files. |
| `lookup_command_smoke` | lookup_integrity | pass | {"hidden_or_wrong_line_count": 0, "line_count": 26, "query": "Set.image", "returncode": 0, "sample": ["C:\\Users\\sebas\\lean-time-horizon\\tasks\\test\\lt-202-mathlib-image-preimage\\Task.lean:6:    Set.Subset s (Set.preimage f (Set.image f s)) := by", "C:\\Users\\sebas\\lean-time-horizon\\tasks\\test\\lt-202-mathlib-image-preimage\\Task.lean:10:    Set.Subset (Set.image f (Set.preimage f t)) t := by", "C:\\Users\\sebas\\lean-time-horizon\\tasks\\test\\lt-202-mathlib-image-preimage\\Task.lean:15:    Set.preimage f (Set.image f s) = s := by"]} | A single query only proves the command is usable in this checkout. | Keep lookup command read-only and runnable without provider credentials. |
| `lookup_hidden_leak_scan` | lookup_integrity | pass | [{"hidden_or_wrong_line_count": 0, "line_count": 101, "query": "Set.image", "returncode": 0}, {"hidden_or_wrong_line_count": 0, "line_count": 0, "query": "PinCheck", "returncode": 0}] | This is a path-based leak scan over representative queries, not a proof over every possible query. | Keep hidden and wrong directories out of lookup roots and public exports. |
| `planned_sweep_coverage` | evaluation_protocol | pass | expected pairs=18; planned pairs=18; missing=[]; planned_k_values=["10"]. | A plan is not performance evidence. | Regenerate the evaluation protocol whenever accepted tasks or scaffold variants change. |
| `observed_scaffold_data_coverage` | evaluation_protocol | caution | non-infra accepted-provider rows=1; observed pairs=1/18; observed scaffolds=["one-shot"]. | This is intentionally expected to remain caution until real scaffold sweeps are committed. | Run accepted-core provider rows across one-shot, lookup, and lookup_unlimited before scaffold-effect claims. |
| `scaffold_claim_boundary` | reporting | pass | claim scaffold_effects=unsupported; decision scaffold_effect_claim=block. | The implementation can be audited without treating scaffold effects as measured. | Keep scaffold-effect claims blocked until observed scaffold coverage reaches the planned sweep. |

## Interpretation

`pass` means the local implementation or report boundary passes the audit. `caution` means the infrastructure exists but model-result coverage is incomplete. `fail` means scaffold or lookup behavior must be fixed before relying on the artifact.
