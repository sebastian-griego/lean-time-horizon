from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "check_id",
    "scope",
    "status",
    "evidence",
    "failure_examples",
    "required_action",
    "source_artifacts",
]

MAIN_REPORT = ROOT / "reports" / "metr_style_report.md"
CONCISE_REPORT = ROOT / "reports" / "concise_metr_report.md"
README = ROOT / "README.md"

NEGATIVE_MARKERS = [
    "not",
    "do not",
    "unsupported",
    "not supported",
    "not yet",
    "blocked",
    "blocking",
    "missing",
    "absent",
    "before claiming",
    "before any",
    "future",
    "requires",
    "required",
    "outside the current evidence",
    "no ",
]

BLOCKED_PATTERNS = {
    "locked_benchmark_status": [
        r"\blocked benchmark\b",
        r"\bfinal benchmark\b",
        r"\bpopulation-valid\b",
        r"\bbenchmark headline claims\b",
    ],
    "frontier_model_performance": [
        r"\bfrontier-model capability\b",
        r"\bfrontier capability\b",
        r"\bfrontier performance\b",
        r"\bfrontier-model performance\b",
        r"\bmodel rankings\b",
        r"\bcharacteriz(?:e|es|ing|ed) frontier\b",
    ],
    "scaffold_effects": [
        r"\blookup helps\b",
        r"\biterative compile/debug helps\b",
        r"\bscaffold effects are measured\b",
        r"\bscaffold-effect conclusions\b",
    ],
    "statistical_performance_reporting": [
        r"\bpass@10-by-scaffold plots\b",
        r"\bfamily means\b",
        r"\bconfidence intervals as substantive results\b",
    ],
    "hosted_qa_status": [
        r"\bFull Env QA passed\b",
        r"\bEnv Linter findings are settled\b",
        r"\bhosted problem versions are frozen\b",
    ],
}


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
    scope: str,
    status: str,
    evidence: str,
    failure_examples: list[str],
    required_action: str,
    source_artifacts: list[str],
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "scope": scope,
        "status": status,
        "evidence": evidence,
        "failure_examples": compact_json(failure_examples[:8]),
        "required_action": required_action,
        "source_artifacts": ";".join(source_artifacts),
    }


def contains_all(text: str, needles: list[str]) -> tuple[bool, list[str]]:
    lower = text.lower()
    missing = [needle for needle in needles if needle.lower() not in lower]
    return not missing, missing


def line_context(lines: list[str], index: int) -> str:
    start = max(0, index - 1)
    end = min(len(lines), index + 2)
    return " ".join(line.strip() for line in lines[start:end])


def unsafe_blocked_phrase_examples(paths: list[Path]) -> list[str]:
    examples: list[str] = []
    compiled = {
        claim_id: [re.compile(pattern, flags=re.IGNORECASE) for pattern in patterns]
        for claim_id, patterns in BLOCKED_PATTERNS.items()
    }
    for path in paths:
        lines = read_text(path).splitlines()
        for i, line in enumerate(lines):
            context = line_context(lines, i)
            context_lower = context.lower()
            for claim_id, patterns in compiled.items():
                if not any(pattern.search(context) for pattern in patterns):
                    continue
                if any(marker in context_lower for marker in NEGATIVE_MARKERS):
                    continue
                examples.append(f"{path.relative_to(ROOT)}:{i + 1}:{claim_id}:{line.strip()}")
    return examples


def section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start == -1:
        return ""
    next_start = text.find("\n## ", start + len(marker))
    return text[start:] if next_start == -1 else text[start:next_start]


def build_rows() -> list[dict[str, str]]:
    authorization = read_csv(ROOT / "data" / "claim_authorization_matrix.csv")
    main_report = read_text(MAIN_REPORT)
    concise_report = read_text(CONCISE_REPORT)
    readme = read_text(README)
    status_counts = Counter(row_data.get("authorization_status", "") for row_data in authorization)
    claim_ids = {row_data.get("claim_id", "") for row_data in authorization}
    blocked_ids = {
        row_data.get("claim_id", "")
        for row_data in authorization
        if row_data.get("authorization_status") == "blocked"
    }
    caveated_ids = {
        row_data.get("claim_id", "")
        for row_data in authorization
        if row_data.get("authorization_status") == "allowed_with_caveat"
    }

    rows: list[dict[str, str]] = []
    matrix_ok = bool(authorization) and len(blocked_ids) >= 4 and len(caveated_ids) >= 4
    rows.append(row(
        "authorization_matrix_loaded",
        "claim_authorization",
        "pass" if matrix_ok else "fail",
        (
            f"authorization rows={len(authorization)}; statuses={compact_json(dict(sorted(status_counts.items())))}; "
            f"blocked={len(blocked_ids)}; caveated={len(caveated_ids)}"
        ),
        [] if matrix_ok else ["claim authorization matrix missing or under-specified"],
        "Regenerate scripts/generate_claim_authorization_matrix.py and inspect blocked/caveated coverage.",
        ["data/claim_authorization_matrix.csv", "reports/claim_authorization_matrix.md"],
    ))

    report_has_section = "## Claim Authorization Matrix" in main_report
    missing_claim_ids = sorted(claim_id for claim_id in claim_ids if f"`{claim_id}`" not in main_report)
    section_ok = report_has_section and not missing_claim_ids
    rows.append(row(
        "main_report_authorization_section",
        "main_report",
        "pass" if section_ok else "fail",
        f"section_present={report_has_section}; claim_ids_in_matrix={len(claim_ids)}; missing_claim_ids={compact_json(missing_claim_ids)}",
        missing_claim_ids,
        "Regenerate reports/metr_style_report.md after claim authorization and ensure every authorization row is visible.",
        ["reports/metr_style_report.md", "data/claim_authorization_matrix.csv"],
    ))

    abstract_text = "\n".join(main_report.splitlines()[:35])
    abstract_ok, abstract_missing = contains_all(
        abstract_text,
        [
            "not a locked benchmark",
            "6 accepted core tasks",
            "8 calibration-only tasks",
            "limited task count",
            "author-estimated human times",
            "tiny smoke-model evidence",
        ],
    )
    rows.append(row(
        "abstract_scope_boundaries",
        "main_report",
        "pass" if abstract_ok else "fail",
        "front-matter scope phrases checked before the first task table",
        abstract_missing,
        "Keep locked-benchmark, sample-size, human-time, and provider-smoke limitations in the report abstract/front matter.",
        ["reports/metr_style_report.md"],
    ))

    run_section = section(main_report, "Committed Run Results") + "\n" + section(main_report, "Model Result Analysis")
    run_ok, run_missing = contains_all(
        run_section,
        [
            "not model performance",
            "excluded from benchmark pass-rate summaries",
            "smoke evidence only",
            "planned primary sweep remains mostly uncovered",
        ],
    )
    rows.append(row(
        "run_result_boundary_wording",
        "main_report",
        "pass" if run_ok else "fail",
        "committed-run section checked for local-QA and smoke-row boundaries",
        run_missing,
        "Keep local QA and tiny provider smoke rows explicitly separated from benchmark performance claims.",
        ["reports/metr_style_report.md", "data/run_results.csv"],
    ))

    claim_ledger = section(main_report, "Claim Ledger")
    ledger_ok, ledger_missing = contains_all(
        claim_ledger,
        [
            "v0.1 is a locked benchmark",
            "not supported",
            "Reported model pass rates characterize frontier performance",
            "only tiny smoke-sweep rows are committed",
        ],
    )
    rows.append(row(
        "claim_ledger_blocks_overclaims",
        "main_report",
        "pass" if ledger_ok else "fail",
        "claim ledger checked for explicit not-supported locked-benchmark and frontier-performance rows",
        ledger_missing,
        "Keep tempting overclaims in the claim ledger as unsupported, not as conclusions.",
        ["reports/metr_style_report.md", "reports/claim_evidence_audit.md"],
    ))

    concise_ok, concise_missing = contains_all(
        concise_report,
        [
            "not a locked benchmark",
            "Claim Boundaries",
            "Evidence Upgrade Path",
            "Capabilities And Expected Failures",
            "Remaining Blockers",
            "Next Work",
            "Evidence Appendix",
        ],
    )
    concise_line_count = len(concise_report.splitlines())
    concise_status = "pass" if concise_ok and concise_line_count <= 220 else "fail"
    rows.append(row(
        "concise_report_scope_and_length",
        "concise_report",
        concise_status,
        f"concise report exists={CONCISE_REPORT.exists()}; line_count={concise_line_count}; missing_scope_phrases={compact_json(concise_missing)}",
        concise_missing + ([f"line_count={concise_line_count}"] if concise_line_count > 220 else []),
        "Regenerate scripts/generate_concise_report.py and keep the reviewer-facing report concise and claim-bounded.",
        ["reports/concise_metr_report.md", "scripts/generate_concise_report.py"],
    ))

    unsafe_examples = unsafe_blocked_phrase_examples([MAIN_REPORT, CONCISE_REPORT, README])
    rows.append(row(
        "blocked_phrase_context_scan",
        "reports_and_readme",
        "pass" if not unsafe_examples else "fail",
        f"blocked-claim phrase contexts scanned across {MAIN_REPORT.relative_to(ROOT)}, {CONCISE_REPORT.relative_to(ROOT)}, and {README.relative_to(ROOT)}; unsafe_contexts={len(unsafe_examples)}",
        unsafe_examples,
        "Rewrite any blocked-claim phrase so the local context clearly says it is unsupported, blocked, missing, or future work.",
        ["reports/metr_style_report.md", "reports/concise_metr_report.md", "README.md", "data/claim_authorization_matrix.csv"],
    ))

    readme_ok, readme_missing = contains_all(
        readme,
        [
            "not a locked benchmark",
            "Do not fake results",
            "Local QA rows are validation evidence, not model performance",
            "API keys stay in environment variables",
        ],
    )
    rows.append(row(
        "readme_scope_boundaries",
        "readme",
        "pass" if readme_ok else "fail",
        "README checked for locked-benchmark, model-result, and credential-scope boundaries",
        readme_missing,
        "Keep the README top-level scope aligned with the report's claim authorization matrix.",
        ["README.md"],
    ))

    limitations = section(main_report, "Limitations")
    limitations_ok, limitations_missing = contains_all(
        limitations,
        [
            "below the 20-task target",
            "no accepted T4",
            "not measured independent solves",
            "tiny real provider smoke sweep",
            "Hosted Taiga/Env Linter QA is not represented",
            "not a locked benchmark",
        ],
    )
    rows.append(row(
        "limitations_cover_blockers",
        "main_report",
        "pass" if limitations_ok else "fail",
        "limitations section checked against blocked authorization themes",
        limitations_missing,
        "Keep task-count, T4, independent-timing, provider-smoke, hosted-QA, and locked-benchmark caveats in the limitations section.",
        ["reports/metr_style_report.md", "reports/threats_to_validity.md"],
    ))

    line_count = len(main_report.splitlines())
    table_count = main_report.count("\n| ")
    too_long = line_count > 800
    rows.append(row(
        "report_length_and_appendix_boundary",
        "main_report",
        "caution" if too_long else "pass",
        f"main report line_count={line_count}; markdown_table_rows={table_count}",
        [f"line_count={line_count}"] if too_long else [],
        "The report is evidence-rich but appendix-heavy; when results mature, move long generated tables out of the main narrative.",
        ["reports/metr_style_report.md"],
    ))
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row_data["status"] for row_data in rows)
    scope_counts = Counter(row_data["scope"] for row_data in rows)
    lines = [
        "# Report Claim Conformance Audit",
        "",
        "This generated audit checks whether the main report and README obey the claim-authorization matrix. It is intentionally textual and conservative: it catches unsupported claim wording, missing front-matter caveats, and report-shape drift.",
        "",
        "## Summary",
        "",
        f"- checks: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- scopes: `{compact_json(dict(sorted(scope_counts.items())))}`",
        "",
        "## Check Table",
        "",
        "| check | scope | status | evidence | failure examples | required action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row_data in rows:
        lines.append(
            f"| `{row_data['check_id']}` | {row_data['scope']} | {row_data['status']} | "
            f"{escaped(row_data['evidence'])} | `{escaped(row_data['failure_examples'])}` | "
            f"{escaped(row_data['required_action'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`fail` rows mean the report or README may be overclaiming or missing a required caveat. `caution` rows do not block local report use, but they mark places where the report is less skimmable or less mature than the playbook's final-report target.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "report_claim_conformance_audit.csv", rows)
    write_markdown(ROOT / "reports" / "report_claim_conformance_audit.md", rows)
    failures = sum(1 for row_data in rows if row_data["status"] == "fail")
    print(
        "wrote data/report_claim_conformance_audit.csv and "
        f"reports/report_claim_conformance_audit.md with {len(rows)} checks; failures={failures}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
