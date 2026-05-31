from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAK_PATTERNS = [
    "hidden/",
    "hidden\\",
    "PinCheck",
    "Reference.lean",
    "/wrong/",
    "\\wrong\\",
]


def run(cmd: list[str], cwd: Path, lean_path_dir: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if lean_path_dir is not None:
        existing = env.get("LEAN_PATH", "")
        env["LEAN_PATH"] = str(lean_path_dir) + (os.pathsep + existing if existing else "")
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )


def discover_exported_tasks(out: Path) -> list[Path]:
    return sorted(path.parent for path in out.rglob("metadata.json"))


def validate_task(task: Path) -> list[str]:
    errors: list[str] = []
    metadata = json.loads((task / "metadata.json").read_text(encoding="utf-8"))
    task_id = metadata.get("task_id", task.name)
    if (task / "hidden").exists():
        errors.append(f"{task_id}: hidden directory exported")
    if (task / "wrong").exists():
        errors.append(f"{task_id}: wrong directory exported")
    if not (task / "Prompt.md").exists():
        errors.append(f"{task_id}: missing Prompt.md")
    artifacts: list[Path] = []
    for public_file in metadata.get("public_files", ["Task.lean"]):
        path = task / public_file
        if not path.exists():
            errors.append(f"{task_id}: missing public file listed in metadata: {public_file}")
            continue
        if path.suffix == ".lean":
            olean = path.with_suffix(".olean")
            ilean = path.with_suffix(".ilean")
            artifacts.extend([olean, ilean])
            result = run(
                [
                    "lake",
                    "env",
                    "lean",
                    "-o",
                    str(olean),
                    "-i",
                    str(ilean),
                    str(path),
                ],
                cwd=ROOT,
                lean_path_dir=task,
            )
            if result.returncode != 0:
                errors.append(f"{task_id}: exported Lean file does not compile: {public_file}\n{result.stdout}")
                break
    for artifact in artifacts:
        if artifact.exists():
            artifact.unlink()
    for path in list(task.glob("*.md")) + list(task.rglob("*.lean")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in LEAK_PATTERNS:
            if pattern in text:
                errors.append(f"{task_id}: public file {path.relative_to(task)} contains leak pattern {pattern!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "public_tasks")
    args = parser.parse_args()
    out = args.out.resolve()
    if not out.exists():
        print(f"public export directory does not exist: {out}")
        return 1
    tasks = discover_exported_tasks(out)
    errors: list[str] = []
    for task in tasks:
        errors.extend(validate_task(task))
    if errors:
        print("PUBLIC EXPORT VALIDATION FAILURES:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"validated public export with {len(tasks)} tasks: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
