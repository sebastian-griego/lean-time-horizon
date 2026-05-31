from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def search_roots() -> list[Path]:
    roots = [ROOT / "LeanTimeHorizon.lean", ROOT / "tasks"]
    lake_packages = ROOT / ".lake" / "packages"
    if lake_packages.exists():
        roots.extend(path for path in [lake_packages / "mathlib" / "Mathlib", lake_packages / "std" / "Std"] if path.exists())
    return roots


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Lean/Std/Mathlib text lookup for model scaffolds.")
    parser.add_argument("query", help="literal text or regex pattern to search for")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    roots = [str(path) for path in search_roots() if path.exists()]
    if not roots:
        print("no Lean lookup roots found")
        return 1
    cmd = ["rg", "-n", "--glob", "*.lean", args.query, *roots]
    proc = subprocess.run(cmd, cwd=ROOT, text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines = proc.stdout.splitlines()
    for line in lines[: args.limit]:
        print(line)
    if len(lines) > args.limit:
        print(f"... truncated {len(lines) - args.limit} additional matches")
    return 0 if proc.returncode in {0, 1} else proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
