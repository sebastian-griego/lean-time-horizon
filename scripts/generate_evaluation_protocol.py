from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIMARY_K = 10

PLAN_FIELDS = [
    "task_id",
    "split",
    "family",
    "human_time_bucket",
    "scaffold",
    "planned_k",
    "analysis_set",
    "primary_endpoint",
    "sweep_command",
]

FAILURE_LABELS = [
    "none",
    "library_search",
    "premise_selection",
    "theorem_decomposition",
    "semantic_formalization",
    "hidden_pin_failure",
    "proof_debugging",
    "codebase_navigation",
    "invariant_design",
    "termination",
    "timeout",
    "reward_hack_attempt",
    "grader_false_negative",
    "infra_failure",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def write_plan(path: Path, accepted: list[dict[str, str]], scaffolds: list[str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for task in accepted:
        for scaffold in scaffolds:
            rows.append(
                {
                    "task_id": task["task_id"],
                    "split": task["split"],
                    "family": task["family"],
                    "human_time_bucket": task["human_time_bucket"],
                    "scaffold": scaffold,
                    "planned_k": PRIMARY_K,
                    "analysis_set": "primary_accepted_v0",
                    "primary_endpoint": "pass_at_k",
                    "sweep_command": (
                        "python scripts/run_model_sweep.py --provider command --model MODEL "
                        f"--scaffold {scaffold} --attempts {PRIMARY_K} --acceptance-status accepted_v0"
                    ),
                }
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PLAN_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def write_protocol(path: Path, accepted: list[dict[str, str]], calibration: list[dict[str, str]], scaffolds: list[dict[str, str]], plan_rows: list[dict[str, object]]) -> None:
    family_counts = Counter(task["family"] for task in accepted)
    bucket_counts = Counter(task["human_time_bucket"] for task in accepted)
    scaffold_names = [row["scaffold"] for row in scaffolds]
    command_lines = []
    for scaffold in scaffold_names:
        command_lines.extend(
            [
                "```powershell",
                (
                    "$env:LEAN_MODEL_RUNNER = \"python scripts/your_runner.py\"\n"
                    f"python scripts/run_model_sweep.py --provider command --model MODEL --scaffold {scaffold} "
                    f"--attempts {PRIMARY_K} --acceptance-status accepted_v0"
                ),
                "```",
                "",
            ]
        )
    labels = "\n".join(f"- `{label}`" for label in FAILURE_LABELS)
    plan_counts = Counter(row["scaffold"] for row in plan_rows)
    scaffold_table = "\n".join(
        f"| `{row['scaffold']}` | {row['lookup']} | {row['iterative_compile_feedback']} | {row['submission_limit']} | {row['description']} |"
        for row in scaffolds
    )
    protocol = f"""# Evaluation Protocol v0.1

This protocol defines how to turn the current local artifact into a defensible model-evaluation run. It does not claim that those model runs have happened. The current report remains a v0.1 audit artifact until the planned sweeps, independent timing review, and hosted QA are complete.

## Analysis Sets

- Primary analysis set: `accepted_v0` tasks only.
- Calibration set: `calibration_only` tasks, used for lower-bound checks and harness sanity, not headline capability claims.
- Excluded from capability claims: `rejected_*` tasks, infra-failure rows, local QA rows, and any task whose public export or hidden validation fails after the run.

Current primary set: `{len(accepted)}` accepted tasks. Family counts: `{compact_json(dict(sorted(family_counts.items())))}`. Human-time bucket counts: `{compact_json(dict(sorted(bucket_counts.items())))}`.

Current calibration set: `{len(calibration)}` tasks.

## Scaffold Ladder

| scaffold | lookup | iterative compile feedback | submission limit per attempt | description |
| --- | --- | --- | --- | --- |
{scaffold_table}

The primary sweep plan is every accepted task crossed with every scaffold at `k={PRIMARY_K}`. `data/model_sweep_plan.csv` contains `{len(plan_rows)}` planned rows: `{compact_json(dict(sorted(plan_counts.items())))}`.

## Primary Endpoint

The primary endpoint is task-level `pass_at_k` for `(task, model, scaffold, k)` rows:

- `successes_out_of_k` is the number of successful completed attempts in the row.
- `pass_at_k` is binary: `1.0` if `successes_out_of_k > 0`, else `0.0`.
- `attempts_completed` must equal `k` for ordinary pass@k rows unless the row is explicitly marked as an infra failure or aborted QA row.
- Local QA rows validate graders and wrong submissions; they are excluded from model capability summaries.

The runner now treats `--attempts {PRIMARY_K}` as `{PRIMARY_K}` independent attempts for `one-shot` and `lookup`. Only `lookup_unlimited` carries grader feedback from a failed attempt into the next attempt.

## Secondary Analyses

Report these only after the primary sweep exists:

- mean `pass_at_k` by scaffold over accepted tasks;
- mean `pass_at_k` by human-time bucket;
- mean `pass_at_k` by task family and required skill, when group sizes are large enough to state the denominator clearly;
- scaffold deltas for the same task set, especially `lookup - one-shot` and `lookup_unlimited - lookup`;
- timeout and infra-failure rates by scaffold/provider;
- primary failure-label counts by scaffold and task family.

Calibration rows may be reported separately to identify lower-bound behavior, but they must not be mixed into accepted-core pass-rate claims.

## Statistical Reporting

All estimates are task-row descriptive statistics until the benchmark has enough accepted tasks and independent timing review.

- Always report numerators and denominators, not just percentages.
- For binary task-row means, report Wilson 95% intervals when shown in tables.
- For family, bucket, or skill summaries, avoid interpreting groups with fewer than five accepted tasks as stable estimates.
- Do not tune task inclusion on test-set model results except to remove broken or invalid tasks with documented reasons.
- Infra-failure rows are retained in `data/run_results.csv`, counted in reliability summaries, and excluded from capability means.

## Failure Labeling Protocol

Each failed model row gets one primary label and optional secondary labels after transcript review. Use `data/failure_label_schema.json` for row shape and the following codebook:

{labels}

Labeling order:

1. Mark `infra_failure`, `timeout`, or `reward_hack_attempt` first when applicable.
2. If public Lean compilation passes but hidden pins fail, use `hidden_pin_failure` unless the transcript clearly shows a more specific semantic-formalization error.
3. Prefer `library_search` for missing API names, `premise_selection` for wrong available lemmas, and `theorem_decomposition` for failures to create viable intermediate goals.
4. Use `proof_debugging` for close Lean proofs with unresolved tactic/type errors.
5. Use `grader_false_negative` only after manual inspection shows the submitted solution is valid and the grader is wrong.

## Human-Time Calibration

Before freeze, each accepted task should receive independent timing evidence from at least one competent Lean user who did not author the task. Record:

- solver background;
- elapsed minutes to first accepted solution;
- whether lookup or compile/debug feedback was used;
- whether the prompt was ambiguous;
- any reason the metadata p50/p90 estimate should change.

Do not infer human time from model pass rates.

## Hosted QA And Freeze Criteria

Before claiming a locked benchmark:

1. Run the local regeneration gate from `README.md`.
2. Export and validate `public_tasks`.
3. Run the primary model-sweep plan or explicitly mark it as deferred.
4. Run hosted Taiga/Full Env QA and Env Linter on the exact intended public task versions.
5. Record hosted QA findings, fixes, and rebuttals in committed artifacts.
6. Freeze task versions only after warning/error/critical QA findings are fixed or rebutted.

## Planned Sweep Commands

Replace `MODEL` and `LEAN_MODEL_RUNNER` with the provider/model adapter under test. API keys must stay in environment variables and must not be committed.

{chr(10).join(command_lines).strip()}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(protocol, encoding="utf-8")


def main() -> int:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    scaffolds = read_csv(ROOT / "data" / "scaffold_variants.csv")
    accepted = [row for row in metadata if row.get("acceptance_status") == "accepted_v0"]
    calibration = [row for row in metadata if row.get("acceptance_status") == "calibration_only"]
    scaffold_names = [row["scaffold"] for row in scaffolds]
    plan_rows = write_plan(ROOT / "data" / "model_sweep_plan.csv", accepted, scaffold_names)
    write_protocol(ROOT / "reports" / "evaluation_protocol.md", accepted, calibration, scaffolds, plan_rows)
    print(f"wrote data/model_sweep_plan.csv with {len(plan_rows)} rows and reports/evaluation_protocol.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
