from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATUSES = {"accepted_v0", "calibration_only"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def discover_source_tasks() -> dict[str, Path]:
    tasks: dict[str, Path] = {}
    for split in ("dev", "test", "candidates"):
        base = ROOT / "tasks" / split
        if not base.exists():
            continue
        for metadata_path in sorted(base.glob("*/metadata.json")):
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            tasks[str(metadata["task_id"])] = metadata_path.parent
    return tasks


def build_bundle(statuses: set[str]) -> dict[str, object]:
    metadata_rows = read_csv(ROOT / "data" / "task_metadata.csv")
    source_tasks = discover_source_tasks()
    tasks: dict[str, object] = {}
    missing: list[str] = []
    for row in metadata_rows:
        task_id = row["task_id"]
        if row.get("acceptance_status") not in statuses:
            continue
        task_dir = source_tasks.get(task_id)
        if task_dir is None:
            missing.append(f"{task_id}: missing source task")
            continue
        pin_path = task_dir / "hidden" / "PinCheck.lean"
        if not pin_path.exists():
            missing.append(f"{task_id}: missing hidden/PinCheck.lean")
            continue
        pin_text = pin_path.read_text(encoding="utf-8")
        tasks[task_id] = {
            "task_id": task_id,
            "split": row.get("split", ""),
            "acceptance_status": row.get("acceptance_status", ""),
            "pincheck_lean": pin_text,
            "pincheck_sha256": sha256_text(pin_text),
        }
    if missing:
        raise RuntimeError("cannot build hidden bundle: " + "; ".join(missing))
    return {
        "schema_version": 1,
        "bundle_role": "taiga_runtime_hidden_pin_bundle",
        "not_public_artifact": True,
        "task_count": len(tasks),
        "task_statuses": sorted(statuses),
        "tasks": tasks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "tmp" / "taiga_hidden_bundle.json")
    parser.add_argument("--status", action="append", dest="statuses")
    args = parser.parse_args()

    statuses = set(args.statuses or DEFAULT_STATUSES)
    bundle = build_bundle(statuses)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out} with {bundle['task_count']} hidden pin entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
