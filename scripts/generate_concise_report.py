from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def parse_list(value: str) -> list[str]:
    if not value:
        return []
    try:
        data = json.loads(value)
        if isinstance(data, list):
            return [str(item) for item in data]
    except json.JSONDecodeError:
        pass
    return [item.strip() for item in value.split(";") if item.strip()]


def bullets(counter: Counter[str]) -> str:
    return "\n".join(f"- `{key}`: {value}" for key, value in sorted(counter.items())) or "- _None_"


def table(rows: list[list[str]]) -> str:
    if not rows:
        return "_None._"
    header = rows[0]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in rows[1:]:
        lines.append("| " + " | ".join(cell.replace("|", "/") for cell in row) + " |")
    return "\n".join(lines)


def row_by_id(rows: list[dict[str, str]], key: str, value: str) -> dict[str, str]:
    return next((row for row in rows if row.get(key) == value), {})


def requirement_summary(requirements: list[dict[str, str]]) -> tuple[str, str]:
    counts = Counter(row.get("status", "unknown") for row in requirements)
    gaps = [row for row in requirements if row.get("status") != "supported"]
    rows = [["requirement", "status", "current evidence", "next step"]]
    for row in gaps:
        rows.append([
            f"`{row.get('requirement_id', '')}`",
            row.get("status", ""),
            row.get("evidence", ""),
            row.get("gap_or_next_step", ""),
        ])
    return bullets(counts), table(rows)


def task_table(tasks: list[dict[str, str]]) -> str:
    rows = [["task", "split", "family", "bucket", "p50/p90", "review note"]]
    for task in tasks:
        rows.append([
            f"`{task.get('task_id', '')}`",
            task.get("split", ""),
            task.get("family", ""),
            task.get("human_time_bucket", ""),
            f"{task.get('human_minutes_p50', '')}/{task.get('human_minutes_p90', '')}",
            task.get("difficulty_review_notes", ""),
        ])
    return table(rows)


def claim_table(claims: list[dict[str, str]]) -> str:
    rows = [["claim", "authorization", "allowed wording", "required caveat"]]
    for claim in claims:
        if claim.get("authorization_status") == "allowed":
            continue
        rows.append([
            f"`{claim.get('claim_id', '')}`",
            claim.get("authorization_status", ""),
            claim.get("allowed_wording", ""),
            claim.get("required_caveat", ""),
        ])
    return table(rows)


def capability_table(diagnostic_rows: list[dict[str, str]]) -> str:
    rows = [["capability", "status", "accepted tasks", "limit"]]
    for row in diagnostic_rows:
        if row.get("area") != "diagnostic_capability":
            continue
        capability = row.get("check_id", "").removeprefix("capability_")
        rows.append([
            f"`{capability}`",
            row.get("status", ""),
            str(row.get("accepted_task_count", "")),
            row.get("diagnostic_limit", ""),
        ])
    return table(rows)


def gap_table(rows_in: list[dict[str, str]]) -> str:
    rows = [["claim", "priority", "current status", "blocking requirements"]]
    selected = [
        row for row in rows_in
        if row.get("upgrade_priority") in {"highest", "high"}
        or row.get("authorization_status") == "blocked"
    ]
    for row in selected[:8]:
        rows.append([
            f"`{row.get('claim_id', '')}`",
            row.get("upgrade_priority", ""),
            row.get("authorization_status", ""),
            row.get("blocking_requirements", ""),
        ])
    return table(rows)


def main() -> int:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    requirements = read_csv(ROOT / "data" / "requirement_coverage.csv")
    diagnostic = read_csv(ROOT / "data" / "diagnostic_coverage_audit.csv")
    construct = read_csv(ROOT / "data" / "construct_validity_matrix.csv")
    candidate_pruning = read_csv(ROOT / "data" / "candidate_pruning_audit.csv")
    accepted_cards = read_csv(ROOT / "data" / "accepted_task_cards.csv")
    claim_authorization = read_csv(ROOT / "data" / "claim_authorization_matrix.csv")
    research_claim_gap = read_csv(ROOT / "data" / "research_claim_gap_matrix.csv")
    release_decisions = read_csv(ROOT / "data" / "release_decision_log.csv")
    freeze = read_csv(ROOT / "data" / "freeze_readiness_roadmap.csv")
    run_summary = read_csv(ROOT / "data" / "model_result_summary.csv")
    run_rows = read_csv(ROOT / "data" / "run_results.csv")
    run_integrity = read_csv(ROOT / "data" / "run_integrity_audit.csv")
    data_schema_manifest = read_csv(ROOT / "data" / "data_schema_manifest.csv")
    reviewer_reproduction = read_csv(ROOT / "data" / "reviewer_reproduction_steps.csv")
    clean_workspace = read_csv(ROOT / "data" / "clean_workspace_replay.csv")
    grader = read_csv(ROOT / "data" / "grader_hardening_audit.csv")
    human_time = read_csv(ROOT / "data" / "human_time_calibration_audit.csv")
    independent_review_status = read_csv(ROOT / "data" / "independent_review_status_audit.csv")
    failure_label_reviews = read_csv(ROOT / "data" / "failure_label_reviews.csv")
    failure_label_review_audit = read_csv(ROOT / "data" / "failure_label_review_audit.csv")
    statistical_design = read_csv(ROOT / "data" / "statistical_design_thresholds.csv")
    wilson_precision = read_csv(ROOT / "data" / "wilson_precision_table.csv")
    figure_manifest = read_csv(ROOT / "data" / "figure_manifest.csv")

    accepted = [row for row in metadata if row.get("acceptance_status") == "accepted_v0"]
    calibration = [row for row in metadata if row.get("acceptance_status") == "calibration_only"]
    rejected = [row for row in metadata if row.get("acceptance_status", "").startswith("rejected_")]
    requirement_counts, requirement_gap_table = requirement_summary(requirements)
    auth_counts = Counter(row.get("authorization_status", "unknown") for row in claim_authorization)
    gap_priority_counts = Counter(row.get("upgrade_priority", "unknown") for row in research_claim_gap)
    release_counts = Counter(row.get("status", "unknown") for row in release_decisions)
    freeze_counts = Counter(row.get("roadmap_status", "unknown") for row in freeze)
    integrity_failures = sum(1 for row in run_integrity if row.get("integrity_status") == "fail")
    schema_status_counts = Counter(row.get("validation_status", "unknown") for row in data_schema_manifest)
    schema_problem_rows = sum(
        1 for row in data_schema_manifest
        if row.get("validation_status") in {"schema_error", "projection_mismatch", "codebook_gap"}
        or row.get("error_count") not in {"", "0"}
    )
    reproduction_status_counts = Counter(row.get("status", "unknown") for row in reviewer_reproduction)
    reproduction_local_problems = sum(
        1 for row in reviewer_reproduction
        if row.get("phase") == "local_replay" and row.get("status") != "ready"
    )
    reproduction_external_rows = sum(1 for row in reviewer_reproduction if row.get("phase") == "external_evidence")
    clean_workspace_status_counts = Counter(row.get("status", "unknown") for row in clean_workspace)
    clean_workspace_failures = sum(1 for row in clean_workspace if row.get("status") != "pass")
    grader_failures = sum(1 for row in grader if row.get("status") == "fail")
    failure_review_failures = sum(1 for row in failure_label_review_audit if row.get("status") == "fail")
    accepted_without_timing = sum(
        1 for row in human_time
        if row.get("acceptance_status") == "accepted_v0"
        and "accepted_without_independent_timing" in row.get("issues", "")
    )
    independent_review_status_counts = Counter(row.get("status", "unknown") for row in independent_review_status)
    primary_coverage = row_by_id(run_summary, "analysis_set", "primary_plan_coverage")
    accepted_provider = row_by_id(run_summary, "analysis_set", "accepted_core_results")
    provider_versions = sorted({
        f"{row.get('model', '')}:{row.get('model_version', '')}"
        for row in run_rows
        if row.get("qa_stage") != "local_qa"
        and row.get("model", "")
        and row.get("model_version", "")
    })
    construct_support_counts = Counter(row.get("claim_support_level", "unknown") for row in construct)
    construct_singleton_rows = sum(1 for row in construct if row.get("singleton_capabilities"))
    pruning_decision_counts = Counter(row.get("pruning_decision", "unknown") for row in candidate_pruning)
    pruning_status_counts = Counter(row.get("acceptance_status", "unknown") for row in candidate_pruning)
    card_recommendation_counts = Counter(row.get("review_recommendation", "unknown") for row in accepted_cards)
    card_hidden_pin_exercised = sum(
        1 for row in accepted_cards
        if row.get("pin_coverage_grade") == "semantic_pins_exercised"
    )
    statistical_status_counts = Counter(row.get("current_status", "unknown") for row in statistical_design)
    precision_half_rows = [row for row in wilson_precision if row.get("assumed_p") == "0.5"]
    figure_status_counts = Counter(row.get("current_status", "unknown") for row in figure_manifest)
    blocked_figure_rows = sum(1 for row in figure_manifest if row.get("category") == "blocked_performance")
    skill_counts: Counter[str] = Counter()
    failure_mode_counts: Counter[str] = Counter()
    for task in accepted:
        skill_counts.update(parse_list(task.get("skills", "")))
        failure_mode_counts.update(parse_list(task.get("expected_failure_modes", "")))

    lines = [
        "# Concise METR-Style Report",
        "",
        "## Bottom Line",
        "",
        (
            "This repository is a locally validated v0.1 Lean time-horizon evaluation artifact, "
            "not a locked benchmark. It has enough local task, grading, reporting, and "
            "anti-overclaim evidence to support review, but not enough accepted-task scale, "
            "independent human timing or task review, provider/scaffold coverage, or hosted QA to support "
            "population-level frontier-model claims."
        ),
        "",
        f"- accepted core tasks: `{len(accepted)}`",
        f"- calibration-only tasks: `{len(calibration)}`",
        f"- rejected archive tasks: `{len(rejected)}`",
        f"- requirement statuses: `{compact_json(dict(sorted(Counter(row.get('status', 'unknown') for row in requirements).items())))}`",
        f"- claim authorizations: `{compact_json(dict(sorted(auth_counts.items())))}`",
        f"- release-decision gates: `{compact_json(dict(sorted(release_counts.items())))}`",
        f"- freeze-readiness gates: `{compact_json(dict(sorted(freeze_counts.items())))}`",
        "",
        "## Research Questions",
        "",
        "1. Can a model recover the intended Lean proof or formalization from the public prompt and scaffold?",
        "2. Which failures are diagnostic of formalization, theorem decomposition, proof debugging, codebase navigation, invariant design, or library/API search?",
        "3. How do lookup and iterative compile/debug scaffolds change outcomes once real sweeps are run?",
        "",
        "The current artifact can evaluate local task/grader validity and prepare the scaffold sweep. It cannot yet answer the third question empirically because committed provider data cover only a tiny smoke sample.",
        "",
        "## Task Set",
        "",
        "Accepted core tasks are mixed across six families, with T2/T3 coverage but no accepted T4 task.",
        "",
        "Accepted families:",
        "",
        bullets(Counter(task.get("family", "unknown") for task in accepted)),
        "",
        "Release time buckets:",
        "",
        bullets(Counter(task.get("human_time_bucket", "unknown") for task in accepted + calibration)),
        "",
        "Accepted core rows:",
        "",
        task_table(accepted),
        "",
        "Candidate pruning evidence:",
        "",
        f"- pruning rows: `{len(candidate_pruning)}`",
        f"- pruning decisions: `{compact_json(dict(sorted(pruning_decision_counts.items())))}`",
        f"- acceptance statuses in pruning audit: `{compact_json(dict(sorted(pruning_status_counts.items())))}`",
        "- `reports/candidate_pruning_audit.md` gives a per-task ledger for accepted, calibration-only, and rejected decisions; it is pruning transparency, not model-performance evidence.",
        "",
        "## Capabilities And Expected Failures",
        "",
        "The accepted set is meant to test diagnostic capabilities, not just theorem-proving difficulty. Singleton capability rows are visible limitations rather than hidden assumptions.",
        "",
        capability_table(diagnostic),
        "",
        "Construct-validity matrix:",
        "",
        f"- accepted task rows traced: `{len(construct)}`",
        f"- support levels: `{compact_json(dict(sorted(construct_support_counts.items())))}`",
        f"- rows with singleton-covered capabilities: `{construct_singleton_rows}/{len(construct)}`",
        "- this is task-level construct evidence, not capability-level performance evidence.",
        f"- accepted-task card recommendations: `{compact_json(dict(sorted(card_recommendation_counts.items())))}`",
        f"- accepted-task cards with wrong controls reaching semantic pins: `{card_hidden_pin_exercised}/{len(accepted_cards)}`",
        "- `reports/accepted_task_cards.md` gives a per-accepted-task synthesis of review status, proof signals, pin-stage evidence, local QA, asset counts, and benchmark-grade blockers without exposing hidden proof contents.",
        "",
        "Most common accepted-task skills:",
        "",
        bullets(Counter(dict(skill_counts.most_common(8)))),
        "",
        "Expected failure modes are author/reviewer forecasts until broader model transcripts are independently labeled. Common expected modes include:",
        "",
        bullets(Counter(dict(failure_mode_counts.most_common(8)))),
        "",
        f"Committed single-review smoke adjudications: `{len(failure_label_reviews)}` rows; failure-label review-audit failures: `{failure_review_failures}`. These rows are transcript provenance evidence, not failure-distribution evidence.",
        "",
        "## Grading And Integrity",
        "",
        "The grader is Lean-first: submissions must pass forbidden-construct scanning, public compilation, hidden `PinCheck.lean`, and axiom auditing. Local QA rows validate reference solutions and wrong submissions; they are not model performance.",
        "",
        f"- run-integrity failures: `{integrity_failures}`",
        f"- data-schema manifest statuses: `{compact_json(dict(sorted(schema_status_counts.items())))}`",
        f"- data-schema problem rows: `{schema_problem_rows}`",
        f"- reviewer reproduction statuses: `{compact_json(dict(sorted(reproduction_status_counts.items())))}`",
        f"- reviewer reproduction local problem rows: `{reproduction_local_problems}`; external-evidence rows blocked: `{reproduction_external_rows}`",
        f"- clean-workspace replay statuses: `{compact_json(dict(sorted(clean_workspace_status_counts.items())))}`",
        f"- clean-workspace replay failures: `{clean_workspace_failures}`",
        f"- grader-hardening failures: `{grader_failures}`",
        "- public export validator checks hidden/wrong files are absent from `public_tasks`.",
        "- hidden pins are meaningful finite probes, not proof of full semantic equivalence.",
        "",
        "## Model Evidence",
        "",
        (
            "Committed provider rows are smoke evidence only. They show the runner and transcript path can work, "
            "but they do not characterize frontier performance, scaffold effects, family-level performance, "
            "or failure distributions."
        ),
        "",
        f"- planned accepted-core task/scaffold cells: `{primary_coverage.get('planned_cells', '0')}`",
        f"- covered non-infra primary cells: `{primary_coverage.get('covered_cells_noninfra', '0')}`",
        f"- accepted-core provider rows: `{accepted_provider.get('rows_total', '0')}` total, `{accepted_provider.get('rows_noninfra', '0')}` non-infra",
        f"- provider/model versions in committed smoke rows: `{compact_json(provider_versions)}`",
        f"- statistical claim-tier statuses: `{compact_json(dict(sorted(statistical_status_counts.items())))}`",
        f"- Wilson precision ledger rows for assumed p=0.5: `{len(precision_half_rows)}`",
        f"- figure-manifest statuses: `{compact_json(dict(sorted(figure_status_counts.items())))}`",
        f"- blocked performance-plot rows in figure manifest: `{blocked_figure_rows}`",
        "- the statistical analysis plan treats current provider rows as smoke provenance only; performance estimates and scaffold effects stay blocked by threshold rows.",
        "- the figure manifest allows descriptive/provenance SVGs while keeping unsupported performance plots intentionally absent.",
        "",
        "## Claim Boundaries",
        "",
        "The report now has explicit claim authorization and a prose conformance audit. Blocked claims may appear only as limitations or future work.",
        "",
        "- `reports/report_claim_conformance_audit.md` checks this narrative, the detailed report, and README for blocked-claim wording.",
        "- `reports/report_shape_audit.md` checks whether this narrative answers the playbook report-shape questions or explicitly blocks unsupported analyses.",
        "- `reports/report_count_consistency_audit.md` checks that repeated top-line counts agree with committed CSV/JSON sources.",
        "- `reports/regeneration_command_consistency.md` checks that README, manifest, and reviewer local-replay commands stay synchronized.",
        "- `reports/candidate_pruning_audit.md` makes the aggressive pruning decision reviewable for every tracked task.",
        "- `reports/accepted_task_cards.md` makes per-task caveats and benchmark-grade blockers easy to inspect without turning them into stronger claims.",
        "- `reports/independent_task_review_packet.md` and `reports/independent_review_status_audit.md` make missing non-author task reviews explicit.",
        "- `reports/data_schema_manifest.md` records schema-backed data contracts and generated CSV boundaries.",
        "- `reports/reviewer_reproduction_packet.md` gives an ordered local replay workflow and separates external-evidence blockers.",
        "- `reports/clean_workspace_replay.md` records a bounded temporary-workspace replay outside the dirty working directory.",
        "- `reports/research_claim_gap_matrix.md` records the evidence packages needed before stronger claims are allowed.",
        "- `reports/threat_coverage_audit.md` checks that open blockers and non-allowed claims are represented in threats-to-validity rows.",
        "- `reports/statistical_analysis_plan.md` records minimum evidence thresholds, blocked overclaim wording, and Wilson precision limits before broader model sweeps.",
        "- `reports/figure_manifest.md` maps generated figures to source data and records blocked performance plots.",
        "",
        claim_table(claim_authorization),
        "",
        "## Evidence Upgrade Path",
        "",
        f"Upgrade priorities: `{compact_json(dict(sorted(gap_priority_counts.items())))}`. High-priority rows are not ready; they are a checklist for evidence that must exist before stronger wording is permitted.",
        "",
        gap_table(research_claim_gap),
        "",
        "## Remaining Blockers",
        "",
        requirement_gap_table,
        "",
        "## Validity Notes",
        "",
        f"- accepted tasks without independent timing observations: `{accepted_without_timing}/{len(accepted)}`",
        f"- independent task-review status counts: `{compact_json(dict(sorted(independent_review_status_counts.items())))}`",
        "- task-count target remains 20-50 accepted tasks; v0.1 has 6 accepted core tasks.",
        "- accepted human-time coverage is T2/T3 only; there is no T4 accepted stretch task.",
        "- capability-level claims remain weak where a capability is represented by a singleton accepted task.",
        "- hosted Taiga/Env Linter QA artifacts are absent.",
        "- the detailed evidence report remains appendix-heavy by design; this concise report is the reviewer-facing narrative.",
        "",
        "## Next Work",
        "",
        "1. Collect independent Lean-human timing and task-quality review observations for every accepted task.",
        "2. Add a small number of hard-reviewed T3/T4 tasks only if they meet the existing diagnostic bar.",
        "3. Run the accepted-core scaffold sweep across one-shot, lookup, and lookup_unlimited with documented provider versions.",
        "4. Run hosted QA and commit Env Linter findings or rebuttals for exact public task versions.",
        "5. Regenerate this report and keep blocked claims blocked until the corresponding evidence is committed.",
        "",
        "## Evidence Appendix",
        "",
        "Detailed evidence is in `reports/metr_style_report.md`, `reports/evidence_appendix.md`, `reports/report_source_traceability.md`, `reports/report_count_consistency_audit.md`, `reports/regeneration_command_consistency.md`, `reports/candidate_pruning_audit.md`, `reports/accepted_task_cards.md`, `reports/independent_task_review_packet.md`, `reports/independent_review_status_audit.md`, `reports/requirement_coverage.md`, `reports/data_schema_manifest.md`, `reports/reviewer_reproduction_packet.md`, `reports/clean_workspace_replay.md`, `reports/claim_authorization_matrix.md`, `reports/research_claim_gap_matrix.md`, `reports/threat_coverage_audit.md`, `reports/statistical_analysis_plan.md`, `reports/figure_manifest.md`, `reports/report_claim_conformance_audit.md`, `reports/report_shape_audit.md`, and the committed CSVs under `data/`.",
        "",
    ]

    out = ROOT / "reports" / "concise_metr_report.md"
    text = "\n".join(lines)
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} with {len(text.splitlines())} lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
