# Run Result Integrity Audit

This generated audit checks `data/run_results.csv` against task metadata, known failure labels, pass@k arithmetic, score vectors, and JSONL transcript files. It is evidence for data hygiene only; it does not add model-performance evidence.

## Summary

- rows checked: `71`
- integrity statuses: `{"pass": 71}`
- qa stages: `{"local_qa": 68, "model_sweep": 3}`
- model/source rows: `{"anthropic": 3, "plausible_wrong:AllLeVacuous": 1, "plausible_wrong:AllSomeOnly": 1, "plausible_wrong:AppendInsteadOfReverse": 1, "plausible_wrong:BagEqTrivial": 1, "plausible_wrong:CountsAllEntries": 1, "plausible_wrong:DropRightSide": 1, "plausible_wrong:EmptyOnly": 1, "plausible_wrong:EndpointsOnly": 1, "plausible_wrong:FirstIncrementOnly": 1, "plausible_wrong:FirstPairOnly": 1, "plausible_wrong:FrontQueue": 1, "plausible_wrong:IdentityMap": 1, "plausible_wrong:IdentityProjection": 1, "plausible_wrong:LeafOnly": 1, "plausible_wrong:LengthAsSum": 1, "plausible_wrong:LengthBagEq": 1, "plausible_wrong:LengthInsteadOfSum": 1, "plausible_wrong:LengthOnly": 1, "plausible_wrong:ListEquality": 1, "plausible_wrong:MissingSurjectivity": 1, "plausible_wrong:NeedsExtraHyp": 1, "plausible_wrong:NoUpperClip": 1, "plausible_wrong:NonemptyHaystack": 1, "plausible_wrong:OldApiProof": 1, "plausible_wrong:OldEntryOnly": 1, "plausible_wrong:OnlySmallGrad": 1, "plausible_wrong:ProjectionAdd": 1, "plausible_wrong:ReverseAppend": 1, "plausible_wrong:Reversed": 1, "plausible_wrong:SetMembershipOnly": 1, "plausible_wrong:SingleIncrementOnly": 1, "plausible_wrong:SingletonBatchOnly": 1, "plausible_wrong:SpendAlwaysSubtract": 1, "plausible_wrong:UnivOnlySurjectivity": 1, "plausible_wrong:Vacuous": 4, "plausible_wrong:WeakAllGt": 1, "plausible_wrong:WeakHelper": 1, "plausible_wrong:Weakened": 2, "reference_solution": 26}`
- missing transcript files: `0`
- transcript parse failures: `0`
- pass@k arithmetic failures: `0`
- transcript consistency failures: `0`

## Failed Rows

_None._

## Warning Rows

_None._

## Interpretation

A passing row means the committed run-result row is internally consistent with its transcript and metadata. Provider rows remain smoke evidence unless the planned accepted-core scaffold sweep is actually covered.
