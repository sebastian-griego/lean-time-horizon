from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "evidence_id",
    "claim_area",
    "current_evidence_grade",
    "grade_rank",
    "adequate_for_current_wording",
    "current_wording_allowed",
    "unsupported_stronger_wording",
    "evidence_summary",
    "missing_upgrade_evidence",
    "source_artifacts",
]

GRADE_RANKS = {
    "none": 0,
    "author_estimate_or_plan": 1,
    "local_generated_audit": 2,
    "local_mechanical_validation": 3,
    "local_manual_review": 4,
    "provider_smoke": 5,
    "independent_review": 6,
    "exact_k_provider_sweep": 7,
    "hosted_qa": 8,
    "frozen_release": 9,
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


def req_map() -> dict[str, dict[str, str]]:
    return {
        row.get("requirement_id", ""): row
        for row in read_csv(ROOT / "data" / "requirement_coverage.csv")
    }


def claim_map() -> dict[str, dict[str, str]]:
    return {
        row.get("claim_id", ""): row
        for row in read_csv(ROOT / "data" / "claim_authorization_matrix.csv")
    }


def req(reqs: dict[str, dict[str, str]], requirement_id: str) -> str:
    row = reqs.get(requirement_id, {})
    if not row:
        return f"`{requirement_id}`=missing"
    return f"`{requirement_id}`={row.get('status', 'unknown')}: {row.get('evidence', '')}"


def auth(claims: dict[str, dict[str, str]], claim_id: str) -> str:
    row = claims.get(claim_id, {})
    if not row:
        return f"`{claim_id}`=missing"
    return f"`{claim_id}`={row.get('authorization_status', 'unknown')}"


def row(
    evidence_id: str,
    claim_area: str,
    current_evidence_grade: str,
    adequate_for_current_wording: bool,
    current_wording_allowed: str,
    unsupported_stronger_wording: str,
    evidence_summary: str,
    missing_upgrade_evidence: str,
    source_artifacts: list[str],
) -> dict[str, str]:
    if current_evidence_grade not in GRADE_RANKS:
        raise ValueError(f"unknown evidence grade for {evidence_id}: {current_evidence_grade}")
    return {
        "evidence_id": evidence_id,
        "claim_area": claim_area,
        "current_evidence_grade": current_evidence_grade,
        "grade_rank": str(GRADE_RANKS[current_evidence_grade]),
        "adequate_for_current_wording": "true" if adequate_for_current_wording else "false",
        "current_wording_allowed": current_wording_allowed,
        "unsupported_stronger_wording": unsupported_stronger_wording,
        "evidence_summary": evidence_summary,
        "missing_upgrade_evidence": missing_upgrade_evidence,
        "source_artifacts": ";".join(source_artifacts),
    }


def build_rows() -> list[dict[str, str]]:
    reqs = req_map()
    claims = claim_map()
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    run_results = read_csv(ROOT / "data" / "run_results.csv")
    coverage = read_csv(ROOT / "data" / "model_sweep_coverage_audit.csv")
    independent_reviews = read_csv(ROOT / "data" / "independent_task_reviews.csv")
    human_timing = read_csv(ROOT / "data" / "human_time_observations.csv")
    hosted = read_csv(ROOT / "data" / "hosted_qa_readiness_audit.csv")
    security = read_csv(ROOT / "data" / "security_leakage_audit.csv")
    validation = read_csv(ROOT / "data" / "validation_manifest_audit.csv")
    analysis_decisions = read_csv(ROOT / "data" / "analysis_decision_register.csv")

    accepted = [item for item in metadata if item.get("acceptance_status") == "accepted_v0"]
    nonlocal_rows = [item for item in run_results if item.get("qa_stage") != "local_qa"]
    noninfra = [item for item in nonlocal_rows if item.get("infra_fail_count") in {"", "0", 0}]
    coverage_counts = Counter(item.get("coverage_status", "unknown") for item in coverage)
    hosted_counts = Counter(item.get("status", "unknown") for item in hosted)
    analysis_counts = Counter(item.get("current_evidence_status", "unknown") for item in analysis_decisions)
    validation_failures = sum(1 for item in validation if item.get("status") == "fail")
    security_failures = sum(1 for item in security if item.get("status") == "fail")

    return [
        row(
            "local_artifact_validation",
            "artifact_validity",
            "local_mechanical_validation",
            True,
            "Local v0.1 artifact validity with caveats.",
            "Locked, hosted-QA-cleared, or final benchmark status.",
            (
                f"{auth(claims, 'local_artifact_validity')}; {req(reqs, 'public_prompts_scaffolds')}; "
                f"{req(reqs, 'hidden_references_pins')}; {req(reqs, 'automatic_lean_scoring')}; "
                f"validation_manifest_failures={validation_failures}; security_failures={security_failures}"
            ),
            "Hosted QA, problem-version mapping, independent review, full pass@k sweeps, and accepted-task scale.",
            [
                "reports/validation_manifest_audit.md",
                "reports/requirement_coverage.md",
                "reports/security_leakage_audit.md",
                "reports/clean_workspace_replay.md",
            ],
        ),
        row(
            "accepted_task_quality",
            "task_validity",
            "local_manual_review",
            True,
            "Internally reviewed six-task accepted core with explicit caveats.",
            "Benchmark-grade, representative, independently reviewed accepted set.",
            (
                f"accepted_tasks={len(accepted)}; independent_review_rows={len(independent_reviews)}; "
                f"{auth(claims, 'accepted_core_quality')}; {req(reqs, 'accepted_task_cards')}; "
                f"{req(reqs, 'independent_task_quality_review')}"
            ),
            "Completed non-author reviews, more accepted T2/T3/T4 tasks, and refreshed task-quality review.",
            [
                "reports/accepted_task_review.md",
                "reports/accepted_task_cards.md",
                "reports/independent_review_status_audit.md",
                "reports/candidate_pruning_audit.md",
            ],
        ),
        row(
            "human_time_calibration",
            "calibration",
            "author_estimate_or_plan",
            True,
            "Author/reviewer p50 and p90 estimates with missing independent timing stated as a limitation.",
            "Calibrated time-horizon scaling or independently timed bucket trends.",
            (
                f"human_timing_rows={len(human_timing)}; {auth(claims, 'time_horizon_scope')}; "
                f"{req(reqs, 'human_time_calibration_audit')}; {req(reqs, 'independent_human_time_review')}"
            ),
            "Independent timed solves for every accepted task, with extra scrutiny for T3/T4 rows.",
            [
                "reports/human_time_calibration_audit.md",
                "reports/human_timing_collection_packet.md",
                "data/human_time_observations.csv",
            ],
        ),
        row(
            "grader_semantic_validity",
            "grading_validity",
            "local_mechanical_validation",
            True,
            "Lean scoring, forbidden-construct scanning, axiom auditing, and finite hidden-pin probes.",
            "Full semantic equivalence or complete resistance to all weakened formalizations.",
            (
                f"{auth(claims, 'hidden_pin_and_grader_strength')}; {req(reqs, 'pin_coverage_audit')}; "
                f"{req(reqs, 'grader_hardening_audit')}; {req(reqs, 'axiom_audit_policy')}"
            ),
            "Independent pin review, stronger future same-signature hidden-pin controls where feasible, and hosted isolation evidence.",
            [
                "reports/grader_hardening_audit.md",
                "reports/pin_coverage_audit.md",
                "docs/axiom_policy.md",
                "scripts/validate_task.py",
            ],
        ),
        row(
            "run_data_integrity",
            "data_validity",
            "local_mechanical_validation",
            True,
            "Run rows have schema, transcript, pass@k arithmetic, infra, and local-QA separation checks.",
            "Representative model-performance estimates, scaffold effects, or failure distributions.",
            (
                f"run_rows={len(run_results)}; nonlocal_rows={len(nonlocal_rows)}; noninfra_rows={len(noninfra)}; "
                f"{auth(claims, 'run_data_integrity')}; {req(reqs, 'run_integrity_audit')}; "
                f"{req(reqs, 'run_result_semantics')}"
            ),
            "Broader non-infra provider rows at the planned k, plus transcript review for failed provider rows.",
            [
                "data/run_results.csv",
                "reports/run_integrity_audit.md",
                "reports/passk_claim_boundary_audit.md",
                "reports/model_evidence_provenance_audit.md",
            ],
        ),
        row(
            "model_performance_evidence",
            "performance_claim",
            "provider_smoke" if noninfra else "none",
            True,
            "Provider smoke provenance only, with performance claims blocked.",
            "Frontier capability estimates, model rankings, pass@10 means, or family/bucket performance claims.",
            (
                f"nonlocal_rows={len(nonlocal_rows)}; noninfra_rows={len(noninfra)}; "
                f"coverage_statuses={compact_json(dict(sorted(coverage_counts.items())))}; "
                f"{auth(claims, 'frontier_model_performance')}; {req(reqs, 'frontier_model_evidence')}"
            ),
            "Exact-k non-infra rows for the planned accepted_v0 x scaffold cells, with model versions and transcripts.",
            [
                "reports/model_run_analysis.md",
                "reports/model_sweep_coverage_audit.md",
                "reports/model_evidence_provenance_audit.md",
                "data/run_results.csv",
            ],
        ),
        row(
            "scaffold_comparison_evidence",
            "scaffold_effects",
            "author_estimate_or_plan",
            True,
            "Prospective scaffold ladder and coverage ledger only.",
            "Lookup benefit, iterative-debug benefit, or paired scaffold-effect estimates.",
            (
                f"planned_cells={len(coverage)}; coverage_statuses={compact_json(dict(sorted(coverage_counts.items())))}; "
                f"{auth(claims, 'scaffold_effects')}; {req(reqs, 'scaffold_result_comparison')}; "
                f"analysis_decision_statuses={compact_json(dict(sorted(analysis_counts.items())))}"
            ),
            "Complete paired exact-k rows for the same tasks, model versions, and scaffolds.",
            [
                "reports/evaluation_protocol.md",
                "reports/analysis_decision_register.md",
                "reports/model_sweep_coverage_audit.md",
                "reports/scaffold_support_audit.md",
            ],
        ),
        row(
            "failure_taxonomy_evidence",
            "failure_analysis",
            "local_generated_audit",
            True,
            "Failure taxonomy, transcript queue, and smoke adjudication workflow are present.",
            "Dominant failure modes or distributional taxonomy claims.",
            (
                f"{auth(claims, 'failure_taxonomy_results')}; {req(reqs, 'transcript_review_packet')}; "
                f"{req(reqs, 'failure_label_review_audit')}"
            ),
            "Broad provider failures with independent transcript review and enough rows for distributions.",
            [
                "reports/transcript_review_packet.md",
                "reports/failure_label_review_audit.md",
                "data/failure_label_reviews.csv",
            ],
        ),
        row(
            "statistical_reporting_evidence",
            "statistical_validity",
            "local_generated_audit",
            True,
            "Preregistered statistical thresholds, Wilson precision planning, and blocked performance plots.",
            "Published performance intervals, pass@10-by-scaffold plots, or subgroup performance means.",
            (
                f"{auth(claims, 'statistical_performance_reporting')}; {req(reqs, 'statistical_analysis_plan')}; "
                f"{req(reqs, 'statistical_reporting_audit')}; {req(reqs, 'figure_manifest_audit')}"
            ),
            "Sufficient accepted-task scale and exact-k provider coverage for each plotted comparison.",
            [
                "reports/statistical_analysis_plan.md",
                "reports/statistical_reporting_audit.md",
                "reports/figure_manifest.md",
            ],
        ),
        row(
            "hosted_operational_evidence",
            "operational_validity",
            "local_generated_audit",
            True,
            "Taiga packaging scaffold and local wrapper-isolation checks only.",
            "Hosted-QA-cleared, Env-Linter-cleared, or exact hosted problem-version claims.",
            (
                f"hosted_statuses={compact_json(dict(sorted(hosted_counts.items())))}; "
                f"{auth(claims, 'hosted_qa_status')}; {req(reqs, 'hosted_qa_env_linter')}"
            ),
            "Hosted problem-version rows, Full Env QA, Env Linter findings, dispositions, and immutable image digests.",
            [
                "reports/hosted_qa_readiness_audit.md",
                "reports/taiga_wrapper_isolation_audit.md",
                "taiga/problems_metadata.template.json",
            ],
        ),
        row(
            "locked_benchmark_evidence",
            "benchmark_status",
            "none",
            True,
            "No locked-benchmark claim is allowed; only blockers and exit criteria are reported.",
            "Final, locked, population-valid, or benchmark-ready status.",
            (
                f"{auth(claims, 'locked_benchmark_status')}; {req(reqs, 'portfolio_accepted_count')}; "
                f"{req(reqs, 'time_horizon_spread')}; {req(reqs, 'scaffold_result_comparison')}; "
                f"{req(reqs, 'hosted_qa_env_linter')}"
            ),
            "Clear every freeze-readiness block gate, then tag exact source/export/hosted problem versions.",
            [
                "reports/research_claim_gap_matrix.md",
                "reports/release_decision_log.md",
                "reports/freeze_readiness_roadmap.md",
            ],
        ),
    ]


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    grade_counts = Counter(item["current_evidence_grade"] for item in rows)
    area_counts = Counter(item["claim_area"] for item in rows)
    lines = [
        "# Evidence Strength Matrix",
        "",
        "This generated matrix grades the evidence behind each major report claim. It separates local mechanical validation, author/internal review, provider smoke rows, independent review, exact-k provider sweeps, hosted QA, and frozen-release evidence. It is a claim-control artifact, not new model evidence.",
        "",
        "## Summary",
        "",
        f"- evidence rows: `{len(rows)}`",
        f"- grades: `{compact_json(dict(sorted(grade_counts.items())))}`",
        f"- claim areas: `{compact_json(dict(sorted(area_counts.items())))}`",
        f"- rows adequate for current wording: `{sum(1 for item in rows if item['adequate_for_current_wording'] == 'true')}/{len(rows)}`",
        "",
        "## Grade Ladder",
        "",
        "| grade | rank | interpretation |",
        "| --- | ---: | --- |",
    ]
    grade_notes = {
        "none": "No positive evidence for the stronger claim; only blockers or exit criteria are present.",
        "author_estimate_or_plan": "A prospective plan or author/reviewer estimate exists, but no empirical or independent observation supports the stronger claim.",
        "local_generated_audit": "Generated local reports check consistency, boundaries, or readiness from committed files.",
        "local_mechanical_validation": "Local scripts or Lean checks validate builds, graders, schemas, scans, hashes, or arithmetic.",
        "local_manual_review": "Author-side/manual review has been committed, but non-author review is still missing.",
        "provider_smoke": "At least one non-local provider row exists, but not enough exact-k coverage for benchmark estimates.",
        "independent_review": "Non-author review/timing evidence has been collected and audited.",
        "exact_k_provider_sweep": "Planned accepted-task provider/scaffold cells are covered at the reported k.",
        "hosted_qa": "Hosted QA, Env Linter, and problem-version evidence are committed.",
        "frozen_release": "Exact source/export/hosted versions are mapped and tagged after all blockers clear.",
    }
    for grade, rank in sorted(GRADE_RANKS.items(), key=lambda item: item[1]):
        lines.append(f"| `{grade}` | {rank} | {grade_notes[grade]} |")
    lines.extend([
        "",
        "## Evidence Table",
        "",
        "| evidence | area | grade | current wording allowed | unsupported stronger wording | missing upgrade evidence |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for item in rows:
        lines.append(
            f"| `{item['evidence_id']}` | {item['claim_area']} | {item['current_evidence_grade']} | "
            f"{escaped(item['current_wording_allowed'])} | Unsupported stronger wording: {escaped(item['unsupported_stronger_wording'])} | "
            f"{escaped(item['missing_upgrade_evidence'])} |"
        )
    lines.extend([
        "",
        "## Source Detail",
        "",
        "| evidence | summary | sources |",
        "| --- | --- | --- |",
    ])
    for item in rows:
        lines.append(
            f"| `{item['evidence_id']}` | {escaped(item['evidence_summary'])} | {escaped(item['source_artifacts'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "A high grade in one row does not transfer to another row. For example, local mechanical validation supports local artifact claims, but it cannot support frontier-performance, scaffold-effect, hosted-QA, or locked-benchmark claims. Rows with `provider_smoke`, `author_estimate_or_plan`, or `local_generated_audit` grades should remain caveated until the listed upgrade evidence is committed.",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "evidence_strength_matrix.csv", rows)
    write_markdown(ROOT / "reports" / "evidence_strength_matrix.md", rows)
    print(
        "wrote data/evidence_strength_matrix.csv and reports/evidence_strength_matrix.md "
        f"with {len(rows)} evidence rows"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
