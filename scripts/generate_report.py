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
    points = [(float(r["human_minutes_p50"]), r["human_time_bucket"], r["family"]) for r in rows]
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


def summarize_run_results(rows: list[dict[str, str]]) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        try:
            grouped[row["scaffold"]].append(float(row["successes_out_of_10"]) / 10.0)
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


def main() -> int:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    run_rows = read_csv(ROOT / "data" / "run_results.csv")

    family_counts = Counter(row["family"] for row in metadata)
    split_counts = Counter(row["split"] for row in metadata)
    bucket_counts = Counter(row["human_time_bucket"] for row in metadata)
    skill_counts: Counter[str] = Counter()
    for row in metadata:
        skill_counts.update(parse_list(row.get("skills", "")))

    figures = ROOT / "reports" / "figures"
    write_bar_svg(figures / "task_counts_by_family.svg", "Accepted tasks by family", dict(family_counts), "tasks")
    write_bar_svg(figures / "task_counts_by_bucket.svg", "Accepted tasks by human-time bucket", dict(bucket_counts), "tasks")
    write_bar_svg(figures / "top_skills.svg", "Most common required skills", dict(skill_counts.most_common(10)), "tasks")
    if run_rows:
        model_counts = Counter(row["model"] for row in run_rows)
        write_bar_svg(figures / "run_rows_by_model.svg", "Committed run-result rows by model/source", dict(model_counts), "rows")
    write_scatter_svg(figures / "task_minutes_by_bucket.svg", "Problem-level human time estimates", metadata)

    run_summary = summarize_run_results(run_rows)
    report = ROOT / "reports" / "metr_style_report.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    families_md = "\n".join(f"- `{k}`: {v}" for k, v in sorted(family_counts.items()))
    buckets_md = "\n".join(f"- `{k}`: {v}" for k, v in sorted(bucket_counts.items()))
    splits_md = "\n".join(f"- `{k}`: {v}" for k, v in sorted(split_counts.items()))
    run_md = "\n".join(
        f"- `{scaffold}`: mean score {stats['mean']:.2f} over {int(stats['n'])} committed rows, CI proxy {stats['ci95']:.2f}"
        for scaffold, stats in sorted(run_summary.items())
    ) or "- No committed model-sweep rows. Local QA rows can be generated with `python scripts/record_local_qa_results.py`."

    report.write_text(
        f"""# Lean Time-Horizon Benchmark Report

## Summary

This repository contains {len(metadata)} accepted Lean tasks for evaluating how far models get on realistic formalization and verification work as task horizon increases.

The split is:

{splits_md}

Task families:

{families_md}

Human-time buckets:

{buckets_md}

## Task Portfolio

The task set intentionally mixes algorithm correctness, proof repair, semantic formalization, invariant verification, small formal library construction, and a small direct theorem-proving slice. The benchmark is not designed as an olympiad theorem-proving set.

The current accepted set is Lean/Std-only and pinned to Lean 4.28.0. This keeps clean-checkout validation fast and reduces dependency drift, at the cost of excluding Mathlib-heavy domains from this first batch.

## Grading

Each accepted task has:

- a public prompt and public `Task.lean`
- hidden reference solution and hidden semantic pins
- at least one plausible wrong submission
- metadata with split, family, domain, human-time estimate, skills, scaffold sensitivity, and expected failures
- local validation through `scripts/validate_task.py`

The grader scans forbidden constructs before Lean runs, compiles the submitted task, compiles hidden pins against the submitted declarations, and audits axioms. The allowed axiom policy is documented in `docs/axiom_policy.md`.

## Scaffold Variants

The supported scaffold ladder is:

- `one-shot`: one submission, no lookup
- `lookup`: one submission with read-only Lean/Std lookup available
- `lookup_unlimited`: lookup plus iterative compile/debug attempts

`scripts/run_model_sweep.py` implements the scaffold loop and transcript/result writing. Provider-specific API calls are intentionally delegated to environment-configured commands so API keys remain outside the repo.

## Committed Results

Committed run-result rows currently summarize local QA or explicitly run sweeps only. They are not presented as frontier-model performance unless a real provider sweep has been run and committed.

{run_md}

## Figures

- `reports/figures/task_counts_by_family.svg`
- `reports/figures/task_counts_by_bucket.svg`
- `reports/figures/task_minutes_by_bucket.svg`
- `reports/figures/top_skills.svg`
- `reports/figures/run_rows_by_model.svg` when run-result rows exist

## Failure Taxonomy

Failures should be labeled with one primary label from `data/failure_labels.csv`. The most important expected labels for this batch are semantic formalization, hidden pin failure, proof debugging, library search, codebase navigation, invariant design, and theorem decomposition.

## Limitations

- No expensive frontier-model pass@10 sweep is committed by default. The repo includes the runner and schema; users can run real sweeps with environment-provided model commands.
- Hosted Taiga/Env Linter QA is not represented in this local artifact. The local gate enforces the playbook acceptance checklist, but hosted QA would still be required before platform delivery.
- Human-time estimates are author estimates with confidence notes, not second-reviewer measured times.
- The first accepted batch uses Lean/Std only. A future Mathlib batch should add richer algebra, analysis, and real verification codebases.

## Next Batch

The next increment should add Mathlib-backed tasks, at least one T3 codebase repair package, and real pass@10 model results across the three scaffold variants.
""",
        encoding="utf-8",
    )
    print(f"wrote {report.relative_to(ROOT)} and figures under {figures.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
