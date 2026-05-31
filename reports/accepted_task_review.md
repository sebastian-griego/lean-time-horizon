# Accepted Task Review

This is a hard reviewer-style audit of the v0.1 tasks that were marked
`accepted_v0` at the start of this review pass:

`lt-105`, `lt-107`, `lt-108`, `lt-201`, `lt-202`, `lt-203`, `lt-204`,
`lt-205`, and `lt-206`.

The review applies the playbook standard that diagnostic validity matters more
than task count. A task is not benchmark-grade merely because it validates; it
must make model failures interpretable and be hard to game. The outcome of this
pass is intentionally stricter than `reports/difficulty_audit.md`: three small
accepted rows are downgraded to calibration-only, and retained rows carry
caveats where automation or finite hidden pins limit interpretability.

## Summary

| task | recommendation | post-review status | bucket review | one-shot likelihood | primary capability |
| --- | --- | --- | --- | --- | --- |
| `lt-201` | keep with caveat | `accepted_v0` | T2 is defensible but borderline; multi-file context is doing much of the work | maybe | codebase navigation plus generalized proof repair |
| `lt-203` | keep | `accepted_v0` | T2 is defensible for semantic formalization plus downstream lemmas | maybe | semantic formalization and theorem decomposition |
| `lt-105` | downgrade | `calibration_only` | T2 was too generous; T1 better matches the short automation-heavy proof | likely | lower-bound proof-repair calibration |
| `lt-107` | downgrade | `calibration_only` | T2 was too generous; compact two-lemma formalization is T1 | likely | lower-bound semantic-formalization calibration |
| `lt-108` | downgrade | `calibration_only` | T2 was too generous; recursive predicate design is useful but small | likely | lower-bound recursive-spec calibration |
| `lt-202` | keep with caveat | `accepted_v0` | T2 is defensible because Mathlib/API lookup dominates | maybe | Mathlib API search and witness decomposition |
| `lt-204` | keep | `accepted_v0` | T2 is defensible for a multi-helper invariant package | maybe | invariant design and helper-lemma composition |
| `lt-205` | keep | `accepted_v0` | T3 is plausible but lower-end; should be independently timed | unlikely | small library construction and interface reuse |
| `lt-206` | keep with caveat | `accepted_v0` | T2 is defensible, but proof is automation-heavy | maybe | algorithm invariant decomposition and multiplicity preservation |

## `lt-201` Multi-File Cache Repair

Recommendation: keep with caveat.

Human-time bucket: T2 is defensible but borderline. The Lean proof is not long,
but the task requires reading `Model.lean`, preserving the fixed `Cache.touch`
and `Cache.touchAll` semantics, and generalizing over the recursive cache state.

Reference proof automation: automation-dominated. The reference is mostly
induction, cases, and `simp`; this should not be presented as deep theorem
proving.

Hidden pins: adequate for the current task shape. Pins check theorem signatures,
batch count consequences, and direct `touch`/`touchAll` key and entry order
examples. Because `Model.lean` is fixed and not the submitted file, this is a
proof-repair task rather than a semantic-formalization task.

Wrong submissions: after this review, wrong files keep the target theorem
statements unchanged and fail because the proof repair is incomplete or uses the
wrong field, not because extra hypotheses were added. These are meaningful
proof-debugging failures. A same-signature solution that compiles publicly but
fails hidden semantic pins is not realistic here: with fixed definitions and
fixed theorem statements, a compiled proof is already semantically correct.

Likely frontier one-shot solvability: maybe. The proof idea is simple, but
models may fail by not generalizing the induction over `c` or by confusing
`keys` and `entries`.

Actually measures: codebase navigation, API preservation, generalized
structural induction, and compile-debug repair.

Before benchmark-grade: needs independent human timing and preferably a larger
API-change context where navigation matters more than `simp` cleanup.

## `lt-203` Exact Coverage Formalization

Recommendation: keep.

Human-time bucket: T2 is defensible. The reference proof is moderate, but the
task is mostly about choosing the right semantic relation, not proof length.

Reference proof automation: not automation-dominated. It uses constructors,
membership reasoning, and transitive composition rather than one large tactic.

Hidden pins: strong for v0.1. Duplicated examples were removed. Pins now reject
vacuous relations, exact-list equality, missing elements, and duplicate-sensitive
interpretations while allowing multiplicity-insensitive coverage.

Wrong submissions: meaningful. `Vacuous.lean` and `ListEquality.lean` keep the
public API shape and fail hidden semantic checks rather than relying on changed
theorem signatures.

Likely frontier one-shot solvability: maybe. A model can solve it if it infers
membership equivalence; common failures should be interpretable.

Actually measures: semantic formalization, hidden-pin debugging, theorem
decomposition around an interface, and membership reasoning.

Before benchmark-grade: add independent review of the natural-language prompt
and run a real scaffold comparison to see whether lookup or compile feedback is
the main bottleneck.

## `lt-105` Counter Batched Increment

Recommendation: downgrade.

Human-time bucket: T2 is not deserved. The corrected task is a T1 generalized
induction with arithmetic normalization; metadata was updated accordingly.

Reference proof automation: automation-dominated. The proof is short and mostly
`simp` after induction.

Hidden pins: useful but not enough for accepted-core status. Pins catch
first-element-only `sumList`/`incAll` semantics and simple batched examples.

Wrong submissions: improved. At least one wrong submission compiles publicly and
fails hidden semantic checks; the singleton-only proof failure now keeps theorem
signatures unchanged instead of adding an extra hypothesis.

Likely frontier one-shot solvability: likely.

Actually measures: lower-bound proof repair, accumulator generalization, and
whether the model preserves a batched API rather than singleton behavior.

Before benchmark-grade: expand into a real multi-file repair or add downstream
consumers whose proofs require the batched theorem; otherwise keep it as
calibration-only.

## `lt-107` Contains-All Formalization

Recommendation: downgrade.

Human-time bucket: T2 is not deserved. The target relation and two public lemmas
are compact; T1 is the honest bucket.

Reference proof automation: not automation-dominated, but very short.

Hidden pins: good for calibration. They catch vacuous and nonempty-haystack
relations, empty needle behavior, duplicate-insensitive membership, and missing
elements.

Wrong submissions: meaningful. Wrong definitions keep theorem signatures
unchanged and fail hidden semantic examples rather than type-shape checks.

Likely frontier one-shot solvability: likely.

Actually measures: basic semantic formalization and quantifier direction.

Before benchmark-grade: combine with more downstream lemmas or a richer spec
where the model must choose between multiple plausible formal statements.

## `lt-108` Adjacent Nondecreasing Spec

Recommendation: downgrade.

Human-time bucket: T2 is not deserved. Recursive predicate design is useful, but
the accepted proof surface is too small; T1 is more honest.

Reference proof automation: not automation-dominated, but only because the proof
is constructor-level and tiny.

Hidden pins: good for calibration. They catch vacuous definitions and
first-pair-only definitions by testing a tail violation.

Wrong submissions: meaningful. Wrong definitions keep theorem signatures
unchanged and fail hidden semantic pins.

Likely frontier one-shot solvability: likely.

Actually measures: lower-bound recursive predicate design and semantic
edge-case handling.

Before benchmark-grade: require more constructors/destructors or downstream
theorems, such as append/concat preservation under boundary conditions.

## `lt-202` Mathlib Image/Preimage Package

Recommendation: keep with caveat.

Human-time bucket: T2 is defensible. Difficulty comes from Mathlib set notation,
image/preimage API knowledge, injectivity/surjectivity premises, and witness
decomposition.

Reference proof automation: not automation-dominated. The proof is mostly
intro/rcases/rw/exact witness construction.

Hidden pins: adequate but not semantic in the formalization sense. The theorem
statements are fixed, so hidden checks mostly guard against changed statements
and exercise downstream examples.

Wrong submissions: after this review, wrong files keep theorem statements
unchanged and fail as proof/API reasoning failures. They do not compile publicly
and then fail hidden semantic pins, because a same-statement compiled proof of
these fixed theorems would be valid.

Likely frontier one-shot solvability: maybe, with strong lookup sensitivity.

Actually measures: Mathlib lookup, premise selection, set extensionality, and
existential witness construction.

Before benchmark-grade: add a more Mathlib-heavy companion task with less
obvious theorem names, or collect real scaffold data showing lookup separates
API discovery from proof reasoning.

## `lt-204` Capped-List Invariant

Recommendation: keep.

Human-time bucket: T2 is deserved. The task requires several helper lemmas
before the final bundled invariant.

Reference proof automation: not dominated by a single tactic, though `simp` and
`omega` do substantial local work.

Hidden pins: strengthened in this review. Pins now check all helper theorem
shapes, exact capped-list examples, zero-cap behavior, idempotent allLe reuse,
and the final bundled invariant.

Wrong submissions: meaningful. `LengthAsSum.lean` compiles publicly and fails
hidden semantic checks because it changes `sumList`; `LengthOnly.lean` keeps
the theorem signatures unchanged and fails as an identity-projection proof
failure.

Likely frontier one-shot solvability: maybe.

Actually measures: invariant design, helper-lemma decomposition, list induction,
and arithmetic proof repair.

Before benchmark-grade: add independent timing and consider a less direct public
lemma sequence so the model must design more of the invariant interface.

## `lt-205` Count-Based Bag Library

Recommendation: keep.

Human-time bucket: T3 is plausible but lower-end. The package has eight
dependent lemmas and downstream reuse, but the reference proof is still compact
for T3; independent timing is needed.

Reference proof automation: not mechanically automation-dominated, but it uses
`simp` and small arithmetic cleanup heavily.

Hidden pins: strengthened in this review. Pins check the helper theorem shapes,
positive and negative BagEq behavior, multiplicity sensitivity, union reuse, and
insertion behavior.

Wrong submissions: meaningful. `LengthBagEq.lean` compiles publicly and fails
hidden semantic checks because length equality is not multiplicity equality.
`SetMembershipOnly.lean` now keeps theorem signatures unchanged and fails
because set-style counts cannot prove the multiplicity theorems.

Likely frontier one-shot solvability: unlikely relative to the rest of v0.1.

Actually measures: small library construction, interface reuse, induction over
recursive counts, and avoiding set/multiset confusion.

Before benchmark-grade: add a second downstream consumer theorem or independent
human solve; T3 status should not rely only on author estimate.

## `lt-206` Partition/Count Correctness

Recommendation: keep with caveat.

Human-time bucket: T2 is deserved. It has several mutually reinforcing
properties: length preservation, side predicates, count preservation, and a
bundled final spec.

Reference proof automation: automation-dominated. The proof uses repeated
`simp`/`omega`; this should be reported plainly.

Hidden pins: strengthened in this review. Pins now include the final
`partition_spec` theorem shape, exact partition examples with duplicates,
side-predicate negative examples, count preservation, and bundled invariant
reuse.

Wrong submissions: meaningful enough for v0.1. `WeakAllGt.lean` compiles
publicly and fails hidden semantic pins because `allGt` is vacuous.
`DropRightSide.lean` keeps theorem signatures unchanged and fails because the
implementation drops right-side elements.

Likely frontier one-shot solvability: maybe.

Actually measures: algorithm correctness over a recursive partition, invariant
composition, duplicate-sensitive count preservation, and proof debugging around
branch-local arithmetic.

Before benchmark-grade: reduce reliance on automation or add a richer invariant
that cannot be closed mostly by `simp`/`omega`; collect independent timing.

## Overall Judgment

This v0.1 set is stronger after the review, but it is still not a locked
benchmark. The core set should be reported as a small, reviewed artifact with
known caveats:

- accepted core count is intentionally reduced;
- three useful but small tasks are calibration-only;
- retained proof-repair/direct-theorem tasks cannot always support
  same-signature public-compilation wrong answers that fail hidden semantic
  pins, because fixed theorem statements make compiled proofs semantically
  decisive;
- several tasks still need independent human timing and scaffold data.

