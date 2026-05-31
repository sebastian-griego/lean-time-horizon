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
    return {
        scaffold: {
            "mean": sum(values) / len(values) if values else 0.0,
            "n": len(values),
            "ci95": 1.96 * math.sqrt((sum((v - (sum(values) / len(values))) ** 2 for v in values) / len(values)) / len(values)) if len(values) > 1 else 0.0,
        }
        for scaffold, values in grouped.items()
    }


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


def main() -> int:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    run_rows = read_csv(ROOT / "data" / "run_results.csv")
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

    model_summary = summarize_model_results(run_rows)
    model_rows = [row for row in run_rows if row.get("qa_stage") != "local_qa"]
    infra_model_rows = [row for row in model_rows if row.get("infra_fail_count") not in {"", "0", 0}]
    model_failure_counts = Counter(row.get("failure_label", "unknown") for row in model_rows if row.get("failure_label") != "none")
    model_md = "\n".join(
        f"- `{scaffold}`: pass@k mean {stats['mean']:.2f} over {int(stats['n'])} task rows, CI proxy {stats['ci95']:.2f}"
        for scaffold, stats in sorted(model_summary.items())
    ) or "- No real provider model-sweep rows are committed. Local QA rows are validation evidence only."
    local_rows = [row for row in run_rows if row.get("qa_stage") == "local_qa"]
    local_md = f"{len(local_rows)} local QA rows are committed for reference solutions and plausible wrong submissions." if local_rows else "No local QA rows are committed yet."

    report = ROOT / "reports" / "metr_style_report.md"
    report.write_text(
        f"""# Lean Time-Horizon Benchmark v0.1 Report

## Executive Summary

This repository is now organized as a v0.1 Lean time-horizon evaluation artifact rather than a raw candidate pool. The release set contains {len(accepted)} accepted core tasks and {len(calibration)} calibration-only tasks. The remaining {len(rejected)} tasks are retained as a rejected archive, and {len(pending)} tasks remain pending review.

The accepted core set is intentionally smaller than the original target of 20. The original task batch was downgraded because many rows were dominated by `rfl`, `simp`, `omega`, `cases`, or one obvious library lemma. v0.1 keeps those rows out of benchmark statistics unless they serve a calibration role.

## Accepted v0.1 Core Task Set

{task_table(accepted)}

## Calibration-Only Release Tasks

{task_table(calibration)}

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

## Grader And Integrity Controls

The grader is Lean-first. For each submission it copies the public files listed in `metadata.json`, replaces the submission file, scans forbidden constructs, compiles public Lean files, compiles hidden semantic pins, and audits axioms on declared targets. Accepted and calibration tasks must have at least two wrong submissions.

Hidden pins check more than type signatures where possible: semantic formalization tasks include positive and negative examples; invariant tasks include edge cases and downstream bundled consequences; library tasks include downstream reuse through public lemmas. The grader still cannot prove that a task measures every intended cognitive skill, and it cannot replace human review of whether a task is too automation-dominated.

## Public Export

`scripts/export_public_tasks.py` exports the release set by default: `accepted_v0`, `calibration_only`, and pending candidates if any. It copies every file listed in metadata `public_files` plus `Prompt.md` and `metadata.json`. `scripts/validate_public_export.py` checks that hidden and wrong directories are absent, all public files are present, exported Lean files compile, and obvious hidden-reference path strings do not leak.

## Scaffold And Model-Run Support

The supported scaffold ladder is `one-shot`, `lookup`, and `lookup_unlimited`. Lookup is a real read-only command, `python scripts/lean_lookup.py QUERY`, which searches local Lean task files and installed Std/Mathlib files when available. External model runners receive `PROMPT_PATH`, `MODEL`, `TASK_ID`, `ATTEMPT_INDEX`, `SCAFFOLD`, `LEAN_LOOKUP_COMMAND`, `TASK_PUBLIC_DIR`, and `TASK_PUBLIC_FILES`.

## Committed Run Results

{local_md} These rows are not model performance and are excluded from benchmark pass-rate summaries.

Real model-sweep rows:

{model_md}

{model_run_table(model_rows)}

Model-sweep infra failures: {len(infra_model_rows)}. Infra-failure rows are retained in `data/run_results.csv` and transcripts, but excluded from pass-rate summaries.

No provider API credentials or runner commands are committed. To run a real smoke sweep, configure one of `OPENAI_LEAN_RUNNER`, `ANTHROPIC_LEAN_RUNNER`, `GEMINI_LEAN_RUNNER`, or `LEAN_MODEL_RUNNER` and use `scripts/run_model_sweep.py`.

Observed model-sweep failure labels:

{bullets(model_failure_counts)}

## Difficulty Audit Summary

The regenerated difficulty audit separates mechanical signals from manual judgments. Mechanical signals include reference proof lines, declaration count, public file count, public lemma count, tactic profile, automation dominance, Mathlib use, multi-file context, hidden pin strength, and wrong-submission count. Manual fields include frontier one-shot solvability estimates, p50/p90 human time, scaffold sensitivity, diagnostic value, and final accept/reject rationale.

## Limitations

- The v0.1 accepted core is below the 20-task target because the original pool did not meet the diagnostic-quality bar.
- The release has limited T3 coverage and no accepted T4 stretch task yet.
- Human-time estimates are author/reviewer estimates, not measured independent solves.
- Hidden pins are stronger than type checks, but they remain finite semantic probes.
- Only a tiny real provider smoke sweep is committed; it is adapter/proof-debugging evidence, not a benchmark performance claim.
- Hosted Taiga/Env Linter QA is not represented in this local artifact.

## Before Claiming A Locked Benchmark

The next step is to add more high-quality T2/T3/T4 tasks, run independent human review, execute real provider smoke sweeps across the scaffold ladder, run hosted QA, settle linter findings, and freeze exact public task versions.
""",
        encoding="utf-8",
    )
    print(f"wrote {report.relative_to(ROOT)} and figures under {figures.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
