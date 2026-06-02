# Model Sweep Execution Packet

This generated packet turns the planned accepted-core scaffold sweep into concrete provider-run commands and post-run evidence checks. It does not call provider APIs and does not create model results.

## Summary

- command rows: `12`
- scaffold command counts: `{"lookup": 4, "lookup_unlimited": 4, "one-shot": 4}`
- provider routes: `{"anthropic": 3, "command": 3, "gemini": 3, "openai": 3}`
- checklist statuses: `{"blocked": 3, "planned": 1, "ready": 3}`
- credentials policy: `all provider keys stay in environment variables; no secrets are committed`

## Pre-Run Setup

1. Run the local validation gate from `README.md` before starting a provider sweep.
2. Set exactly one runner command environment variable for the provider route under test.
3. Keep provider API keys in the shell environment only.
4. Run a one-task smoke command and inspect transcript output before a full accepted-core sweep.
5. Do not edit task prompts, public scaffolds, hidden checks, or accepted status between scaffold conditions for a reported model.

## Command Table

| provider | scaffold | runner env | k | full sweep command | smoke command |
| --- | --- | --- | ---: | --- | --- |
| `command` | `lookup` | `LEAN_MODEL_RUNNER` | 10 | `python scripts/run_model_sweep.py --provider command --model MODEL --scaffold lookup --attempts 10 --acceptance-status accepted_v0` | `python scripts/run_model_sweep.py --provider command --model MODEL --scaffold lookup --attempts 1 --task-id lt-201` |
| `anthropic` | `lookup` | `ANTHROPIC_LEAN_RUNNER` | 10 | `python scripts/run_model_sweep.py --provider anthropic --model MODEL --scaffold lookup --attempts 10 --acceptance-status accepted_v0` | `python scripts/run_model_sweep.py --provider anthropic --model MODEL --scaffold lookup --attempts 1 --task-id lt-201` |
| `openai` | `lookup` | `OPENAI_LEAN_RUNNER` | 10 | `python scripts/run_model_sweep.py --provider openai --model MODEL --scaffold lookup --attempts 10 --acceptance-status accepted_v0` | `python scripts/run_model_sweep.py --provider openai --model MODEL --scaffold lookup --attempts 1 --task-id lt-201` |
| `gemini` | `lookup` | `GEMINI_LEAN_RUNNER` | 10 | `python scripts/run_model_sweep.py --provider gemini --model MODEL --scaffold lookup --attempts 10 --acceptance-status accepted_v0` | `python scripts/run_model_sweep.py --provider gemini --model MODEL --scaffold lookup --attempts 1 --task-id lt-201` |
| `command` | `lookup_unlimited` | `LEAN_MODEL_RUNNER` | 10 | `python scripts/run_model_sweep.py --provider command --model MODEL --scaffold lookup_unlimited --attempts 10 --acceptance-status accepted_v0` | `python scripts/run_model_sweep.py --provider command --model MODEL --scaffold lookup_unlimited --attempts 1 --task-id lt-201` |
| `anthropic` | `lookup_unlimited` | `ANTHROPIC_LEAN_RUNNER` | 10 | `python scripts/run_model_sweep.py --provider anthropic --model MODEL --scaffold lookup_unlimited --attempts 10 --acceptance-status accepted_v0` | `python scripts/run_model_sweep.py --provider anthropic --model MODEL --scaffold lookup_unlimited --attempts 1 --task-id lt-201` |
| `openai` | `lookup_unlimited` | `OPENAI_LEAN_RUNNER` | 10 | `python scripts/run_model_sweep.py --provider openai --model MODEL --scaffold lookup_unlimited --attempts 10 --acceptance-status accepted_v0` | `python scripts/run_model_sweep.py --provider openai --model MODEL --scaffold lookup_unlimited --attempts 1 --task-id lt-201` |
| `gemini` | `lookup_unlimited` | `GEMINI_LEAN_RUNNER` | 10 | `python scripts/run_model_sweep.py --provider gemini --model MODEL --scaffold lookup_unlimited --attempts 10 --acceptance-status accepted_v0` | `python scripts/run_model_sweep.py --provider gemini --model MODEL --scaffold lookup_unlimited --attempts 1 --task-id lt-201` |
| `command` | `one-shot` | `LEAN_MODEL_RUNNER` | 10 | `python scripts/run_model_sweep.py --provider command --model MODEL --scaffold one-shot --attempts 10 --acceptance-status accepted_v0` | `python scripts/run_model_sweep.py --provider command --model MODEL --scaffold one-shot --attempts 1 --task-id lt-201` |
| `anthropic` | `one-shot` | `ANTHROPIC_LEAN_RUNNER` | 10 | `python scripts/run_model_sweep.py --provider anthropic --model MODEL --scaffold one-shot --attempts 10 --acceptance-status accepted_v0` | `python scripts/run_model_sweep.py --provider anthropic --model MODEL --scaffold one-shot --attempts 1 --task-id lt-201` |
| `openai` | `one-shot` | `OPENAI_LEAN_RUNNER` | 10 | `python scripts/run_model_sweep.py --provider openai --model MODEL --scaffold one-shot --attempts 10 --acceptance-status accepted_v0` | `python scripts/run_model_sweep.py --provider openai --model MODEL --scaffold one-shot --attempts 1 --task-id lt-201` |
| `gemini` | `one-shot` | `GEMINI_LEAN_RUNNER` | 10 | `python scripts/run_model_sweep.py --provider gemini --model MODEL --scaffold one-shot --attempts 10 --acceptance-status accepted_v0` | `python scripts/run_model_sweep.py --provider gemini --model MODEL --scaffold one-shot --attempts 1 --task-id lt-201` |

## Evidence Checklist

| check | phase | status | evidence | next action |
| --- | --- | --- | --- | --- |
| `local_validation_before_sweep` | pre_run | ready | run_integrity rows: 71; run_results rows: 71; failing rows: 0; report exists: True. | Run lake build, validate_all, public export validation, and run_integrity immediately before provider sweeps. |
| `provider_runner_contract` | pre_run | ready | provider readiness rows: 12; required checks covered: 12/12; failures: 0; cautions: 1; blocks: 1; report exists: True. | Set the relevant runner env var and provider API key in the shell only; run a one-task smoke command first. |
| `scaffold_ladder_contract` | pre_run | ready | scaffold audit rows: 11; required checks covered: 11/11; failures: 0; cautions: 1; report exists: True. | Keep one-shot, lookup, and lookup_unlimited prompt semantics fixed across provider runs. |
| `planned_primary_cells` | run | planned | accepted_tasks=6; planned_rows=18; scaffolds=["lookup", "lookup_unlimited", "one-shot"]; planned_k=["10"]; command_rows=12 | Run exactly the accepted_v0 x scaffold commands for each provider/model being reported. |
| `transcript_and_run_result_evidence` | post_run | blocked | Non-infra model rows: 2; scaffolds observed: ["one-shot"]; planned rows: 18. | Commit run_results rows and transcript JSONL files, regenerate the transcript queue, complete failure-label review rows, then rerun integrity, model-result analysis, and model-sweep coverage audit. |
| `frontier_claim_boundary` | post_run | blocked | Non-infra model rows: 2 over 6 accepted tasks; total model rows including infra failures: 3. | Keep frontier and scaffold-effect claims unsupported until non-infra accepted-core coverage is broad enough. |
| `statistical_report_refresh` | post_run | blocked | rows=9; statuses={"block": 5, "pass": 4} | Rerun statistical reporting after provider rows are committed; report raw n and Wilson intervals. |

## Post-Run Refresh

`post_run_commands` in `data/model_sweep_execution_commands.csv` records the regeneration chain to run after provider rows are appended. The report must keep scaffold-effect and frontier-performance claims blocked until run-result coverage, transcript integrity, and statistical reporting audits support them.
