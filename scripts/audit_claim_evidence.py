from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "claim_id",
    "claim",
    "claim_type",
    "support_status",
    "evidence_strength",
    "primary_evidence",
    "counterevidence_or_limits",
    "stronger_claim_requires",
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


def requirement_map() -> dict[str, dict[str, str]]:
    return {row["requirement_id"]: row for row in read_csv(ROOT / "data" / "requirement_coverage.csv")}


def status(reqs: dict[str, dict[str, str]], requirement_id: str) -> str:
    return reqs.get(requirement_id, {}).get("status", "missing")


def evidence(reqs: dict[str, dict[str, str]], requirement_id: str) -> str:
    row = reqs.get(requirement_id, {})
    if not row:
        return f"`{requirement_id}` missing from requirement coverage."
    return f"`{requirement_id}`: {row.get('status', '')}; {row.get('evidence', '')}"


def all_status(reqs: dict[str, dict[str, str]], ids: list[str], target: str = "supported") -> bool:
    return all(status(reqs, requirement_id) == target for requirement_id in ids)


def any_status(reqs: dict[str, dict[str, str]], ids: list[str], target: str) -> bool:
    return any(status(reqs, requirement_id) == target for requirement_id in ids)


def row(
    claim_id: str,
    claim: str,
    claim_type: str,
    support_status: str,
    evidence_strength: str,
    primary_evidence: str,
    counterevidence_or_limits: str,
    stronger_claim_requires: str,
) -> dict[str, str]:
    return {
        "claim_id": claim_id,
        "claim": claim,
        "claim_type": claim_type,
        "support_status": support_status,
        "evidence_strength": evidence_strength,
        "primary_evidence": primary_evidence,
        "counterevidence_or_limits": counterevidence_or_limits,
        "stronger_claim_requires": stronger_claim_requires,
    }


def build_rows() -> list[dict[str, str]]:
    reqs = requirement_map()
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    run_integrity = read_csv(ROOT / "data" / "run_integrity_audit.csv")
    pin_coverage = read_csv(ROOT / "data" / "pin_coverage_audit.csv")
    model_summary = read_csv(ROOT / "data" / "model_result_summary.csv")
    accepted = [task for task in metadata if task.get("acceptance_status") == "accepted_v0"]
    calibration = [task for task in metadata if task.get("acceptance_status") == "calibration_only"]
    rejected = [task for task in metadata if task.get("acceptance_status", "").startswith("rejected_")]
    accepted_pin = [row for row in pin_coverage if row.get("acceptance_status") == "accepted_v0"]
    accepted_hidden_pin_tasks = sum(1 for row in accepted_pin if int(row.get("wrongs_failing_hidden_pin_stage", "0") or "0") > 0)
    mutable_pin_rows = [
        row for row in accepted_pin
        if row.get("same_signature_hidden_wrong_feasibility") == "feasible_via_definition_semantics"
    ]
    mutable_hidden_pin_tasks = sum(
        1 for row in mutable_pin_rows
        if int(row.get("wrongs_failing_hidden_pin_stage", "0") or "0") > 0
    )
    proof_only_pin_rows = [
        row for row in accepted_pin
        if row.get("same_signature_hidden_wrong_feasibility")
        == "structurally_infeasible_for_same_signature_proof_wrongs"
    ]
    semantic_role_rows = [
        row for row in accepted_pin
        if row.get("hidden_pin_role") == "semantic_positive_negative_guard"
    ]
    run_failures = [row for row in run_integrity if row.get("integrity_status") == "fail"]
    primary_coverage = next(
        (
            row for row in model_summary
            if row.get("analysis_set") == "primary_plan_coverage"
            and row.get("group_by") == "all"
            and row.get("group") == "all"
        ),
        {},
    )

    release_ids = [
        "public_prompts_scaffolds",
        "hidden_references_pins",
        "wrong_submission_controls",
        "automatic_lean_scoring",
        "forbidden_construct_scan",
        "axiom_audit_policy",
        "metadata_completeness",
        "schemas_present",
        "run_result_semantics",
        "scaffold_support",
        "lookup_scaffold_no_hidden_leak",
        "transcript_failure_workflow",
        "public_export_no_hidden_leak",
        "candidate_pruning_audit",
        "semantic_formalization_pins",
    ]
    research_ids = [
        "evaluation_protocol_plan",
        "model_result_analysis",
        "report_from_committed_data",
        "difficulty_audit_report",
        "manual_accepted_task_review",
        "task_quality_matrix",
        "diagnostic_coverage_audit",
        "human_time_calibration_audit",
        "pin_coverage_audit",
        "run_integrity_audit",
        "grader_hardening_audit",
        "statistical_reporting_audit",
        "provider_readiness_audit",
        "hosted_qa_readiness_audit",
        "release_decision_log",
        "scaffold_support_audit",
        "prompt_contract_audit",
        "task_asset_manifest",
        "reproducibility_manifest",
    ]
    locked_ids = [
        "portfolio_accepted_count",
        "dev_test_split",
        "mixed_realistic_portfolio",
        "time_horizon_spread",
        "scaffold_result_comparison",
        "frontier_model_evidence",
        "independent_human_time_review",
        "hosted_qa_env_linter",
    ]

    rows: list[dict[str, str]] = []
    rows.append(row(
        "local_release_artifact",
        "The repository is a locally validated v0.1 release artifact with public scaffolds, hidden checks, Lean scoring, integrity controls, and complete metadata.",
        "artifact_validity",
        "supported" if all_status(reqs, release_ids) else "partial",
        "high" if all_status(reqs, release_ids) else "medium",
        "; ".join(evidence(reqs, requirement_id) for requirement_id in release_ids),
        "This is a local artifact claim, not a hosted/frozen benchmark claim.",
        "Hosted QA, independent review, and broader accepted task count are still required for a locked benchmark.",
    ))
    rows.append(row(
        "research_report_evidence",
        "The report is generated from committed data and includes research-quality caveats, task quality matrices, diagnostic-coverage checks, human-time calibration checks, task-asset hashes, prompt-contract checks, pin coverage, run integrity, grader-hardening checks, statistical reporting checks, provider-readiness checks, hosted-QA readiness checks, scaffold-support checks, release-decision gates, and a prospective evaluation protocol.",
        "report_validity",
        "supported" if all_status(reqs, research_ids) else "partial",
        "high" if all_status(reqs, research_ids) else "medium",
        "; ".join(evidence(reqs, requirement_id) for requirement_id in research_ids),
        "The report is still limited by missing broad model sweeps and independent human timing.",
        "Run the planned scaffold sweep, collect independent timing, and add external QA artifacts.",
    ))
    rows.append(row(
        "accepted_core_reviewed",
        "The six accepted-core tasks are internally reviewed and higher quality than the original candidate pool.",
        "task_validity",
        "supported",
        "medium",
        f"{len(accepted)} accepted_v0 tasks, {len(calibration)} calibration-only tasks, {len(rejected)} rejected archive tasks; {evidence(reqs, 'manual_accepted_task_review')}; {evidence(reqs, 'difficulty_audit_report')}; {evidence(reqs, 'task_quality_matrix')}; {evidence(reqs, 'diagnostic_coverage_audit')}",
        "This is an internal-review claim. Several accepted rows retain caveats and the core size is below the target benchmark size.",
        "Independent Lean-human review and more accepted high-quality T2/T3/T4 rows.",
    ))
    rows.append(row(
        "hidden_pin_strength",
        "Hidden checks provide meaningful anti-gaming evidence for accepted tasks, with semantic hidden-pin failures on mutable-definition tasks and signature/downstream guards on proof-only fixed-statement tasks.",
        "grading_validity",
        (
            "supported"
            if mutable_pin_rows
            and mutable_hidden_pin_tasks == len(mutable_pin_rows)
            and len(proof_only_pin_rows) + len(mutable_pin_rows) == len(accepted_pin)
            else "partial"
        ),
        "medium",
        (
            f"{accepted_hidden_pin_tasks}/{len(accepted)} accepted tasks have at least one wrong submission reaching hidden pins; "
            f"{mutable_hidden_pin_tasks}/{len(mutable_pin_rows)} mutable-definition accepted tasks have hidden-pin wrong failures; "
            f"{len(proof_only_pin_rows)} proof-only accepted tasks are structurally infeasible for same-signature wrong proofs; "
            f"{len(semantic_role_rows)}/{len(accepted_pin)} accepted tasks have semantic positive/negative guards; "
            f"{evidence(reqs, 'pin_coverage_audit')}; {evidence(reqs, 'semantic_formalization_pins')}"
        ),
        "Proof-only fixed-statement rows do not have semantic hidden wrongs because Lean compilation already certifies exact same-signature theorem proofs; hidden pins remain finite probes.",
        "Add independent reviewer assessment of hidden pins and strengthen any future mutable accepted task until it has at least one public-compiling wrong that fails hidden pins.",
    ))
    rows.append(row(
        "run_data_integrity",
        "Committed run-result rows are internally consistent with transcripts, failure labels, score vectors, and pass@k semantics.",
        "data_validity",
        "supported" if status(reqs, "run_integrity_audit") == "supported" and not run_failures else "partial",
        "high" if status(reqs, "run_integrity_audit") == "supported" and not run_failures else "medium",
        f"{evidence(reqs, 'run_integrity_audit')}; {evidence(reqs, 'grader_hardening_audit')}; {evidence(reqs, 'run_result_semantics')}",
        "This validates data hygiene only; it does not make the smoke rows representative.",
        "Maintain this audit for future provider sweeps and require zero failing rows before reporting results.",
    ))
    rows.append(row(
        "time_horizon_measurement",
        "The current artifact measures model behavior across increasing time horizons.",
        "construct_validity",
        "partial",
        "low",
        f"{evidence(reqs, 'time_horizon_spread')}; {evidence(reqs, 'diagnostic_coverage_audit')}; {evidence(reqs, 'human_time_calibration_audit')}; accepted buckets: {compact_json(dict(Counter(task.get('human_time_bucket') for task in accepted)))}",
        "Accepted core has only T2/T3 coverage and no T4; human times are author/reviewer estimates rather than independent solves.",
        "Add independently timed T3/T4 tasks before claiming strong time-horizon measurement.",
    ))
    rows.append(row(
        "scaffold_effects",
        "The report supports conclusions about how lookup and iterative compile/debug scaffolds change model performance.",
        "performance_claim",
        "unsupported" if status(reqs, "scaffold_result_comparison") != "supported" else "supported",
        "none" if status(reqs, "scaffold_result_comparison") != "supported" else "medium",
        f"{evidence(reqs, 'evaluation_protocol_plan')}; {evidence(reqs, 'scaffold_result_comparison')}; {evidence(reqs, 'provider_readiness_audit')}; {evidence(reqs, 'statistical_reporting_audit')}; primary plan coverage: {compact_json(primary_coverage)}",
        "The scaffold ladder is implemented and planned, but real accepted-core provider data cover only one one-shot cell.",
        "Run accepted-core pass@10 or equivalent rows across one-shot, lookup, and lookup_unlimited.",
    ))
    rows.append(row(
        "frontier_performance",
        "Committed provider rows characterize frontier-model performance on this benchmark.",
        "performance_claim",
        "unsupported",
        "none",
        f"{evidence(reqs, 'frontier_model_evidence')}; {evidence(reqs, 'model_result_analysis')}; {evidence(reqs, 'provider_readiness_audit')}; {evidence(reqs, 'statistical_reporting_audit')}",
        "Only tiny smoke evidence is committed, including an infra failure; local QA rows are not model performance.",
        "Run the planned accepted-core scaffold sweep with documented provider versions and cost/infra notes.",
    ))
    rows.append(row(
        "locked_benchmark",
        "v0.1 is a locked benchmark suitable for population-level frontier-model claims.",
        "benchmark_status",
        "unsupported",
        "none",
        "; ".join(evidence(reqs, requirement_id) for requirement_id in locked_ids + ["hosted_qa_readiness_audit"]),
        "The artifact has 6 accepted tasks, no hosted QA, no independent timing, no T4 accepted task, and limited provider data.",
        "Reach the 20-50 accepted-task target, run hosted QA, collect independent timing, complete scaffold sweeps, and freeze exact public task versions.",
    ))
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row["support_status"] for row in rows)
    type_counts = Counter(row["claim_type"] for row in rows)
    lines = [
        "# Claim Evidence Audit",
        "",
        "This generated audit turns the report's claim ledger into explicit evidence rows. It separates local artifact-validity claims from performance and locked-benchmark claims, so unsupported conclusions are visible rather than implied.",
        "",
        "## Summary",
        "",
        f"- claims audited: `{len(rows)}`",
        f"- support statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- claim types: `{compact_json(dict(sorted(type_counts.items())))}`",
        "",
        "## Claim Table",
        "",
        "| claim id | type | support | strength | claim | limits | stronger claim requires |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['claim_id']}` | {row['claim_type']} | {row['support_status']} | {row['evidence_strength']} | "
            f"{escaped(row['claim'])} | {escaped(row['counterevidence_or_limits'])} | {escaped(row['stronger_claim_requires'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "Claims marked `supported` are supported by the current local artifact. Claims marked `partial` have meaningful evidence but should not be stated without caveats. Claims marked `unsupported` are included because they are tempting overclaims that the current evidence explicitly does not justify.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "claim_evidence_audit.csv", rows)
    write_markdown(ROOT / "reports" / "claim_evidence_audit.md", rows)
    print(f"wrote data/claim_evidence_audit.csv and reports/claim_evidence_audit.md with {len(rows)} claim rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
