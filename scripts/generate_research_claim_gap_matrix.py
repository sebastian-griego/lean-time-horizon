from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "claim_id",
    "claim_area",
    "authorization_status",
    "claim_support_status",
    "evidence_strength",
    "upgrade_priority",
    "blocking_requirements",
    "blocking_requirement_statuses",
    "minimum_evidence_package",
    "exit_criteria",
    "allowed_wording_now",
    "forbidden_overclaim",
    "source_artifacts",
]

GAP_PLAN: dict[str, dict[str, object]] = {
    "local_artifact_validity": {
        "priority": "medium",
        "requirements": [
            "hosted_qa_env_linter",
            "independent_human_time_review",
            "scaffold_result_comparison",
            "portfolio_accepted_count",
        ],
        "package": "Hosted QA evidence, independent timing/review, broader accepted-task scale, and real scaffold sweeps if this wording is upgraded beyond local artifact validity.",
        "exit": "The local-only caveat can be relaxed only after hosted QA, independent timing, accepted-count, and scaffold-sweep gates are all supported.",
        "artifacts": [
            "reports/validation_manifest.json",
            "reports/hosted_qa_readiness_audit.md",
            "reports/human_time_calibration_audit.md",
        ],
    },
    "research_report_scope": {
        "priority": "medium",
        "requirements": [
            "scaffold_result_comparison",
            "frontier_model_evidence",
            "independent_human_time_review",
            "hosted_qa_env_linter",
        ],
        "package": "Accepted-core provider sweeps, independent timing observations, hosted QA findings/dispositions, and regenerated claim audits.",
        "exit": "The report may make stronger empirical conclusions only when provider, timing, and hosted-QA evidence are committed and claim-conformance remains passing.",
        "artifacts": [
            "reports/model_sweep_execution_packet.md",
            "reports/human_timing_collection_packet.md",
            "reports/hosted_qa_readiness_audit.md",
        ],
    },
    "accepted_core_quality": {
        "priority": "high",
        "requirements": [
            "portfolio_accepted_count",
            "time_horizon_spread",
            "independent_human_time_review",
        ],
        "package": "20-50 hard-reviewed accepted tasks, stronger T3/T4 coverage, independent Lean-human timing, and refreshed per-task review.",
        "exit": "Accepted-core quality can support benchmark-level aggregates only after scale, depth, and independent review gates are supported.",
        "artifacts": [
            "reports/accepted_task_review.md",
            "reports/task_quality_matrix.md",
            "reports/construct_validity_matrix.md",
            "data/human_time_observations.csv",
        ],
    },
    "hidden_pin_and_grader_strength": {
        "priority": "medium",
        "requirements": [],
        "package": "Independent hidden-pin review, more same-signature semantic wrong submissions for future mutable tasks, and zero grader-hardening failures.",
        "exit": "Do not upgrade to exhaustive semantic-equivalence wording; finite pins can only support stronger finite-probe confidence after independent review.",
        "artifacts": [
            "reports/pin_coverage_audit.md",
            "reports/grader_hardening_audit.md",
            "tasks/*/*/hidden/PinCheck.lean",
        ],
    },
    "run_data_integrity": {
        "priority": "maintain",
        "requirements": [],
        "package": "Keep run-integrity and pass@k arithmetic audits green after every new provider sweep.",
        "exit": "No upgrade needed for the narrow data-integrity claim; do not extend it to performance without the performance gates.",
        "artifacts": [
            "data/run_results.csv",
            "reports/run_integrity_audit.md",
            "data/run_results_schema.json",
        ],
    },
    "time_horizon_scope": {
        "priority": "high",
        "requirements": [
            "time_horizon_spread",
            "independent_human_time_review",
            "portfolio_accepted_count",
        ],
        "package": "Independently timed T2/T3/T4 tasks, including at least one T4 stretch row and enough accepted tasks to avoid singleton bucket claims.",
        "exit": "The report can claim robust time-horizon measurement only after accepted tasks cover meaningful T2/T3/T4 depth with independent timing evidence.",
        "artifacts": [
            "reports/human_time_calibration_audit.md",
            "reports/human_timing_collection_packet.md",
            "data/human_time_observations.csv",
        ],
    },
    "scaffold_effects": {
        "priority": "high",
        "requirements": [
            "scaffold_result_comparison",
            "frontier_model_evidence",
        ],
        "package": "Non-infra pass@k rows across accepted_v0 x one-shot/lookup/lookup_unlimited cells, with fixed k, model versions, transcripts, and run-integrity checks.",
        "exit": "Empirical scaffold-effect claims require the planned accepted-core scaffold sweep to be covered and analyzed with raw n and intervals.",
        "artifacts": [
            "reports/evaluation_protocol.md",
            "reports/model_sweep_execution_packet.md",
            "reports/model_run_analysis.md",
        ],
    },
    "frontier_model_performance": {
        "priority": "high",
        "requirements": [
            "frontier_model_evidence",
            "scaffold_result_comparison",
            "hosted_qa_env_linter",
        ],
        "package": "Documented frontier/open-model provider rows with model versions, transcripts, infra notes, hosted-QA-cleared tasks, and integrity audits.",
        "exit": "Frontier-performance wording remains blocked until broad provider rows exist on stable, locally and hosted-QA-checked task versions.",
        "artifacts": [
            "reports/provider_readiness_audit.md",
            "reports/model_run_analysis.md",
            "data/run_results.csv",
        ],
    },
    "failure_taxonomy_results": {
        "priority": "medium",
        "requirements": [
            "frontier_model_evidence",
            "scaffold_result_comparison",
            "transcript_review_packet",
            "failure_label_review_audit",
        ],
        "package": "Independently adjudicated non-local transcripts after broader provider sweeps, with failure-label schema, review templates, and transcript-evidence audits retained.",
        "exit": "Dominant-failure-mode claims require enough non-local transcripts and completed adjudication rows, not author-forecast failure modes.",
        "artifacts": [
            "reports/transcript_review_packet.md",
            "reports/failure_label_review_audit.md",
            "data/failure_label_reviews.csv",
            "data/failure_label_review_template.csv",
            "data/failure_label_schema.json",
        ],
    },
    "statistical_performance_reporting": {
        "priority": "high",
        "requirements": [
            "scaffold_result_comparison",
            "frontier_model_evidence",
            "portfolio_accepted_count",
        ],
        "package": "Sufficiently covered accepted-core sweeps, raw task-row numerators, Wilson intervals, and regenerated statistical reporting checks.",
        "exit": "Performance plots should stay blocked until scaffold/provider coverage and accepted-task scale support the plotted comparisons.",
        "artifacts": [
            "reports/statistical_reporting_audit.md",
            "data/statistical_reporting_audit.csv",
            "reports/model_run_analysis.md",
        ],
    },
    "hosted_qa_status": {
        "priority": "high",
        "requirements": [
            "hosted_qa_env_linter",
        ],
        "package": "Hosted/Taiga package evidence, exact problem-version mapping, Full Env QA runs, Env Linter findings, and rebuttal/fix dispositions.",
        "exit": "Hosted-QA wording can be upgraded only after warning/error/critical findings are fixed or concretely rebutted for exact final versions.",
        "artifacts": [
            "reports/hosted_qa_readiness_audit.md",
            "reports/freeze_readiness_roadmap.md",
        ],
    },
    "locked_benchmark_status": {
        "priority": "highest",
        "requirements": [
            "portfolio_accepted_count",
            "time_horizon_spread",
            "scaffold_result_comparison",
            "frontier_model_evidence",
            "independent_human_time_review",
            "hosted_qa_env_linter",
        ],
        "package": "20-50 accepted tasks, T2/T3/T4 depth, independent timing, completed scaffold/provider sweeps, hosted QA, settled findings, and frozen exact public versions.",
        "exit": "The locked-benchmark claim remains blocked until every locked-benchmark requirement is supported and the release/freeze gates have no blocking rows.",
        "artifacts": [
            "reports/freeze_readiness_roadmap.md",
            "reports/release_decision_log.md",
            "reports/threats_to_validity.md",
        ],
    },
}

EVIDENCE_CLAIM_MAP = {
    "local_artifact_validity": "local_release_artifact",
    "research_report_scope": "research_report_evidence",
    "accepted_core_quality": "accepted_core_reviewed",
    "hidden_pin_and_grader_strength": "hidden_pin_strength",
    "run_data_integrity": "run_data_integrity",
    "time_horizon_scope": "time_horizon_measurement",
    "scaffold_effects": "scaffold_effects",
    "frontier_model_performance": "frontier_performance",
    "locked_benchmark_status": "locked_benchmark",
}

SUPPORT_OVERRIDES = {
    "failure_taxonomy_results": ("partial", "low"),
    "statistical_performance_reporting": ("unsupported", "none"),
    "hosted_qa_status": ("unsupported", "none"),
}


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


def requirement_statuses(ids: list[str], reqs: dict[str, dict[str, str]]) -> str:
    if not ids:
        return "none"
    parts = []
    for requirement_id in ids:
        row = reqs.get(requirement_id, {})
        if not row:
            parts.append(f"`{requirement_id}`=missing")
            continue
        evidence = row.get("evidence", "").replace("\n", " ")
        if len(evidence) > 220:
            evidence = evidence[:217] + "..."
        parts.append(f"`{requirement_id}`={row.get('status', 'unknown')}: {evidence}")
    return "; ".join(parts)


def build_rows() -> list[dict[str, str]]:
    authorizations = read_csv(ROOT / "data" / "claim_authorization_matrix.csv")
    claims = {
        row["claim_id"]: row
        for row in read_csv(ROOT / "data" / "claim_evidence_audit.csv")
    }
    requirements = {
        row["requirement_id"]: row
        for row in read_csv(ROOT / "data" / "requirement_coverage.csv")
    }

    rows: list[dict[str, str]] = []
    for auth in authorizations:
        claim_id = auth.get("claim_id", "")
        evidence_claim_id = EVIDENCE_CLAIM_MAP.get(claim_id, claim_id)
        claim = claims.get(evidence_claim_id, {})
        support_status, evidence_strength = SUPPORT_OVERRIDES.get(
            claim_id,
            (
                claim.get("support_status", "missing"),
                claim.get("evidence_strength", "missing"),
            ),
        )
        plan = GAP_PLAN.get(claim_id, {})
        blocking_requirements = [str(item) for item in plan.get("requirements", [])]
        source_artifacts = [
            "reports/claim_authorization_matrix.md",
            "reports/claim_evidence_audit.md",
            "reports/requirement_coverage.md",
            *[str(item) for item in plan.get("artifacts", [])],
        ]
        rows.append({
            "claim_id": claim_id,
            "claim_area": auth.get("claim_area", ""),
            "authorization_status": auth.get("authorization_status", ""),
            "claim_support_status": support_status,
            "evidence_strength": evidence_strength,
            "upgrade_priority": str(plan.get("priority", "review")),
            "blocking_requirements": ";".join(blocking_requirements) if blocking_requirements else "none",
            "blocking_requirement_statuses": requirement_statuses(blocking_requirements, requirements),
            "minimum_evidence_package": str(plan.get("package", auth.get("evidence_to_upgrade", ""))),
            "exit_criteria": str(plan.get("exit", auth.get("evidence_to_upgrade", ""))),
            "allowed_wording_now": auth.get("allowed_wording", ""),
            "forbidden_overclaim": auth.get("forbidden_wording", ""),
            "source_artifacts": ";".join(dict.fromkeys(source_artifacts)),
        })
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    auth_counts = Counter(row["authorization_status"] for row in rows)
    priority_counts = Counter(row["upgrade_priority"] for row in rows)
    blocked = [
        row for row in rows
        if row["authorization_status"] == "blocked" or row["upgrade_priority"] in {"high", "highest"}
    ]
    lines = [
        "# Research Claim Gap Matrix",
        "",
        "This generated matrix turns the claim authorization layer into an upgrade plan. It states what evidence would have to be committed before each caveated or blocked claim can be strengthened. It does not create new results and should not be read as evidence that a blocked claim has been satisfied.",
        "",
        "## Summary",
        "",
        f"- claims tracked: `{len(rows)}`",
        f"- authorization statuses: `{compact_json(dict(sorted(auth_counts.items())))}`",
        f"- upgrade priorities: `{compact_json(dict(sorted(priority_counts.items())))}`",
        f"- high-or-blocked upgrade rows: `{len(blocked)}`",
        "",
        "## High-Priority Gaps",
        "",
        "| claim | authorization | priority | blocking requirements | minimum evidence package | exit criteria |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in blocked:
        lines.append(
            f"| `{row['claim_id']}` | {row['authorization_status']} | {row['upgrade_priority']} | "
            f"`{row['blocking_requirements']}` | {escaped(row['minimum_evidence_package'])} | "
            f"{escaped(row['exit_criteria'])} |"
        )
    lines.extend([
        "",
        "## Full Matrix",
        "",
        "| claim | area | authorization | support | priority | blocking requirement statuses | forbidden overclaim |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ])
    for row in rows:
        lines.append(
            f"| `{row['claim_id']}` | {row['claim_area']} | {row['authorization_status']} | "
            f"{row['claim_support_status']}/{row['evidence_strength']} | {row['upgrade_priority']} | "
            f"{escaped(row['blocking_requirement_statuses'])} | {escaped(row['forbidden_overclaim'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`upgrade_priority` describes review urgency, not task priority. `highest` and `high` rows are the claims most likely to mislead readers if they are strengthened before the listed evidence package exists. Rows with `maintain` are already supported only for their narrow wording.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "research_claim_gap_matrix.csv", rows)
    write_markdown(ROOT / "reports" / "research_claim_gap_matrix.md", rows)
    high_or_blocked = sum(
        1 for row in rows
        if row["authorization_status"] == "blocked" or row["upgrade_priority"] in {"high", "highest"}
    )
    print(
        "wrote data/research_claim_gap_matrix.csv and "
        f"reports/research_claim_gap_matrix.md with {len(rows)} rows; high_or_blocked={high_or_blocked}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
