from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def discover_tasks() -> list[Path]:
    tasks: list[Path] = []
    for split in ["dev", "test", "candidates"]:
        base = ROOT / "tasks" / split
        if base.exists():
            tasks.extend(sorted(p for p in base.iterdir() if (p / "metadata.json").exists()))
    return tasks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "public_tasks")
    args = parser.parse_args()
    out = args.out
    if out.exists():
        shutil.rmtree(out)
    for task in discover_tasks():
        rel = task.relative_to(ROOT / "tasks")
        dest = out / rel
        dest.mkdir(parents=True, exist_ok=True)
        for name in ["Prompt.md", "Task.lean", "metadata.json"]:
            shutil.copyfile(task / name, dest / name)
    print(f"exported {len(discover_tasks())} public tasks to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
