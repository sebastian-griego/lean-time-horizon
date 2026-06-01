from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_model_sweep import build_prompt  # noqa: E402

RELEASE_STATUSES = {"accepted_v0", "calibration_only", "candidate_review_pending"}

FIELDS = [
    "task_id",
    "split",
    "acceptance_status",
    "family",
    "status",
    "prompt_checks_passed",
    "prompt_checks_total",
    "runner_supplied_fields",
    "missing_or_caution_fields",
    "leak_patterns_found",
    "notes",
]

FORBIDDEN_TERMS = [
    "sorry",
    "admit",
    "axiom",
    "constant",
    "opaque",
    "unsafe",
    "run_cmd",
    "run_tac",
    "Lean.addDecl",
    "#eval",
    "#exit",
]

LEAK_PATTERNS = [
    "hidden/",
    "hidden\\",
    "Reference.lean",
    "PinCheck",
    "/wrong/",
    "\\wrong\\",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def discover_task_dirs() -> dict[str, Path]:
    task_dirs: dict[str, Path] = {}
    for split in ["dev", "test", "candidates"]:
        base = ROOT / "tasks" / split
        if not base.exists():
            continue
        for task_dir in sorted(path for path in base.iterdir() if path.is_dir()):
            metadata_path = task_dir / "metadata.json"
            if not metadata_path.exists():
                continue
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            task_dirs[str(metadata["task_id"])] = task_dir
    return task_dirs


def has_any(text: str, patterns: list[str]) -> bool:
    lower = text.lower()
    return any(pattern.lower() in lower for pattern in patterns)


def regex_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def check_prompt(task: dict[str, str], task_dir: Path) -> dict[str, str]:
    prompt_path = task_dir / "Prompt.md"
    prompt = prompt_path.read_text(encoding="utf-8", errors="replace") if prompt_path.exists() else ""
    model_prompt = build_prompt(task_dir, "lookup_unlimited") if prompt_path.exists() else ""
    submission_file = task.get("submission_file", "Task.lean")
    public_files = json.loads(task.get("public_files", "[\"Task.lean\"]"))

    checks: dict[str, bool] = {}
    runner_supplied: list[str] = []
    cautions: list[str] = []

    checks["prompt_exists"] = bool(prompt)
    checks["exact_deliverable"] = regex_any(
        prompt,
        [
            r"\bdeliverable\b",
            r"\bcomplete\b",
            r"\bprove\b",
            r"\brepair\b",
            r"\bformaliz(e|ation)\b",
            r"\bbuild\b",
        ],
    )
    checks["edit_scope"] = submission_file in prompt and regex_any(prompt, [r"\bedit\b", r"\bcomplete\b", r"\breplace\b"])
    checks["theorem_statement_policy"] = regex_any(
        prompt,
        [
            r"do not change [\s\S]{0,180}(statement|theorem name|declaration name)",
            r"without changing [\s\S]{0,180}statement",
            r"do not [\s\S]{0,180}weaken[\s\S]{0,80}statement",
        ],
    )
    checks["helper_lemma_policy"] = regex_any(prompt, [r"helper lemma", r"helper lemmas", r"may add helper", r"may introduce helper"])
    checks["forbidden_constructs"] = all(term in prompt for term in FORBIDDEN_TERMS)
    checks["submission_format"] = regex_any(prompt, [r"submission", r"complete contents", r"deliverable"])
    if not checks["submission_format"] and f"Return the complete contents of {submission_file} only" in model_prompt:
        checks["submission_format"] = True
        runner_supplied.append("submission_format")
    checks["tool_affordance"] = "Scaffold: lookup_unlimited" in model_prompt and "lean_lookup.py QUERY" in model_prompt
    if checks["tool_affordance"] and "lean_lookup.py QUERY" not in prompt:
        runner_supplied.append("tool_affordance")
    checks["attempt_limit"] = "iterative compile/debug attempts" in model_prompt or regex_any(prompt, [r"one submission", r"attempt", r"timeout"])
    if checks["attempt_limit"] and not regex_any(prompt, [r"one submission", r"attempt", r"timeout"]):
        runner_supplied.append("attempt_limit")
    checks["import_policy"] = regex_any(
        prompt,
        [
            r"do not change [\s\S]{0,180}imports?",
            r"do not edit [\s\S]{0,180}imports?",
            r"do not remove [\s\S]{0,180}imports?",
            r"imports? may",
            r"imports? must",
        ],
    )
    if not checks["import_policy"]:
        cautions.append("import_policy_not_explicit")
    checks["public_files_match"] = all(public_file in model_prompt for public_file in public_files)

    leak_patterns = [pattern for pattern in LEAK_PATTERNS if pattern in prompt]
    missing = [name for name, ok in checks.items() if not ok]
    failed = [name for name in missing if name != "import_policy"]
    status = "pass"
    if failed or leak_patterns:
        status = "fail"
    elif cautions or runner_supplied:
        status = "caution"

    return {
        "task_id": task["task_id"],
        "split": task["split"],
        "acceptance_status": task["acceptance_status"],
        "family": task["family"],
        "status": status,
        "prompt_checks_passed": str(sum(1 for ok in checks.values() if ok)),
        "prompt_checks_total": str(len(checks)),
        "runner_supplied_fields": json.dumps(sorted(set(runner_supplied))),
        "missing_or_caution_fields": json.dumps(sorted(set(missing + cautions))),
        "leak_patterns_found": json.dumps(leak_patterns),
        "notes": "Prompt contract is evaluated against Prompt.md plus runner scaffold wrapper.",
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row["status"] for row in rows)
    family_counts = Counter(row["family"] for row in rows)
    runner_supplied_counts: Counter[str] = Counter()
    missing_counts: Counter[str] = Counter()
    leak_rows = [row for row in rows if row["leak_patterns_found"] != "[]"]
    for row in rows:
        runner_supplied_counts.update(json.loads(row["runner_supplied_fields"]))
        missing_counts.update(json.loads(row["missing_or_caution_fields"]))
    table_lines = [
        "| task | status | checks | runner-supplied fields | missing/caution fields | leaks |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for row in rows:
        table_lines.append(
            f"| `{row['task_id']}` | {row['status']} | {row['prompt_checks_passed']}/{row['prompt_checks_total']} | "
            f"`{row['runner_supplied_fields']}` | `{row['missing_or_caution_fields']}` | `{row['leak_patterns_found']}` |"
        )
    lines = [
        "# Prompt Contract Audit",
        "",
        "This generated audit checks release task prompts against the playbook's public prompt standards. It evaluates the model-facing prompt as `Prompt.md` plus the runner scaffold wrapper, because the wrapper supplies scaffold-specific tool and attempt information.",
        "",
        "## Summary",
        "",
        f"- release tasks audited: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- families: `{compact_json(dict(sorted(family_counts.items())))}`",
        f"- runner-supplied field counts: `{compact_json(dict(sorted(runner_supplied_counts.items())))}`",
        f"- missing/caution field counts: `{compact_json(dict(sorted(missing_counts.items())))}`",
        f"- prompt leak rows: `{len(leak_rows)}`",
        "",
        "## Task Table",
        "",
        "\n".join(table_lines),
        "",
        "## Interpretation",
        "",
        "`pass` means Prompt.md itself covers the checked contract fields and no leak pattern was found. `caution` usually means the runner wrapper supplies tool, attempt, or submission-format fields, or the prompt lacks an explicit import policy. `fail` means a required field or leak check failed.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    metadata = read_csv(ROOT / "data" / "task_metadata.csv")
    task_dirs = discover_task_dirs()
    release_tasks = [task for task in metadata if task.get("acceptance_status") in RELEASE_STATUSES]
    rows = [check_prompt(task, task_dirs[task["task_id"]]) for task in release_tasks]
    write_csv(ROOT / "data" / "prompt_contract_audit.csv", rows)
    write_markdown(ROOT / "reports" / "prompt_contract_audit.md", rows)
    print(f"wrote data/prompt_contract_audit.csv and reports/prompt_contract_audit.md with {len(rows)} prompt rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
