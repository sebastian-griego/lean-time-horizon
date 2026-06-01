# Accepted Task Cards

This generated report creates one reviewer card per `accepted_v0` task by joining metadata, difficulty-audit, task-quality, construct-validity, hidden-pin coverage, asset-manifest, validation-command, and local-QA evidence. It is a synthesis layer for review, not a new acceptance decision and not model-performance evidence.

The cards intentionally describe hidden checks by role, counts, and stage outcomes only. They do not copy hidden proof or hidden `PinCheck.lean` contents.

## Summary

- accepted task cards: `6`
- recommendations: `{"keep": 3, "keep_with_caveat": 3}`
- automation-dominated rows: `2/6`
- rows whose wrong controls exercise semantic hidden pins: `4/6`
- caveated accepted rows: `3/6`

## Card Index

| task | recommendation | bucket | automation | pin coverage | wrong stages | support | one-shot |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `lt-201` | keep_with_caveat | T2 | true | pins_not_exercised_by_wrongs | `{"public_stage": 2}` | task_level_with_caveat | maybe |
| `lt-203` | keep | T2 | false | semantic_pins_exercised | `{"hidden_pin": 2}` | task_level_internal_review_singleton_capability | maybe |
| `lt-202` | keep_with_caveat | T2 | false | pins_not_exercised_by_wrongs | `{"public_stage": 2}` | task_level_with_caveat | maybe |
| `lt-204` | keep | T2 | false | semantic_pins_exercised | `{"hidden_pin": 1, "public_stage": 1}` | task_level_internal_review | maybe |
| `lt-205` | keep | T3 | false | semantic_pins_exercised | `{"hidden_pin": 1, "public_stage": 1}` | task_level_internal_review | unlikely |
| `lt-206` | keep_with_caveat | T2 | true | semantic_pins_exercised | `{"hidden_pin": 1, "unknown": 1}` | task_level_with_caveat | maybe |

## Cards

### `lt-201` multi-file cache touchAll proof repair

- status: `keep_with_caveat` / `accepted_core_with_caveat`
- split/family/domain: `dev` / `proof_repair_codebase` / `multi_file_cache_api_change`
- time estimate: `T2` (`75`/`150` p50/p90 minutes)
- proof signal: `25` reference proof lines; automation dominated `true`; tactic profile `{"cases": 2, "induction": 2, "simp": 6}`
- one-shot likelihood and diagnostic value: `maybe` / `high`
- claimed capabilities: `theorem_decomposition`, `proof_debugging`, `codebase_navigation`
- construct support: `task_level_with_caveat`; limit: singleton capabilities cannot support capability-level generalization; accepted row carries a task-quality caveat; reference proof is automation-dominated
- hidden-pin evidence: `semantic` pins; role `signature_and_downstream_use_guard`; coverage `pins_not_exercised_by_wrongs`; wrong stages `{"public_stage": 2}`
- validation evidence: local QA `{"expected_failure": 2, "passed": 1}`; validation command kinds `reference_pass;wrong_fail:OldEntryOnly;wrong_fail:SingletonBatchOnly`
- asset evidence: prompt=1; public=2; metadata=1; hidden_reference=1; hidden_pincheck=1; wrong_submission=2
- reviewer note: accepted_v0_keep_with_caveat: reference proof is automation-dominated, but the task is retained for multi-file navigation, fixed API semantics, and generalized batch repair; needs independent review before any locked benchmark claim.
- benchmark-grade blocker: Retain in v0.1 only with the recorded caveat; collect independent human timing, full scaffold sweep evidence, and external QA before freeze. independent human timing; accepted-core scaffold sweep; hosted QA evidence; at least one more accepted task for singleton capabilities Fixed theorem statements make same-signature public-compiling wrong proofs structurally infeasible; hidden pins mainly guard signatures and downstream use.

### `lt-203` formalize exact list coverage modulo multiplicity

- status: `keep` / `accepted_core_retained`
- split/family/domain: `dev` / `informal_spec_to_formal` / `semantic_list_membership_relation`
- time estimate: `T2` (`90`/`180` p50/p90 minutes)
- proof signal: `30` reference proof lines; automation dominated `false`; tactic profile `{"constructor": 1, "exact": 7, "intro": 6, "rcases": 2, "rfl": 1, "simp": 2}`
- one-shot likelihood and diagnostic value: `maybe` / `high`
- claimed capabilities: `theorem_decomposition`, `semantic_formalization`, `proof_debugging`
- construct support: `task_level_internal_review_singleton_capability`; limit: singleton capabilities cannot support capability-level generalization
- hidden-pin evidence: `semantic` pins; role `semantic_positive_negative_guard`; coverage `semantic_pins_exercised`; wrong stages `{"hidden_pin": 2}`
- validation evidence: local QA `{"expected_failure": 2, "passed": 1}`; validation command kinds `reference_pass;wrong_fail:ListEquality;wrong_fail:Vacuous`
- asset evidence: prompt=1; public=1; metadata=1; hidden_reference=1; hidden_pincheck=1; wrong_submission=2
- reviewer note: accepted_v0: spec-to-formal task with hidden pins rejecting vacuous, equality-only, and duplicate-sensitive interpretations.
- benchmark-grade blocker: Collect independent timing, hosted QA, and accepted-core scaffold/model evidence before benchmark freeze. independent human timing; accepted-core scaffold sweep; hosted QA evidence; at least one more accepted task for singleton capabilities Mutable definitions have public-compiling wrong controls that exercise semantic hidden pins.

### `lt-202` Mathlib set image/preimage package

- status: `keep_with_caveat` / `accepted_core_with_caveat`
- split/family/domain: `test` / `direct_theorem_proving` / `mathlib_set_image_preimage`
- time estimate: `T2` (`90`/`180` p50/p90 minutes)
- proof signal: `46` reference proof lines; automation dominated `false`; tactic profile `{"constructor": 1, "exact": 9, "intro": 17, "rcases": 6, "rfl": 1, "rw": 3}`
- one-shot likelihood and diagnostic value: `maybe` / `medium_high`
- claimed capabilities: `library_search`, `theorem_decomposition`
- construct support: `task_level_with_caveat`; limit: singleton capabilities cannot support capability-level generalization; accepted row carries a task-quality caveat
- hidden-pin evidence: `mixed` pins; role `signature_and_downstream_use_guard`; coverage `pins_not_exercised_by_wrongs`; wrong stages `{"public_stage": 2}`
- validation evidence: local QA `{"expected_failure": 2, "passed": 1}`; validation command kinds `reference_pass;wrong_fail:MissingSurjectivity;wrong_fail:UnivOnlySurjectivity`
- asset evidence: prompt=1; public=1; metadata=1; hidden_reference=1; hidden_pincheck=1; wrong_submission=2
- reviewer note: accepted_v0_keep_with_caveat: Mathlib-adjacent theorem package requiring image/preimage API lookup, premise selection, and witness decomposition; hidden checks mostly protect fixed theorem signatures rather than semantic formalization choices.
- benchmark-grade blocker: Retain in v0.1 only with the recorded caveat; collect independent human timing, full scaffold sweep evidence, and external QA before freeze. independent human timing; accepted-core scaffold sweep; hosted QA evidence; at least one more accepted task for singleton capabilities Fixed theorem statements make same-signature public-compiling wrong proofs structurally infeasible; hidden pins mainly guard signatures and downstream use.

### `lt-204` capped-list optimizer invariant package

- status: `keep` / `accepted_core_retained`
- split/family/domain: `test` / `invariant_verification_ml_optimization` / `toy_projected_optimizer_list_state`
- time estimate: `T2` (`100`/`200` p50/p90 minutes)
- proof signal: `36` reference proof lines; automation dominated `false`; tactic profile `{"exact": 2, "induction": 3, "omega": 2, "simp": 6, "split": 2, "unfold": 2}`
- one-shot likelihood and diagnostic value: `maybe` / `high`
- claimed capabilities: `theorem_decomposition`, `invariant_design`, `long_horizon_construction`
- construct support: `task_level_internal_review`; limit: task-level evidence only; aggregate claims still require more accepted tasks and model data
- hidden-pin evidence: `semantic` pins; role `semantic_positive_negative_guard`; coverage `semantic_pins_exercised`; wrong stages `{"hidden_pin": 1, "public_stage": 1}`
- validation evidence: local QA `{"expected_failure": 2, "passed": 1}`; validation command kinds `reference_pass;wrong_fail:LengthAsSum;wrong_fail:LengthOnly`
- asset evidence: prompt=1; public=1; metadata=1; hidden_reference=1; hidden_pincheck=1; wrong_submission=2
- reviewer note: accepted_v0: optimizer-style invariant package with helper lemmas for cap bounds, list preservation, and sum monotonicity.
- benchmark-grade blocker: Collect independent timing, hosted QA, and accepted-core scaffold/model evidence before benchmark freeze. independent human timing; accepted-core scaffold sweep; hosted QA evidence Mutable definitions have public-compiling wrong controls that exercise semantic hidden pins.

### `lt-205` count-based bag library construction

- status: `keep` / `accepted_core_retained`
- split/family/domain: `test` / `small_formal_library_construction` / `list_bag_count_interface`
- time estimate: `T3` (`150`/`300` p50/p90 minutes)
- proof signal: `42` reference proof lines; automation dominated `false`; tactic profile `{"exact": 2, "induction": 1, "intro": 4, "omega": 1, "rfl": 2, "rw": 3, "simp": 6}`
- one-shot likelihood and diagnostic value: `unlikely` / `high`
- claimed capabilities: `theorem_decomposition`, `long_horizon_construction`
- construct support: `task_level_internal_review`; limit: task-level evidence only; aggregate claims still require more accepted tasks and model data
- hidden-pin evidence: `semantic` pins; role `semantic_positive_negative_guard`; coverage `semantic_pins_exercised`; wrong stages `{"hidden_pin": 1, "public_stage": 1}`
- validation evidence: local QA `{"expected_failure": 2, "passed": 1}`; validation command kinds `reference_pass;wrong_fail:LengthBagEq;wrong_fail:SetMembershipOnly`
- asset evidence: prompt=1; public=1; metadata=1; hidden_reference=1; hidden_pincheck=1; wrong_submission=2
- reviewer note: accepted_v0: T3 small library construction with dependent count lemmas and downstream BagEq reuse; expected to be hard one-shot.
- benchmark-grade blocker: Independently time at least one human solve and run the planned scaffold sweep before using this as long-horizon evidence. independent human timing; accepted-core scaffold sweep; hosted QA evidence; extra timing review for long-horizon bucket Mutable definitions have public-compiling wrong controls that exercise semantic hidden pins.

### `lt-206` partition/count correctness package

- status: `keep_with_caveat` / `accepted_core_with_caveat`
- split/family/domain: `test` / `algorithm_correctness` / `list_partition_multiplicity_invariant`
- time estimate: `T2` (`100`/`210` p50/p90 minutes)
- proof signal: `60` reference proof lines; automation dominated `true`; tactic profile `{"exact": 1, "induction": 4, "omega": 5, "simp": 14}`
- one-shot likelihood and diagnostic value: `maybe` / `high`
- claimed capabilities: `theorem_decomposition`, `invariant_design`, `long_horizon_construction`
- construct support: `task_level_with_caveat`; limit: accepted row carries a task-quality caveat; reference proof is automation-dominated
- hidden-pin evidence: `semantic` pins; role `semantic_positive_negative_guard`; coverage `semantic_pins_exercised`; wrong stages `{"hidden_pin": 1, "unknown": 1}`
- validation evidence: local QA `{"expected_failure": 2, "passed": 1}`; validation command kinds `reference_pass;wrong_fail:DropRightSide;wrong_fail:WeakAllGt`
- asset evidence: prompt=1; public=1; metadata=1; hidden_reference=1; hidden_pincheck=1; wrong_submission=2
- reviewer note: accepted_v0_keep_with_caveat: reference proof uses substantial simp/omega automation, but the task is retained for the multi-lemma partition invariant, side predicates, and duplicate-sensitive count preservation; needs independent review before any locked benchmark claim.
- benchmark-grade blocker: Retain in v0.1 only with the recorded caveat; collect independent human timing, full scaffold sweep evidence, and external QA before freeze. independent human timing; accepted-core scaffold sweep; hosted QA evidence Mutable definitions have public-compiling wrong controls that exercise semantic hidden pins.

## Interpretation

These cards make the accepted-core limitations harder to miss: proof-only fixed-statement tasks can be valid local proof-repair or Mathlib rows even when same-signature hidden-pin wrongs are structurally infeasible, while mutable-definition tasks should show public-compiling wrong controls that reach semantic pins. Stronger benchmark claims still require independent human timing, broader accepted-task scale, scaffold/provider sweeps, and hosted QA.
