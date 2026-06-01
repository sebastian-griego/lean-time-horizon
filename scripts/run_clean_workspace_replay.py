from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import stat
import subprocess
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPLAY_ROOT = ROOT / "tmp" / "clean_workspace_replay"
WORKSPACE = REPLAY_ROOT / "workspace"

FIELDS = [
    "check_id",
    "phase",
    "status",
    "command",
    "returncode",
    "duration_seconds",
    "workspace_path",
    "stdout_tail",
    "artifacts_checked",
    "limitation",
    "next_action",
]

COMMANDS = [
    {
        "check_id": "workspace_materialization",
        "phase": "setup",
        "command": "materialize tracked and unignored working-tree files into tmp/clean_workspace_replay/workspace",
        "artifacts_checked": "tmp/clean_workspace_replay/workspace",
        "limitation": "This is a local clean workspace from the current working tree, not a remote clone or hosted container.",
        "next_action": "For a release tag, repeat from a remote clean clone or CI runner.",
    },
    {
        "check_id": "mathlib_cache_get",
        "phase": "replay",
        "command": "lake exe cache get",
        "artifacts_checked": ".lake/packages/mathlib/.lake/build/lib/lean",
        "limitation": "This uses the Mathlib cache for local dependency materialization; hosted runners need their own cache or build path.",
        "next_action": "Run this from clean workspaces before validating tasks that import Mathlib.",
    },
    {
        "check_id": "clean_lake_build",
        "phase": "replay",
        "command": "lake build",
        "artifacts_checked": ".lake/build",
        "limitation": "Local toolchain and dependency resolution can differ from hosted QA.",
        "next_action": "Record hosted/Taiga Full Env QA before locked-benchmark claims.",
    },
    {
        "check_id": "reference_validation_smoke",
        "phase": "replay",
        "command": "python scripts/validate_task.py tasks/dev/lt-201-multifile-cache-repair --submission tasks/dev/lt-201-multifile-cache-repair/hidden/Reference.lean --expect pass",
        "artifacts_checked": "tasks/dev/lt-201-multifile-cache-repair/hidden/Reference.lean",
        "limitation": "This is a representative reference-validation smoke, not full validate_all coverage.",
        "next_action": "Use validate_all.py for exhaustive local task validation.",
    },
    {
        "check_id": "wrong_submission_smoke",
        "phase": "replay",
        "command": "python scripts/validate_task.py tasks/dev/lt-203-exact-cover-spec --submission tasks/dev/lt-203-exact-cover-spec/wrong/Vacuous.lean --expect fail",
        "artifacts_checked": "tasks/dev/lt-203-exact-cover-spec/wrong/Vacuous.lean",
        "limitation": "This probes expected-fail behavior for one semantic-pin wrong submission only.",
        "next_action": "Keep validate_all.py as the exhaustive wrong-submission gate.",
    },
    {
        "check_id": "public_export_smoke",
        "phase": "replay",
        "command": "python scripts/export_public_tasks.py --out public_tasks",
        "artifacts_checked": "public_tasks",
        "limitation": "Local public export is not hosted problem packaging.",
        "next_action": "Upload exact public versions and run hosted QA before release freeze.",
    },
    {
        "check_id": "public_export_validation_smoke",
        "phase": "replay",
        "command": "python scripts/validate_public_export.py --out public_tasks",
        "artifacts_checked": "public_tasks",
        "limitation": "This validates local public assets but does not run Env Linter.",
        "next_action": "Run hosted Full Env QA and Env Linter before locked-benchmark claims.",
    },
]


def run_command(args: list[str], cwd: Path, timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
    )


def repo_files() -> list[Path]:
    result = run_command(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        ROOT,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout)
    paths: list[Path] = []
    for line in result.stdout.splitlines():
        rel = Path(line.strip())
        if not line.strip() or rel.parts[0] in {".git", ".lake", "tmp", "public_tasks"}:
            continue
        paths.append(rel)
    return paths


def safe_reset_workspace() -> None:
    resolved_root = REPLAY_ROOT.resolve()
    resolved_tmp = (ROOT / "tmp").resolve()
    if resolved_tmp not in resolved_root.parents and resolved_root != resolved_tmp:
        raise RuntimeError(f"refusing to remove replay root outside tmp: {resolved_root}")
    if REPLAY_ROOT.exists():
        def clear_readonly(func, path, _exc_info):
            os.chmod(path, stat.S_IWRITE)
            func(path)

        shutil.rmtree(REPLAY_ROOT, onerror=clear_readonly)
    WORKSPACE.mkdir(parents=True, exist_ok=True)


def materialize_workspace() -> tuple[int, list[str]]:
    safe_reset_workspace()
    copied = 0
    skipped: list[str] = []
    for rel in repo_files():
        src = ROOT / rel
        if not src.is_file():
            skipped.append(rel.as_posix())
            continue
        dest = WORKSPACE / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        copied += 1
    return copied, skipped


def tail(text: str, line_count: int = 8) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    clean = "\\n".join(lines[-line_count:])[:1800]
    return clean.encode("ascii", errors="replace").decode("ascii")


def command_to_args(command: str) -> list[str]:
    pieces = command.split()
    if not pieces:
        return []
    return pieces


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    status_counts = Counter(row["status"] for row in rows)
    phase_counts = Counter(row["phase"] for row in rows)
    failures = [row for row in rows if row["status"] != "pass"]
    lines = [
        "| check | phase | status | seconds | command | limitation |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['check_id']}` | {row['phase']} | {row['status']} | "
            f"{row['duration_seconds']} | `{row['command']}` | {row['limitation'].replace('|', '/')} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join([
            "# Clean Workspace Replay",
            "",
            "This generated replay creates a temporary workspace from the current tracked plus unignored working-tree files, excluding local build output, ignored secrets, temporary directories, and the existing public export. It then runs a bounded local replay that exercises the Lean toolchain, grader pass/fail behavior, and public export validation.",
            "",
            "It is stronger than a manifest-only command list, but still weaker than a remote clean clone, CI run, hosted Taiga QA, or full provider sweep.",
            "",
            "## Summary",
            "",
            f"- replay checks: `{len(rows)}`",
            f"- phase counts: `{compact_json(dict(sorted(phase_counts.items())))}`",
            f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
            f"- failure rows: `{len(failures)}`",
            f"- workspace: `{WORKSPACE.relative_to(ROOT).as_posix()}`",
            "",
            "## Replay Table",
            "",
            *lines,
            "",
            "## Interpretation",
            "",
            "`pass` means the bounded replay step completed in the temporary clean workspace. This should be treated as local reproducibility smoke evidence only: exhaustive task validation still comes from `validate_all.py`, model-performance evidence still requires real provider sweeps, and locked-benchmark claims still require hosted QA plus independent timing.",
            "",
        ]),
        encoding="utf-8",
    )


def build_rows(timeout: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    setup = COMMANDS[0]
    start = time.perf_counter()
    try:
        copied, skipped = materialize_workspace()
        status = "pass"
        returncode = "0"
        output = f"copied={copied}; skipped={compact_json(skipped[:20])}"
    except Exception as exc:  # noqa: BLE001 - report setup failure as data.
        status = "fail"
        returncode = "1"
        output = str(exc)
    rows.append({
        "check_id": setup["check_id"],
        "phase": setup["phase"],
        "status": status,
        "command": setup["command"],
        "returncode": returncode,
        "duration_seconds": f"{time.perf_counter() - start:.2f}",
        "workspace_path": WORKSPACE.relative_to(ROOT).as_posix(),
        "stdout_tail": output,
        "artifacts_checked": setup["artifacts_checked"],
        "limitation": setup["limitation"],
        "next_action": setup["next_action"],
    })
    if status != "pass":
        return rows

    for spec in COMMANDS[1:]:
        start = time.perf_counter()
        try:
            result = run_command(command_to_args(spec["command"]), WORKSPACE, timeout=timeout)
            status = "pass" if result.returncode == 0 else "fail"
            returncode = str(result.returncode)
            output = tail(result.stdout)
        except subprocess.TimeoutExpired as exc:
            status = "timeout"
            returncode = "timeout"
            output = tail(str(exc.stdout or "") + "\n" + str(exc))
        rows.append({
            "check_id": spec["check_id"],
            "phase": spec["phase"],
            "status": status,
            "command": spec["command"],
            "returncode": returncode,
            "duration_seconds": f"{time.perf_counter() - start:.2f}",
            "workspace_path": WORKSPACE.relative_to(ROOT).as_posix(),
            "stdout_tail": output,
            "artifacts_checked": spec["artifacts_checked"],
            "limitation": spec["limitation"],
            "next_action": spec["next_action"],
        })
        if status != "pass":
            break
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()
    rows = build_rows(args.timeout)
    write_csv(ROOT / "data" / "clean_workspace_replay.csv", rows)
    write_markdown(ROOT / "reports" / "clean_workspace_replay.md", rows)
    failures = sum(1 for row in rows if row["status"] != "pass")
    print(
        "wrote data/clean_workspace_replay.csv and "
        f"reports/clean_workspace_replay.md with {len(rows)} rows; failures={failures}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
