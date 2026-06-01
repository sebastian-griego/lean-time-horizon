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
    "missing_items",
    "source_artifacts",
    "required_action",
]

LOCKED_BLOCKER_THREATS = {
    "portfolio_accepted_count": ["portfolio_scale_and_balance"],
    "time_horizon_spread": ["construct_time_horizon_depth"],
    "scaffold_result_comparison": ["scaffold_sweep_undercoverage", "statistical_power_and_plots"],
    "frontier_model_evidence": ["frontier_performance_undercoverage"],
    "independent_human_time_review": ["author_estimated_human_time"],
    "independent_task_quality_review": ["missing_independent_task_quality_review"],
    "hosted_qa_env_linter": ["hosted_environment_gap"],
}

CLAIM_THREAT_TOKENS = {
    "accepted_core_quality": ["accepted_core_reviewed"],
    "hidden_pin_and_grader_strength": ["hidden_pin_strength", "grading_validity"],
    "time_horizon_scope": ["time_horizon_measurement"],
    "scaffold_effects": ["scaffold_effects"],
    "frontier_model_performance": ["frontier_performance"],
    "failure_taxonomy_results": ["diagnostic_failure_distribution"],
    "statistical_performance_reporting": ["frontier_performance", "scaffold_effects", "family_level_performance"],
    "hosted_qa_status": ["deployment_reliability", "locked_benchmark"],
    "locked_benchmark_status": ["locked_benchmark"],
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


def split_semicolon(value: str) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(";") if part.strip()]


def row(
    check_id: str,
    area: str,
    status: str,
    evidence: str,
    missing_items: list[str],
    source_artifacts: list[str],
    required_action: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "status": status,
        "evidence": evidence,
        "missing_items": compact_json(missing_items[:20]),
        "source_artifacts": ";".join(source_artifacts),
        "required_action": required_action,
    }


def build_rows() -> list[dict[str, str]]:
    threats = read_csv(ROOT / "data" / "threats_to_validity.csv")
    requirements = read_csv(ROOT / "data" / "requirement_coverage.csv")
    authorizations = read_csv(ROOT / "data" / "claim_authorization_matrix.csv")
    freeze = read_csv(ROOT / "data" / "freeze_readiness_roadmap.csv")
    threat_by_id = {threat["threat_id"]: threat for threat in threats}
    claims_limited_by_threat = {
        threat.get("threat_id", ""): split_semicolon(threat.get("claims_limited", ""))
        for threat in threats
    }
    all_claim_tokens = {
        token
        for tokens in claims_limited_by_threat.values()
        for token in tokens
    }

    rows: list[dict[str, str]] = []

    open_locked = [
        req for req in requirements
        if req.get("freeze_relevance") == "required_for_locked_benchmark"
        and req.get("status") != "supported"
    ]
    missing_blocker_threats: list[str] = []
    weak_blocker_threats: list[str] = []
    covered_blockers: dict[str, list[str]] = {}
    for requirement in open_locked:
        requirement_id = requirement.get("requirement_id", "")
        expected_threat_ids = LOCKED_BLOCKER_THREATS.get(requirement_id, [])
        present = [threat_id for threat_id in expected_threat_ids if threat_id in threat_by_id]
        covered_blockers[requirement_id] = present
        if not present:
            missing_blocker_threats.append(requirement_id)
            continue
        for threat_id in present:
            if threat_by_id[threat_id].get("current_status") not in {"block", "caution"}:
                weak_blocker_threats.append(f"{requirement_id}:{threat_id}:{threat_by_id[threat_id].get('current_status')}")
    rows.append(row(
        "locked_blocker_threat_mapping",
        "locked_benchmark_threats",
        "pass" if open_locked and not missing_blocker_threats and not weak_blocker_threats else "fail",
        (
            f"open_locked_requirements={len(open_locked)}; "
            f"covered={compact_json(covered_blockers)}; "
            f"missing={compact_json(missing_blocker_threats)}; "
            f"weak_status={compact_json(weak_blocker_threats)}"
        ),
        missing_blocker_threats + weak_blocker_threats,
        ["data/requirement_coverage.csv", "data/threats_to_validity.csv"],
        "Add or update threat rows whenever a locked-benchmark blocker is partial or not_met.",
    ))

    missing_claim_threats: list[str] = []
    checked_claims: dict[str, list[str]] = {}
    for auth in authorizations:
        claim_id = auth.get("claim_id", "")
        if auth.get("authorization_status") == "allowed":
            continue
        expected_tokens = CLAIM_THREAT_TOKENS.get(claim_id, [])
        checked_claims[claim_id] = expected_tokens
        if expected_tokens and not any(token in all_claim_tokens for token in expected_tokens):
            missing_claim_threats.append(f"{claim_id}:{'|'.join(expected_tokens)}")
    rows.append(row(
        "non_allowed_claim_threat_mapping",
        "claim_threats",
        "pass" if authorizations and not missing_claim_threats else "fail",
        (
            f"non_allowed_claims={sum(1 for auth in authorizations if auth.get('authorization_status') != 'allowed')}; "
            f"expected_tokens={compact_json(checked_claims)}; "
            f"available_tokens={compact_json(sorted(all_claim_tokens))}"
        ),
        missing_claim_threats,
        ["data/claim_authorization_matrix.csv", "data/threats_to_validity.csv"],
        "Keep every caveated or blocked claim tied to at least one threat claims_limited token.",
    ))

    incomplete_threat_rows: list[str] = []
    invalid_status_rows: list[str] = []
    missing_source_paths: list[str] = []
    for threat in threats:
        threat_id = threat.get("threat_id", "")
        for field in ["evidence", "mitigation_in_repo", "stronger_evidence_needed", "claims_limited", "source_artifacts"]:
            if not threat.get(field, "").strip():
                incomplete_threat_rows.append(f"{threat_id}:{field}")
        if threat.get("current_status") not in {"block", "caution", "controlled"}:
            invalid_status_rows.append(f"{threat_id}:{threat.get('current_status')}")
        for artifact in split_semicolon(threat.get("source_artifacts", "")):
            path = ROOT / artifact
            if "*" in artifact:
                continue
            if not path.exists():
                missing_source_paths.append(f"{threat_id}:{artifact}")
    rows.append(row(
        "threat_row_completeness",
        "threat_register_integrity",
        "pass" if threats and not incomplete_threat_rows and not invalid_status_rows and not missing_source_paths else "fail",
        (
            f"threat_rows={len(threats)}; "
            f"statuses={compact_json(dict(sorted(Counter(t.get('current_status', 'unknown') for t in threats).items())))}; "
            f"incomplete={len(incomplete_threat_rows)}; invalid_statuses={len(invalid_status_rows)}; "
            f"missing_source_paths={len(missing_source_paths)}"
        ),
        incomplete_threat_rows + invalid_status_rows + missing_source_paths,
        ["data/threats_to_validity.csv", "reports/threats_to_validity.md"],
        "Every threat row should have evidence, mitigation, stronger-evidence requirements, claim limits, and existing source artifacts.",
    ))

    high_block_threats = [
        threat for threat in threats
        if threat.get("severity") == "high" and threat.get("current_status") == "block"
    ]
    missing_freeze_refs: list[str] = []
    freeze_text = "\n".join(
        " ".join(row_data.values()) for row_data in freeze
    )
    for threat in high_block_threats:
        if not any(token in freeze_text for token in split_semicolon(threat.get("claims_limited", ""))):
            missing_freeze_refs.append(threat.get("threat_id", ""))
    rows.append(row(
        "high_block_threat_freeze_alignment",
        "freeze_alignment",
        "pass" if high_block_threats and not missing_freeze_refs else "fail",
        (
            f"high_block_threats={len(high_block_threats)}; "
            f"freeze_rows={len(freeze)}; missing_freeze_claim_tokens={compact_json(missing_freeze_refs)}"
        ),
        missing_freeze_refs,
        ["data/threats_to_validity.csv", "data/freeze_readiness_roadmap.csv"],
        "High-severity blocking threats should correspond to freeze-roadmap claim limits or gates.",
    ))

    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row_data["status"] for row_data in rows)
    area_counts = Counter(row_data["area"] for row_data in rows)
    lines = [
        "# Threat Coverage Audit",
        "",
        "This generated audit checks whether the threats-to-validity register covers the open locked-benchmark blockers and non-allowed report claims. It does not resolve the threats; it verifies that reviewer-visible limitations are mapped to concrete blockers, claim limits, mitigations, and stronger-evidence requirements.",
        "",
        "## Summary",
        "",
        f"- checks: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- areas: `{compact_json(dict(sorted(area_counts.items())))}`",
        "",
        "## Check Table",
        "",
        "| check | area | status | evidence | missing items | required action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row_data in rows:
        lines.append(
            f"| `{row_data['check_id']}` | {row_data['area']} | {row_data['status']} | "
            f"{escaped(row_data['evidence'])} | `{escaped(row_data['missing_items'])}` | "
            f"{escaped(row_data['required_action'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`pass` means the threat register is aligned with current blockers and claim boundaries. It does not mean the blocker has been solved. `fail` means the report may be hiding or under-specifying a limitation that should remain visible before stronger benchmark claims are made.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "threat_coverage_audit.csv", rows)
    write_markdown(ROOT / "reports" / "threat_coverage_audit.md", rows)
    failures = sum(1 for row_data in rows if row_data["status"] == "fail")
    print(
        "wrote data/threat_coverage_audit.csv and "
        f"reports/threat_coverage_audit.md with {len(rows)} checks; failures={failures}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
