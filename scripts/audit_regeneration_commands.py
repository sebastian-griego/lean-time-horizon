from __future__ import annotations

import ast
import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "check_id",
    "area",
    "status",
    "evidence",
    "mismatches",
    "source_artifacts",
    "required_action",
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


def python_string_list_assignment(path: Path, name: str) -> list[str]:
    module = ast.parse(read_text(path), filename=str(path))
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            continue
        if not isinstance(node.value, (ast.List, ast.Set, ast.Tuple)):
            continue
        values: list[str] = []
        for item in node.value.elts:
            if isinstance(item, ast.Constant) and isinstance(item.value, str):
                values.append(item.value)
        return values
    return []


def read_manifest_commands() -> list[str]:
    path = ROOT / "reports" / "validation_manifest.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    commands = data.get("regeneration_commands", [])
    return [str(command) for command in commands] if isinstance(commands, list) else []


def read_readme_validate_commands() -> list[str]:
    readme = read_text(ROOT / "README.md")
    marker = "Run the local acceptance gate from the repo root:"
    start = readme.find(marker)
    if start == -1:
        return []
    block = readme[start:]
    match = re.search(r"```powershell\r?\n(?P<body>.*?)\r?\n```", block, flags=re.DOTALL)
    if not match:
        return []
    return [
        line.strip()
        for line in match.group("body").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def first_sequence_mismatches(left: list[str], right: list[str], left_name: str, right_name: str) -> list[str]:
    mismatches: list[str] = []
    for index, (left_command, right_command) in enumerate(zip(left, right)):
        if left_command != right_command:
            mismatches.append(
                f"index {index}: {left_name}={left_command!r}; {right_name}={right_command!r}"
            )
            if len(mismatches) >= 8:
                break
    if len(left) != len(right):
        mismatches.append(f"length mismatch: {left_name}={len(left)}; {right_name}={len(right)}")
    left_counts = Counter(left)
    right_counts = Counter(right)
    missing = sorted((right_counts - left_counts).elements())
    extra = sorted((left_counts - right_counts).elements())
    for command in missing[:8]:
        mismatches.append(f"{left_name} missing command from {right_name}: {command}")
    for command in extra[:8]:
        mismatches.append(f"{left_name} extra command not in {right_name}: {command}")
    return mismatches


def split_reviewer_commands(command: str) -> list[str]:
    return [part.strip() for part in command.split(";") if part.strip()]


def row(
    check_id: str,
    area: str,
    status: str,
    evidence: str,
    mismatches: list[str],
    source_artifacts: list[str],
    required_action: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "status": status,
        "evidence": evidence,
        "mismatches": compact_json(mismatches[:16]),
        "source_artifacts": ";".join(source_artifacts),
        "required_action": required_action,
    }


def build_rows() -> list[dict[str, str]]:
    source_commands = python_string_list_assignment(
        ROOT / "scripts" / "write_validation_manifest.py",
        "REGENERATION_COMMANDS",
    )
    readme_commands = read_readme_validate_commands()
    manifest_commands = read_manifest_commands()
    required_commands = python_string_list_assignment(
        ROOT / "scripts" / "audit_validation_manifest.py",
        "REQUIRED_COMMANDS",
    )
    reviewer_rows = read_csv(ROOT / "data" / "reviewer_reproduction_steps.csv")

    rows: list[dict[str, str]] = []
    readme_mismatches = first_sequence_mismatches(
        readme_commands,
        source_commands,
        "README",
        "write_validation_manifest.REGENERATION_COMMANDS",
    )
    rows.append(row(
        "readme_matches_manifest_source",
        "command_sequence",
        "pass" if source_commands and readme_commands == source_commands else "fail",
        (
            f"readme_commands={len(readme_commands)}; source_commands={len(source_commands)}; "
            f"first_readme={readme_commands[:3]}; last_readme={readme_commands[-3:]}"
        ),
        readme_mismatches,
        ["README.md", "scripts/write_validation_manifest.py"],
        "Update README.md and scripts/write_validation_manifest.py together whenever the local gate changes.",
    ))

    manifest_mismatches = first_sequence_mismatches(
        manifest_commands,
        source_commands,
        "validation_manifest.json",
        "write_validation_manifest.REGENERATION_COMMANDS",
    )
    rows.append(row(
        "json_manifest_matches_source",
        "command_sequence",
        "pass" if source_commands and manifest_commands == source_commands else "fail",
        (
            f"manifest_commands={len(manifest_commands)}; source_commands={len(source_commands)}; "
            f"manifest_present={(ROOT / 'reports' / 'validation_manifest.json').exists()}"
        ),
        manifest_mismatches,
        ["reports/validation_manifest.json", "scripts/write_validation_manifest.py"],
        "Run scripts/write_validation_manifest.py after editing the regeneration command list.",
    ))

    required_missing_readme = sorted(set(required_commands) - set(readme_commands))
    required_missing_source = sorted(set(required_commands) - set(source_commands))
    required_missing_manifest = sorted(set(required_commands) - set(manifest_commands))
    rows.append(row(
        "required_commands_in_public_gate",
        "required_command_coverage",
        "pass" if required_commands and not required_missing_readme and not required_missing_source and not required_missing_manifest else "fail",
        (
            f"required={len(required_commands)}; missing_readme={len(required_missing_readme)}; "
            f"missing_source={len(required_missing_source)}; missing_manifest={len(required_missing_manifest)}"
        ),
        [
            *(f"README missing {command}" for command in required_missing_readme),
            *(f"source missing {command}" for command in required_missing_source),
            *(f"manifest missing {command}" for command in required_missing_manifest),
        ],
        ["scripts/audit_validation_manifest.py", "README.md", "scripts/write_validation_manifest.py", "reports/validation_manifest.json"],
        "Keep the required-command set visible in both the README gate and validation manifest command list.",
    ))

    local_reviewer_commands = [
        part
        for reviewer_row in reviewer_rows
        if reviewer_row.get("phase") == "local_replay"
        for part in split_reviewer_commands(reviewer_row.get("command", ""))
    ]
    missing_reviewer = sorted(command for command in local_reviewer_commands if command not in source_commands)
    rows.append(row(
        "reviewer_packet_local_subset",
        "reviewer_reproduction",
        "pass" if reviewer_rows and not missing_reviewer else "fail",
        (
            f"reviewer_rows={len(reviewer_rows)}; local_reviewer_commands={len(local_reviewer_commands)}; "
            f"missing_from_full_gate={len(missing_reviewer)}"
        ),
        missing_reviewer,
        ["data/reviewer_reproduction_steps.csv", "reports/reviewer_reproduction_packet.md", "scripts/write_validation_manifest.py"],
        "Keep reviewer local-replay commands as a subset of the full local regeneration gate.",
    ))

    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row_data["status"] for row_data in rows)
    area_counts = Counter(row_data["area"] for row_data in rows)
    lines = [
        "# Regeneration Command Consistency Audit",
        "",
        "This generated audit checks that the README validation block, the validation-manifest command source, and the committed validation manifest describe the same local regeneration gate. It also verifies that the shorter reviewer reproduction packet is a subset of that gate for local replay commands.",
        "",
        "## Summary",
        "",
        f"- checks: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- areas: `{compact_json(dict(sorted(area_counts.items())))}`",
        "",
        "## Check Table",
        "",
        "| check | area | status | evidence | mismatches | required action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row_data in rows:
        lines.append(
            f"| `{row_data['check_id']}` | {row_data['area']} | {row_data['status']} | "
            f"{escaped(row_data['evidence'])} | `{escaped(row_data['mismatches'])}` | "
            f"{escaped(row_data['required_action'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`pass` means the local replay instructions are synchronized across the public README, the manifest producer, the committed manifest, and the reviewer reproduction packet's local replay subset. This audit does not prove the commands were run on a clean hosted environment; it only prevents stale or contradictory replay instructions.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "regeneration_command_consistency.csv", rows)
    write_markdown(ROOT / "reports" / "regeneration_command_consistency.md", rows)
    failures = sum(1 for row_data in rows if row_data["status"] == "fail")
    print(
        "wrote data/regeneration_command_consistency.csv and "
        f"reports/regeneration_command_consistency.md with {len(rows)} checks; failures={failures}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
