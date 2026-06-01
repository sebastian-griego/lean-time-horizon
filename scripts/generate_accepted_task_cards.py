from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "task_id",
    "title",
    "split",
    "family",
    "domain",
    "human_time_bucket",
    "human_minutes_p50",
    "human_minutes_p90",
    "benchmark_grade_status",
    "review_recommendation",
    "proof_lines",
    "tactic_profile",
    "automation_dominated",
    "frontier_one_shot_likelihood",
    "diagnostic_value",
    "capabilities_claimed",
    "claim_support_level",
    "claim_limit",
    "hidden_pin_strength",
    "pin_role",
    "pin_coverage_grade",
    "wrong_stage_summary",
    "wrong_submission_count",
    "local_qa_summary",
    "asset_summary",
    "validation_command_kinds",
    "review_note",
    "claim_boundary",
    "before_benchmark_grade",
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


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def as_bool(value: str) -> bool:
    return str(value).strip().lower() == "true"


def parse_json_counter(value: str) -> dict[str, int]:
    if not value:
        return {}
    try:
        data = json.loads(value)
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    out: dict[str, int] = {}
    for key, raw in data.items():
        try:
            out[str(key)] = int(raw)
        except (TypeError, ValueError):
            out[str(key)] = 0
    return out


def review_recommendation(metadata: dict[str, str], quality: dict[str, str]) -> str:
    note = metadata.get("difficulty_review_notes", "").lower()
    grade = quality.get("benchmark_grade_status", "")
    if "keep_with_caveat" in note or "with_caveat" in grade:
        return "keep_with_caveat"
    if metadata.get("acceptance_status") == "accepted_v0":
        return "keep"
    return metadata.get("acceptance_status", "unknown")


def hidden_pin_boundary(pin: dict[str, str]) -> str:
    surface = pin.get("submission_surface", "")
    feasibility = pin.get("same_signature_hidden_wrong_feasibility", "")
    role = pin.get("hidden_pin_role", "")
    grade = pin.get("pin_coverage_grade", "")
    if surface == "proof_only_fixed_statements":
        return (
            "Fixed theorem statements make same-signature public-compiling wrong proofs structurally infeasible; "
            "hidden pins mainly guard signatures and downstream use."
        )
    if feasibility == "feasible_via_definition_semantics" and grade == "semantic_pins_exercised":
        return "Mutable definitions have public-compiling wrong controls that exercise semantic hidden pins."
    if role:
        return f"Pin role is {role}; finite hidden checks remain a probe, not full semantic equivalence."
    return "Hidden pin boundary not classified; inspect pin coverage audit before making stronger claims."


def validation_kinds(rows: list[dict[str, str]]) -> str:
    kinds = [row.get("kind", "") for row in rows if row.get("kind")]
    return ";".join(sorted(kinds))


def asset_summary(rows: list[dict[str, str]]) -> str:
    counts = Counter(row.get("asset_role", "unknown") for row in rows)
    wanted = ["prompt", "public", "metadata", "hidden_reference", "hidden_pincheck", "wrong_submission"]
    return "; ".join(f"{role}={counts.get(role, 0)}" for role in wanted)


def local_qa_summary(rows: list[dict[str, str]]) -> str:
    counts = Counter(row.get("qa_findings_status", "unknown") for row in rows)
    ordered = {key: counts[key] for key in sorted(counts)}
    return compact_json(ordered)


def before_benchmark_grade(
    quality: dict[str, str],
    construct: dict[str, str],
    pin: dict[str, str],
) -> str:
    actions = [
        quality.get("next_review_action", "").strip(),
        construct.get("next_evidence_needed", "").strip(),
    ]
    boundary = hidden_pin_boundary(pin)
    actions.append(boundary)
    return " ".join(action for action in actions if action)


def build_rows() -> list[dict[str, str]]:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    difficulty = {row["task_id"]: row for row in read_csv(ROOT / "data" / "difficulty_audit.csv")}
    quality = {row["task_id"]: row for row in read_csv(ROOT / "data" / "task_quality_matrix.csv")}
    construct = {row["task_id"]: row for row in read_csv(ROOT / "data" / "construct_validity_matrix.csv")}
    pin = {row["task_id"]: row for row in read_csv(ROOT / "data" / "pin_coverage_audit.csv")}
    validation_by_task: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(ROOT / "data" / "validation_commands.csv"):
        validation_by_task[row.get("task_id", "")].append(row)
    asset_by_task: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(ROOT / "data" / "task_asset_manifest.csv"):
        asset_by_task[row.get("task_id", "")].append(row)
    qa_by_task: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(ROOT / "data" / "run_results.csv"):
        if row.get("qa_stage") == "local_qa":
            qa_by_task[row.get("task_id", "")].append(row)

    rows: list[dict[str, str]] = []
    for task in metadata:
        if task.get("acceptance_status") != "accepted_v0":
            continue
        task_id = task["task_id"]
        d = difficulty.get(task_id, {})
        q = quality.get(task_id, {})
        c = construct.get(task_id, {})
        p = pin.get(task_id, {})
        stage_counts = parse_json_counter(p.get("wrong_stage_summary", ""))
        hidden_stage_count = stage_counts.get("hidden_pin", 0)
        public_stage_count = stage_counts.get("public_stage", 0)
        claim_limit = c.get("claim_limit", "")
        hidden_boundary = hidden_pin_boundary(p)
        claim_boundary = " ".join(
            item for item in [
                claim_limit,
                f"wrong-stage evidence: hidden_pin={hidden_stage_count}, public_stage={public_stage_count}.",
                hidden_boundary,
            ]
            if item
        )
        rows.append({
            "task_id": task_id,
            "title": task.get("title", ""),
            "split": task.get("split", ""),
            "family": task.get("family", ""),
            "domain": task.get("domain", ""),
            "human_time_bucket": task.get("human_time_bucket", ""),
            "human_minutes_p50": task.get("human_minutes_p50", ""),
            "human_minutes_p90": task.get("human_minutes_p90", ""),
            "benchmark_grade_status": q.get("benchmark_grade_status", ""),
            "review_recommendation": review_recommendation(task, q),
            "proof_lines": d.get("mechanical_reference_proof_lines", q.get("proof_lines", "")),
            "tactic_profile": d.get("mechanical_tactic_profile", q.get("tactic_profile", "")),
            "automation_dominated": d.get("mechanical_automation_dominated", q.get("automation_dominated", "")),
            "frontier_one_shot_likelihood": d.get("manual_frontier_model_one_shot_likelihood", q.get("frontier_one_shot_likelihood", "")),
            "diagnostic_value": d.get("manual_diagnostic_value", q.get("diagnostic_value", "")),
            "capabilities_claimed": c.get("capabilities_claimed", ""),
            "claim_support_level": c.get("claim_support_level", ""),
            "claim_limit": claim_limit,
            "hidden_pin_strength": d.get("mechanical_hidden_pin_strength", q.get("hidden_pin_strength", "")),
            "pin_role": p.get("hidden_pin_role", ""),
            "pin_coverage_grade": p.get("pin_coverage_grade", ""),
            "wrong_stage_summary": p.get("wrong_stage_summary", ""),
            "wrong_submission_count": d.get("mechanical_wrong_submission_count", q.get("wrong_submission_count", "")),
            "local_qa_summary": local_qa_summary(qa_by_task.get(task_id, [])),
            "asset_summary": asset_summary(asset_by_task.get(task_id, [])),
            "validation_command_kinds": validation_kinds(validation_by_task.get(task_id, [])),
            "review_note": task.get("difficulty_review_notes", ""),
            "claim_boundary": claim_boundary,
            "before_benchmark_grade": before_benchmark_grade(q, c, p),
        })
    return rows


def card_markdown(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "_No accepted_v0 task cards generated._"
    blocks: list[str] = []
    for row in rows:
        capabilities = ", ".join(f"`{cap}`" for cap in row["capabilities_claimed"].split(";") if cap) or "_none_"
        blocks.extend([
            f"### `{row['task_id']}` {row['title']}",
            "",
            f"- status: `{row['review_recommendation']}` / `{row['benchmark_grade_status']}`",
            f"- split/family/domain: `{row['split']}` / `{row['family']}` / `{row['domain']}`",
            f"- time estimate: `{row['human_time_bucket']}` (`{row['human_minutes_p50']}`/`{row['human_minutes_p90']}` p50/p90 minutes)",
            f"- proof signal: `{row['proof_lines']}` reference proof lines; automation dominated `{row['automation_dominated']}`; tactic profile `{escaped(row['tactic_profile'])}`",
            f"- one-shot likelihood and diagnostic value: `{row['frontier_one_shot_likelihood']}` / `{row['diagnostic_value']}`",
            f"- claimed capabilities: {capabilities}",
            f"- construct support: `{row['claim_support_level']}`; limit: {escaped(row['claim_limit'])}",
            f"- hidden-pin evidence: `{row['hidden_pin_strength']}` pins; role `{row['pin_role']}`; coverage `{row['pin_coverage_grade']}`; wrong stages `{escaped(row['wrong_stage_summary'])}`",
            f"- validation evidence: local QA `{escaped(row['local_qa_summary'])}`; validation command kinds `{escaped(row['validation_command_kinds'])}`",
            f"- asset evidence: {escaped(row['asset_summary'])}",
            f"- reviewer note: {escaped(row['review_note'])}",
            f"- benchmark-grade blocker: {escaped(row['before_benchmark_grade'])}",
            "",
        ])
    return "\n".join(blocks).rstrip()


def summary_table(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "_None._"
    lines = [
        "| task | recommendation | bucket | automation | pin coverage | wrong stages | support | one-shot |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['task_id']}` | {row['review_recommendation']} | {row['human_time_bucket']} | "
            f"{row['automation_dominated']} | {row['pin_coverage_grade']} | "
            f"`{escaped(row['wrong_stage_summary'])}` | {row['claim_support_level']} | "
            f"{row['frontier_one_shot_likelihood']} |"
        )
    return "\n".join(lines)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    recommendation_counts = Counter(row["review_recommendation"] for row in rows)
    automation_count = sum(1 for row in rows if as_bool(row["automation_dominated"]))
    hidden_exercised = sum(1 for row in rows if row["pin_coverage_grade"] == "semantic_pins_exercised")
    caveat_rows = sum(1 for row in rows if "caveat" in row["benchmark_grade_status"])
    lines = [
        "# Accepted Task Cards",
        "",
        "This generated report creates one reviewer card per `accepted_v0` task by joining metadata, difficulty-audit, task-quality, construct-validity, hidden-pin coverage, asset-manifest, validation-command, and local-QA evidence. It is a synthesis layer for review, not a new acceptance decision and not model-performance evidence.",
        "",
        "The cards intentionally describe hidden checks by role, counts, and stage outcomes only. They do not copy hidden proof or hidden `PinCheck.lean` contents.",
        "",
        "## Summary",
        "",
        f"- accepted task cards: `{len(rows)}`",
        f"- recommendations: `{compact_json(dict(sorted(recommendation_counts.items())))}`",
        f"- automation-dominated rows: `{automation_count}/{len(rows)}`",
        f"- rows whose wrong controls exercise semantic hidden pins: `{hidden_exercised}/{len(rows)}`",
        f"- caveated accepted rows: `{caveat_rows}/{len(rows)}`",
        "",
        "## Card Index",
        "",
        summary_table(rows),
        "",
        "## Cards",
        "",
        card_markdown(rows),
        "",
        "## Interpretation",
        "",
        "These cards make the accepted-core limitations harder to miss: proof-only fixed-statement tasks can be valid local proof-repair or Mathlib rows even when same-signature hidden-pin wrongs are structurally infeasible, while mutable-definition tasks should show public-compiling wrong controls that reach semantic pins. Stronger benchmark claims still require independent human timing, broader accepted-task scale, scaffold/provider sweeps, and hosted QA.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    csv_out = ROOT / "data" / "accepted_task_cards.csv"
    md_out = ROOT / "reports" / "accepted_task_cards.md"
    write_csv(csv_out, rows)
    write_markdown(md_out, rows)
    print(f"wrote {csv_out.relative_to(ROOT)} and {md_out.relative_to(ROOT)} with {len(rows)} accepted task cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
