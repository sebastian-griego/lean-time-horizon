from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "question_id",
    "review_area",
    "verdict",
    "reviewer_question",
    "current_answer",
    "evidence",
    "residual_risk",
    "required_upgrade_evidence",
    "source_artifacts",
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


def by_id(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row.get(key, ""): row for row in rows if row.get(key, "")}


def req_text(reqs: dict[str, dict[str, str]], requirement_id: str) -> str:
    row = reqs.get(requirement_id)
    if not row:
        return f"`{requirement_id}` missing"
    return f"`{requirement_id}`={row.get('status', '')}: {row.get('evidence', '')}"


def claim_text(claims: dict[str, dict[str, str]], claim_id: str) -> str:
    row = claims.get(claim_id)
    if not row:
        return f"`{claim_id}` missing"
    return f"`{claim_id}`={row.get('authorization_status', '')}: {row.get('allowed_wording', '')}"


def audit_status(path: str, status_field: str = "status") -> str:
    rows = read_csv(ROOT / path)
    if not rows:
        return f"{path}: missing or empty"
    counts = Counter(row.get(status_field, "unknown") for row in rows)
    return f"{path}: rows={len(rows)}; {status_field}s={compact_json(dict(sorted(counts.items())))}"


def row(
    question_id: str,
    review_area: str,
    verdict: str,
    reviewer_question: str,
    current_answer: str,
    evidence: str,
    residual_risk: str,
    required_upgrade_evidence: str,
    source_artifacts: list[str],
) -> dict[str, str]:
    return {
        "question_id": question_id,
        "review_area": review_area,
        "verdict": verdict,
        "reviewer_question": reviewer_question,
        "current_answer": current_answer,
        "evidence": evidence,
        "residual_risk": residual_risk,
        "required_upgrade_evidence": required_upgrade_evidence,
        "source_artifacts": ";".join(source_artifacts),
    }


def build_rows() -> list[dict[str, str]]:
    reqs = by_id(read_csv(ROOT / "data" / "requirement_coverage.csv"), "requirement_id")
    claims = by_id(read_csv(ROOT / "data" / "claim_authorization_matrix.csv"), "claim_id")
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    accepted = [task for task in metadata if task.get("acceptance_status") == "accepted_v0"]
    calibration = [task for task in metadata if task.get("acceptance_status") == "calibration_only"]
    rejected = [task for task in metadata if task.get("acceptance_status", "").startswith("rejected_")]
    model_coverage = read_csv(ROOT / "data" / "model_sweep_coverage_audit.csv")
    pass_ready = sum(1 for item in model_coverage if item.get("coverage_status") in {"covered_pass", "covered_fail"})
    smoke_cells = sum(1 for item in model_coverage if item.get("coverage_status") == "smoke_only")
    coverage_statuses = Counter(item.get("coverage_status", "unknown") for item in model_coverage)

    return [
        row(
            "scope_status",
            "scope",
            "pass",
            "Does the report clearly state what the artifact is and is not?",
            "Yes. The authorized wording is a local v0.1 research artifact with explicit blockers; locked-benchmark wording remains blocked.",
            f"{claim_text(claims, 'local_artifact_validity')}; {claim_text(claims, 'locked_benchmark_status')}; {req_text(reqs, 'protocol_deviation_log')}; {req_text(reqs, 'report_claim_conformance_audit')}",
            "A reader could still skim past caveats, so the bottom line and claim ledger must remain prominent.",
            "No stronger scope wording until every locked-benchmark blocker is supported.",
            [
                "reports/concise_metr_report.md",
                "reports/claim_authorization_matrix.md",
                "reports/protocol_deviation_log.md",
                "reports/report_claim_conformance_audit.md",
            ],
        ),
        row(
            "task_portfolio_scale",
            "task_set",
            "block",
            "Is the accepted task set large and deep enough for benchmark-level conclusions?",
            "No. The accepted core is useful for local artifact review but below the 20-50 task target and has no accepted T4 row.",
            (
                f"accepted={len(accepted)}; calibration={len(calibration)}; rejected={len(rejected)}; "
                f"{req_text(reqs, 'portfolio_accepted_count')}; {req_text(reqs, 'time_horizon_spread')}; {req_text(reqs, 'protocol_deviation_log')}"
            ),
            "Family and capability summaries are singleton-heavy and should not be treated as stable population estimates.",
            "Reach 20-50 accepted tasks with independently reviewed T2/T3/T4 depth, including at least one T4 task.",
            [
                "data/task_metadata.csv",
                "reports/candidate_pruning_audit.md",
                "reports/protocol_deviation_log.md",
                "reports/freeze_readiness_roadmap.md",
            ],
        ),
        row(
            "diagnostic_task_quality",
            "task_quality",
            "caution",
            "Do the accepted tasks measure interpretable capabilities rather than only easy theorem proving?",
            "Partially. The accepted core spans six families and multiple diagnostic capabilities, but several rows retain caveats and independent non-author review is still missing.",
            (
                f"{req_text(reqs, 'mixed_realistic_portfolio')}; {req_text(reqs, 'diagnostic_coverage_audit')}; "
                f"{req_text(reqs, 'construct_validity_matrix')}; {req_text(reqs, 'independent_task_quality_review')}"
            ),
            "Internal review and local validation are not substitutes for independent task-quality review.",
            "Collect non-author reviews and expand accepted rows only when they preserve diagnostic diversity.",
            [
                "reports/accepted_task_review.md",
                "reports/diagnostic_coverage_audit.md",
                "reports/construct_validity_matrix.md",
                "reports/independent_task_review_packet.md",
            ],
        ),
        row(
            "grader_semantic_validity",
            "grading",
            "caution",
            "Are grading checks hard to game and semantically meaningful?",
            "Mostly for local review. Lean compilation, forbidden-construct scans, axiom audit, wrong submissions, and hidden pins are in place; hidden pins remain finite probes.",
            (
                f"{req_text(reqs, 'automatic_lean_scoring')}; {req_text(reqs, 'forbidden_construct_scan')}; "
                f"{req_text(reqs, 'axiom_audit_policy')}; {req_text(reqs, 'pin_coverage_audit')}; "
                f"{req_text(reqs, 'grader_hardening_audit')}"
            ),
            "Finite semantic pins cannot prove full equivalence, and proof-only tasks rely more heavily on fixed theorem signatures.",
            "Add independent pin review and more same-signature hidden-pin failures for future mutable-spec tasks.",
            [
                "reports/pin_coverage_audit.md",
                "reports/grader_hardening_audit.md",
                "docs/axiom_policy.md",
            ],
        ),
        row(
            "run_data_and_passk_semantics",
            "run_data",
            "pass",
            "Are run-result rows internally coherent and are smoke rows separated from pass@k evidence?",
            "Yes for the current data. Run integrity and pass@k semantics pass, and exact-k pass@k-ready cells remain separated from smoke-only rows.",
            (
                f"{req_text(reqs, 'run_integrity_audit')}; {req_text(reqs, 'run_result_semantics')}; "
                f"{req_text(reqs, 'model_sweep_coverage_audit')}; {req_text(reqs, 'passk_claim_boundary_audit')}; "
                f"pass_at_k_ready={pass_ready}/{len(model_coverage)}; smoke_only={smoke_cells}; statuses={compact_json(dict(sorted(coverage_statuses.items())))}"
            ),
            "This proves data hygiene, not adequate model sample size.",
            "Maintain zero run-integrity and pass@k-boundary failures after real provider sweeps.",
            [
                "reports/run_integrity_audit.md",
                "reports/model_sweep_coverage_audit.md",
                "reports/passk_claim_boundary_audit.md",
            ],
        ),
        row(
            "model_performance_evidence",
            "model_results",
            "block",
            "Do committed model rows support frontier performance or scaffold-effect claims?",
            "No. The provider rows are smoke provenance only; there are zero exact-k pass@k-ready accepted-core scaffold cells.",
            (
                f"{req_text(reqs, 'frontier_model_evidence')}; {req_text(reqs, 'scaffold_result_comparison')}; "
                f"{claim_text(claims, 'frontier_model_performance')}; {claim_text(claims, 'scaffold_effects')}"
            ),
            "Any pass-rate, ranking, scaffold-effect, family, or time-bucket performance interpretation would overclaim.",
            "Run accepted-core pass@k sweeps across one-shot, lookup, and lookup_unlimited with committed transcripts and model versions.",
            [
                "reports/model_run_analysis.md",
                "reports/model_sweep_execution_packet.md",
                "reports/statistical_reporting_audit.md",
            ],
        ),
        row(
            "statistical_reporting",
            "statistics",
            "block",
            "Are statistical plots and intervals publishable as performance results?",
            "No. The statistical plan exists and correctly blocks performance plots under current coverage.",
            f"{req_text(reqs, 'analysis_decision_register')}; {req_text(reqs, 'evidence_strength_matrix')}; {req_text(reqs, 'statistical_analysis_plan')}; {req_text(reqs, 'statistical_reporting_audit')}; {req_text(reqs, 'figure_manifest_audit')}",
            "Descriptive task-count figures are supported, but performance figures would imply nonexistent coverage.",
            "Generate performance plots only after planned cells are covered and raw n plus Wilson intervals can be reported.",
            [
                "reports/statistical_analysis_plan.md",
                "reports/analysis_decision_register.md",
                "reports/evidence_strength_matrix.md",
                "reports/statistical_reporting_audit.md",
                "reports/figure_manifest.md",
            ],
        ),
        row(
            "human_time_evidence",
            "calibration",
            "block",
            "Are human-time buckets independently calibrated?",
            "No. Accepted tasks have manual review fields but no independent timed solve observations.",
            f"{req_text(reqs, 'human_time_calibration_audit')}; {req_text(reqs, 'independent_human_time_review')}",
            "Time-horizon claims remain author/reviewer-estimate-only.",
            "Collect independent Lean-human solve times or second-reviewer timing rows for every accepted task before freeze.",
            [
                "reports/human_time_calibration_audit.md",
                "reports/human_timing_collection_packet.md",
                "data/human_time_observations.csv",
            ],
        ),
        row(
            "hosted_qa_and_public_export",
            "operational_validity",
            "caution",
            "Are public assets clean, and has hosted QA proven runtime isolation?",
            "Local public export and committed/exported leakage scans are clean, but hosted QA, Env Linter, problem-version mapping, and uploaded-image evidence are absent.",
            (
                f"{req_text(reqs, 'public_export_no_hidden_leak')}; {req_text(reqs, 'hosted_qa_readiness_audit')}; "
                f"{req_text(reqs, 'security_leakage_audit')}; {req_text(reqs, 'hosted_qa_env_linter')}; {claim_text(claims, 'hosted_qa_status')}"
            ),
            "Local wrapper, export, and leakage checks do not prove hosted filesystem-tool isolation or final problem-version behavior.",
            "Run hosted preflight, Full Env QA, Env Linter, and record exact problem versions plus finding dispositions.",
            [
                "reports/hosted_qa_readiness_audit.md",
                "reports/taiga_wrapper_isolation_audit.md",
                "reports/security_leakage_audit.md",
                "public_tasks",
            ],
        ),
        row(
            "local_reproducibility",
            "reproducibility",
            "pass",
            "Can a reviewer reproduce local evidence from committed commands and artifacts?",
            "Yes for the local role. The README gate, reviewer packet, clean-workspace replay, regeneration-command audit, and manifest audit are synchronized and passing.",
            (
                f"{req_text(reqs, 'reviewer_reproduction_packet')}; {req_text(reqs, 'clean_workspace_replay')}; "
                f"{req_text(reqs, 'regeneration_command_consistency')}; {req_text(reqs, 'validation_manifest_audit')}"
            ),
            "This is local reproducibility, not hosted QA or clean remote CI proof.",
            "For a release tag, rerun from a remote clean checkout or CI and record hosted evidence separately.",
            [
                "reports/reviewer_reproduction_packet.md",
                "reports/clean_workspace_replay.md",
                "reports/regeneration_command_consistency.md",
                "reports/validation_manifest.json",
            ],
        ),
        row(
            "claim_control_system",
            "claims",
            "pass",
            "Are tempting overclaims mechanically constrained in the report?",
            "Yes. Claim authorization, evidence-strength grading, claim conformance, count consistency, source traceability, and pass@k boundary audits are present and passing.",
            (
                f"{req_text(reqs, 'claim_authorization_matrix')}; {req_text(reqs, 'report_claim_conformance_audit')}; "
                f"{req_text(reqs, 'evidence_strength_matrix')}; {req_text(reqs, 'report_source_traceability')}; {req_text(reqs, 'report_count_consistency_audit')}; "
                f"{req_text(reqs, 'passk_claim_boundary_audit')}"
            ),
            "Text audits are guardrails; they do not create missing provider, timing, task-review, or hosted evidence.",
            "Keep these audits in the validation gate after every report, run-data, or claim-policy change.",
            [
                "reports/claim_authorization_matrix.md",
                "reports/evidence_strength_matrix.md",
                "reports/report_claim_conformance_audit.md",
                "reports/report_source_traceability.md",
                "reports/passk_claim_boundary_audit.md",
            ],
        ),
        row(
            "upgrade_path",
            "roadmap",
            "pass",
            "Is there a concrete path from this artifact to a locked benchmark?",
            "Yes. The deviation log, gap matrix, release decision log, freeze roadmap, and final-delivery checklist name the missing evidence and exit criteria.",
            (
                f"{req_text(reqs, 'protocol_deviation_log')}; {req_text(reqs, 'research_claim_gap_matrix')}; {req_text(reqs, 'release_decision_log')}; "
                f"{req_text(reqs, 'freeze_readiness_roadmap')}; {req_text(reqs, 'final_delivery_checklist_audit')}"
            ),
            "The roadmap is not evidence that the blocked gates have been completed.",
            "Use the roadmap as the acceptance gate for future task additions, provider sweeps, independent reviews, and hosted QA.",
            [
                "reports/research_claim_gap_matrix.md",
                "reports/protocol_deviation_log.md",
                "reports/release_decision_log.md",
                "reports/freeze_readiness_roadmap.md",
                "reports/final_delivery_checklist_audit.md",
            ],
        ),
    ]


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    status_counts = Counter(row["verdict"] for row in rows)
    area_counts = Counter(row["review_area"] for row in rows)
    lines = [
        "# Peer Review Matrix",
        "",
        "This generated matrix is a skeptical-review checklist for the v0.1 report. It converts existing requirement, claim, validation, model-coverage, and roadmap evidence into reviewer questions, current defensible answers, residual risks, and upgrade evidence. `block` rows are not script failures; they are claims the current artifact must not make.",
        "",
        "## Summary",
        "",
        f"- questions: `{len(rows)}`",
        f"- verdicts: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- review areas: `{compact_json(dict(sorted(area_counts.items())))}`",
        "",
        "## Reviewer Questions",
        "",
        "| question | area | verdict | current answer | residual risk | upgrade evidence |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in rows:
        lines.append(
            f"| `{item['question_id']}` | {item['review_area']} | {item['verdict']} | "
            f"{escaped(item['current_answer'])} | {escaped(item['residual_risk'])} | "
            f"{escaped(item['required_upgrade_evidence'])} |"
        )
    lines.extend([
        "",
        "## Evidence Detail",
        "",
        "| question | reviewer question | evidence | sources |",
        "| --- | --- | --- | --- |",
    ])
    for item in rows:
        lines.append(
            f"| `{item['question_id']}` | {escaped(item['reviewer_question'])} | "
            f"{escaped(item['evidence'])} | {escaped(item['source_artifacts'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`pass` means current artifacts support the narrow answer in that row. `caution` means the answer is defensible only with the stated caveat. `block` means a stronger research or benchmark claim remains unsupported until the listed upgrade evidence is committed.",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "peer_review_matrix.csv", rows)
    write_markdown(ROOT / "reports" / "peer_review_matrix.md", rows)
    counts = Counter(row["verdict"] for row in rows)
    print(
        "wrote data/peer_review_matrix.csv and reports/peer_review_matrix.md "
        f"with {len(rows)} questions; verdicts={compact_json(dict(sorted(counts.items())))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
