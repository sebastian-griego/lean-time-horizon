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


def model_sweep_execution_section(command_rows: list[dict[str, str]], checklist_rows: list[dict[str, str]]) -> str:
    if not command_rows or not checklist_rows:
        return (
            "`reports/model_sweep_execution_packet.md` has not been generated yet. Run "
            "`python scripts/generate_model_sweep_packet.py`, then regenerate this report."
        )
    scaffold_counts = Counter(row.get("scaffold", "unknown") for row in command_rows)
    provider_counts = Counter(row.get("provider_route", "unknown") for row in command_rows)
    checklist_counts = Counter(row.get("current_status", "unknown") for row in checklist_rows)
    command_key_leaks = [
        row for row in command_rows
        if "API_KEY=" in row.get("full_sweep_command", "")
        or "API_KEY=" in row.get("smoke_command", "")
    ]
    checklist_lines = [
        "| check | phase | status | next action |",
        "| --- | --- | --- | --- |",
    ]
    for row in checklist_rows:
        action = row.get("next_action", "").replace("|", "/")
        checklist_lines.append(
            f"| `{row.get('check_id', '')}` | {row.get('phase', '')} | {row.get('current_status', '')} | {action} |"
        )
    return f"""`reports/model_sweep_execution_packet.md`, `data/model_sweep_execution_commands.csv`, and `data/model_sweep_execution_checklist.csv` turn the prospective scaffold sweep into concrete provider-route commands and post-run evidence checks without calling APIs or creating model results.

- command rows: `{len(command_rows)}`
- scaffold command counts: `{compact_json(dict(sorted(scaffold_counts.items())))}`
- provider routes: `{compact_json(dict(sorted(provider_counts.items())))}`
- checklist statuses: `{compact_json(dict(sorted(checklist_counts.items())))}`
- command rows with direct API-key assignments: `{len(command_key_leaks)}`

Model-sweep evidence checklist:

{chr(10).join(checklist_lines)}
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


def statistical_reporting_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/statistical_reporting_audit.md` has not been generated yet. Run "
            "`python scripts/audit_statistical_reporting.py`, then regenerate this report."
        )
    status_counts = Counter(row.get("status", "unknown") for row in rows)
    area_counts = Counter(row.get("area", "unknown") for row in rows)
    blocked = [row for row in rows if row.get("status") == "block"]
    failures = [row for row in rows if row.get("status") == "fail"]
    lines = [
        "| check | area | status | current sample | limitation | next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        current = row.get("current_sample", "").replace("|", "/")
        limitation = row.get("limitation", "").replace("|", "/")
        action = row.get("next_action", "").replace("|", "/")
        lines.append(
            f"| `{row.get('check_id', '')}` | {row.get('area', '')} | {row.get('status', '')} | "
            f"{current} | {limitation} | {action} |"
        )
    return f"""`reports/statistical_reporting_audit.md` and `data/statistical_reporting_audit.csv` check whether the committed provider rows can support the playbook's recommended performance plots and claims.

- checks: `{len(rows)}`
- statuses: `{compact_json(dict(sorted(status_counts.items())))}`
- areas: `{compact_json(dict(sorted(area_counts.items())))}`
- blocked performance outputs: `{len(blocked)}`
- failing statistical hygiene checks: `{len(failures)}`

Statistical reporting checks:

{chr(10).join(lines)}
"""


def provider_readiness_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/provider_readiness_audit.md` has not been generated yet. Run "
            "`python scripts/audit_provider_readiness.py` after model-result analysis, "
            "then regenerate this report."
        )
    status_counts = Counter(row.get("status", "unknown") for row in rows)
    area_counts = Counter(row.get("area", "unknown") for row in rows)
    failures = [row for row in rows if row.get("status") == "fail"]
    cautions = [row for row in rows if row.get("status") == "caution"]
    blocks = [row for row in rows if row.get("status") == "block"]
    lines = [
        "| check | area | status | current state | limitation | next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        current = row.get("current_state", "").replace("|", "/")
        limitation = row.get("limitation", "").replace("|", "/")
        action = row.get("next_action", "").replace("|", "/")
        lines.append(
            f"| `{row.get('check_id', '')}` | {row.get('area', '')} | {row.get('status', '')} | "
            f"{current} | {limitation} | {action} |"
        )
    return f"""`reports/provider_readiness_audit.md` and `data/provider_readiness_audit.csv` check model-runner readiness without using provider credentials or creating new model results. The audit separates runner contracts, adapter coverage, credential policy, transcript evidence, planned sweep commands, and smoke-only provider coverage.

- checks: `{len(rows)}`
- statuses: `{compact_json(dict(sorted(status_counts.items())))}`
- areas: `{compact_json(dict(sorted(area_counts.items())))}`
- failing readiness checks: `{len(failures)}`
- caution rows: `{len(cautions)}`
- blocked provider-evidence rows: `{len(blocks)}`

Provider readiness checks:

{chr(10).join(lines)}
"""


def hosted_qa_readiness_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/hosted_qa_readiness_audit.md` has not been generated yet. Run "
            "`python scripts/audit_hosted_qa_readiness.py` after public export validation, "
            "then regenerate this report."
        )
    status_counts = Counter(row.get("status", "unknown") for row in rows)
    area_counts = Counter(row.get("area", "unknown") for row in rows)
    failures = [row for row in rows if row.get("status") == "fail"]
    blocks = [row for row in rows if row.get("status") == "block"]
    lines = [
        "| check | area | status | current state | next action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        current = row.get("current_state", "").replace("|", "/")
        action = row.get("next_action", "").replace("|", "/")
        lines.append(
            f"| `{row.get('check_id', '')}` | {row.get('area', '')} | {row.get('status', '')} | "
            f"{current} | {action} |"
        )
    return f"""`reports/hosted_qa_readiness_audit.md` and `data/hosted_qa_readiness_audit.csv` distinguish local readiness from missing Taiga/hosted QA evidence.

- checks: `{len(rows)}`
- statuses: `{compact_json(dict(sorted(status_counts.items())))}`
- areas: `{compact_json(dict(sorted(area_counts.items())))}`
- blocked hosted-QA steps: `{len(blocks)}`
- failing local readiness checks: `{len(failures)}`

`block` rows are expected before upload and do not count as generated-script failures. They are evidence that hosted packaging, problem-version records, Full Env QA, Env Linter rows, and finding dispositions have not happened and must not be claimed.

Hosted QA readiness checks:

{chr(10).join(lines)}
"""


def threats_to_validity_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/threats_to_validity.md` has not been generated yet. Run "
            "`python scripts/generate_threats_to_validity.py`, then regenerate this report."
        )
    status_counts = Counter(row.get("current_status", "unknown") for row in rows)
    category_counts = Counter(row.get("category", "unknown") for row in rows)
    severity_counts = Counter(row.get("severity", "unknown") for row in rows)
    block_rows = [row for row in rows if row.get("current_status") == "block"]
    caution_rows = [row for row in rows if row.get("current_status") == "caution"]
    controlled_rows = [row for row in rows if row.get("current_status") == "controlled"]
    lines = [
        "| threat | category | severity | status | evidence | stronger evidence needed | claims limited |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        evidence = row.get("evidence", "").replace("|", "/")
        stronger = row.get("stronger_evidence_needed", "").replace("|", "/")
        claims = row.get("claims_limited", "").replace("|", "/")
        lines.append(
            f"| `{row.get('threat_id', '')}` | {row.get('category', '')} | {row.get('severity', '')} | "
            f"{row.get('current_status', '')} | {evidence} | {stronger} | {claims} |"
        )
    return f"""`reports/threats_to_validity.md` and `data/threats_to_validity.csv` convert the limitations section into a generated evidence register. `block` and `caution` rows are limitations on claims, not validation failures.

- threats: `{len(rows)}`
- statuses: `{compact_json(dict(sorted(status_counts.items())))}`
- categories: `{compact_json(dict(sorted(category_counts.items())))}`
- severities: `{compact_json(dict(sorted(severity_counts.items())))}`
- blocked validity threats: `{len(block_rows)}`
- caution validity threats: `{len(caution_rows)}`
- locally controlled threats: `{len(controlled_rows)}`

Threat register:

{chr(10).join(lines)}
"""


def run_integrity_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/run_integrity_audit.md` has not been generated yet. Run "
            "`python scripts/audit_run_integrity.py`, then regenerate this report."
        )
    status_counts = Counter(row.get("integrity_status", "unknown") for row in rows)
    qa_counts = Counter(row.get("qa_stage", "unknown") for row in rows)
    missing_transcripts = sum(1 for row in rows if row.get("transcript_exists") != "true")
    parse_failures = sum(1 for row in rows if row.get("transcript_parse_ok") != "true")
    arithmetic_failures = sum(1 for row in rows if row.get("arithmetic_ok") != "true")
    transcript_failures = sum(1 for row in rows if row.get("transcript_consistency_ok") != "true")
    failing = [row for row in rows if row.get("integrity_status") == "fail"]
    fail_md = "_None._"
    if failing:
        lines = [
            "| row | task | model | issue |",
            "| ---: | --- | --- | --- |",
        ]
        for row in failing[:12]:
            issue = row.get("issues", "").replace("|", "/")
            lines.append(f"| {row.get('row_index', '')} | `{row.get('task_id', '')}` | {row.get('model', '')} | {issue} |")
        fail_md = "\n".join(lines)
    return f"""`reports/run_integrity_audit.md` and `data/run_integrity_audit.csv` verify that committed run rows are internally consistent with task metadata, known failure labels, score vectors, pass@k semantics, and JSONL transcript files.

- rows checked: `{len(rows)}`
- integrity statuses: `{compact_json(dict(sorted(status_counts.items())))}`
- qa stages: `{compact_json(dict(sorted(qa_counts.items())))}`
- missing transcript files: `{missing_transcripts}`
- transcript parse failures: `{parse_failures}`
- pass@k arithmetic failures: `{arithmetic_failures}`
- transcript consistency failures: `{transcript_failures}`

Failing integrity rows:

{fail_md}
"""


def grader_hardening_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/grader_hardening_audit.md` has not been generated yet. Run "
            "`python scripts/audit_grader_hardening.py`, then regenerate this report."
        )
    status_counts = Counter(row.get("status", "unknown") for row in rows)
    area_counts = Counter(row.get("area", "unknown") for row in rows)
    failures = [row for row in rows if row.get("status") == "fail"]
    lines = [
        "| check | area | status | hardening limit | next action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        limit = row.get("hardening_limit", "").replace("|", "/")
        action = row.get("next_action", "").replace("|", "/")
        lines.append(
            f"| `{row.get('check_id', '')}` | {row.get('area', '')} | {row.get('status', '')} | "
            f"{limit} | {action} |"
        )
    return f"""`reports/grader_hardening_audit.md` and `data/grader_hardening_audit.csv` probe local anti-gaming controls: forbidden-construct scanner coverage, comment/string false-positive controls, task-specific bans, grader stage ordering, axiom allowlist consistency, validation-command coverage, and local QA reference/wrong outcomes.

- checks: `{len(rows)}`
- statuses: `{compact_json(dict(sorted(status_counts.items())))}`
- areas: `{compact_json(dict(sorted(area_counts.items())))}`
- failing hardening checks: `{len(failures)}`

Grader hardening checks:

{chr(10).join(lines)}
"""


def claim_evidence_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/claim_evidence_audit.md` has not been generated yet. Run "
            "`python scripts/audit_claim_evidence.py` after requirement coverage, then regenerate this report."
        )
    status_counts = Counter(row.get("support_status", "unknown") for row in rows)
    type_counts = Counter(row.get("claim_type", "unknown") for row in rows)
    lines = [
        "| claim | type | support | strength | claim text | limit | stronger claim requires |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        claim = row.get("claim", "").replace("|", "/")
        limit = row.get("counterevidence_or_limits", "").replace("|", "/")
        stronger = row.get("stronger_claim_requires", "").replace("|", "/")
        lines.append(
            f"| `{row.get('claim_id', '')}` | {row.get('claim_type', '')} | {row.get('support_status', '')} | "
            f"{row.get('evidence_strength', '')} | {claim} | {limit} | {stronger} |"
        )
    return f"""`reports/claim_evidence_audit.md` and `data/claim_evidence_audit.csv` map report claims to evidence strength and limits. This keeps local artifact-validity claims separate from performance and locked-benchmark claims.

- claims audited: `{len(rows)}`
- support statuses: `{compact_json(dict(sorted(status_counts.items())))}`
- claim types: `{compact_json(dict(sorted(type_counts.items())))}`

Claim support table:

{chr(10).join(lines)}
"""


def claim_authorization_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/claim_authorization_matrix.md` has not been generated yet. Run "
            "`python scripts/generate_claim_authorization_matrix.py` after claim evidence, "
            "then regenerate this report."
        )
    status_counts = Counter(row.get("authorization_status", "unknown") for row in rows)
    area_counts = Counter(row.get("claim_area", "unknown") for row in rows)
    lines = [
        "| claim | area | status | allowed wording | required caveat | forbidden wording |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        allowed = row.get("allowed_wording", "").replace("|", "/")
        caveat = row.get("required_caveat", "").replace("|", "/")
        forbidden = row.get("forbidden_wording", "").replace("|", "/")
        lines.append(
            f"| `{row.get('claim_id', '')}` | {row.get('claim_area', '')} | "
            f"{row.get('authorization_status', '')} | {allowed} | {caveat} | {forbidden} |"
        )
    return f"""`reports/claim_authorization_matrix.md` and `data/claim_authorization_matrix.csv` turn evidence audits into explicit report wording controls. This is stricter than the claim ledger: it records what wording is allowed, what caveat must travel with it, and what stronger wording is blocked.

- authorization rows: `{len(rows)}`
- authorization statuses: `{compact_json(dict(sorted(status_counts.items())))}`
- claim areas: `{compact_json(dict(sorted(area_counts.items())))}`

Claim authorization table:

{chr(10).join(lines)}
"""


def report_claim_conformance_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/report_claim_conformance_audit.md` has not been generated yet. Run "
            "`python scripts/audit_report_claim_conformance.py` after report generation, "
            "then regenerate this report."
        )
    status_counts = Counter(row.get("status", "unknown") for row in rows)
    scope_counts = Counter(row.get("scope", "unknown") for row in rows)
    lines = [
        "| check | scope | status | evidence | required action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        evidence = row.get("evidence", "").replace("|", "/")
        action = row.get("required_action", "").replace("|", "/")
        lines.append(
            f"| `{row.get('check_id', '')}` | {row.get('scope', '')} | {row.get('status', '')} | "
            f"{evidence} | {action} |"
        )
    return f"""`reports/report_claim_conformance_audit.md` and `data/report_claim_conformance_audit.csv` check that the concise report, detailed report, and README obey the claim-authorization matrix. The audit scans for missing caveats, blocked-claim phrase contexts, and report-shape drift.

- checks: `{len(rows)}`
- statuses: `{compact_json(dict(sorted(status_counts.items())))}`
- scopes: `{compact_json(dict(sorted(scope_counts.items())))}`

Claim-conformance checks:

{chr(10).join(lines)}
"""


def report_shape_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/report_shape_audit.md` has not been generated yet. Run "
            "`python scripts/audit_report_shape.py` after the concise report and claim-conformance audit, "
            "then regenerate this report."
        )
    status_counts = Counter(row.get("answer_status", "unknown") for row in rows)
    lines = [
        "| check | playbook question | answer status | evidence | limitation | next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        evidence = row.get("evidence", "").replace("|", "/")
        limitation = row.get("limitation", "").replace("|", "/")
        action = row.get("next_action", "").replace("|", "/")
        lines.append(
            f"| `{row.get('check_id', '')}` | {row.get('playbook_question', '')} | "
            f"{row.get('answer_status', '')} | {evidence} | {limitation} | {action} |"
        )
    return f"""`reports/report_shape_audit.md` and `data/report_shape_audit.csv` check whether the concise METR-style report answers the playbook's main report-shape questions. `blocked_by_evidence` rows are expected in v0.1 when the report explicitly says the current data cannot support a scaffold, time-horizon, or failure-distribution analysis.

- checks: `{len(rows)}`
- answer statuses: `{compact_json(dict(sorted(status_counts.items())))}`

Report-shape checks:

{chr(10).join(lines)}
"""


def release_decision_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/release_decision_log.md` has not been generated yet. Run "
            "`python scripts/generate_release_decision_log.py` after requirement and claim audits, "
            "then regenerate this report."
        )
    status_counts = Counter(row.get("status", "unknown") for row in rows)
    block_rows = [row for row in rows if row.get("status") == "block"]
    caution_rows = [row for row in rows if row.get("status") == "caution"]
    lines = [
        "| gate | scope | status | decision | next action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        decision = row.get("decision", "").replace("|", "/")
        action = row.get("required_next_action", "").replace("|", "/")
        lines.append(
            f"| `{row.get('gate_id', '')}` | {row.get('decision_scope', '')} | {row.get('status', '')} | "
            f"{decision} | {action} |"
        )
    return f"""`reports/release_decision_log.md` and `data/release_decision_log.csv` translate the evidence audits into explicit gate decisions. This is the report's operational conclusion: what can be used now, what requires caveats, and what is blocked.

- gates: `{len(rows)}`
- gate statuses: `{compact_json(dict(sorted(status_counts.items())))}`
- blocked stronger claims: `{len(block_rows)}`
- caution gates: `{len(caution_rows)}`

Decision table:

{chr(10).join(lines)}
"""


def freeze_readiness_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/freeze_readiness_roadmap.md` has not been generated yet. Run "
            "`python scripts/generate_freeze_readiness_roadmap.py` after requirement, claim, "
            "release, hosted-QA, and statistical audits, then regenerate this report."
        )
    status_counts = Counter(row.get("roadmap_status", "unknown") for row in rows)
    category_counts = Counter(row.get("category", "unknown") for row in rows)
    blockers = [row for row in rows if row.get("roadmap_status") == "block"]
    lines = [
        "| gate | category | status | exit criteria | next action | blocks claims |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        criteria = row.get("exit_criteria", "").replace("|", "/")
        action = row.get("concrete_next_action", "").replace("|", "/")
        blocks = row.get("blocks_claims", "").replace(";", ", ")
        lines.append(
            f"| `{row.get('gate_id', '')}` | {row.get('category', '')} | {row.get('roadmap_status', '')} | "
            f"{criteria} | {action} | `{blocks}` |"
        )
    return f"""`reports/freeze_readiness_roadmap.md` and `data/freeze_readiness_roadmap.csv` synthesize the requirement, claim, release-decision, hosted-QA, statistical, model-run, and metadata audits into concrete gates for turning the local v0.1 artifact into a locked benchmark. It is a planning ledger, not evidence that blocked gates are complete.

- gates: `{len(rows)}`
- roadmap statuses: `{compact_json(dict(sorted(status_counts.items())))}`
- categories: `{compact_json(dict(sorted(category_counts.items())))}`
- blocking gates before locked benchmark: `{len(blockers)}`

Freeze-readiness gates:

{chr(10).join(lines)}
"""


def scaffold_support_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/scaffold_support_audit.md` has not been generated yet. Run "
            "`python scripts/audit_scaffold_support.py`, then regenerate this report."
        )
    status_counts = Counter(row.get("status", "unknown") for row in rows)
    area_counts = Counter(row.get("area", "unknown") for row in rows)
    failures = [row for row in rows if row.get("status") == "fail"]
    cautions = [row for row in rows if row.get("status") == "caution"]
    lines = [
        "| check | area | status | evidence | next action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        evidence = row.get("evidence", "").replace("|", "/")
        action = row.get("required_next_action", "").replace("|", "/")
        lines.append(
            f"| `{row.get('check_id', '')}` | {row.get('area', '')} | {row.get('status', '')} | "
            f"{evidence} | {action} |"
        )
    return f"""`reports/scaffold_support_audit.md` and `data/scaffold_support_audit.csv` audit the scaffold ladder itself: prompt affordances, runner environment contract, attempt-count semantics, lookup safety, planned sweep coverage, observed provider coverage, and the boundary around scaffold-effect claims.

- checks: `{len(rows)}`
- statuses: `{compact_json(dict(sorted(status_counts.items())))}`
- areas: `{compact_json(dict(sorted(area_counts.items())))}`
- failing checks: `{len(failures)}`
- caution checks: `{len(cautions)}`

Scaffold audit table:

{chr(10).join(lines)}
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


def diagnostic_coverage_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/diagnostic_coverage_audit.md` has not been generated yet. Run "
            "`python scripts/audit_diagnostic_coverage.py` after the task quality matrix, "
            "then regenerate this report."
        )
    status_counts = Counter(row.get("status", "unknown") for row in rows)
    area_counts = Counter(row.get("area", "unknown") for row in rows)
    cautions = [row for row in rows if row.get("status") == "caution"]
    blocks = [row for row in rows if row.get("status") == "block"]
    failures = [row for row in rows if row.get("status") == "fail"]
    lines = [
        "| check | area | status | accepted tasks | diagnostic limit | next action |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for row in rows:
        limit = row.get("diagnostic_limit", "").replace("|", "/")
        action = row.get("next_action", "").replace("|", "/")
        lines.append(
            f"| `{row.get('check_id', '')}` | {row.get('area', '')} | {row.get('status', '')} | "
            f"{row.get('accepted_task_count', '')} | {limit} | {action} |"
        )
    return f"""`reports/diagnostic_coverage_audit.md` and `data/diagnostic_coverage_audit.csv` map accepted_v0 tasks to playbook task families, diagnostic capabilities, failure-label coverage, automation caveats, one-shot solvability balance, and construct-validity gaps.

- checks: `{len(rows)}`
- statuses: `{compact_json(dict(sorted(status_counts.items())))}`
- areas: `{compact_json(dict(sorted(area_counts.items())))}`
- caution rows: `{len(cautions)}`
- blocked construct-validity rows: `{len(blocks)}`
- failing data-integrity rows: `{len(failures)}`

Diagnostic coverage checks:

{chr(10).join(lines)}
"""


def human_time_calibration_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/human_time_calibration_audit.md` has not been generated yet. Run "
            "`python scripts/audit_human_time_calibration.py`, then regenerate this report."
        )
    status_counts = Counter(row.get("calibration_status", "unknown") for row in rows)
    bucket_counts = Counter(row.get("human_time_bucket", "unknown") for row in rows)
    accepted = [row for row in rows if row.get("acceptance_status") == "accepted_v0"]
    accepted_without_timing = [
        row for row in accepted
        if int(row.get("successful_independent_observation_count", "0") or "0") == 0
    ]
    issue_counts: Counter[str] = Counter()
    for row in rows:
        issue_counts.update(parse_list(row.get("issues", "")))
    table_lines = [
        "| task | bucket | p50/p90 | bucket range | status | timings | issues |",
        "| --- | --- | ---: | --- | --- | ---: | --- |",
    ]
    for row in accepted:
        table_lines.append(
            f"| `{row.get('task_id', '')}` | {row.get('human_time_bucket', '')} | "
            f"{row.get('human_minutes_p50', '')}/{row.get('human_minutes_p90', '')} | "
            f"{row.get('bucket_range_minutes', '')} | {row.get('calibration_status', '')} | "
            f"{row.get('successful_independent_observation_count', '')} | "
            f"`{row.get('issues', '')}` |"
        )
    return f"""`reports/human_time_calibration_audit.md` and `data/human_time_calibration_audit.csv` check that metadata p50 estimates fall inside their assigned bucket, p90 is not below p50, manual review status is recorded, and independent human timing observations are explicitly counted.

- tasks audited: `{len(rows)}`
- calibration statuses: `{compact_json(dict(sorted(status_counts.items())))}`
- task buckets: `{compact_json(dict(sorted(bucket_counts.items())))}`
- issue counts: `{compact_json(dict(sorted(issue_counts.items())))}`
- accepted-core tasks without successful independent timing: `{len(accepted_without_timing)}/{len(accepted)}`

Accepted-core human-time rows:

{chr(10).join(table_lines)}
"""


def human_timing_packet_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/human_timing_collection_packet.md` has not been generated yet. Run "
            "`python scripts/generate_human_timing_packet.py`, then regenerate this report."
        )
    bucket_counts = Counter(row.get("human_time_bucket", "unknown") for row in rows)
    family_counts = Counter(row.get("family", "unknown") for row in rows)
    hidden_leaks = [
        row for row in rows
        if "hidden" in row.get("validation_command", "").lower()
        or "Reference.lean" in row.get("validation_command", "")
    ]
    table_lines = [
        "| task | bucket | p50/p90 | condition | validation command |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in rows:
        condition = row.get("recommended_timing_condition", "").replace("|", "/")
        command = row.get("validation_command", "").replace("|", "/")
        table_lines.append(
            f"| `{row.get('task_id', '')}` | {row.get('human_time_bucket', '')} | "
            f"{row.get('human_minutes_p50', '')}/{row.get('human_minutes_p90', '')} | "
            f"{condition} | `{command}` |"
        )
    return f"""`reports/human_timing_collection_packet.md`, `data/human_timing_collection_plan.csv`, and `data/human_time_observations_template.csv` make independent timing collection operational without fabricating observations.

- accepted tasks in timing plan: `{len(rows)}`
- bucket counts: `{compact_json(dict(sorted(bucket_counts.items())))}`
- family counts: `{compact_json(dict(sorted(family_counts.items())))}`
- validation commands containing hidden-reference paths: `{len(hidden_leaks)}`

Accepted-task timing collection plan:

{chr(10).join(table_lines)}
"""


def transcript_review_packet_section(queue_rows: list[dict[str, str]]) -> str:
    if not queue_rows:
        return (
            "`reports/transcript_review_packet.md` has not been generated yet. Run "
            "`python scripts/generate_transcript_review_packet.py`, then regenerate this report."
        )
    priority_counts = Counter(row.get("review_priority", "unknown") for row in queue_rows)
    label_counts = Counter(row.get("failure_label_current", "unknown") for row in queue_rows)
    status_counts = Counter(row.get("qa_findings_status", "unknown") for row in queue_rows)
    missing_transcripts = [row for row in queue_rows if row.get("transcript_exists") != "true"]
    high_priority = [
        row for row in queue_rows
        if row.get("review_priority") in {"critical", "high"}
    ]
    table_lines = [
        "| priority | run id | task | scaffold | pass@k | current label | action |",
        "| --- | --- | --- | --- | ---: | --- | --- |",
    ]
    for row in queue_rows:
        action = row.get("review_action", "").replace("|", "/")
        table_lines.append(
            f"| {row.get('review_priority', '')} | `{row.get('run_id', '')}` | `{row.get('task_id', '')}` | "
            f"{row.get('scaffold', '')} | {row.get('pass_at_k', '')} | `{row.get('failure_label_current', '')}` | {action} |"
        )
    return f"""`reports/transcript_review_packet.md`, `data/transcript_review_queue.csv`, and `data/failure_label_review_template.csv` make failure-label review operational without fabricating adjudicated labels.

- queued non-local rows: `{len(queue_rows)}`
- review priorities: `{compact_json(dict(sorted(priority_counts.items())))}`
- current failure labels: `{compact_json(dict(sorted(label_counts.items())))}`
- QA finding statuses: `{compact_json(dict(sorted(status_counts.items())))}`
- missing transcript files in queue: `{len(missing_transcripts)}`
- high/critical review rows: `{len(high_priority)}`

Transcript review queue:

{chr(10).join(table_lines)}
"""


def task_asset_manifest_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/task_asset_manifest.md` has not been generated yet. Run "
            "`python scripts/generate_task_asset_manifest.py --public-export public_tasks`, then regenerate this report."
        )
    role_counts = Counter(row.get("asset_role", "unknown") for row in rows)
    status_counts = Counter(row.get("acceptance_status", "unknown") for row in rows if row.get("asset_role") == "metadata")
    missing = [row for row in rows if row.get("exists") != "true"]
    missing_export = [
        row for row in rows
        if row.get("public_export_expected") == "true" and row.get("public_export_exists") != "true"
    ]
    hidden_exported = [
        row for row in rows
        if (row.get("asset_role", "").startswith("hidden") or row.get("asset_role") == "wrong_submission")
        and row.get("public_export_exists") == "true"
    ]
    accepted = sorted({row.get("task_id", "") for row in rows if row.get("acceptance_status") == "accepted_v0"})
    wrong_counts = Counter(row.get("task_id", "") for row in rows if row.get("asset_role") == "wrong_submission")
    accepted_lines = [
        "| task | public assets | wrong submissions | hidden ref | pincheck |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for task_id in accepted:
        task_rows = [row for row in rows if row.get("task_id") == task_id]
        public_count = sum(1 for row in task_rows if row.get("asset_role") in {"metadata", "prompt", "public"})
        hidden_ref = next((row for row in task_rows if row.get("asset_role") == "hidden_reference"), {})
        pincheck = next((row for row in task_rows if row.get("asset_role") == "hidden_pincheck"), {})
        accepted_lines.append(
            f"| `{task_id}` | {public_count} | {wrong_counts.get(task_id, 0)} | "
            f"{hidden_ref.get('exists', 'missing')} | {pincheck.get('exists', 'missing')} |"
        )
    return f"""`reports/task_asset_manifest.md` and `data/task_asset_manifest.csv` provide a task-file-level hash ledger for prompts, metadata, public Lean files, hidden references, hidden pins, and wrong submissions. The report summarizes coverage without copying hidden proof contents.

- task count: `{len({row.get('task_id', '') for row in rows})}`
- asset rows: `{len(rows)}`
- task statuses: `{compact_json(dict(sorted(status_counts.items())))}`
- asset roles: `{compact_json(dict(sorted(role_counts.items())))}`
- missing task assets: `{len(missing)}`
- release public assets missing from public export: `{len(missing_export)}`
- hidden/wrong assets present in public export: `{len(hidden_exported)}`

Accepted task asset coverage:

{chr(10).join(accepted_lines)}
"""


def prompt_contract_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/prompt_contract_audit.md` has not been generated yet. Run "
            "`python scripts/audit_prompt_contracts.py`, then regenerate this report."
        )
    status_counts = Counter(row.get("status", "unknown") for row in rows)
    runner_counts: Counter[str] = Counter()
    missing_counts: Counter[str] = Counter()
    leak_rows = [row for row in rows if row.get("leak_patterns_found") != "[]"]
    failures = [row for row in rows if row.get("status") == "fail"]
    for row in rows:
        runner_counts.update(parse_list(row.get("runner_supplied_fields", "")))
        missing_counts.update(parse_list(row.get("missing_or_caution_fields", "")))
    table_lines = [
        "| task | status | checks | runner-supplied fields | missing/caution fields | leaks |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for row in rows:
        table_lines.append(
            f"| `{row.get('task_id', '')}` | {row.get('status', '')} | "
            f"{row.get('prompt_checks_passed', '')}/{row.get('prompt_checks_total', '')} | "
            f"`{row.get('runner_supplied_fields', '')}` | "
            f"`{row.get('missing_or_caution_fields', '')}` | "
            f"`{row.get('leak_patterns_found', '')}` |"
        )
    return f"""`reports/prompt_contract_audit.md` and `data/prompt_contract_audit.csv` audit release prompts against public prompt standards. The audit evaluates `Prompt.md` plus the runner wrapper because the wrapper supplies scaffold-specific lookup, attempt-limit, and submission-format instructions.

- prompt rows: `{len(rows)}`
- statuses: `{compact_json(dict(sorted(status_counts.items())))}`
- failing rows: `{len(failures)}`
- hidden-material leak rows: `{len(leak_rows)}`
- runner-supplied field counts: `{compact_json(dict(sorted(runner_counts.items())))}`
- missing/caution field counts: `{compact_json(dict(sorted(missing_counts.items())))}`

Prompt contract rows:

{chr(10).join(table_lines)}
"""


def pin_coverage_section(rows: list[dict[str, str]]) -> str:
    if not rows:
        return (
            "`reports/pin_coverage_audit.md` has not been generated yet. Run "
            "`python scripts/audit_pin_coverage.py` after local QA transcripts are regenerated, "
            "then regenerate this report."
        )
    grade_counts = Counter(row.get("pin_coverage_grade", "unknown") for row in rows)
    accepted = [row for row in rows if row.get("acceptance_status") == "accepted_v0"]
    accepted_with_hidden = sum(1 for row in accepted if int(row.get("wrongs_failing_hidden_pin_stage", "0") or 0) > 0)
    accepted_hidden = sum(int(row.get("wrongs_failing_hidden_pin_stage", "0") or 0) for row in accepted)
    accepted_public = sum(int(row.get("wrongs_failing_public_stage", "0") or 0) for row in accepted)
    feasibility_counts = Counter(row.get("same_signature_hidden_wrong_feasibility", "unknown") for row in accepted)
    role_counts = Counter(row.get("hidden_pin_role", "unknown") for row in accepted)
    table_lines = [
        "| task | grade | surface | hidden-pin role | same-signature hidden-wrong feasibility | public-stage wrongs | hidden-pin wrongs | note |",
        "| --- | --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in accepted:
        note = row.get("review_note", "").replace("|", "/")
        table_lines.append(
            f"| `{row.get('task_id', '')}` | {row.get('pin_coverage_grade', '')} | "
            f"{row.get('submission_surface', '')} | {row.get('hidden_pin_role', '')} | "
            f"{row.get('same_signature_hidden_wrong_feasibility', '')} | {row.get('wrongs_failing_public_stage', '')} | "
            f"{row.get('wrongs_failing_hidden_pin_stage', '')} | {note} |"
        )
    return f"""`reports/pin_coverage_audit.md` and `data/pin_coverage_audit.csv` make hidden-check evidence inspectable by separating public-stage wrong failures from wrong submissions that actually reach `PinCheck.lean`. It also classifies whether same-signature hidden wrongs are meaningful for the task surface: proof-only fixed-statement rows are already semantically certified by Lean if the fixed theorem compiles, while mutable-definition rows can have public-compiling semantic wrongs that hidden pins should catch.

- pin coverage grades: `{compact_json(dict(sorted(grade_counts.items())))}`
- accepted-core tasks with at least one hidden-pin wrong failure: `{accepted_with_hidden}/{len(accepted)}`
- accepted-core wrong failures at public stage: `{accepted_public}`
- accepted-core wrong failures at hidden-pin stage: `{accepted_hidden}`
- accepted-core same-signature hidden-wrong feasibility: `{compact_json(dict(sorted(feasibility_counts.items())))}`
- accepted-core hidden-pin roles: `{compact_json(dict(sorted(role_counts.items())))}`

Accepted-core hidden-pin coverage:

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
    diagnostic_coverage_rows = read_csv(ROOT / "data" / "diagnostic_coverage_audit.csv")
    human_time_rows = read_csv(ROOT / "data" / "human_time_calibration_audit.csv")
    human_timing_plan_rows = read_csv(ROOT / "data" / "human_timing_collection_plan.csv")
    transcript_review_queue_rows = read_csv(ROOT / "data" / "transcript_review_queue.csv")
    task_asset_rows = read_csv(ROOT / "data" / "task_asset_manifest.csv")
    prompt_contract_rows = read_csv(ROOT / "data" / "prompt_contract_audit.csv")
    pin_coverage_rows = read_csv(ROOT / "data" / "pin_coverage_audit.csv")
    run_integrity_rows = read_csv(ROOT / "data" / "run_integrity_audit.csv")
    grader_hardening_rows = read_csv(ROOT / "data" / "grader_hardening_audit.csv")
    claim_evidence_rows = read_csv(ROOT / "data" / "claim_evidence_audit.csv")
    claim_authorization_rows = read_csv(ROOT / "data" / "claim_authorization_matrix.csv")
    report_claim_conformance_rows = read_csv(ROOT / "data" / "report_claim_conformance_audit.csv")
    report_shape_rows = read_csv(ROOT / "data" / "report_shape_audit.csv")
    release_decision_rows = read_csv(ROOT / "data" / "release_decision_log.csv")
    freeze_readiness_rows = read_csv(ROOT / "data" / "freeze_readiness_roadmap.csv")
    scaffold_support_rows = read_csv(ROOT / "data" / "scaffold_support_audit.csv")
    requirement_rows = read_csv(ROOT / "data" / "requirement_coverage.csv")
    model_sweep_plan = read_csv(ROOT / "data" / "model_sweep_plan.csv")
    model_sweep_execution_commands = read_csv(ROOT / "data" / "model_sweep_execution_commands.csv")
    model_sweep_execution_checklist = read_csv(ROOT / "data" / "model_sweep_execution_checklist.csv")
    model_result_summary = read_csv(ROOT / "data" / "model_result_summary.csv")
    statistical_reporting_rows = read_csv(ROOT / "data" / "statistical_reporting_audit.csv")
    provider_readiness_rows = read_csv(ROOT / "data" / "provider_readiness_audit.csv")
    hosted_qa_readiness_rows = read_csv(ROOT / "data" / "hosted_qa_readiness_audit.csv")
    threats_to_validity_rows = read_csv(ROOT / "data" / "threats_to_validity.csv")
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

## Reader Guide

`reports/concise_metr_report.md` is the reviewer-facing concise narrative. This file is the detailed generated evidence appendix: it intentionally includes long tables, hashes, and audit rows that should not be read as a locked-benchmark claim.

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

## Diagnostic Coverage Audit

{diagnostic_coverage_section(diagnostic_coverage_rows)}

## Human-Time Estimates

Human-time buckets follow the project playbook:

- `T0`: 5-15 minutes.
- `T1`: 15-45 minutes.
- `T2`: 45-120 minutes.
- `T3`: 2-6 hours.
- `T4`: 6+ hours.

The p50/p90 estimates in metadata are reviewer estimates, not measured independent solves. The hard review downgraded three rows from accepted core to calibration-only because their proof surface and likely one-shot solvability did not justify accepted T2 status.

## Human-Time Calibration Audit

{human_time_calibration_section(human_time_rows)}

## Human Timing Collection Packet

{human_timing_packet_section(human_timing_plan_rows)}

## Transcript Review Packet

{transcript_review_packet_section(transcript_review_queue_rows)}

## Grader And Integrity Controls

The grader is Lean-first. For each submission it copies the public files listed in `metadata.json`, replaces the submission file, scans forbidden constructs, compiles public Lean files, compiles hidden semantic pins, and audits axioms on declared targets. Accepted and calibration tasks must have at least two wrong submissions.

Hidden pins check more than type signatures where possible: semantic formalization tasks include positive and negative examples; invariant tasks include edge cases and downstream bundled consequences; library tasks include downstream reuse through public lemmas. The grader still cannot prove that a task measures every intended cognitive skill, and it cannot replace human review of whether a task is too automation-dominated.

The axiom policy allows only the standard Lean axioms documented in `docs/axiom_policy.md`. Source-level escape hatches such as `sorry`, `admit`, `axiom`, `constant`, `unsafe`, custom elaboration, and command execution are rejected by the forbidden-construct scanner before Lean grading.

## Grader Hardening Audit

{grader_hardening_section(grader_hardening_rows)}

## Public Export

`scripts/export_public_tasks.py` exports the release set by default: `accepted_v0`, `calibration_only`, and pending candidates if any. It copies every file listed in metadata `public_files` plus `Prompt.md` and `metadata.json`. `scripts/validate_public_export.py` checks that hidden and wrong directories are absent, all public files are present, exported Lean files compile, and obvious hidden-reference path strings do not leak.

## Prompt Contract Audit

{prompt_contract_section(prompt_contract_rows)}

## Scaffold And Model-Run Support

The supported scaffold ladder is `one-shot`, `lookup`, and `lookup_unlimited`. Lookup is a real read-only command, `python scripts/lean_lookup.py QUERY`, which searches metadata-listed public Lean task files and installed Std/Mathlib files when available. External model runners receive `PROMPT_PATH`, `MODEL`, `TASK_ID`, `ATTEMPT_INDEX`, `SCAFFOLD`, `LEAN_LOOKUP_COMMAND`, `TASK_PUBLIC_DIR`, and `TASK_PUBLIC_FILES`.

## Scaffold Support Audit

{scaffold_support_section(scaffold_support_rows)}

## Evaluation Protocol

{evaluation_protocol_section(model_sweep_plan)}

## Model Sweep Execution Packet

{model_sweep_execution_section(model_sweep_execution_commands, model_sweep_execution_checklist)}

## Model Result Analysis

{model_analysis_section(model_result_summary)}

## Statistical Reporting Audit

{statistical_reporting_section(statistical_reporting_rows)}

## Provider Readiness Audit

{provider_readiness_section(provider_readiness_rows)}

## Hosted QA Readiness Audit

{hosted_qa_readiness_section(hosted_qa_readiness_rows)}

## Threats To Validity Register

{threats_to_validity_section(threats_to_validity_rows)}

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

## Run Result Integrity Audit

{run_integrity_section(run_integrity_rows)}

## Claim Evidence Audit

{claim_evidence_section(claim_evidence_rows)}

## Claim Authorization Matrix

{claim_authorization_section(claim_authorization_rows)}

## Report Claim Conformance Audit

{report_claim_conformance_section(report_claim_conformance_rows)}

## Report Shape Audit

{report_shape_section(report_shape_rows)}

## Release Decision Log

{release_decision_section(release_decision_rows)}

## Freeze Readiness Roadmap

{freeze_readiness_section(freeze_readiness_rows)}

## Difficulty Audit Summary

The regenerated difficulty audit separates mechanical signals from manual judgments. Mechanical signals include reference proof lines, declaration count, public file count, public lemma count, tactic profile, automation dominance, Mathlib use, multi-file context, hidden pin strength, and wrong-submission count. Manual fields include frontier one-shot solvability estimates, p50/p90 human time, scaffold sensitivity, diagnostic value, and final accept/reject rationale.

## Accepted Task Review

`reports/accepted_task_review.md` records the per-task reviewer judgment for every row that was marked `accepted_v0` at the start of the hardening pass. It explicitly distinguishes keep, downgrade, and keep-with-caveat recommendations; checks whether buckets are deserved; audits hidden pins and wrong submissions; and lists what must change before each task can be treated as benchmark-grade.

## Task Quality Matrix

{task_quality_section(task_quality_rows)}

## Task Asset Manifest

{task_asset_manifest_section(task_asset_rows)}

## Hidden Pin Coverage Audit

{pin_coverage_section(pin_coverage_rows)}

## Requirement Coverage Audit

{requirement_coverage_section(requirement_rows)}

## Reproducibility Checklist

The intended local regeneration gate is:

```powershell
lake build
python scripts/validate_all.py
python scripts/audit_difficulty.py
python scripts/generate_task_quality_matrix.py
python scripts/audit_diagnostic_coverage.py
python scripts/audit_human_time_calibration.py
python scripts/generate_human_timing_packet.py
python scripts/record_local_qa_results.py
python scripts/generate_transcript_review_packet.py
python scripts/audit_pin_coverage.py
python scripts/audit_run_integrity.py
python scripts/audit_grader_hardening.py
python scripts/generate_evaluation_protocol.py
python scripts/generate_model_sweep_packet.py
python scripts/analyze_model_results.py
python scripts/generate_report.py
python scripts/audit_statistical_reporting.py
python scripts/audit_provider_readiness.py
python scripts/generate_report.py
python scripts/export_public_tasks.py --out public_tasks
python scripts/validate_public_export.py --out public_tasks
python scripts/audit_hosted_qa_readiness.py
python scripts/generate_task_asset_manifest.py --public-export public_tasks
python scripts/audit_prompt_contracts.py
python scripts/audit_scaffold_support.py
python scripts/generate_threats_to_validity.py
python scripts/audit_requirement_coverage.py --public-export public_tasks
python scripts/audit_claim_evidence.py
python scripts/generate_claim_authorization_matrix.py
python scripts/generate_concise_report.py
python scripts/audit_report_claim_conformance.py
python scripts/audit_report_shape.py
python scripts/generate_release_decision_log.py
python scripts/generate_freeze_readiness_roadmap.py
python scripts/audit_scaffold_support.py
python scripts/audit_requirement_coverage.py --public-export public_tasks
python scripts/audit_claim_evidence.py
python scripts/generate_claim_authorization_matrix.py
python scripts/generate_concise_report.py
python scripts/audit_report_claim_conformance.py
python scripts/audit_report_shape.py
python scripts/generate_release_decision_log.py
python scripts/generate_freeze_readiness_roadmap.py
python scripts/audit_scaffold_support.py
python scripts/audit_requirement_coverage.py --public-export public_tasks
python scripts/audit_claim_evidence.py
python scripts/generate_claim_authorization_matrix.py
python scripts/generate_concise_report.py
python scripts/audit_report_claim_conformance.py
python scripts/audit_report_shape.py
python scripts/generate_release_decision_log.py
python scripts/generate_freeze_readiness_roadmap.py
python scripts/write_validation_manifest.py --public-export public_tasks
python scripts/generate_report.py
```

The public export validator checks that hidden references and wrong submissions are absent from `public_tasks`, all metadata-listed public files are present, exported Lean files compile, and obvious hidden-reference path strings do not leak.

{validation_manifest_section(validation_manifest)}

## Threats To Validity

The generated register in `reports/threats_to_validity.md` is the authoritative limitations table for this report. It currently keeps the strongest benchmark claims blocked where evidence is missing, including task-count scale, T3/T4 time-horizon depth, independent human timing, scaffold-sweep coverage, frontier/open-model coverage, statistical power, and hosted QA.

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
