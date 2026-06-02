# Task Asset Manifest

This generated manifest records task-asset paths and hashes without embedding hidden proof contents. It supports reproducibility review, public-export checks, and future version-freeze decisions.

## Summary

- task count: `26`
- asset rows: `173`
- task statuses: `{"accepted_v0": 6, "calibration_only": 8, "rejected_duplicate": 2, "rejected_too_easy": 10}`
- asset roles: `{"hidden_pincheck": 26, "hidden_reference": 26, "metadata": 26, "prompt": 26, "public": 27, "wrong_submission": 42}`
- missing task assets: `0`
- release public assets missing from public export: `0`
- hidden/wrong assets present in public export: `0`
- accepted tasks with fewer than two wrong submissions: `0`
- accepted hidden reference gaps: `0`
- accepted hidden pincheck gaps: `0`

## Accepted Task Asset Coverage

| task | public assets | wrong submissions | hidden reference | hidden pincheck |
| --- | ---: | ---: | --- | --- |
| `lt-201` | 4 | 2 | true | true |
| `lt-202` | 3 | 2 | true | true |
| `lt-203` | 3 | 2 | true | true |
| `lt-204` | 3 | 3 | true | true |
| `lt-205` | 3 | 3 | true | true |
| `lt-206` | 3 | 2 | true | true |

## Hash Ledger

The full CSV at `data/task_asset_manifest.csv` contains one row per asset with byte count, line count, and SHA-256 hash. Hidden proof and pin contents are not copied into this report.
