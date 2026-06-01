from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def search_roots() -> list[Path]:
    roots = [ROOT / "LeanTimeHorizon.lean"]
    for split in ["dev", "test", "candidates"]:
        base = ROOT / "tasks" / split
        if not base.exists():
            continue
        for task_dir in sorted(path for path in base.iterdir() if path.is_dir()):
            metadata_path = task_dir / "metadata.json"
            if not metadata_path.exists():
                continue
            try:
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            for public_file in metadata.get("public_files", ["Task.lean"]):
                public_path = task_dir / public_file
                if public_path.suffix == ".lean":
                    roots.append(public_path)
    lake_packages = ROOT / ".lake" / "packages"
    if lake_packages.exists():
        roots.extend(path for path in [lake_packages / "mathlib" / "Mathlib", lake_packages / "std" / "Std"] if path.exists())
    return roots


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Read-only Lean/Std/Mathlib text lookup for model scaffolds.")
    parser.add_argument("query", help="literal text or regex pattern to search for")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    roots = [str(path) for path in search_roots() if path.exists()]
    if not roots:
        print("no Lean lookup roots found")
        return 1
    cmd = [
        "rg",
        "-n",
        "--glob",
        "*.lean",
        "--glob",
        "!**/hidden/**",
        "--glob",
        "!**/wrong/**",
        args.query,
        *roots,
    ]
    proc = subprocess.run(cmd, cwd=ROOT, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines = proc.stdout.splitlines()
    for line in lines[: args.limit]:
        print(line)
    if len(lines) > args.limit:
        print(f"... truncated {len(lines) - args.limit} additional matches")
    return 0 if proc.returncode in {0, 1} else proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
