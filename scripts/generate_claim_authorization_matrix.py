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
    "allowed_wording",
    "required_caveat",
    "forbidden_wording",
    "current_evidence",
    "evidence_to_upgrade",
    "blocking_requirements",
    "source_artifacts",
]

VALID_AUTHORIZATIONS = {"allowed", "allowed_with_caveat", "blocked"}


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


def requirement_map() -> dict[str, dict[str, str]]:
    return {
        row["requirement_id"]: row
        for row in read_csv(ROOT / "data" / "requirement_coverage.csv")
    }


def claim_map() -> dict[str, dict[str, str]]:
    return {
        row["claim_id"]: row
        for row in read_csv(ROOT / "data" / "claim_evidence_audit.csv")
    }


def req_status(reqs: dict[str, dict[str, str]], requirement_id: str) -> str:
    return reqs.get(requirement_id, {}).get("status", "missing")


def claim_status(claims: dict[str, dict[str, str]], claim_id: str) -> str:
    return claims.get(claim_id, {}).get("support_status", "missing")


def req_evidence(reqs: dict[str, dict[str, str]], requirement_id: str) -> str:
    row = reqs.get(requirement_id, {})
    if not row:
        return f"`{requirement_id}` missing from requirement coverage"
    return f"`{requirement_id}`={row.get('status', '')}: {row.get('evidence', '')}"


def claim_evidence(claims: dict[str, dict[str, str]], claim_id: str) -> str:
    row = claims.get(claim_id, {})
    if not row:
        return f"`{claim_id}` missing from claim evidence"
    return f"`{claim_id}`={row.get('support_status', '')}/{row.get('evidence_strength', '')}: {row.get('counterevidence_or_limits', '')}"


def blocking_requirements(reqs: dict[str, dict[str, str]], ids: list[str]) -> str:
    blocked = [
        requirement_id
        for requirement_id in ids
        if req_status(reqs, requirement_id) != "supported"
    ]
    return ";".join(blocked)


def status_for_claim(
    claims: dict[str, dict[str, str]],
    claim_id: str,
    *,
    caveat_for_partial: bool = True,
) -> str:
    status = claim_status(claims, claim_id)
    if status == "supported":
        return "allowed_with_caveat"
    if status == "partial" and caveat_for_partial:
        return "allowed_with_caveat"
    return "blocked"


def row(
    claim_id: str,
    claim_area: str,
    authorization_status: str,
    allowed_wording: str,
    required_caveat: str,
    forbidden_wording: str,
    current_evidence: str,
    evidence_to_upgrade: str,
    blocking_ids: list[str],
    source_artifacts: list[str],
) -> dict[str, str]:
    if authorization_status not in VALID_AUTHORIZATIONS:
        raise ValueError(f"invalid authorization status for {claim_id}: {authorization_status}")
    return {
        "claim_id": claim_id,
        "claim_area": claim_area,
        "authorization_status": authorization_status,
        "allowed_wording": allowed_wording,
        "required_caveat": required_caveat,
        "forbidden_wording": forbidden_wording,
        "current_evidence": current_evidence,
        "evidence_to_upgrade": evidence_to_upgrade,
        "blocking_requirements": ";".join(blocking_ids),
        "source_artifacts": ";".join(source_artifacts),
    }


def build_rows() -> list[dict[str, str]]:
    reqs = requirement_map()
    claims = claim_map()
    threats = read_csv(ROOT / "data" / "threats_to_validity.csv")
    statistical = read_csv(ROOT / "data" / "statistical_reporting_audit.csv")
    transcript_review = read_csv(ROOT / "data" / "transcript_review_queue.csv")
    failure_label_reviews = read_csv(ROOT / "data" / "failure_label_reviews.csv")
    failure_label_review_audit = read_csv(ROOT / "data" / "failure_label_review_audit.csv")

    threat_status_counts = Counter(row.get("current_status", "unknown") for row in threats)
    statistical_block_count = sum(1 for row in statistical if row.get("status") == "block")
    transcript_unreviewed_count = sum(
        1 for row in transcript_review
        if row.get("qa_findings_status") in {"", "unreviewed"}
    )
    transcript_reviewed_count = len({
        row.get("run_id", "")
        for row in failure_label_reviews
        if row.get("run_id", "")
    })
    failure_label_review_failures = sum(
        1 for row in failure_label_review_audit
        if row.get("status") == "fail"
    )

    local_release_ids = [
        "public_prompts_scaffolds",
        "hidden_references_pins",
        "wrong_submission_controls",
        "automatic_lean_scoring",
        "forbidden_construct_scan",
        "axiom_audit_policy",
        "metadata_completeness",
        "run_result_semantics",
        "scaffold_support",
        "lookup_scaffold_no_hidden_leak",
        "public_export_no_hidden_leak",
    ]
    locked_ids = [
        "portfolio_accepted_count",
        "time_horizon_spread",
        "scaffold_result_comparison",
        "frontier_model_evidence",
        "independent_human_time_review",
        "hosted_qa_env_linter",
    ]

    rows: list[dict[str, str]] = []
    rows.append(row(
        "local_artifact_validity",
        "artifact_validity",
        "allowed_with_caveat" if all(req_status(reqs, requirement_id) == "supported" for requirement_id in local_release_ids) else "blocked",
        "The repo is a locally validated v0.1 research artifact with public tasks, hidden checks, Lean scoring, integrity scans, and metadata.",
        "Say this is local validation only; hosted QA, independent timing, and full model sweeps are outside the current evidence.",
        "Do not call the artifact a locked benchmark, final benchmark, or hosted-QA-cleared benchmark.",
        "; ".join([claim_evidence(claims, "local_release_artifact")] + [req_evidence(reqs, requirement_id) for requirement_id in local_release_ids]),
        "Hosted QA evidence, independent review, full scaffold sweeps, and a larger accepted set.",
        blocking_requirements(reqs, local_release_ids).split(";") if blocking_requirements(reqs, local_release_ids) else [],
        [
            "reports/claim_evidence_audit.md",
            "reports/requirement_coverage.md",
            "reports/validation_manifest.json",
        ],
    ))
    rows.append(row(
        "research_report_scope",
        "report_validity",
        status_for_claim(claims, "research_report_evidence"),
        "The report is a generated research review memo that makes task-quality, grading, reproducibility, and evidence-limit claims from committed artifacts.",
        "Pair this with the limitations that broad provider sweeps, independent human timing, and hosted QA are missing.",
        "Do not describe the report as proving frontier capability trends or benchmark-valid pass-rate effects.",
        f"{claim_evidence(claims, 'research_report_evidence')}; threat statuses={compact_json(dict(sorted(threat_status_counts.items())))}",
        "Complete the planned model sweeps, collect independent timing, and add hosted QA/finding dispositions.",
        ["scaffold_result_comparison", "frontier_model_evidence", "independent_human_time_review", "hosted_qa_env_linter"],
        [
            "reports/metr_style_report.md",
            "reports/threats_to_validity.md",
            "reports/release_decision_log.md",
        ],
    ))
    rows.append(row(
        "accepted_core_quality",
        "task_validity",
        status_for_claim(claims, "accepted_core_reviewed"),
        "The six accepted-core tasks are internally reviewed and stronger than the original candidate pool.",
        "Say the core is small, internally reviewed, and still has caveat rows; do not generalize from family-level singletons.",
        "Do not say the accepted set is benchmark-grade, representative, or sufficient for population-level model claims.",
        f"{claim_evidence(claims, 'accepted_core_reviewed')}; {req_evidence(reqs, 'portfolio_accepted_count')}; {req_evidence(reqs, 'diagnostic_coverage_audit')}; {req_evidence(reqs, 'construct_validity_matrix')}",
        "Independent Lean-human review plus more hard-reviewed T2/T3/T4 accepted tasks.",
        blocking_requirements(reqs, ["portfolio_accepted_count", "time_horizon_spread"]).split(";") if blocking_requirements(reqs, ["portfolio_accepted_count", "time_horizon_spread"]) else [],
        [
            "reports/accepted_task_review.md",
            "reports/task_quality_matrix.md",
            "reports/construct_validity_matrix.md",
            "reports/difficulty_audit.md",
        ],
    ))
    rows.append(row(
        "hidden_pin_and_grader_strength",
        "grading_validity",
        status_for_claim(claims, "hidden_pin_strength"),
        "Hidden checks provide meaningful anti-gaming probes for accepted tasks, especially mutable-definition semantic-pin tasks.",
        "Note that proof-only fixed-statement rows mostly rely on Lean typechecking plus downstream signature guards, and all pins are finite probes.",
        "Do not claim hidden pins prove full semantic equivalence or catch every weakened formalization.",
        f"{claim_evidence(claims, 'hidden_pin_strength')}; {req_evidence(reqs, 'pin_coverage_audit')}; {req_evidence(reqs, 'grader_hardening_audit')}",
        "Independent pin review and additional same-signature hidden-pin failures for future mutable-definition tasks.",
        [],
        [
            "reports/pin_coverage_audit.md",
            "reports/grader_hardening_audit.md",
            "tasks/*/*/hidden/PinCheck.lean",
        ],
    ))
    rows.append(row(
        "run_data_integrity",
        "data_validity",
        "allowed" if claim_status(claims, "run_data_integrity") == "supported" and req_status(reqs, "run_integrity_audit") == "supported" else "blocked",
        "Committed run-result rows are internally consistent with transcripts, score vectors, failure labels, and pass@k arithmetic.",
        "No extra caveat is needed for this narrow data-integrity wording; add the limitation before discussing model performance.",
        "Do not infer model pass rates, scaffold effects, or failure distributions from local QA rows.",
        f"{claim_evidence(claims, 'run_data_integrity')}; {req_evidence(reqs, 'run_integrity_audit')}; {req_evidence(reqs, 'run_result_semantics')}",
        "Keep zero failing run-integrity rows after broad provider sweeps and transcript review.",
        blocking_requirements(reqs, ["run_integrity_audit", "run_result_semantics"]).split(";") if blocking_requirements(reqs, ["run_integrity_audit", "run_result_semantics"]) else [],
        [
            "data/run_results.csv",
            "reports/run_integrity_audit.md",
            "data/run_results_schema.json",
        ],
    ))
    rows.append(row(
        "time_horizon_scope",
        "construct_validity",
        "allowed_with_caveat" if claim_status(claims, "time_horizon_measurement") == "partial" else "blocked",
        "The artifact explores a limited T2/T3-only slice of time-horizon evaluation design.",
        "State that accepted human times are author/reviewer estimates, there is no T4 row, and no independent timing observations are committed.",
        "Do not claim robust measurement of increasing time horizon or calibrated human-time scaling.",
        f"{claim_evidence(claims, 'time_horizon_measurement')}; {req_evidence(reqs, 'time_horizon_spread')}; {req_evidence(reqs, 'independent_human_time_review')}",
        "Add independently timed T3/T4 rows, including at least one T4 task, before stronger time-horizon claims.",
        blocking_requirements(reqs, ["time_horizon_spread", "independent_human_time_review"]).split(";") if blocking_requirements(reqs, ["time_horizon_spread", "independent_human_time_review"]) else [],
        [
            "reports/human_time_calibration_audit.md",
            "reports/human_timing_collection_packet.md",
            "data/human_time_observations.csv",
        ],
    ))
    rows.append(row(
        "scaffold_effects",
        "performance_claim",
        "blocked" if claim_status(claims, "scaffold_effects") != "supported" else "allowed_with_caveat",
        "The scaffold ladder and execution plan are implemented; empirical scaffold-effect conclusions are not yet supported.",
        "Only describe planned scaffold comparisons and the fact that current provider rows do not cover lookup or iterative debug cells.",
        "Do not claim lookup helps, iterative compile/debug helps, or scaffold effects are measured from committed rows.",
        f"{claim_evidence(claims, 'scaffold_effects')}; {req_evidence(reqs, 'scaffold_result_comparison')}; {req_evidence(reqs, 'model_sweep_execution_packet')}",
        "Run accepted-core pass@k rows across one-shot, lookup, and lookup_unlimited with documented provider versions.",
        blocking_requirements(reqs, ["scaffold_result_comparison", "frontier_model_evidence"]).split(";") if blocking_requirements(reqs, ["scaffold_result_comparison", "frontier_model_evidence"]) else [],
        [
            "reports/evaluation_protocol.md",
            "reports/model_sweep_execution_packet.md",
            "reports/model_run_analysis.md",
        ],
    ))
    rows.append(row(
        "frontier_model_performance",
        "performance_claim",
        "blocked",
        "No frontier-performance conclusion is authorized from the committed provider smoke rows.",
        "It is acceptable to state that provider adapters and smoke transcripts exist, but they are not benchmark results.",
        "Do not report committed smoke rows as characterizing frontier capability or model rankings.",
        f"{claim_evidence(claims, 'frontier_performance')}; {req_evidence(reqs, 'frontier_model_evidence')}; {req_evidence(reqs, 'provider_readiness_audit')}",
        "Run documented frontier/open-model sweeps after local and hosted QA are stable.",
        blocking_requirements(reqs, ["frontier_model_evidence", "scaffold_result_comparison"]).split(";") if blocking_requirements(reqs, ["frontier_model_evidence", "scaffold_result_comparison"]) else [],
        [
            "reports/provider_readiness_audit.md",
            "reports/model_run_analysis.md",
            "data/run_results.csv",
        ],
    ))
    rows.append(row(
        "failure_taxonomy_results",
        "failure_analysis",
        "allowed_with_caveat",
        "The repo has a failure-label schema, transcript links, a transcript review queue, and a single-review audit for the committed smoke rows.",
        f"Current adjudication is single-review smoke evidence only: reviewed rows {transcript_reviewed_count}/{len(transcript_review)}, raw queue rows still marked unreviewed in run_results {transcript_unreviewed_count}, audit failures {failure_label_review_failures}.",
        "Do not claim dominant failure modes, distributional failure analysis, or adjudicated taxonomy results.",
        f"{req_evidence(reqs, 'transcript_failure_workflow')}; {req_evidence(reqs, 'transcript_review_packet')}; {req_evidence(reqs, 'failure_label_review_audit')}",
        "Collect independently adjudicated non-local transcripts after broad provider sweeps.",
        [],
        [
            "reports/transcript_review_packet.md",
            "reports/failure_label_review_audit.md",
            "data/failure_label_reviews.csv",
            "data/failure_label_review_template.csv",
            "data/failure_label_schema.json",
        ],
    ))
    rows.append(row(
        "statistical_performance_reporting",
        "statistical_validity",
        "blocked",
        "Statistical reporting checks exist and currently block recommended performance plots.",
        "Describe the statistical audit as a guardrail for future sweeps, not as performance evidence.",
        "Do not publish pass@10-by-scaffold plots, family means, or confidence intervals as substantive results yet.",
        f"{req_evidence(reqs, 'statistical_analysis_plan')}; {req_evidence(reqs, 'statistical_reporting_audit')}; statistical block rows={statistical_block_count}",
        "Run sufficiently covered accepted-core sweeps and report raw n, task-row numerators, and intervals.",
        ["scaffold_result_comparison", "frontier_model_evidence"],
        [
            "reports/statistical_analysis_plan.md",
            "data/statistical_design_thresholds.csv",
            "data/wilson_precision_table.csv",
            "reports/statistical_reporting_audit.md",
            "data/statistical_reporting_audit.csv",
            "reports/model_run_analysis.md",
        ],
    ))
    rows.append(row(
        "hosted_qa_status",
        "operational_validity",
        "blocked",
        "Hosted/Taiga QA readiness has been audited, and the hosted QA evidence is currently absent.",
        "State only that local validation is ready for a hosted QA loop; do not imply hosted checks have run.",
        "Do not claim Full Env QA passed, Env Linter findings are settled, or hosted problem versions are frozen.",
        f"{req_evidence(reqs, 'hosted_qa_env_linter')}; {req_evidence(reqs, 'hosted_qa_readiness_audit')}",
        "Run hosted Full Env QA, record Env Linter findings/rebuttals, and commit exact problem-version evidence.",
        ["hosted_qa_env_linter"],
        [
            "reports/hosted_qa_readiness_audit.md",
            "reports/freeze_readiness_roadmap.md",
        ],
    ))
    rows.append(row(
        "locked_benchmark_status",
        "benchmark_status",
        "blocked",
        "v0.1 is not a locked benchmark; it is a local v0.1 research artifact with explicit blockers.",
        "Every report summary should preserve this boundary until all locked-benchmark gates are satisfied.",
        "Do not call v0.1 final, locked, population-valid, or suitable for benchmark headline claims.",
        f"{claim_evidence(claims, 'locked_benchmark')}; {req_evidence(reqs, 'freeze_readiness_roadmap')}; locked blockers={blocking_requirements(reqs, locked_ids)}",
        "Reach 20-50 accepted tasks, add T3/T4 depth, collect independent timing, complete scaffold/provider sweeps, run hosted QA, and freeze exact public versions.",
        blocking_requirements(reqs, locked_ids).split(";") if blocking_requirements(reqs, locked_ids) else [],
        [
            "reports/freeze_readiness_roadmap.md",
            "reports/release_decision_log.md",
            "reports/threats_to_validity.md",
        ],
    ))
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row["authorization_status"] for row in rows)
    area_counts = Counter(row["claim_area"] for row in rows)
    lines = [
        "# Claim Authorization Matrix",
        "",
        "This generated matrix is the report's wording control layer. It turns evidence audits into explicit allowed, caveated, and blocked claims so reviewers can see where the artifact stops.",
        "",
        "## Summary",
        "",
        f"- claims authorized: `{len(rows)}`",
        f"- authorization statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- claim areas: `{compact_json(dict(sorted(area_counts.items())))}`",
        "",
        "## Authorization Table",
        "",
        "| claim | area | status | allowed wording | required caveat | forbidden wording | evidence to upgrade | blockers |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row_data in rows:
        lines.append(
            f"| `{row_data['claim_id']}` | {row_data['claim_area']} | {row_data['authorization_status']} | "
            f"{escaped(row_data['allowed_wording'])} | {escaped(row_data['required_caveat'])} | "
            f"{escaped(row_data['forbidden_wording'])} | {escaped(row_data['evidence_to_upgrade'])} | "
            f"`{row_data['blocking_requirements']}` |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`allowed` claims can be stated as written. `allowed_with_caveat` claims require the caveat in the same paragraph or nearby table. `blocked` claims should appear only as limitations or future-work targets, not as conclusions.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "claim_authorization_matrix.csv", rows)
    write_markdown(ROOT / "reports" / "claim_authorization_matrix.md", rows)
    print(
        "wrote data/claim_authorization_matrix.csv and "
        f"reports/claim_authorization_matrix.md with {len(rows)} rows"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
