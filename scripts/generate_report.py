from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def parse_list(value: str) -> list[str]:
    if not value:
        return []
    try:
        data = json.loads(value)
        if isinstance(data, list):
            return [str(x) for x in data]
    except json.JSONDecodeError:
        pass
    return [x.strip() for x in value.split(";") if x.strip()]


def write_bar_svg(path: Path, title: str, counts: dict[str, float], y_label: str = "count") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    labels = list(counts)
    values = [counts[k] for k in labels]
    max_value = max(values) if values else 1
    width = max(720, 120 * max(1, len(labels)))
    height = 420
    margin_l, margin_b, margin_t, margin_r = 80, 90, 50, 30
    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b
    bar_w = plot_w / max(1, len(labels)) * 0.72
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{width/2}" y="28" text-anchor="middle" font-family="Arial" font-size="18" fill="#111">{title}</text>',
        f'<line x1="{margin_l}" y1="{height-margin_b}" x2="{width-margin_r}" y2="{height-margin_b}" stroke="#333"/>',
        f'<line x1="{margin_l}" y1="{margin_t}" x2="{margin_l}" y2="{height-margin_b}" stroke="#333"/>',
        f'<text x="20" y="{height/2}" transform="rotate(-90 20 {height/2})" text-anchor="middle" font-family="Arial" font-size="12" fill="#333">{y_label}</text>',
    ]
    for i, (label, value) in enumerate(zip(labels, values)):
        x = margin_l + (i + 0.14) * plot_w / max(1, len(labels))
        h = 0 if max_value == 0 else value / max_value * plot_h
        y = height - margin_b - h
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{h:.1f}" fill="#3b82f6"/>')
        parts.append(f'<text x="{x + bar_w/2:.1f}" y="{y - 6:.1f}" text-anchor="middle" font-family="Arial" font-size="12" fill="#111">{value:g}</text>')
        parts.append(f'<text x="{x + bar_w/2:.1f}" y="{height-margin_b+18}" text-anchor="end" transform="rotate(-35 {x + bar_w/2:.1f} {height-margin_b+18})" font-family="Arial" font-size="11" fill="#333">{label}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_scatter_svg(path: Path, title: str, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 760, 420
    margin_l, margin_b, margin_t, margin_r = 80, 70, 50, 40
    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b
    points = [(float(r["human_minutes_p50"]), r["human_time_bucket"], r["family"]) for r in rows if r.get("human_minutes_p50")]
    max_x = max([p[0] for p in points] + [1])
    buckets = ["T0", "T1", "T2", "T3", "T4"]
    colors = {
        "algorithm_correctness": "#2563eb",
        "proof_repair_codebase": "#16a34a",
        "informal_spec_to_formal": "#dc2626",
        "invariant_verification_ml_optimization": "#9333ea",
        "small_formal_library_construction": "#d97706",
        "direct_theorem_proving": "#0891b2",
    }
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{width/2}" y="28" text-anchor="middle" font-family="Arial" font-size="18" fill="#111">{title}</text>',
        f'<line x1="{margin_l}" y1="{height-margin_b}" x2="{width-margin_r}" y2="{height-margin_b}" stroke="#333"/>',
        f'<line x1="{margin_l}" y1="{margin_t}" x2="{margin_l}" y2="{height-margin_b}" stroke="#333"/>',
        f'<text x="{width/2}" y="{height-20}" text-anchor="middle" font-family="Arial" font-size="12" fill="#333">human p50 minutes</text>',
        f'<text x="20" y="{height/2}" transform="rotate(-90 20 {height/2})" text-anchor="middle" font-family="Arial" font-size="12" fill="#333">time bucket</text>',
    ]
    for i, bucket in enumerate(buckets):
        y = margin_t + (len(buckets) - 1 - i) * plot_h / max(1, len(buckets) - 1)
        parts.append(f'<text x="{margin_l-10}" y="{y+4:.1f}" text-anchor="end" font-family="Arial" font-size="11" fill="#333">{bucket}</text>')
        parts.append(f'<line x1="{margin_l}" y1="{y:.1f}" x2="{width-margin_r}" y2="{y:.1f}" stroke="#eee"/>')
    for minutes, bucket, family in points:
        x = margin_l + (minutes / max_x) * plot_w
        y_index = buckets.index(bucket) if bucket in buckets else 0
        y = margin_t + (len(buckets) - 1 - y_index) * plot_h / max(1, len(buckets) - 1)
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{colors.get(family, "#555")}" opacity="0.82"><title>{family}: {minutes:g} min</title></circle>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n <= 0:
        return 0.0, 0.0
    p = successes / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def summarize_model_results(rows: list[dict[str, str]]) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        if row.get("qa_stage") == "local_qa":
            continue
        try:
            if int(row.get("infra_fail_count", "0")) > 0:
                continue
        except ValueError:
            continue
        try:
            grouped[row["scaffold"]].append(float(row["pass_at_k"]))
        except (KeyError, ValueError):
            continue
    summary: dict[str, dict[str, float]] = {}
    for scaffold, values in grouped.items():
        successes = sum(1 for value in values if value > 0)
        low, high = wilson_interval(successes, len(values))
        summary[scaffold] = {
            "mean": sum(values) / len(values) if values else 0.0,
            "successes": float(successes),
            "n": float(len(values)),
            "ci_low": low,
            "ci_high": high,
        }
    return summary


def bullets(counter: Counter[str]) -> str:
    return "\n".join(f"- `{k}`: {v}" for k, v in sorted(counter.items())) or "- _None_"


def task_table(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "_None._"
    lines = [
        "| task | split | family | bucket | p50/p90 | diagnostic role |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]
    for row in rows:
        note = row.get("difficulty_review_notes", "").replace("|", "/")
        lines.append(
            f"| `{row['task_id']}` | {row['split']} | {row['family']} | {row['human_time_bucket']} | "
            f"{row['human_minutes_p50']}/{row['human_minutes_p90']} | {note} |"
        )
    return "\n".join(lines)


def model_run_table(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "_None._"
    lines = [
        "| task | provider | model | scaffold | k | pass@k | failure | transcript |",
        "| --- | --- | --- | --- | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row.get('task_id', '')}` | {row.get('model', '')} | {row.get('model_version', '')} | "
            f"{row.get('scaffold', '')} | {row.get('k', '')} | {row.get('pass_at_k', '')} | "
            f"{row.get('failure_label', '')} | `{row.get('transcript_link', '')}` |"
        )
    return "\n".join(lines)


def evidence_table(rows: list[dict[str, str]], audit_by_id: dict[str, dict[str, str]]) -> str:
    if not rows:
        return "_None._"
    lines = [
        "| task | proof lines | automation dominated | hidden pins | wrongs | one-shot estimate | diagnostic value |",
        "| --- | ---: | --- | --- | ---: | --- | --- |",
    ]
    for row in rows:
        audit = audit_by_id.get(row["task_id"], {})
        lines.append(
            f"| `{row['task_id']}` | {audit.get('mechanical_reference_proof_lines', '?')} | "
            f"{audit.get('mechanical_automation_dominated', '?')} | "
            f"{audit.get('mechanical_hidden_pin_strength', '?')} | "
            f"{audit.get('mechanical_wrong_submission_count', '?')} | "
            f"{audit.get('manual_frontier_model_one_shot_likelihood', row.get('frontier_model_one_shot_likelihood', 'unknown'))} | "
            f"{audit.get('manual_diagnostic_value', row.get('diagnostic_value', 'unknown'))} |"
        )
    return "\n".join(lines)


def requirement_coverage_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`data/requirement_coverage.csv` has not been generated yet. Run "
            "`python scripts/audit_requirement_coverage.py --public-export public_tasks` "
            "after public export validation, then regenerate this report."
        )
    counts = Counter(row.get("status", "unknown") for row in rows)
    count_md = "\n".join(f"- `{status}`: {counts.get(status, 0)}" for status in ["supported", "partial", "not_met"])
    freeze_counts = Counter((row.get("freeze_relevance", "unspecified"), row.get("status", "unknown")) for row in rows)
    freeze_lines = []
    for freeze_relevance in sorted({row.get("freeze_relevance", "unspecified") for row in rows}):
        parts = [f"{status} {freeze_counts[(freeze_relevance, status)]}" for status in ["supported", "partial", "not_met"] if freeze_counts[(freeze_relevance, status)]]
        freeze_lines.append(f"- `{freeze_relevance}`: {', '.join(parts)}")
    freeze_md = "\n".join(freeze_lines) or "- _None_"
    gaps = [row for row in rows if row.get("status") != "supported"]
    if gaps:
        gap_lines = [
            "| id | area | freeze relevance | status | evidence | next step |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for row in gaps:
            evidence = row.get("evidence", "").replace("|", "/")
            next_step = row.get("gap_or_next_step", "").replace("|", "/")
            gap_lines.append(
                f"| `{row.get('requirement_id', '')}` | {row.get('area', '')} | {row.get('freeze_relevance', '')} | {row.get('status', '')} | "
                f"{evidence} | {next_step} |"
            )
        gap_md = "\n".join(gap_lines)
    else:
        gap_md = "_No partial or unmet requirements recorded._"
    return f"""`reports/requirement_coverage.md` and `data/requirement_coverage.csv` map the repository to the committed checklist in `data/benchmark_requirements.csv`. This is a stricter evidence index than the narrative claim ledger.

Status counts:

{count_md}

Freeze relevance counts:

{freeze_md}

Partial or unmet requirements:

{gap_md}
"""


def evaluation_protocol_section(plan_rows: list[dict[str, str]]) -> str:
    if not plan_rows:
        return (
            "`reports/evaluation_protocol.md` has not been generated yet. Run "
            "`python scripts/generate_evaluation_protocol.py`, then regenerate this report."
        )
    scaffold_counts = Counter(row.get("scaffold", "unknown") for row in plan_rows)
    task_count = len({row.get("task_id") for row in plan_rows})
    k_values = sorted({row.get("planned_k", "") for row in plan_rows})
    return f"""`reports/evaluation_protocol.md` defines the planned primary analysis before broad model sweeps are run. The primary plan is accepted-core tasks crossed with the scaffold ladder at fixed `k`.

- planned task count: `{task_count}`
- planned rows in `data/model_sweep_plan.csv`: `{len(plan_rows)}`
- planned k values: `{', '.join(k_values)}`
- scaffold row counts: `{compact_json(dict(sorted(scaffold_counts.items())))}`

The protocol specifies that headline capability claims use accepted-core rows only, local QA is validation evidence only, infra failures are retained but excluded from capability means, and binary task-row means should report numerators, denominators, and Wilson intervals.
"""


def model_analysis_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/model_run_analysis.md` has not been generated yet. Run "
            "`python scripts/analyze_model_results.py`, then regenerate this report."
        )
    by_id = {(row.get("analysis_set"), row.get("group_by"), row.get("group")): row for row in rows}
    primary = by_id.get(("primary_plan_coverage", "all", "all"), {})
    accepted = by_id.get(("accepted_core_results", "all", "all"), {})
    smoke = by_id.get(("all_provider_smoke_rows", "all", "all"), {})
    return f"""`reports/model_run_analysis.md` and `data/model_result_summary.csv` analyze committed provider rows against the planned primary sweep.

- planned accepted-core task/scaffold cells: `{primary.get('planned_cells', 0)}`
- planned cells with any committed accepted-core provider row: `{primary.get('covered_cells_any', 0)}`
- planned cells with a non-infra accepted-core provider row: `{primary.get('covered_cells_noninfra', 0)}`
- accepted-core provider rows: `{accepted.get('rows_total', 0)}` total, `{accepted.get('rows_noninfra', 0)}` non-infra
- accepted-core successes among non-infra provider rows: `{accepted.get('successes', 0)}`
- all committed provider smoke rows: `{smoke.get('rows_total', 0)}` total, `{smoke.get('rows_noninfra', 0)}` non-infra

The committed provider rows are smoke evidence only; the planned primary sweep remains mostly uncovered.
"""


def task_quality_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/task_quality_matrix.md` has not been generated yet. Run "
            "`python scripts/generate_task_quality_matrix.py`, then regenerate this report."
        )
    grade_counts = Counter(row.get("benchmark_grade_status", "unknown") for row in rows)
    role_counts = Counter(row.get("release_role", "unknown") for row in rows)
    accepted = [row for row in rows if row.get("release_role") == "accepted_core"]
    accepted_caveats = [row for row in accepted if row.get("benchmark_grade_status") == "accepted_core_with_caveat"]
    automation = [row for row in accepted if row.get("automation_dominated") == "true"]
    likely = [row for row in accepted if row.get("frontier_one_shot_likelihood") in {"likely", "very_likely"}]
    table_lines = [
        "| task | grade | bucket | proof lines | automation | pins | wrongs | one-shot | next action |",
        "| --- | --- | --- | ---: | --- | --- | ---: | --- | --- |",
    ]
    for row in accepted:
        action = row.get("next_review_action", "").replace("|", "/")
        table_lines.append(
            f"| `{row.get('task_id', '')}` | {row.get('benchmark_grade_status', '')} | "
            f"{row.get('human_time_bucket', '')} | {row.get('proof_lines', '')} | "
            f"{row.get('automation_dominated', '')} | {row.get('hidden_pin_strength', '')} | "
            f"{row.get('wrong_submission_count', '')} | {row.get('frontier_one_shot_likelihood', '')} | "
            f"{action} |"
        )
    return f"""`reports/task_quality_matrix.md` and `data/task_quality_matrix.csv` provide a generated one-row-per-task quality ledger joining metadata with difficulty-audit signals. This is meant for reviewer navigation; acceptance still comes from task metadata, validation, and `reports/accepted_task_review.md`.

- release roles: `{compact_json(dict(sorted(role_counts.items())))}`
- benchmark-grade statuses: `{compact_json(dict(sorted(grade_counts.items())))}`
- accepted-core caveat rows: `{len(accepted_caveats)}/{len(accepted)}`
- accepted-core automation-dominated rows: `{len(automation)}/{len(accepted)}`
- accepted-core likely/very-likely one-shot rows: `{len(likely)}/{len(accepted)}`

Accepted-core quality rows:

{chr(10).join(table_lines)}
"""


def one_line_command_result(value: object) -> str:
    if not isinstance(value, dict):
        return str(value)
    lines = value.get("stdout_first_line", [])
    if isinstance(lines, list) and lines:
        return str(lines[0]).strip()
    return f"exit {value.get('returncode', '?')}"


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def validation_manifest_section(manifest: dict) -> str:
    if not manifest:
        return (
            "## Validation Manifest\n\n"
            "`reports/validation_manifest.json` has not been generated yet. Run "
            "`python scripts/write_validation_manifest.py --public-export public_tasks` "
            "after the local validation gate passes, then regenerate this report.\n"
        )

    tool_versions = manifest.get("tool_versions", {})
    git = manifest.get("git", {})
    task_summary = manifest.get("task_summary", {})
    run_summary = manifest.get("run_result_summary", {})
    public_export = manifest.get("public_export", {})
    artifacts = manifest.get("artifacts", [])
    artifact_lines = [
        "| artifact | sha256 prefix | rows | bytes |",
        "| --- | --- | ---: | ---: |",
    ]
    for artifact in artifacts:
        if not artifact.get("exists"):
            artifact_lines.append(f"| `{artifact.get('path', '')}` | missing |  |  |")
            continue
        artifact_lines.append(
            f"| `{artifact.get('path', '')}` | `{str(artifact.get('sha256', ''))[:12]}` | "
            f"{artifact.get('row_count', '')} | {artifact.get('bytes', '')} |"
        )

    status_lines = git.get("status_short", [])
    status_md = "`clean`" if not status_lines else f"`{len(status_lines)} pre-commit path(s) recorded`"

    commands = manifest.get("regeneration_commands", [])
    command_md = "\n".join(f"{i}. `{command}`" for i, command in enumerate(commands, start=1)) or "_None recorded._"

    return f"""## Validation Manifest

`reports/validation_manifest.json` records the local toolchain, task/run counts, public-export summary, expected regeneration commands, and artifact hashes. The main report itself is intentionally omitted from the hash list to avoid a self-referential report hash.

Generated at UTC: `{manifest.get('generated_at_utc', 'unknown')}`

Git branch/head at generation: `{git.get('branch', 'unknown')}` / `{str(git.get('head', 'unknown'))[:12]}`. Worktree status at generation: {status_md}. The exact status lines are kept in the JSON manifest because this file is generated before the final commit.

Toolchain:

- Lean: `{one_line_command_result(tool_versions.get('lean', {}))}`
- Lake: `{one_line_command_result(tool_versions.get('lake', {}))}`
- Python: `{tool_versions.get('python', 'unknown')}`
- Platform: `{tool_versions.get('platform', 'unknown')}`

Task summary:

- total tasks in metadata: `{task_summary.get('task_count', 0)}`
- acceptance statuses: `{compact_json(task_summary.get('acceptance_status_counts', {}))}`
- run-result rows: `{run_summary.get('row_count', 0)}` total, `{run_summary.get('local_qa_row_count', 0)}` local QA, `{run_summary.get('model_sweep_row_count', 0)}` model-sweep
- public export: `{public_export.get('task_count', 0)}` tasks at `{public_export.get('relative_path', public_export.get('path', 'not recorded'))}`, hidden/wrong paths found: `{public_export.get('hidden_or_wrong_path_count', 'unknown')}`

Regeneration commands:

{command_md}

Key artifact hashes:

{chr(10).join(artifact_lines)}
"""


def main() -> int:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    run_rows = read_csv(ROOT / "data" / "run_results.csv")
    difficulty_rows = read_csv(ROOT / "data" / "difficulty_audit.csv")
    task_quality_rows = read_csv(ROOT / "data" / "task_quality_matrix.csv")
    requirement_rows = read_csv(ROOT / "data" / "requirement_coverage.csv")
    model_sweep_plan = read_csv(ROOT / "data" / "model_sweep_plan.csv")
    model_result_summary = read_csv(ROOT / "data" / "model_result_summary.csv")
    validation_manifest = read_json(ROOT / "reports" / "validation_manifest.json")
    audit_by_id = {row["task_id"]: row for row in difficulty_rows}
    metadata_by_id = {row["task_id"]: row for row in metadata}
    accepted = [row for row in metadata if row.get("acceptance_status") == "accepted_v0"]
    calibration = [row for row in metadata if row.get("acceptance_status") == "calibration_only"]
    rejected = [row for row in metadata if row.get("acceptance_status", "").startswith("rejected_")]
    pending = [row for row in metadata if row.get("acceptance_status") == "candidate_review_pending"]
    release = accepted + calibration

    figures = ROOT / "reports" / "figures"
    write_bar_svg(figures / "task_counts_by_family.svg", "Accepted v0 core tasks by family", dict(Counter(row["family"] for row in accepted)), "tasks")
    write_bar_svg(figures / "task_counts_by_bucket.svg", "Accepted and calibration tasks by human-time bucket", dict(Counter(row["human_time_bucket"] for row in release)), "tasks")
    skill_counts: Counter[str] = Counter()
    for row in release:
        skill_counts.update(parse_list(row.get("skills", "")))
    write_bar_svg(figures / "top_skills.svg", "Most common release-task skills", dict(skill_counts.most_common(10)), "tasks")
    if run_rows:
        write_bar_svg(figures / "run_rows_by_model.svg", "Committed QA/model rows by source", dict(Counter(row["model"] for row in run_rows)), "rows")
    write_scatter_svg(figures / "task_minutes_by_bucket.svg", "Release-task human time estimates", release)

    model_rows = [row for row in run_rows if row.get("qa_stage") != "local_qa"]
    accepted_model_rows = [row for row in model_rows if metadata_by_id.get(row.get("task_id", ""), {}).get("acceptance_status") == "accepted_v0"]
    model_summary = summarize_model_results(accepted_model_rows)
    infra_model_rows = [row for row in model_rows if row.get("infra_fail_count") not in {"", "0", 0}]
    model_failure_counts = Counter(row.get("failure_label", "unknown") for row in model_rows if row.get("failure_label") != "none")
    model_md = "\n".join(
        f"- `{scaffold}`: pass@k mean {stats['mean']:.2f} "
        f"({int(stats['successes'])}/{int(stats['n'])} rows; Wilson 95% CI {stats['ci_low']:.2f}-{stats['ci_high']:.2f})"
        for scaffold, stats in sorted(model_summary.items())
    ) or "- No accepted-core non-infra provider rows are committed. Local QA rows are validation evidence only."
    local_rows = [row for row in run_rows if row.get("qa_stage") == "local_qa"]
    local_md = f"{len(local_rows)} local QA rows are committed for reference solutions and plausible wrong submissions." if local_rows else "No local QA rows are committed yet."
    local_status_counts = Counter(row.get("qa_findings_status", "unknown") for row in local_rows)
    local_status_md = bullets(local_status_counts)

    report = ROOT / "reports" / "metr_style_report.md"
    report.write_text(
        f"""# Lean Time-Horizon Benchmark v0.1 Report

## Abstract

This repository is a v0.1 Lean time-horizon evaluation artifact for studying how far models get on realistic formalization and verification tasks as task horizon increases. It is not a locked benchmark. The release set contains {len(accepted)} accepted core tasks and {len(calibration)} calibration-only tasks. The remaining {len(rejected)} tasks are retained as a rejected archive, and {len(pending)} tasks remain pending review.

The accepted core set is intentionally smaller than the original target of 20. The original task batch was downgraded because many rows were dominated by `rfl`, `simp`, `omega`, `cases`, or one obvious library lemma. A stricter accepted-task review is maintained in `reports/accepted_task_review.md`; v0.1 keeps downgraded rows out of benchmark statistics unless they serve a calibration role.

## Research Questions

This artifact is designed to support three narrow evaluation questions:

1. Can a model recover the intended Lean proof or formalization from a public prompt and scaffold?
2. Which failures are diagnostic of time-horizon bottlenecks such as semantic formalization, theorem decomposition, proof debugging, codebase navigation, invariant design, or library/API search?
3. How much do scaffold affordances change outcomes, especially lookup and iterative compile/debug attempts?

The artifact is not yet suitable for population-level claims about frontier-model capability. It has limited task count, author-estimated human times, and only tiny smoke-model evidence.

## Unit Of Analysis And Scoring

The unit of analysis is a `(task, model, scaffold, k)` row. A task attempt is scored as pass only if the submitted Lean file:

- passes forbidden-construct scanning;
- compiles with the public scaffold files;
- compiles hidden `PinCheck.lean` against the submitted declarations;
- passes axiom audit on the metadata-listed declarations.

`successes_out_of_k` is the number of successful attempts among the allowed attempts for that row. `pass_at_k` is binary for that task row: `1.0` if any attempt succeeds and `0.0` otherwise. Local QA rows for reference solutions and wrong submissions are validation evidence, not model performance.

## Task Selection Protocol

Task status is assigned by metadata, not by directory alone:

- `accepted_v0`: core task retained after manual review and local validation.
- `calibration_only`: release task retained for lower-bound calibration, harness checks, or simple semantic-pin regression tests.
- `rejected_*`: archived task retained for auditability but excluded from release claims.
- `candidate_review_pending`: generated task not yet accepted.

Acceptance requires more than a passing reference solution: wrong submissions must fail, hidden checks must test meaningful behavior where possible, metadata must include human-time and diagnostic fields, and the accepted-task review must document known limitations. Tasks can be downgraded after review even when they validate.

## Accepted v0.1 Core Task Set

{task_table(accepted)}

## Accepted Core Evidence Matrix

{evidence_table(accepted, audit_by_id)}

## Calibration-Only Release Tasks

{task_table(calibration)}

## Calibration Evidence Matrix

{evidence_table(calibration, audit_by_id)}

## Portfolio Counts

Acceptance status:

{bullets(Counter(row.get("acceptance_status", "unspecified") for row in metadata))}

Accepted core families:

{bullets(Counter(row["family"] for row in accepted))}

Release human-time buckets:

{bullets(Counter(row["human_time_bucket"] for row in release))}

## What The Tasks Measure

The accepted core tasks are intended to test library/API search, theorem decomposition, semantic formalization, proof debugging, codebase navigation, invariant design, and small library construction. The calibration-only rows are retained to verify the harness, establish lower time-bucket behavior, and catch regressions in simple Lean proof generation.

Scaffold-sensitive tasks are marked in metadata. Lookup-sensitive rows include Mathlib image/preimage reasoning and semantic-list formalization. Iterative compile/debug sensitivity is expected for multi-file proof repair, invariant packages, and library-construction rows.

## Human-Time Estimates

Human-time buckets follow the project playbook:

- `T0`: 5-15 minutes.
- `T1`: 15-45 minutes.
- `T2`: 45-120 minutes.
- `T3`: 2-6 hours.
- `T4`: 6+ hours.

The p50/p90 estimates in metadata are reviewer estimates, not measured independent solves. The hard review downgraded three rows from accepted core to calibration-only because their proof surface and likely one-shot solvability did not justify accepted T2 status.

## Grader And Integrity Controls

The grader is Lean-first. For each submission it copies the public files listed in `metadata.json`, replaces the submission file, scans forbidden constructs, compiles public Lean files, compiles hidden semantic pins, and audits axioms on declared targets. Accepted and calibration tasks must have at least two wrong submissions.

Hidden pins check more than type signatures where possible: semantic formalization tasks include positive and negative examples; invariant tasks include edge cases and downstream bundled consequences; library tasks include downstream reuse through public lemmas. The grader still cannot prove that a task measures every intended cognitive skill, and it cannot replace human review of whether a task is too automation-dominated.

The axiom policy allows only the standard Lean axioms documented in `docs/axiom_policy.md`. Source-level escape hatches such as `sorry`, `admit`, `axiom`, `constant`, `unsafe`, custom elaboration, and command execution are rejected by the forbidden-construct scanner before Lean grading.

## Public Export

`scripts/export_public_tasks.py` exports the release set by default: `accepted_v0`, `calibration_only`, and pending candidates if any. It copies every file listed in metadata `public_files` plus `Prompt.md` and `metadata.json`. `scripts/validate_public_export.py` checks that hidden and wrong directories are absent, all public files are present, exported Lean files compile, and obvious hidden-reference path strings do not leak.

## Scaffold And Model-Run Support

The supported scaffold ladder is `one-shot`, `lookup`, and `lookup_unlimited`. Lookup is a real read-only command, `python scripts/lean_lookup.py QUERY`, which searches local Lean task files and installed Std/Mathlib files when available. External model runners receive `PROMPT_PATH`, `MODEL`, `TASK_ID`, `ATTEMPT_INDEX`, `SCAFFOLD`, `LEAN_LOOKUP_COMMAND`, `TASK_PUBLIC_DIR`, and `TASK_PUBLIC_FILES`.

## Evaluation Protocol

{evaluation_protocol_section(model_sweep_plan)}

## Model Result Analysis

{model_analysis_section(model_result_summary)}

## Committed Run Results

{local_md} These rows are not model performance and are excluded from benchmark pass-rate summaries.

Local QA row status:

{local_status_md}

Accepted-core provider row summary:

{model_md}

All committed non-local rows:

{model_run_table(model_rows)}

Model-sweep infra failures: {len(infra_model_rows)}. Infra-failure rows are retained in `data/run_results.csv` and transcripts, but excluded from pass-rate summaries.

No provider API credentials or runner commands are committed. To run a real smoke sweep, configure one of `OPENAI_LEAN_RUNNER`, `ANTHROPIC_LEAN_RUNNER`, `GEMINI_LEAN_RUNNER`, or `LEAN_MODEL_RUNNER` and use `scripts/run_model_sweep.py`.

Observed model-sweep failure labels:

{bullets(model_failure_counts)}

## Difficulty Audit Summary

The regenerated difficulty audit separates mechanical signals from manual judgments. Mechanical signals include reference proof lines, declaration count, public file count, public lemma count, tactic profile, automation dominance, Mathlib use, multi-file context, hidden pin strength, and wrong-submission count. Manual fields include frontier one-shot solvability estimates, p50/p90 human time, scaffold sensitivity, diagnostic value, and final accept/reject rationale.

## Accepted Task Review

`reports/accepted_task_review.md` records the per-task reviewer judgment for every row that was marked `accepted_v0` at the start of the hardening pass. It explicitly distinguishes keep, downgrade, and keep-with-caveat recommendations; checks whether buckets are deserved; audits hidden pins and wrong submissions; and lists what must change before each task can be treated as benchmark-grade.

## Task Quality Matrix

{task_quality_section(task_quality_rows)}

## Requirement Coverage Audit

{requirement_coverage_section(requirement_rows)}

## Reproducibility Checklist

The intended local regeneration gate is:

```powershell
lake build
python scripts/validate_all.py
python scripts/audit_difficulty.py
python scripts/generate_task_quality_matrix.py
python scripts/record_local_qa_results.py
python scripts/generate_evaluation_protocol.py
python scripts/analyze_model_results.py
python scripts/generate_report.py
python scripts/export_public_tasks.py --out public_tasks
python scripts/validate_public_export.py --out public_tasks
python scripts/audit_requirement_coverage.py --public-export public_tasks
python scripts/write_validation_manifest.py --public-export public_tasks
python scripts/generate_report.py
```

The public export validator checks that hidden references and wrong submissions are absent from `public_tasks`, all metadata-listed public files are present, exported Lean files compile, and obvious hidden-reference path strings do not leak.

{validation_manifest_section(validation_manifest)}

## Threats To Validity

Construct validity:

- Lean success is a strong signal for formal correctness of fixed theorems, but it does not by itself prove that a task measures the intended cognitive capability.
- Hidden semantic pins are finite probes. They reject known vacuous or weakened formalizations but cannot exhaustively characterize semantic equivalence.
- Fixed-statement proof tasks cannot always have a same-signature wrong answer that compiles publicly and then fails hidden semantic pins; if the theorem statement and definitions are fixed, a compiled proof is already semantically decisive.

Internal validity:

- Difficulty labels rely on author/reviewer estimates and mechanical proof profiles, not independent human solves.
- Automation-dominated references can understate model difficulty if models fail earlier on decomposition or API search, but they can also overstate benchmark quality if retained without caveats.
- The tiny committed provider smoke sweep is insufficient for performance claims and includes an infra-failure row.

External validity:

- v0.1 has only {len(accepted)} accepted core tasks and limited T3/T4 coverage.
- Most tasks are small Lean packages rather than large real-world formalization projects.
- Mathlib coverage is narrow.

Reliability and security:

- Validation is reproducible locally through committed scripts and CSVs, but hosted Taiga/Env Linter QA has not been run.
- API credentials are expected only through environment variables and are not part of the repo.

## Claim Ledger

| claim | current evidence | status |
| --- | --- | --- |
| Local references and wrong submissions validate as expected | `python scripts/validate_all.py`; `data/run_results.csv`; local QA transcripts | supported locally |
| Public task export excludes hidden material | `python scripts/export_public_tasks.py --out public_tasks`; `python scripts/validate_public_export.py --out public_tasks` | supported locally |
| Accepted core tasks are higher quality than the original pool | `reports/accepted_task_review.md`; `reports/difficulty_audit.md`; downgraded metadata statuses | supported by internal review |
| v0.1 is a locked benchmark | independent timing, hosted QA, broader model sweeps, and freeze review are missing | not supported |
| Reported model pass rates characterize frontier performance | only tiny smoke-sweep rows are committed | not supported |

## Limitations

- The v0.1 accepted core is below the 20-task target because the original pool did not meet the diagnostic-quality bar.
- The release has limited T3 coverage and no accepted T4 stretch task yet.
- Human-time estimates are author/reviewer estimates, not measured independent solves.
- Hidden pins are stronger than type checks, but they remain finite semantic probes.
- Only a tiny real provider smoke sweep is committed; it is adapter/proof-debugging evidence, not a benchmark performance claim.
- Hosted Taiga/Env Linter QA is not represented in this local artifact.
- The artifact is not a locked benchmark. The accepted rows still need independent human timing, broader scaffold data, and external QA before a freeze.

## Before Claiming A Locked Benchmark

The next step is to add more high-quality T2/T3/T4 tasks, run independent human review, execute real provider smoke sweeps across the scaffold ladder, run hosted QA, settle linter findings, and freeze exact public task versions.
""",
        encoding="utf-8",
    )
    print(f"wrote {report.relative_to(ROOT)} and figures under {figures.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
