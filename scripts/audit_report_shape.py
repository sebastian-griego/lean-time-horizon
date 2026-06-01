from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "check_id",
    "playbook_question",
    "answer_status",
    "evidence",
    "limitation",
    "next_action",
    "source_artifacts",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def row(
    check_id: str,
    playbook_question: str,
    answer_status: str,
    evidence: str,
    limitation: str,
    next_action: str,
    source_artifacts: list[str],
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "playbook_question": playbook_question,
        "answer_status": answer_status,
        "evidence": evidence,
        "limitation": limitation,
        "next_action": next_action,
        "source_artifacts": ";".join(source_artifacts),
    }


def has_all(text: str, phrases: list[str]) -> tuple[bool, list[str]]:
    lower = text.lower()
    missing = [phrase for phrase in phrases if phrase.lower() not in lower]
    return not missing, missing


def main() -> int:
    concise = read_text(ROOT / "reports" / "concise_metr_report.md")
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    requirements = read_csv(ROOT / "data" / "requirement_coverage.csv")
    diagnostic = read_csv(ROOT / "data" / "diagnostic_coverage_audit.csv")
    conformance = read_csv(ROOT / "data" / "report_claim_conformance_audit.csv")
    model_summary = read_csv(ROOT / "data" / "model_result_summary.csv")

    accepted = [task for task in metadata if task.get("acceptance_status") == "accepted_v0"]
    calibration = [task for task in metadata if task.get("acceptance_status") == "calibration_only"]
    capability_rows = [row for row in diagnostic if row.get("area") == "diagnostic_capability"]
    singleton_capabilities = [
        row.get("check_id", "").removeprefix("capability_")
        for row in capability_rows
        if row.get("status") == "caution"
    ]
    primary_coverage = next(
        (
            row for row in model_summary
            if row.get("analysis_set") == "primary_plan_coverage"
            and row.get("group_by") == "all"
            and row.get("group") == "all"
        ),
        {},
    )
    requirement_by_id = {row.get("requirement_id", ""): row for row in requirements}
    conformance_failures = [row for row in conformance if row.get("status") == "fail"]

    rows: list[dict[str, str]] = []
    ok, missing = has_all(concise, ["## Task Set", "accepted core tasks", "Accepted core rows"])
    rows.append(row(
        "tasks_built",
        "What tasks were built?",
        "answered" if ok and accepted else "needs_attention",
        f"accepted={len(accepted)}; calibration={len(calibration)}; missing_phrases={compact_json(missing)}",
        "The accepted set is below the final 20-50 task target.",
        "Keep accepted/calibration/rejected status visible and expand only with hard-reviewed tasks.",
        ["reports/concise_metr_report.md", "data/task_metadata.csv"],
    ))

    ok, missing = has_all(concise, ["## Capabilities And Expected Failures", "diagnostic capabilities", "Expected failure modes"])
    rows.append(row(
        "capabilities_tested",
        "What capabilities do the tasks test?",
        "answered_with_caveat" if ok and capability_rows else "needs_attention",
        f"capability_rows={len(capability_rows)}; singleton_capabilities={compact_json(singleton_capabilities)}; missing_phrases={compact_json(missing)}",
        "Some capabilities are represented by only one accepted task, so capability-level claims remain weak.",
        "Add independently reviewed tasks for singleton capabilities before making capability-level performance claims.",
        [
            "reports/concise_metr_report.md",
            "reports/diagnostic_coverage_audit.md",
            "reports/construct_validity_matrix.md",
            "data/diagnostic_coverage_audit.csv",
        ],
    ))

    ok, missing = has_all(concise, ["one-shot", "lookup", "lookup_unlimited"])
    rows.append(row(
        "scaffolds_compared",
        "What scaffolds were compared?",
        "answered_with_blocker" if ok else "needs_attention",
        f"planned_cells={primary_coverage.get('planned_cells', '0')}; covered_noninfra={primary_coverage.get('covered_cells_noninfra', '0')}; missing_phrases={compact_json(missing)}",
        "The scaffold ladder is planned and implemented, but committed provider evidence covers only a tiny one-shot smoke sample.",
        "Run the accepted-core scaffold sweep before interpreting scaffold effects.",
        [
            "reports/concise_metr_report.md",
            "reports/evaluation_protocol.md",
            "reports/model_run_analysis.md",
        ],
    ))

    scaffold_req = requirement_by_id.get("scaffold_result_comparison", {})
    time_req = requirement_by_id.get("time_horizon_spread", {})
    statistical_plan_req = requirement_by_id.get("statistical_analysis_plan", {})
    rows.append(row(
        "success_changes_by_scaffold_and_bucket",
        "How does success change with scaffold and human-time bucket?",
        "blocked_by_evidence",
        f"scaffold_result_comparison={scaffold_req.get('status', 'missing')}; time_horizon_spread={time_req.get('status', 'missing')}; statistical_analysis_plan={statistical_plan_req.get('status', 'missing')}; primary_covered_noninfra={primary_coverage.get('covered_cells_noninfra', '0')}",
        "Real scaffold/time-horizon performance summaries are not supported by committed data.",
        "Run pass@k sweeps across accepted_v0 x scaffold cells, meet the statistical threshold rows, and add independently timed T3/T4 tasks.",
        [
            "data/model_result_summary.csv",
            "data/statistical_design_thresholds.csv",
            "reports/statistical_analysis_plan.md",
            "reports/statistical_reporting_audit.md",
            "reports/human_time_calibration_audit.md",
        ],
    ))

    ok, missing = has_all(concise, ["Expected failure modes", "not characterize", "failure distributions"])
    rows.append(row(
        "failure_modes_dominate",
        "What failure modes dominate?",
        "blocked_by_evidence" if ok else "needs_attention",
        f"concision_mentions_failure_limits={ok}; missing_phrases={compact_json(missing)}",
        "Expected failure modes are documented, but broad model transcripts are not independently adjudicated.",
        "Use the transcript review packet and failure-label review audit after broader provider sweeps before claiming dominant failure modes.",
        [
            "reports/concise_metr_report.md",
            "reports/transcript_review_packet.md",
            "reports/failure_label_review_audit.md",
            "data/failure_label_reviews.csv",
            "data/failure_label_review_template.csv",
        ],
    ))

    ok, missing = has_all(concise, ["## Next Work", "independent Lean-human timing", "hosted QA"])
    rows.append(row(
        "next_batch_needs",
        "What does the next batch need?",
        "answered" if ok else "needs_attention",
        f"missing_phrases={compact_json(missing)}",
        "Next work is a concrete blocker list, not a claim that the benchmark is locked.",
        "Keep next-work items tied to requirement/freeze gates.",
        ["reports/concise_metr_report.md", "reports/freeze_readiness_roadmap.md"],
    ))

    line_count = len(concise.splitlines())
    rows.append(row(
        "skimmability",
        "Is the main report skimmable?",
        "answered" if line_count <= 220 else "needs_attention",
        f"concise_report_lines={line_count}; conformance_failures={len(conformance_failures)}",
        "The concise report is short, and row-level generated tables live in the evidence appendix instead of the main narrative.",
        "Keep the concise and main reports short and keep long tables in generated appendices.",
        [
            "reports/concise_metr_report.md",
            "reports/metr_style_report.md",
            "reports/evidence_appendix.md",
            "reports/report_claim_conformance_audit.md",
        ],
    ))
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row["answer_status"] for row in rows)
    lines = [
        "# Report Shape Audit",
        "",
        "This generated audit checks the concise METR-style report against the report-shape questions in `docs/lean_eval_project_playbook.md`. `blocked_by_evidence` is an honest answer, not an audit failure: it means the report explicitly says the current data cannot support that analysis yet.",
        "",
        "## Summary",
        "",
        f"- checks: `{len(rows)}`",
        f"- answer statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        "",
        "## Check Table",
        "",
        "| check | playbook question | answer status | evidence | limitation | next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row_data in rows:
        lines.append(
            f"| `{row_data['check_id']}` | {escaped(row_data['playbook_question'])} | "
            f"{row_data['answer_status']} | {escaped(row_data['evidence'])} | "
            f"{escaped(row_data['limitation'])} | {escaped(row_data['next_action'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`answered` rows are directly handled by the concise report. `answered_with_caveat` rows are handled but have construct-validity limits. `answered_with_blocker` and `blocked_by_evidence` rows are acceptable only because the report states the missing evidence rather than implying a result.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main_entry() -> int:
    rows = main()
    write_csv(ROOT / "data" / "report_shape_audit.csv", rows)
    write_markdown(ROOT / "reports" / "report_shape_audit.md", rows)
    blockers = sum(1 for row in rows if row["answer_status"] == "needs_attention")
    print(f"wrote data/report_shape_audit.csv and reports/report_shape_audit.md with {len(rows)} checks; needs_attention={blockers}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main_entry())
