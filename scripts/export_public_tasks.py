from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATUSES = {"accepted_v0", "calibration_only", "candidate_review_pending"}


def load_metadata(task: Path) -> dict:
    return json.loads((task / "metadata.json").read_text(encoding="utf-8"))


def discover_tasks(statuses: set[str] | None) -> list[Path]:
    tasks: list[Path] = []
    for split in ["dev", "test", "candidates"]:
        base = ROOT / "tasks" / split
        if base.exists():
            for task in sorted(p for p in base.iterdir() if (p / "metadata.json").exists()):
                metadata = load_metadata(task)
                if statuses is None or metadata.get("acceptance_status") in statuses:
                    tasks.append(task)
    return tasks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "public_tasks")
    parser.add_argument(
        "--status",
        action="append",
        dest="statuses",
        help=(
            "acceptance_status to export. May be repeated. "
            "Defaults to accepted_v0, calibration_only, and candidate_review_pending."
        ),
    )
    parser.add_argument(
        "--all-statuses",
        action="store_true",
        help="export every task with metadata, including rejected tasks",
    )
    args = parser.parse_args()
    statuses = None if args.all_statuses else set(args.statuses or DEFAULT_STATUSES)
    out = args.out
    if out.exists():
        shutil.rmtree(out)
    tasks = discover_tasks(statuses)
    for task in tasks:
        metadata = load_metadata(task)
        rel = task.relative_to(ROOT / "tasks")
        dest = out / rel
        dest.mkdir(parents=True, exist_ok=True)
        public_names = ["Prompt.md", "metadata.json", *metadata.get("public_files", ["Task.lean"])]
        for name in dict.fromkeys(public_names):
            src = task / name
            if not src.exists():
                raise FileNotFoundError(f"{metadata['task_id']} lists missing public file {name}")
            dst = dest / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
    status_note = "all statuses" if statuses is None else ", ".join(sorted(statuses))
    print(f"exported {len(tasks)} public tasks to {out} ({status_note})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
