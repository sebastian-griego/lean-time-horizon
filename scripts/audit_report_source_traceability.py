from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_REPORT = ROOT / "reports" / "metr_style_report.md"

FIELDS = [
    "section_id",
    "heading",
    "status",
    "evidence",
    "source_artifacts",
    "missing_sources",
    "missing_phrases",
    "limitation",
    "next_action",
]

SECTION_SPECS = [
    {
        "section_id": "abstract_scope",
        "heading": "Abstract",
        "source_artifacts": [
            "data/task_metadata.csv",
            "reports/accepted_task_review.md",
            "data/run_results.csv",
        ],
        "required_phrases": [
            "not a locked benchmark",
            "6 accepted core tasks",
            "8 calibration-only tasks",
            "tiny smoke-model evidence",
        ],
        "limitation": "The abstract is a scope boundary, not evidence for benchmark-scale claims.",
        "next_action": "Keep sample-size and locked-benchmark caveats in the front matter.",
    },
    {
        "section_id": "reader_guide",
        "heading": "Reader Guide",
        "source_artifacts": [
            "reports/concise_metr_report.md",
            "reports/evidence_appendix.md",
        ],
        "required_phrases": [
            "main research report",
            "concise_metr_report.md",
            "evidence_appendix.md",
        ],
        "limitation": "The reader guide explains report layering; it is not an evidence source by itself.",
        "next_action": "Keep main, concise, and appendix roles distinct.",
    },
    {
        "section_id": "research_questions",
        "heading": "Research Questions",
        "source_artifacts": [
            "docs/lean_eval_project_playbook.md",
            "data/model_result_summary.csv",
        ],
        "required_phrases": [
            "current artifact can support local task/grader validity review",
            "cannot yet answer the third question empirically",
        ],
        "limitation": "The scaffold-effect question remains a planned analysis until provider sweeps exist.",
        "next_action": "Keep unsupported research questions marked as blocked by evidence.",
    },
    {
        "section_id": "unit_scoring",
        "heading": "Unit Of Analysis And Scoring",
        "source_artifacts": [
            "data/run_results_schema.json",
            "harness/forbidden_constructs.py",
            "scripts/validate_task.py",
            "docs/axiom_policy.md",
        ],
        "required_phrases": [
            "(task, model, scaffold, k)",
            "successes_out_of_k",
            "pass_at_k",
            "not model performance",
        ],
        "limitation": "This describes scoring semantics; it does not establish model performance coverage.",
        "next_action": "Keep pass@k and local-QA boundaries explicit whenever run-result rows change.",
    },
    {
        "section_id": "data_schema_manifest",
        "heading": "Data Schema Manifest",
        "source_artifacts": [
            "reports/data_schema_manifest.md",
            "data/data_schema_manifest.csv",
            "data/run_results_schema.json",
            "data/task_metadata_schema.json",
            "data/failure_label_review_schema.json",
            "data/independent_task_review_schema.json",
        ],
        "required_phrases": [
            "schema-backed datasets",
            "generated CSVs",
            "problem rows",
            "Data schema ledger",
        ],
        "limitation": "The data schema manifest validates row shape and schema boundaries; it does not make sample-size or benchmark-readiness claims.",
        "next_action": "Regenerate the manifest after schema, run-result, timing, or transcript-review data changes.",
    },
    {
        "section_id": "task_selection",
        "heading": "Task Selection Protocol",
        "source_artifacts": [
            "data/task_metadata.csv",
            "reports/accepted_task_review.md",
            "reports/difficulty_audit.md",
        ],
        "required_phrases": [
            "accepted_v0",
            "calibration_only",
            "rejected_*",
            "candidate_review_pending",
        ],
        "limitation": "Task status is internal v0.1 review status, not a hosted/frozen benchmark status.",
        "next_action": "Keep metadata status as the source of truth for accepted/calibration/rejected rows.",
    },
    {
        "section_id": "candidate_pruning",
        "heading": "Candidate Pruning Audit",
        "source_artifacts": [
            "data/candidate_pruning_audit.csv",
            "reports/candidate_pruning_audit.md",
            "data/task_metadata.csv",
            "data/difficulty_audit.csv",
            "data/task_quality_matrix.csv",
        ],
        "required_phrases": [
            "pruning decision visible",
            "accepted-core rate",
            "rejected archive rows",
            "not model performance",
        ],
        "limitation": "The pruning audit explains internal v0.1 selection decisions; it is not evidence for benchmark-scale sufficiency.",
        "next_action": "Regenerate candidate-pruning rows after metadata, difficulty, or task-quality changes.",
    },
    {
        "section_id": "accepted_core",
        "heading": "Accepted v0.1 Core Task Set",
        "source_artifacts": [
            "data/task_metadata.csv",
            "data/difficulty_audit.csv",
            "reports/task_quality_matrix.md",
        ],
        "required_phrases": ["lt-201", "lt-205", "accepted_v0"],
        "limitation": "The accepted set is small and includes caveated rows.",
        "next_action": "Do not use this table for population-level benchmark claims.",
    },
    {
        "section_id": "accepted_evidence_matrix",
        "heading": "Accepted Core Evidence Matrix",
        "source_artifacts": [
            "data/difficulty_audit.csv",
            "reports/difficulty_audit.md",
            "data/task_quality_matrix.csv",
        ],
        "required_phrases": [
            "automation dominated",
            "hidden pins",
            "one-shot estimate",
        ],
        "limitation": "Mechanical proof signals are useful triage evidence, not independent task-quality proof.",
        "next_action": "Use the accepted-task review before strengthening benchmark-grade wording.",
    },
    {
        "section_id": "accepted_task_cards",
        "heading": "Accepted Task Cards",
        "source_artifacts": [
            "data/accepted_task_cards.csv",
            "reports/accepted_task_cards.md",
            "data/pin_coverage_audit.csv",
            "data/task_asset_manifest.csv",
            "data/run_results.csv",
        ],
        "required_phrases": [
            "accepted task cards",
            "local-QA evidence",
            "do not expose hidden proof contents",
            "not model-performance evidence",
        ],
        "limitation": "Task cards synthesize existing local evidence and caveats; they are not a new acceptance decision or performance evidence.",
        "next_action": "Regenerate accepted-task cards after task, pin, asset, validation, or local-QA evidence changes.",
    },
    {
        "section_id": "independent_task_review_packet",
        "heading": "Independent Task Review Packet",
        "source_artifacts": [
            "data/independent_task_review_plan.csv",
            "data/independent_task_review_template.csv",
            "data/independent_task_reviews.csv",
            "data/independent_review_status_audit.csv",
            "reports/independent_task_review_packet.md",
            "reports/independent_review_status_audit.md",
        ],
        "required_phrases": [
            "non-author task-quality review workflow",
            "intentionally empty",
            "not independent validation evidence",
            "accepted-review coverage",
        ],
        "limitation": "The packet makes review collection operational; it does not substitute for completed non-author review rows.",
        "next_action": "Collect non-author task-quality reviews and rerun the status audit before strengthening accepted-task claims.",
    },
    {
        "section_id": "calibration_tasks",
        "heading": "Calibration-Only Release Tasks",
        "source_artifacts": [
            "data/task_metadata.csv",
            "data/difficulty_audit.csv",
            "reports/task_quality_matrix.md",
        ],
        "required_phrases": ["calibration_only", "lt-001", "lt-108"],
        "limitation": "Calibration-only tasks are release artifacts but not accepted-core benchmark rows.",
        "next_action": "Keep calibration rows excluded from accepted-core performance claims.",
    },
    {
        "section_id": "portfolio_counts",
        "heading": "Portfolio Counts",
        "source_artifacts": [
            "data/task_metadata.csv",
            "data/requirement_coverage.csv",
            "data/claim_authorization_matrix.csv",
            "data/release_decision_log.csv",
            "data/freeze_readiness_roadmap.csv",
        ],
        "required_phrases": [
            "acceptance statuses",
            "requirement statuses",
            "release-decision gates",
            "freeze-readiness gates",
        ],
        "limitation": "Counts summarize v0.1 artifacts and include explicit blockers.",
        "next_action": "Regenerate counts after any task-status or claim-audit change.",
    },
    {
        "section_id": "capabilities",
        "heading": "What The Tasks Measure",
        "source_artifacts": [
            "data/diagnostic_coverage_audit.csv",
            "data/construct_validity_matrix.csv",
            "data/task_quality_matrix.csv",
            "reports/accepted_task_review.md",
        ],
        "required_phrases": [
            "library/API search",
            "theorem decomposition",
            "semantic formalization",
            "Capability-level claims are weak",
            "construct-validity",
        ],
        "limitation": "Capability coverage is singleton-heavy in the accepted core.",
        "next_action": "Use diagnostic-coverage rows before making capability-level claims.",
    },
    {
        "section_id": "construct_validity_trace",
        "heading": "Construct Validity Trace",
        "source_artifacts": [
            "data/construct_validity_matrix.csv",
            "reports/construct_validity_matrix.md",
            "data/diagnostic_coverage_audit.csv",
            "data/task_quality_matrix.csv",
        ],
        "required_phrases": [
            "accepted construct rows",
            "singleton-covered capabilities",
            "task-level claim boundary",
        ],
        "limitation": "The construct-validity trace supports task-level review only, not capability-level performance claims.",
        "next_action": "Keep singleton and caveat boundaries visible until more accepted tasks and model evidence exist.",
    },
    {
        "section_id": "human_time",
        "heading": "Human-Time Estimates",
        "source_artifacts": [
            "data/human_time_calibration_audit.csv",
            "data/human_time_observations.csv",
            "reports/human_timing_collection_packet.md",
        ],
        "required_phrases": [
            "reviewer estimates",
            "not measured independent solves",
            "no accepted T4 row",
        ],
        "limitation": "Independent timing observations are absent.",
        "next_action": "Collect independent timed solves before strengthening time-horizon claims.",
    },
    {
        "section_id": "grading_integrity",
        "heading": "Grader And Integrity Controls",
        "source_artifacts": [
            "scripts/validate_task.py",
            "harness/forbidden_constructs.py",
            "docs/axiom_policy.md",
            "data/grader_hardening_audit.csv",
            "data/pin_coverage_audit.csv",
        ],
        "required_phrases": [
            "Lean-first",
            "forbidden constructs",
            "finite probes",
            "axiom policy",
        ],
        "limitation": "Finite hidden pins do not prove complete semantic equivalence.",
        "next_action": "Keep hidden-pin and axiom caveats attached to grading claims.",
    },
    {
        "section_id": "public_export",
        "heading": "Public Export",
        "source_artifacts": [
            "scripts/export_public_tasks.py",
            "scripts/validate_public_export.py",
            "data/task_asset_manifest.csv",
            "public_tasks",
        ],
        "required_phrases": [
            "hidden and wrong directories are absent",
            "exported Lean files compile",
        ],
        "limitation": "Local public export validation is not hosted QA.",
        "next_action": "Rerun public export validation after task or prompt changes.",
    },
    {
        "section_id": "scaffold_support",
        "heading": "Scaffold And Model-Run Support",
        "source_artifacts": [
            "data/scaffold_variants.csv",
            "scripts/lean_lookup.py",
            "scripts/run_model_sweep.py",
            "data/scaffold_support_audit.csv",
        ],
        "required_phrases": ["one-shot", "lookup", "lookup_unlimited", "read-only command"],
        "limitation": "Scaffold support exists, but scaffold-effect evidence is not yet covered.",
        "next_action": "Run accepted-core scaffold sweeps before interpreting scaffold effects.",
    },
    {
        "section_id": "model_result_analysis",
        "heading": "Model Result Analysis",
        "source_artifacts": [
            "data/model_result_summary.csv",
            "reports/model_run_analysis.md",
            "data/model_sweep_plan.csv",
        ],
        "required_phrases": [
            "planned accepted-core task/scaffold cells",
            "smoke evidence only",
            "planned primary sweep remains mostly uncovered",
        ],
        "limitation": "Provider rows are tiny smoke evidence only.",
        "next_action": "Keep primary sweep undercoverage visible until broader provider rows are committed.",
    },
    {
        "section_id": "model_provenance",
        "heading": "Model Evidence Provenance Audit",
        "source_artifacts": [
            "data/model_evidence_provenance_audit.csv",
            "reports/model_evidence_provenance_audit.md",
            "data/run_results.csv",
        ],
        "required_phrases": [
            "model versions",
            "sample sizes",
            "local-QA exclusion",
            "anthropic:claude-sonnet-4-6",
        ],
        "limitation": "Traceable model provenance does not imply adequate sample size.",
        "next_action": "Rerun provenance audit after every model sweep.",
    },
    {
        "section_id": "statistical_analysis_plan",
        "heading": "Statistical Analysis Plan",
        "source_artifacts": [
            "reports/statistical_analysis_plan.md",
            "data/statistical_design_thresholds.csv",
            "data/wilson_precision_table.csv",
            "reports/statistical_reporting_audit.md",
        ],
        "required_phrases": [
            "minimum evidence thresholds",
            "precision and claim-tier ledger",
            "Wilson",
            "blocked overclaim",
        ],
        "limitation": "The statistical plan defines evidence thresholds; it does not create model-performance evidence.",
        "next_action": "Keep blocked claim tiers blocked until committed sweeps meet the threshold rows.",
    },
    {
        "section_id": "figure_manifest",
        "heading": "Figure Manifest And Plot Boundaries",
        "source_artifacts": [
            "reports/figure_manifest.md",
            "data/figure_manifest.csv",
            "reports/figures/task_counts_by_family.svg",
            "reports/figures/task_counts_by_bucket.svg",
            "reports/figures/task_minutes_by_bucket.svg",
        ],
        "required_phrases": [
            "generated SVGs",
            "source artifacts",
            "blocked performance plots",
            "intentionally absent",
        ],
        "limitation": "The figure manifest allows descriptive and provenance figures while blocking unsupported performance plots.",
        "next_action": "Regenerate the figure manifest after report or model-result changes.",
    },
    {
        "section_id": "committed_runs",
        "heading": "Committed Run Results",
        "source_artifacts": [
            "data/run_results.csv",
            "data/model_result_summary.csv",
            "transcripts",
        ],
        "required_phrases": [
            "not model performance",
            "excluded from benchmark pass-rate summaries",
            "Infra-failure rows are retained",
        ],
        "limitation": "The table is smoke-run provenance, not benchmark performance.",
        "next_action": "Keep infra rows retained but excluded from pass-rate summaries.",
    },
    {
        "section_id": "claim_authorization",
        "heading": "Claim Authorization Matrix",
        "source_artifacts": [
            "data/claim_authorization_matrix.csv",
            "reports/claim_authorization_matrix.md",
            "data/claim_evidence_audit.csv",
        ],
        "required_phrases": [
            "allowed_with_caveat",
            "blocked",
            "forbidden wording",
        ],
        "limitation": "Allowed wording is narrower than full benchmark-readiness wording.",
        "next_action": "Keep blocked claims visible as blocked until evidence upgrades land.",
    },
    {
        "section_id": "remaining_blockers",
        "heading": "Remaining Blockers",
        "source_artifacts": [
            "data/requirement_coverage.csv",
            "reports/research_claim_gap_matrix.md",
            "reports/freeze_readiness_roadmap.md",
        ],
        "required_phrases": [
            "portfolio_accepted_count",
            "scaffold_result_comparison",
            "hosted_qa_env_linter",
        ],
        "limitation": "Blockers are intentionally unresolved in v0.1.",
        "next_action": "Use this table as the upgrade path, not as a completion claim.",
    },
    {
        "section_id": "evidence_files",
        "heading": "Report And Evidence Files",
        "source_artifacts": [
            "reports/evidence_appendix.md",
            "reports/concise_metr_report.md",
            "reports/requirement_coverage.md",
            "reports/report_source_traceability.md",
            "reports/data_schema_manifest.md",
            "reports/reviewer_reproduction_packet.md",
            "reports/clean_workspace_replay.md",
            "reports/candidate_pruning_audit.md",
            "reports/accepted_task_cards.md",
            "reports/independent_task_review_packet.md",
            "reports/independent_review_status_audit.md",
            "reports/failure_label_review_audit.md",
            "reports/statistical_analysis_plan.md",
            "reports/figure_manifest.md",
        ],
        "required_phrases": [
            "evidence_appendix.md",
            "concise_metr_report.md",
            "requirement_coverage.md",
            "data_schema_manifest.md",
            "reviewer_reproduction_packet.md",
            "clean_workspace_replay.md",
            "candidate_pruning_audit.md",
            "accepted_task_cards.md",
            "independent_task_review_packet.md",
            "independent_review_status_audit.md",
            "failure_label_review_audit.md",
            "statistical_analysis_plan.md",
            "figure_manifest.md",
        ],
        "limitation": "The source map improves traceability but does not create new model evidence.",
        "next_action": "Keep new report artifacts listed in README, manifest, and source traceability.",
    },
    {
        "section_id": "reproducibility",
        "heading": "Reproducibility Checklist",
        "source_artifacts": [
            "README.md",
            "reports/validation_manifest.json",
            "reports/validation_manifest_audit.md",
            "reports/reviewer_reproduction_packet.md",
            "reports/clean_workspace_replay.md",
            "data/reviewer_reproduction_steps.csv",
            "data/clean_workspace_replay.csv",
            "data/validation_manifest_audit.csv",
            "scripts/write_validation_manifest.py",
        ],
        "required_phrases": [
            "local regeneration gate",
            "Reviewer reproduction ledger",
            "Clean workspace replay ledger",
            "validation_manifest.json",
            "validation_manifest_audit.md",
            "generation-time git state",
            "external-evidence rows still blocked",
            "public export validator",
        ],
        "limitation": "The manifest records local reproducibility, not hosted QA.",
        "next_action": "Regenerate the manifest after every report or script change.",
    },
    {
        "section_id": "claim_ledger",
        "heading": "Claim Ledger",
        "source_artifacts": [
            "data/claim_authorization_matrix.csv",
            "data/claim_evidence_audit.csv",
            "reports/report_claim_conformance_audit.md",
        ],
        "required_phrases": [
            "not supported",
            "v0.1 is a locked benchmark",
            "Reported model pass rates characterize frontier performance",
        ],
        "limitation": "The ledger is a prose summary of narrower generated claim controls.",
        "next_action": "Keep tempting overclaims marked unsupported.",
    },
    {
        "section_id": "limitations",
        "heading": "Limitations",
        "source_artifacts": [
            "reports/threats_to_validity.md",
            "data/research_claim_gap_matrix.csv",
            "data/freeze_readiness_roadmap.csv",
        ],
        "required_phrases": [
            "below the 20-task target",
            "no accepted T4",
            "not measured independent solves",
            "not a locked benchmark",
        ],
        "limitation": "Limitations remain active blockers.",
        "next_action": "Do not mark the benchmark locked until limitations are backed by stronger evidence.",
    },
]


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


def section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start == -1:
        return ""
    next_start = text.find("\n## ", start + len(marker))
    return text[start:] if next_start == -1 else text[start:next_start]


def main_headings(text: str) -> list[str]:
    return [match.group(1).strip() for match in re.finditer(r"^## (.+)$", text, flags=re.MULTILINE)]


def artifact_missing(artifact: str) -> bool:
    return not (ROOT / artifact).exists()


def make_row(
    section_id: str,
    heading: str,
    status: str,
    evidence: str,
    source_artifacts: list[str],
    missing_sources: list[str],
    missing_phrases: list[str],
    limitation: str,
    next_action: str,
) -> dict[str, str]:
    return {
        "section_id": section_id,
        "heading": heading,
        "status": status,
        "evidence": evidence,
        "source_artifacts": ";".join(source_artifacts),
        "missing_sources": compact_json(missing_sources),
        "missing_phrases": compact_json(missing_phrases),
        "limitation": limitation,
        "next_action": next_action,
    }


def build_rows() -> list[dict[str, str]]:
    report = read_text(MAIN_REPORT)
    headings = main_headings(report)
    expected_headings = [spec["heading"] for spec in SECTION_SPECS]
    unmapped_headings = sorted(set(headings) - set(expected_headings) - {"Before Claiming A Locked Benchmark"})
    missing_expected_headings = sorted(set(expected_headings) - set(headings))
    rows = [
        make_row(
            "main_section_inventory",
            "all mapped sections",
            "pass" if not unmapped_headings and not missing_expected_headings else "fail",
            (
                f"main headings={len(headings)}; mapped specs={len(SECTION_SPECS)}; "
                f"unmapped={compact_json(unmapped_headings)}; missing_expected={compact_json(missing_expected_headings)}"
            ),
            ["reports/metr_style_report.md"],
            [],
            missing_expected_headings,
            "This inventory guards against adding unsupported main-report sections.",
            "Update SECTION_SPECS whenever the main report gains or loses a section.",
        )
    ]

    lower_report = report.lower()
    for spec in SECTION_SPECS:
        section_text = section(report, spec["heading"])
        section_present = bool(section_text)
        lower_section = section_text.lower()
        missing_sources = [
            artifact for artifact in spec["source_artifacts"]
            if artifact_missing(artifact)
        ]
        missing_phrases = [
            phrase for phrase in spec["required_phrases"]
            if phrase.lower() not in lower_section
        ]
        source_mentions = [
            artifact for artifact in spec["source_artifacts"]
            if artifact.lower() in lower_report
        ]
        status = "pass" if section_present and not missing_sources and not missing_phrases else "fail"
        rows.append(make_row(
            spec["section_id"],
            spec["heading"],
            status,
            (
                f"section_present={section_present}; sources={len(spec['source_artifacts'])}; "
                f"source_mentions_in_main_report={len(source_mentions)}; "
                f"missing_sources={len(missing_sources)}; missing_phrases={len(missing_phrases)}"
            ),
            spec["source_artifacts"],
            missing_sources,
            missing_phrases if section_present else [f"missing section: {spec['heading']}"],
            spec["limitation"],
            spec["next_action"],
        ))
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row["status"] for row in rows)
    lines = [
        "# Report Source Traceability Audit",
        "",
        "This generated audit maps each main-report section to committed CSV, report, script, or task-export evidence. It checks section presence, source-artifact existence, and section-level phrases that keep claims tied to the intended evidence boundary.",
        "",
        "## Summary",
        "",
        f"- rows: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        "",
        "## Traceability Table",
        "",
        "| section | status | evidence | sources | missing sources | missing phrases | limitation | next action |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['section_id']}` | {row['status']} | {escaped(row['evidence'])} | "
            f"{escaped(row['source_artifacts'])} | `{escaped(row['missing_sources'])}` | "
            f"`{escaped(row['missing_phrases'])}` | {escaped(row['limitation'])} | "
            f"{escaped(row['next_action'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`pass` means the section is present, its declared source artifacts exist, and the section contains the required boundary phrases. This audit does not judge whether the underlying evidence is sufficient for stronger benchmark claims; that remains controlled by the requirement, claim-authorization, and freeze-readiness reports.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "report_source_traceability.csv", rows)
    write_markdown(ROOT / "reports" / "report_source_traceability.md", rows)
    failures = sum(1 for row in rows if row["status"] == "fail")
    print(
        "wrote data/report_source_traceability.csv and "
        f"reports/report_source_traceability.md with {len(rows)} rows; failures={failures}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
