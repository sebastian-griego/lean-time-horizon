# Overnight Progress Log

## Checkpoint 1: Repository orientation

- Read the project playbook, README, difficulty audit, task metadata, and METR-style report.
- Confirmed baseline repo was a validated candidate pool, not a v0.1 benchmark release.
- Found core gaps: no accepted statuses, only one wrong submission per task, incomplete public export, hardcoded difficulty audit, and local QA summarized too much like model performance.
- Blocker: none.

## Checkpoint 2: Infrastructure hardening

- Added status-aware validation for accepted and calibration tasks.
- Reworked public export to copy every metadata `public_files` entry.
- Added `scripts/validate_public_export.py`.
- Added read-only lookup support with `scripts/lean_lookup.py`.
- Added a minimal `scripts/anthropic_runner.py` adapter for real smoke sweeps when `ANTHROPIC_API_KEY` is available.
- Reworked difficulty audit generation to separate mechanical signals from metadata-based manual judgments.
- Reworked report generation so local QA rows are validation evidence, not model performance.
- Blocker: none.

## Checkpoint 3: Task release selection and hardening

- Promoted 9 core tasks to `accepted_v0`: `lt-105`, `lt-107`, `lt-108`, `lt-201`, `lt-202`, `lt-203`, `lt-204`, `lt-205`, and `lt-206`.
- Marked 5 tasks as `calibration_only`: `lt-001`, `lt-002`, `lt-003`, `lt-004`, and `lt-101`.
- Marked 12 weak or duplicate tasks as rejected archive rows.
- Added second wrong submissions for all accepted and calibration tasks.
- Strengthened hidden pins on accepted and calibration tasks with edge cases, downstream reuse, or semantic counterexamples.
- Added new accepted task `lt-206`, a partition/count algorithm-correctness package.
- Blocker: accepted core remains below the 20-task target and has only one T3 task; the report states this limitation rather than inflating weak rows.

## Checkpoint 4: Validation and runs

- `lake build` passed.
- `python scripts/validate_all.py` passed on 26 tasks after promotion and hardening.
- `python scripts/audit_difficulty.py` regenerated `data/difficulty_audit.csv` and `reports/difficulty_audit.md`.
- `python scripts/record_local_qa_results.py` wrote 66 local QA rows.
- Ran a tiny real Anthropic one-shot smoke sweep with `claude-sonnet-4-6`: `lt-001` passed, `lt-201` failed with proof-debugging after an initial adapter Unicode infra failure.
- `python scripts/generate_report.py` regenerated the METR-style report and figures.
- `python scripts/export_public_tasks.py --out public_tasks` exported 14 release tasks.
- `python scripts/validate_public_export.py --out public_tasks` passed after fixing multi-file export compilation.
- Blocker: no hosted Taiga/Env Linter QA was run in this local workflow.
