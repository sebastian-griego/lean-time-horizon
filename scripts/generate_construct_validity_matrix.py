from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CAPABILITY_FIELDS = {
    "library_search": "requires_library_search",
    "theorem_decomposition": "requires_decomposition",
    "semantic_formalization": "requires_semantic_formalization",
    "proof_debugging": "requires_proof_debugging",
    "codebase_navigation": "requires_codebase_navigation",
    "invariant_design": "requires_invariant_design",
    "long_horizon_construction": "requires_long_horizon_construction",
}

FIELDS = [
    "task_id",
    "split",
    "family",
    "domain",
    "human_time_bucket",
    "human_minutes_p50",
    "human_minutes_p90",
    "benchmark_grade_status",
    "capabilities_claimed",
    "capability_count",
    "singleton_capabilities",
    "non_singleton_capabilities",
    "proof_lines",
    "automation_dominated",
    "hidden_pin_strength",
    "wrong_submission_count",
    "frontier_one_shot_likelihood",
    "diagnostic_value",
    "construct_evidence",
    "claim_support_level",
    "claim_limit",
    "next_evidence_needed",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def as_bool(value: str) -> bool:
    return str(value).strip().lower() == "true"


def claimed_capabilities(row: dict[str, str]) -> list[str]:
    return [
        capability
        for capability, field in CAPABILITY_FIELDS.items()
        if as_bool(row.get(field, "false"))
    ]


def claim_support_level(row: dict[str, str], singletons: list[str]) -> str:
    grade = row.get("benchmark_grade_status", "")
    if "caveat" in grade or as_bool(row.get("automation_dominated", "false")):
        return "task_level_with_caveat"
    if singletons:
        return "task_level_internal_review_singleton_capability"
    return "task_level_internal_review"


def claim_limit(singletons: list[str], row: dict[str, str]) -> str:
    limits: list[str] = []
    if singletons:
        limits.append(
            "singleton capabilities cannot support capability-level generalization"
        )
    if "caveat" in row.get("benchmark_grade_status", ""):
        limits.append("accepted row carries a task-quality caveat")
    if as_bool(row.get("automation_dominated", "false")):
        limits.append("reference proof is automation-dominated")
    if row.get("frontier_one_shot_likelihood") in {"likely", "very_likely"}:
        limits.append("frontier one-shot estimate is high")
    return "; ".join(limits) if limits else "task-level evidence only; aggregate claims still require more accepted tasks and model data"


def next_evidence_needed(singletons: list[str], row: dict[str, str]) -> str:
    actions = [
        "independent human timing",
        "accepted-core scaffold sweep",
        "hosted QA evidence",
    ]
    if singletons:
        actions.append("at least one more accepted task for singleton capabilities")
    if row.get("human_time_bucket") in {"T3", "T4"}:
        actions.append("extra timing review for long-horizon bucket")
    if as_bool(row.get("automation_dominated", "false")):
        actions.append("non-automation-dominated companion evidence")
    return "; ".join(actions)


def build_rows() -> list[dict[str, str]]:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    quality = read_csv(ROOT / "data" / "task_quality_matrix.csv")
    quality_by_id = {
        row["task_id"]: row
        for row in quality
        if row.get("release_role") == "accepted_core"
    }
    accepted_meta = [
        row for row in metadata
        if row.get("acceptance_status") == "accepted_v0"
    ]
    accepted_quality = [quality_by_id.get(row["task_id"], {}) for row in accepted_meta]
    capability_counts: Counter[str] = Counter()
    for row in accepted_quality:
        capability_counts.update(claimed_capabilities(row))

    rows: list[dict[str, str]] = []
    for metadata_row in accepted_meta:
        task_id = metadata_row["task_id"]
        quality_row = quality_by_id.get(task_id, {})
        capabilities = claimed_capabilities(quality_row)
        singletons = [capability for capability in capabilities if capability_counts[capability] == 1]
        non_singletons = [capability for capability in capabilities if capability_counts[capability] > 1]
        evidence_bits = [
            f"family={metadata_row.get('family', '')}",
            f"bucket={metadata_row.get('human_time_bucket', '')}",
            f"proof_lines={quality_row.get('proof_lines', '')}",
            f"pins={quality_row.get('hidden_pin_strength', '')}",
            f"wrongs={quality_row.get('wrong_submission_count', '')}",
            f"diagnostic={quality_row.get('diagnostic_value', '')}",
        ]
        rows.append({
            "task_id": task_id,
            "split": metadata_row.get("split", ""),
            "family": metadata_row.get("family", ""),
            "domain": metadata_row.get("domain", ""),
            "human_time_bucket": metadata_row.get("human_time_bucket", ""),
            "human_minutes_p50": metadata_row.get("human_minutes_p50", ""),
            "human_minutes_p90": metadata_row.get("human_minutes_p90", ""),
            "benchmark_grade_status": quality_row.get("benchmark_grade_status", ""),
            "capabilities_claimed": ";".join(capabilities),
            "capability_count": str(len(capabilities)),
            "singleton_capabilities": ";".join(singletons),
            "non_singleton_capabilities": ";".join(non_singletons),
            "proof_lines": quality_row.get("proof_lines", ""),
            "automation_dominated": quality_row.get("automation_dominated", ""),
            "hidden_pin_strength": quality_row.get("hidden_pin_strength", ""),
            "wrong_submission_count": quality_row.get("wrong_submission_count", ""),
            "frontier_one_shot_likelihood": quality_row.get("frontier_one_shot_likelihood", ""),
            "diagnostic_value": quality_row.get("diagnostic_value", ""),
            "construct_evidence": "; ".join(evidence_bits),
            "claim_support_level": claim_support_level(quality_row, singletons),
            "claim_limit": claim_limit(singletons, quality_row),
            "next_evidence_needed": next_evidence_needed(singletons, metadata_row),
        })
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def capability_summary(rows: list[dict[str, str]]) -> str:
    capability_tasks: dict[str, list[str]] = {capability: [] for capability in CAPABILITY_FIELDS}
    for row in rows:
        for capability in row.get("capabilities_claimed", "").split(";"):
            if capability in capability_tasks and row["task_id"] not in capability_tasks[capability]:
                capability_tasks[capability].append(row["task_id"])
    lines = [
        "| capability | accepted tasks | claim boundary |",
        "| --- | ---: | --- |",
    ]
    for capability, task_ids in capability_tasks.items():
        if len(task_ids) >= 2:
            boundary = "represented by more than one accepted task, but still not a performance claim"
        elif len(task_ids) == 1:
            boundary = "singleton-covered; treat as design intent only"
        else:
            boundary = "not represented in accepted_v0"
        task_text = ", ".join(f"`{task_id}`" for task_id in sorted(task_ids)) or "_none_"
        lines.append(f"| `{capability}` | {task_text} | {boundary} |")
    return "\n".join(lines)


def task_table(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "_None._"
    lines = [
        "| task | grade | capabilities | singleton caps | evidence | support | limit |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        caps = ", ".join(f"`{cap}`" for cap in row["capabilities_claimed"].split(";") if cap)
        singleton = ", ".join(f"`{cap}`" for cap in row["singleton_capabilities"].split(";") if cap) or "_none_"
        lines.append(
            f"| `{row['task_id']}` | {row['benchmark_grade_status']} | {caps} | "
            f"{singleton} | {escaped(row['construct_evidence'])} | "
            f"{row['claim_support_level']} | {escaped(row['claim_limit'])} |"
        )
    return "\n".join(lines)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    support_counts = Counter(row["claim_support_level"] for row in rows)
    singleton_tasks = [row for row in rows if row["singleton_capabilities"]]
    automation_tasks = [row for row in rows if as_bool(row["automation_dominated"])]
    caveat_tasks = [row for row in rows if "caveat" in row["benchmark_grade_status"]]
    lines = [
        "# Construct Validity Matrix",
        "",
        "This generated matrix is a reviewer aid for construct validity. It links each accepted_v0 task to the diagnostic capabilities it is supposed to exercise, the mechanical evidence behind that claim, and the boundary on what the row can support. It is not model-performance evidence.",
        "",
        "## Summary",
        "",
        f"- accepted task rows: `{len(rows)}`",
        f"- support levels: `{compact_json(dict(sorted(support_counts.items())))}`",
        f"- rows with singleton-covered capabilities: `{len(singleton_tasks)}/{len(rows)}`",
        f"- automation-dominated accepted rows: `{len(automation_tasks)}/{len(rows)}`",
        f"- caveated accepted rows: `{len(caveat_tasks)}/{len(rows)}`",
        "",
        "## Capability Trace",
        "",
        capability_summary(rows),
        "",
        "## Accepted Task Construct Rows",
        "",
        task_table(rows),
        "",
        "## Interpretation",
        "",
        "The matrix supports only a task-level construct-validity claim: the accepted tasks have documented intended capabilities and local evidence that those capabilities are plausibly exercised. It does not support capability-level performance claims, family-level generalization, or a robust time-horizon measurement claim. Singleton-covered capabilities, automation-dominated rows, and missing independent timing remain active limitations.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    csv_out = ROOT / "data" / "construct_validity_matrix.csv"
    md_out = ROOT / "reports" / "construct_validity_matrix.md"
    write_csv(csv_out, rows)
    write_markdown(md_out, rows)
    print(f"wrote {csv_out.relative_to(ROOT)} and {md_out.relative_to(ROOT)} with {len(rows)} accepted task rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
