from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def discover_tasks() -> list[Path]:
    task_dirs: list[Path] = []
    for split in ["dev", "test"]:
        base = ROOT / "tasks" / split
        if base.exists():
            task_dirs.extend(sorted(p for p in base.iterdir() if (p / "metadata.json").exists()))
    return task_dirs


def run_validation(task_dir: Path, submission: Path, expect: str) -> bool:
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "validate_task.py"),
        str(task_dir),
        "--submission",
        str(submission),
        "--expect",
        expect,
    ]
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(proc.stdout)
    return proc.returncode == 0


def metadata_rows(task_dirs: list[Path]) -> list[dict[str, object]]:
    rows = []
    for task_dir in task_dirs:
        metadata = json.loads((task_dir / "metadata.json").read_text(encoding="utf-8"))
        rows.append(metadata)
    return rows


def write_metadata_csv(rows: list[dict[str, object]], path: Path) -> None:
    fields = [
        "task_id",
        "title",
        "split",
        "family",
        "domain",
        "source_type",
        "human_time_bucket",
        "human_minutes_p50",
        "human_minutes_p90",
        "human_estimate_confidence",
        "skills",
        "scaffolds",
        "expected_failure_modes",
        "scaffold_sensitivity",
        "qa_status",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: json.dumps(row[key]) if isinstance(row.get(key), list) else row.get(key, "")
                    for key in fields
                }
            )


def write_validation_commands(task_dirs: list[Path], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["task_id", "kind", "command"])
        writer.writeheader()
        for task_dir in task_dirs:
            metadata = json.loads((task_dir / "metadata.json").read_text(encoding="utf-8"))
            rel = task_dir.relative_to(ROOT).as_posix()
            writer.writerow(
                {
                    "task_id": metadata["task_id"],
                    "kind": "reference_pass",
                    "command": f"python scripts/validate_task.py {rel} --submission {rel}/hidden/Reference.lean --expect pass",
                }
            )
            for wrong in sorted((task_dir / "wrong").glob("*.lean")):
                writer.writerow(
                    {
                        "task_id": metadata["task_id"],
                        "kind": f"wrong_fail:{wrong.stem}",
                        "command": f"python scripts/validate_task.py {rel} --submission {rel}/wrong/{wrong.name} --expect fail",
                    }
                )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata-csv", type=Path, default=ROOT / "data" / "task_metadata.csv")
    parser.add_argument("--validation-commands-csv", type=Path, default=ROOT / "data" / "validation_commands.csv")
    args = parser.parse_args()

    tmp = ROOT / "tmp"
    tmp.mkdir(exist_ok=True)

    task_dirs = discover_tasks()
    failures: list[str] = []
    for task_dir in task_dirs:
        print(f"== {task_dir.relative_to(ROOT)} reference ==")
        if not run_validation(task_dir, task_dir / "hidden" / "Reference.lean", "pass"):
            failures.append(f"{task_dir.name}: reference failed")
        wrongs = sorted((task_dir / "wrong").glob("*.lean"))
        if not wrongs:
            failures.append(f"{task_dir.name}: no wrong submissions")
        for wrong in wrongs:
            print(f"== {task_dir.relative_to(ROOT)} wrong {wrong.name} ==")
            if not run_validation(task_dir, wrong, "fail"):
                failures.append(f"{task_dir.name}: wrong submission accepted ({wrong.name})")

    rows = metadata_rows(task_dirs)
    write_metadata_csv(rows, args.metadata_csv)
    write_validation_commands(task_dirs, args.validation_commands_csv)
    print(f"wrote {args.metadata_csv.relative_to(ROOT)} with {len(rows)} tasks")
    print(f"wrote {args.validation_commands_csv.relative_to(ROOT)}")

    if failures:
        print("VALIDATION FAILURES:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("all tasks validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
