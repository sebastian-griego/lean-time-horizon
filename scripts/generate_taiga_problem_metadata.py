from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATUSES = {"accepted_v0", "calibration_only"}
PLACEHOLDER_IMAGE = "REPLACE_WITH_IMMUTABLE_TAIGA_IMAGE_DIGEST"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_problem(row: dict[str, str], image: str) -> dict[str, object]:
    task_id = row["task_id"]
    return {
        "image": image,
        "startup_command": "python -u /workspace/lean-time-horizon/taiga/mcp_server.py",
        "id": task_id,
        "required_tools": ["bash", "str_replace_editor"],
        "scratchpad": "allowed",
        "enabled_package_managers": [],
        "tool_timeout_seconds": 600,
        "setup_timeout_seconds": 300,
        "startup_timeout_seconds": 1800,
        "grading_timeout_seconds": max(900, int(row.get("human_minutes_p90", "0") or 0) * 60),
        "output_directory": f"/workdir/out/{task_id}",
        "metadata": {
            "task_id": task_id,
            "split": row.get("split", ""),
            "family": row.get("family", ""),
            "domain": row.get("domain", ""),
            "acceptance_status": row.get("acceptance_status", ""),
            "human_time_bucket": row.get("human_time_bucket", ""),
            "human_minutes_p50": row.get("human_minutes_p50", ""),
            "human_minutes_p90": row.get("human_minutes_p90", ""),
            "public_export_path": f"public_tasks/{row.get('split', '')}/{task_id}",
        },
    }


def build_metadata(rows: list[dict[str, str]], image: str, owner: str, name: str) -> dict[str, object]:
    selected = [row for row in rows if row.get("acceptance_status") in DEFAULT_STATUSES]
    selected.sort(key=lambda row: (row.get("split", ""), row.get("task_id", "")))
    return {
        "problem_set": {
            "owner": owner,
            "name": name,
            "description": (
                "Lean time-horizon v0.1 public task export. This file is a generated "
                "Taiga problems-metadata template and is not hosted QA evidence until "
                "PLACEHOLDER image values are replaced by immutable uploaded image digests "
                "and Taiga problem-version IDs are committed separately."
            ),
            "version": "0.1-template",
            "created_at": datetime(2026, 6, 1, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
            "metadata": {
                "repo_artifact": "lean-time-horizon",
                "template_status": "not_uploaded",
                "public_export": "public_tasks",
                "task_statuses": sorted(DEFAULT_STATUSES),
            },
            "problems": [build_problem(row, image) for row in selected],
        }
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "taiga" / "problems_metadata.template.json")
    parser.add_argument("--image", default=PLACEHOLDER_IMAGE)
    parser.add_argument("--owner", default="sebas")
    parser.add_argument("--name", default="lean-time-horizon-v0-1")
    args = parser.parse_args()

    metadata_rows = read_csv(ROOT / "data" / "task_metadata.csv")
    payload = build_metadata(metadata_rows, args.image, args.owner, args.name)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out} with {len(payload['problem_set']['problems'])} problems")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
