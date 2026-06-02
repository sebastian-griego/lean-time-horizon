from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "check_id",
    "area",
    "status",
    "evidence",
    "bad_matches",
    "source_artifacts",
    "required_action",
]

READY_STATUSES = {"covered_pass", "covered_fail"}

LEGACY_FORBIDDEN_PHRASES = [
    "primary sweep coverage: `1/18` planned cells covered",
    "covered non-infra primary cells: `1`",
    "one covered accepted-core non-infra cell",
    "Do not imply a time-horizon trend from one covered accepted-core non-infra cell",
]

REPORT_SCAN_PATHS = [
    "reports/metr_style_report.md",
    "reports/concise_metr_report.md",
    "reports/release_decision_log.md",
    "reports/freeze_readiness_roadmap.md",
    "reports/statistical_analysis_plan.md",
    "reports/statistical_reporting_audit.md",
    "reports/figure_manifest.md",
    "reports/threats_to_validity.md",
    "reports/claim_authorization_matrix.md",
    "reports/requirement_coverage.md",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


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


def as_int(value: str | int | None) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def coverage_counts() -> dict[str, object]:
    rows = read_csv(ROOT / "data" / "model_sweep_coverage_audit.csv")
    plan_rows = read_csv(ROOT / "data" / "model_sweep_plan.csv")
    statuses = Counter(row.get("coverage_status", "unknown") for row in rows)
    ready = sum(1 for row in rows if row.get("coverage_status") in READY_STATUSES)
    noninfra_any = sum(1 for row in rows if as_int(row.get("noninfra_rows")) > 0)
    smoke_only = statuses.get("smoke_only", 0)
    missing = statuses.get("missing", 0)
    infra_only = statuses.get("infra_only", 0)
    return {
        "rows": rows,
        "plan_rows": plan_rows,
        "planned": len(rows),
        "planned_from_plan": len(plan_rows),
        "ready": ready,
        "noninfra_any": noninfra_any,
        "smoke_only": smoke_only,
        "missing": missing,
        "infra_only": infra_only,
        "statuses": dict(sorted(statuses.items())),
    }


def row(
    check_id: str,
    area: str,
    status: str,
    evidence: str,
    bad_matches: list[str],
    source_artifacts: list[str],
    required_action: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "status": status,
        "evidence": evidence,
        "bad_matches": compact_json(bad_matches[:16]),
        "source_artifacts": ";".join(source_artifacts),
        "required_action": required_action,
    }


def missing_phrases(text: str, phrases: list[str]) -> list[str]:
    lower = text.lower()
    return [phrase for phrase in phrases if phrase.lower() not in lower]


def bad_phrase_matches(paths: list[str]) -> list[str]:
    matches: list[str] = []
    for relative in paths:
        text = read_text(ROOT / relative)
        for phrase in LEGACY_FORBIDDEN_PHRASES:
            if phrase.lower() in text.lower():
                matches.append(f"{relative}: {phrase}")
    return matches


def build_rows() -> list[dict[str, str]]:
    counts = coverage_counts()
    planned = int(counts["planned"])
    planned_from_plan = int(counts["planned_from_plan"])
    ready = int(counts["ready"])
    noninfra_any = int(counts["noninfra_any"])
    statuses = counts["statuses"]
    status_json = compact_json(statuses)

    rows: list[dict[str, str]] = []
    ledger_bad: list[str] = []
    if planned == 0:
        ledger_bad.append("model_sweep_coverage_audit has zero rows")
    if planned != planned_from_plan:
        ledger_bad.append(f"coverage rows {planned} != plan rows {planned_from_plan}")
    rows.append(row(
        "strict_coverage_ledger_counts",
        "source_data",
        "pass" if not ledger_bad else "fail",
        (
            f"planned_cells={planned}; plan_rows={planned_from_plan}; "
            f"pass_at_k_ready={ready}; aggregate_noninfra_smoke={noninfra_any}; "
            f"statuses={status_json}"
        ),
        ledger_bad,
        [
            "data/model_sweep_coverage_audit.csv",
            "data/model_sweep_plan.csv",
            "reports/model_sweep_coverage_audit.md",
        ],
        "Regenerate scripts/audit_model_sweep_coverage.py and inspect planned-cell coverage mismatches.",
    ))

    main_report = read_text(ROOT / "reports" / "metr_style_report.md")
    main_required = [
        f"primary sweep pass@k-ready coverage: `{ready}/{planned}` planned cells ready",
        f"aggregate non-infra smoke-covered cells: `{noninfra_any}/{planned}`",
        "strict planned-cell coverage statuses",
        "no benchmark pass-rate or interval is reported",
    ]
    main_missing = missing_phrases(main_report, main_required)
    main_bad = [
        match for match in bad_phrase_matches(["reports/metr_style_report.md"])
        if match
    ]
    rows.append(row(
        "main_report_passk_boundary",
        "report_text",
        "pass" if not main_missing and not main_bad else "fail",
        (
            f"expected_ready={ready}/{planned}; expected_smoke={noninfra_any}/{planned}; "
            f"missing_required={len(main_missing)}; legacy_bad_matches={len(main_bad)}"
        ),
        main_missing + main_bad,
        ["reports/metr_style_report.md", "data/model_sweep_coverage_audit.csv"],
        "Regenerate reports and keep pass@k-ready and smoke-covered counts separate in the main report.",
    ))

    concise_report = read_text(ROOT / "reports" / "concise_metr_report.md")
    concise_required = [
        f"pass@k-ready primary cells: `{ready}`",
        f"aggregate non-infra smoke-covered primary cells: `{noninfra_any}`",
        "No benchmark pass-rate or interval is reported from the current rows.",
    ]
    concise_missing = missing_phrases(concise_report, concise_required)
    concise_bad = bad_phrase_matches(["reports/concise_metr_report.md"])
    rows.append(row(
        "concise_report_passk_boundary",
        "report_text",
        "pass" if not concise_missing and not concise_bad else "fail",
        (
            f"expected_ready={ready}; expected_smoke={noninfra_any}; "
            f"missing_required={len(concise_missing)}; legacy_bad_matches={len(concise_bad)}"
        ),
        concise_missing + concise_bad,
        ["reports/concise_metr_report.md", "data/model_sweep_coverage_audit.csv"],
        "Regenerate the concise report and keep smoke rows out of pass@k-ready wording.",
    ))

    release_text = read_text(ROOT / "reports" / "release_decision_log.md")
    freeze_text = read_text(ROOT / "reports" / "freeze_readiness_roadmap.md")
    release_freeze_required = [
        f"strict pass@k-ready cells={ready}/{planned}",
        f"pass@k-ready cells={ready}/{planned}",
        f"coverage statuses={status_json}",
        "accepted-core provider data have 0 pass@k-ready planned cells" if ready == 0 else "accepted-core provider data have",
    ]
    release_freeze_missing = [
        phrase
        for phrase in release_freeze_required
        if phrase.lower() not in f"{release_text}\n{freeze_text}".lower()
    ]
    release_freeze_bad = bad_phrase_matches([
        "reports/release_decision_log.md",
        "reports/freeze_readiness_roadmap.md",
    ])
    rows.append(row(
        "release_and_freeze_passk_boundary",
        "release_gates",
        "pass" if not release_freeze_missing and not release_freeze_bad else "fail",
        (
            f"ready={ready}/{planned}; statuses={status_json}; "
            f"missing_required={len(release_freeze_missing)}; legacy_bad_matches={len(release_freeze_bad)}"
        ),
        release_freeze_missing + release_freeze_bad,
        [
            "reports/release_decision_log.md",
            "reports/freeze_readiness_roadmap.md",
            "data/model_sweep_coverage_audit.csv",
        ],
        "Regenerate release/freeze reports after model-sweep coverage changes.",
    ))

    stats_text = "\n".join([
        read_text(ROOT / "reports" / "statistical_analysis_plan.md"),
        read_text(ROOT / "reports" / "statistical_reporting_audit.md"),
        read_text(ROOT / "reports" / "figure_manifest.md"),
        read_text(ROOT / "reports" / "threats_to_validity.md"),
    ])
    stats_required = [
        f"pass@k-ready accepted task/scaffold cells: `{ready}`",
        f"aggregate non-infra smoke-covered cells: `{noninfra_any}`",
        f"{ready}/{planned} accepted task/scaffold cells covered by exact-k non-infra provider rows",
        "zero pass@k-ready accepted-core cells" if ready == 0 else "pass@k-ready accepted-core cells",
    ]
    stats_missing = missing_phrases(stats_text, stats_required)
    stats_bad = bad_phrase_matches([
        "reports/statistical_analysis_plan.md",
        "reports/statistical_reporting_audit.md",
        "reports/figure_manifest.md",
        "reports/threats_to_validity.md",
    ])
    rows.append(row(
        "statistical_and_plot_passk_boundary",
        "statistical_reporting",
        "pass" if not stats_missing and not stats_bad else "fail",
        (
            f"ready={ready}/{planned}; aggregate_smoke={noninfra_any}; "
            f"missing_required={len(stats_missing)}; legacy_bad_matches={len(stats_bad)}"
        ),
        stats_missing + stats_bad,
        [
            "reports/statistical_analysis_plan.md",
            "reports/statistical_reporting_audit.md",
            "reports/figure_manifest.md",
            "reports/threats_to_validity.md",
            "data/model_sweep_coverage_audit.csv",
        ],
        "Keep performance plots and statistical claims blocked until exact-k planned cells are covered.",
    ))

    claim_text = "\n".join([
        read_text(ROOT / "reports" / "claim_authorization_matrix.md"),
        read_text(ROOT / "reports" / "claim_evidence_audit.md"),
        read_text(ROOT / "reports" / "requirement_coverage.md"),
    ])
    claim_required = [
        f"pass@k-ready cells: {ready}/{planned}",
        f"statuses: {status_json}",
        "model_sweep_coverage_audit",
        "scaffold_result_comparison",
    ]
    claim_missing = missing_phrases(claim_text, claim_required)
    claim_bad = bad_phrase_matches([
        "reports/claim_authorization_matrix.md",
        "reports/claim_evidence_audit.md",
        "reports/requirement_coverage.md",
    ])
    rows.append(row(
        "claim_and_requirement_passk_boundary",
        "claim_controls",
        "pass" if not claim_missing and not claim_bad else "fail",
        (
            f"ready={ready}/{planned}; statuses={status_json}; "
            f"missing_required={len(claim_missing)}; legacy_bad_matches={len(claim_bad)}"
        ),
        claim_missing + claim_bad,
        [
            "reports/claim_authorization_matrix.md",
            "reports/claim_evidence_audit.md",
            "reports/requirement_coverage.md",
            "data/model_sweep_coverage_audit.csv",
        ],
        "Keep claim and requirement reports tied to the strict coverage audit before upgrading scaffold or frontier claims.",
    ))

    legacy_matches = bad_phrase_matches(REPORT_SCAN_PATHS)
    rows.append(row(
        "legacy_aggregate_phrase_scan",
        "legacy_phrase_scan",
        "pass" if not legacy_matches else "fail",
        (
            f"files_scanned={len(REPORT_SCAN_PATHS)}; "
            f"forbidden_phrases={len(LEGACY_FORBIDDEN_PHRASES)}; matches={len(legacy_matches)}"
        ),
        legacy_matches,
        REPORT_SCAN_PATHS,
        "Remove stale aggregate-coverage language that could make smoke rows look like pass@k evidence.",
    ))

    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row_data["status"] for row_data in rows)
    area_counts = Counter(row_data["area"] for row_data in rows)
    lines = [
        "# Pass@k Claim-Boundary Audit",
        "",
        "This generated audit checks that report artifacts keep strict pass@k-ready evidence separate from smoke-only or missing planned cells. It does not create model results or judge model quality; it prevents wording drift after provider smoke rows are committed.",
        "",
        "## Summary",
        "",
        f"- checks: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- areas: `{compact_json(dict(sorted(area_counts.items())))}`",
        "",
        "## Check Table",
        "",
        "| check | area | status | evidence | bad matches | required action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row_data in rows:
        lines.append(
            f"| `{row_data['check_id']}` | {row_data['area']} | {row_data['status']} | "
            f"{escaped(row_data['evidence'])} | `{escaped(row_data['bad_matches'])}` | "
            f"{escaped(row_data['required_action'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`pass` means the audited reports use the strict `data/model_sweep_coverage_audit.csv` categories consistently. A passing row is not performance evidence: `covered_pass` and `covered_fail` only indicate exact-k row-shape readiness, while `smoke_only`, `infra_only`, and `missing` remain excluded from pass@k estimates.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "passk_claim_boundary_audit.csv", rows)
    write_markdown(ROOT / "reports" / "passk_claim_boundary_audit.md", rows)
    failures = sum(1 for row_data in rows if row_data["status"] == "fail")
    print(
        "wrote data/passk_claim_boundary_audit.csv and "
        f"reports/passk_claim_boundary_audit.md with {len(rows)} checks; failures={failures}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
