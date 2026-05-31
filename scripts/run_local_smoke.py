from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()
    tasks = []
    for split in ["dev", "test"]:
        base = ROOT / "tasks" / split
        if base.exists():
            tasks.extend(sorted(p for p in base.iterdir() if (p / "metadata.json").exists()))
    ok = True
    for task in tasks[: args.limit]:
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "validate_task.py"),
                str(task),
                "--submission",
                str(task / "hidden" / "Reference.lean"),
                "--expect",
                "pass",
            ],
            cwd=ROOT,
        )
        ok = ok and proc.returncode == 0
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
