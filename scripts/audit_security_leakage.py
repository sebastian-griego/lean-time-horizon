from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "check_id",
    "area",
    "status",
    "finding_count",
    "evidence",
    "scanned_scope",
    "limitation",
    "next_action",
]

SECRET_PATTERNS = [
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("anthropic_key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("gemini_key", re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b")),
    (
        "generic_secret_assignment",
        re.compile(
            r"\b(?:api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"]?"
            r"([A-Za-z0-9_./+=-]{20,})['\"]?",
            re.IGNORECASE,
        ),
    ),
]

SENSITIVE_FILENAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".npmrc",
    "credentials.json",
    "service_account.json",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
}
SENSITIVE_SUFFIXES = {".pem", ".p12", ".pfx", ".key"}

SKIP_DIR_PARTS = {
    ".git",
    ".lake",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    "lake-packages",
    "tmp",
}

HIDDEN_PATH_PARTS = {"hidden", "wrong"}
HIDDEN_FILENAMES = {"Reference.lean", "PinCheck.lean", "Grader.lean"}
LOW_INFORMATION_PREFIXES = ("import ", "open ", "namespace ", "end ", "set_option ")
SELF_AUDIT_ARTIFACTS = [
    Path("scripts/audit_security_leakage.py"),
    Path("data/security_leakage_audit.csv"),
    Path("reports/security_leakage_audit.md"),
]


def run_git_ls_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    paths: list[Path] = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        paths.append(ROOT / raw.decode("utf-8", errors="replace"))
    return paths


def repo_artifact_paths() -> list[Path]:
    paths = set(run_git_ls_files())
    for relative in SELF_AUDIT_ARTIFACTS:
        path = ROOT / relative
        if path.exists():
            paths.add(path)
    return sorted(paths)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def should_skip(path: Path) -> bool:
    parts = set(path.relative_to(ROOT).parts)
    return bool(parts & SKIP_DIR_PARTS)


def is_text(path: Path) -> bool:
    try:
        data = path.read_bytes()
    except OSError:
        return False
    if b"\0" in data:
        return False
    try:
        data.decode("utf-8")
        return True
    except UnicodeDecodeError:
        try:
            data.decode("utf-8", errors="replace")
            return True
        except UnicodeError:
            return False


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def public_export_paths() -> list[Path]:
    public_dir = ROOT / "public_tasks"
    if not public_dir.exists():
        return []
    return sorted(path for path in public_dir.rglob("*") if path.is_file())


def tracked_text_paths() -> list[Path]:
    return [
        path
        for path in repo_artifact_paths()
        if path.exists() and path.is_file() and not should_skip(path) and is_text(path)
    ]


def secret_findings(paths: list[Path]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in paths:
        text = read_text(path)
        for pattern_name, pattern in SECRET_PATTERNS:
            for match_index, _ in enumerate(pattern.finditer(text), start=1):
                findings.append({
                    "pattern": pattern_name,
                    "path": rel(path) if path.is_relative_to(ROOT) else str(path),
                    "match_index": str(match_index),
                })
    return findings


def sensitive_file_findings(paths: list[Path]) -> list[str]:
    findings: list[str] = []
    for path in paths:
        name = path.name
        if name.endswith(".example") or name.endswith(".template"):
            continue
        if name in SENSITIVE_FILENAMES or path.suffix.lower() in SENSITIVE_SUFFIXES:
            findings.append(rel(path))
    return findings


def public_hidden_path_findings(paths: list[Path]) -> list[str]:
    findings: list[str] = []
    for path in paths:
        parts = set(path.relative_to(ROOT).parts) if path.is_relative_to(ROOT) else set(path.parts)
        if parts & HIDDEN_PATH_PARTS or path.name in HIDDEN_FILENAMES:
            findings.append(rel(path) if path.is_relative_to(ROOT) else str(path))
    return findings


def normalized_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("--"):
            continue
        lines.append(re.sub(r"\s+", " ", stripped))
    return lines


def text_windows(path: Path, window_size: int = 4) -> dict[str, str]:
    lines = normalized_lines(read_text(path))
    windows: dict[str, str] = {}
    for index in range(0, max(0, len(lines) - window_size + 1)):
        window_lines = lines[index : index + window_size]
        if sum(not line.startswith(LOW_INFORMATION_PREFIXES) for line in window_lines) < 2:
            continue
        window = "\n".join(window_lines)
        if len(window) < 180:
            continue
        fingerprint = hashlib.sha256(window.encode("utf-8")).hexdigest()[:16]
        windows[fingerprint] = rel(path)
    return windows


def public_task_baseline_windows(hidden_path: Path) -> set[str]:
    task_dir = hidden_path.parent.parent
    if not task_dir.exists():
        return set()
    baseline: set[str] = set()
    for path in sorted(task_dir.rglob("*")):
        if not path.is_file() or not is_text(path):
            continue
        parts = set(path.relative_to(ROOT).parts)
        if parts & HIDDEN_PATH_PARTS:
            continue
        baseline.update(text_windows(path).keys())
    return baseline


def hidden_content_findings(paths: list[Path]) -> list[dict[str, str]]:
    tracked = tracked_text_paths()
    hidden_files = [
        path
        for path in tracked
        if "hidden" in path.relative_to(ROOT).parts and path.suffix == ".lean"
    ]
    fingerprints: dict[str, str] = {}
    for hidden_file in hidden_files:
        public_baseline = public_task_baseline_windows(hidden_file)
        for fingerprint, source in text_windows(hidden_file).items():
            if fingerprint not in public_baseline:
                fingerprints[fingerprint] = source

    public_targets = [
        path
        for path in tracked
        if not (set(path.relative_to(ROOT).parts) & HIDDEN_PATH_PARTS)
    ]
    public_targets.extend(path for path in paths if is_text(path))

    findings: list[dict[str, str]] = []
    for target in sorted(set(public_targets)):
        lines = normalized_lines(read_text(target))
        for index in range(0, max(0, len(lines) - 4 + 1)):
            window = "\n".join(lines[index : index + 4])
            if len(window) < 180:
                continue
            fingerprint = hashlib.sha256(window.encode("utf-8")).hexdigest()[:16]
            hidden_source = fingerprints.get(fingerprint)
            if hidden_source:
                findings.append({
                    "fingerprint": fingerprint,
                    "hidden_source": hidden_source,
                    "public_path": rel(target) if target.is_relative_to(ROOT) else str(target),
                })
    return findings


def provider_policy_ok(paths: list[Path]) -> tuple[bool, str]:
    provider_files = [
        ROOT / "scripts" / "run_model_sweep.py",
        ROOT / "scripts" / "openai_runner.py",
        ROOT / "scripts" / "anthropic_runner.py",
        ROOT / "scripts" / "gemini_runner.py",
        ROOT / "reports" / "model_sweep_execution_packet.md",
        ROOT / "data" / "model_sweep_execution_commands.csv",
    ]
    existing = [path for path in provider_files if path.exists()]
    text = "\n".join(read_text(path) for path in existing if is_text(path))
    required_env_mentions = [
        "OPENAI_LEAN_RUNNER",
        "ANTHROPIC_LEAN_RUNNER",
        "GEMINI_LEAN_RUNNER",
        "LEAN_MODEL_RUNNER",
    ]
    mentions = {name: (name in text) for name in required_env_mentions}
    findings = secret_findings([path for path in existing if is_text(path)])
    ok = all(mentions.values()) and not findings
    evidence = f"env_mentions={json.dumps(mentions, sort_keys=True)}; provider_secret_pattern_findings={len(findings)}"
    return ok, evidence


def row(
    check_id: str,
    area: str,
    status: str,
    finding_count: int,
    evidence: str,
    scanned_scope: str,
    limitation: str,
    next_action: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "status": status,
        "finding_count": str(finding_count),
        "evidence": evidence,
        "scanned_scope": scanned_scope,
        "limitation": limitation,
        "next_action": next_action,
    }


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def build_rows() -> list[dict[str, str]]:
    tracked = tracked_text_paths()
    public_paths = public_export_paths()
    public_text_paths = [path for path in public_paths if is_text(path)]

    secrets = secret_findings(tracked + public_text_paths)
    secret_counts = Counter(finding["pattern"] for finding in secrets)
    repo_paths = repo_artifact_paths()
    sensitive_files = sensitive_file_findings(repo_paths)
    hidden_path_leaks = public_hidden_path_findings(public_paths)
    content_leaks = hidden_content_findings(public_paths)
    provider_ok, provider_evidence = provider_policy_ok(tracked)

    rows = [
        row(
            "tracked_secret_pattern_scan",
            "credential_hygiene",
            "pass" if not secrets else "fail",
            len(secrets),
            f"pattern_counts={compact_json(dict(sorted(secret_counts.items())))}; matched_values_are_not_reported=true",
            f"tracked_text_files={len(tracked)}; public_export_text_files={len(public_text_paths)}",
            "Pattern scanning can miss novel credential formats and may flag only committed/exported text, not private local environment files.",
            "Keep provider keys in environment variables and rerun after adding provider adapters or reports.",
        ),
        row(
            "tracked_sensitive_filename_scan",
            "credential_hygiene",
            "pass" if not sensitive_files else "fail",
            len(sensitive_files),
            f"sensitive_tracked_paths={len(sensitive_files)}",
            f"repo_artifact_files={len(repo_paths)}",
            "This checks filenames in tracked git files plus the audit's own generated artifacts; arbitrary untracked local developer files are intentionally outside the report artifact.",
            "Do not commit .env files, private keys, or provider credential JSON.",
        ),
        row(
            "public_export_hidden_path_scan",
            "hidden_material",
            "pass" if not hidden_path_leaks else "fail",
            len(hidden_path_leaks),
            f"hidden_or_wrong_public_paths={len(hidden_path_leaks)}",
            f"public_export_files={len(public_paths)}",
            "This verifies exported file paths, not hosted problem-version filesystem isolation.",
            "Rerun export and hosted QA before treating public tasks as deployed problem versions.",
        ),
        row(
            "hidden_content_fingerprint_scan",
            "hidden_material",
            "pass" if not content_leaks else "fail",
            len(content_leaks),
            f"verbatim_hidden_window_matches={len(content_leaks)}; hidden_windows_are_fingerprinted_not_printed=true",
            "tracked public/report/data/script text outside hidden/wrong plus public_tasks",
            "Fingerprint windows catch verbatim multi-line leaks, not paraphrases or single-line theorem statements.",
            "Rerun after report, task, public export, or hidden-check edits.",
        ),
        row(
            "provider_credential_policy_scan",
            "credential_hygiene",
            "pass" if provider_ok else "fail",
            0 if provider_ok else 1,
            provider_evidence,
            "provider runner scripts and model-sweep execution packet",
            "Environment-variable policy evidence does not prove provider runs were executed or that external secrets are valid.",
            "Keep runner commands environment-variable based and do not commit provider API keys.",
        ),
    ]
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    status_counts = Counter(row_data["status"] for row_data in rows)
    area_counts = Counter(row_data["area"] for row_data in rows)
    lines = [
        "# Security And Leakage Audit",
        "",
        "This generated audit checks the committed artifact for credential hygiene and hidden-material leakage. It scans tracked repository text plus the generated public task export, reports counts and fingerprints only, and never prints matched secret values or hidden Lean snippets.",
        "",
        "## Summary",
        "",
        f"- checks: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- areas: `{compact_json(dict(sorted(area_counts.items())))}`",
        "",
        "## Check Table",
        "",
        "| check | area | status | findings | evidence | scanned scope | limitation | next action |",
        "| --- | --- | --- | ---: | --- | --- | --- | --- |",
    ]
    for item in rows:
        lines.append(
            f"| `{item['check_id']}` | {item['area']} | {item['status']} | {item['finding_count']} | "
            f"{escaped(item['evidence'])} | {escaped(item['scanned_scope'])} | "
            f"{escaped(item['limitation'])} | {escaped(item['next_action'])} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`pass` means this local committed/exported artifact has no findings for the corresponding scan. It does not prove that private untracked developer files are secret-free, and it does not replace hosted environment QA.",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "security_leakage_audit.csv", rows)
    write_markdown(ROOT / "reports" / "security_leakage_audit.md", rows)
    failures = sum(1 for row_data in rows if row_data["status"] == "fail")
    print(
        "wrote data/security_leakage_audit.csv and reports/security_leakage_audit.md "
        f"with {len(rows)} checks; failures={failures}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
