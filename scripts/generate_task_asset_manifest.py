from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_STATUSES = {"accepted_v0", "calibration_only", "candidate_review_pending"}

FIELDS = [
    "task_id",
    "split",
    "acceptance_status",
    "family",
    "asset_role",
    "relative_path",
    "metadata_listed_public_file",
    "public_export_expected",
    "public_export_exists",
    "exists",
    "bytes",
    "sha256",
    "line_count",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_tasks() -> list[Path]:
    tasks: list[Path] = []
    for split in ["dev", "test", "candidates"]:
        base = ROOT / "tasks" / split
        if not base.exists():
            continue
        tasks.extend(sorted(path for path in base.iterdir() if (path / "metadata.json").exists()))
    return tasks


def export_path_for(task_dir: Path, relative_asset: str, public_export: Path | None) -> Path | None:
    if public_export is None:
        return None
    return public_export.resolve() / task_dir.relative_to(ROOT / "tasks") / relative_asset


def asset_row(
    task_dir: Path,
    metadata: dict,
    asset_role: str,
    relative_asset: str,
    listed_public: bool,
    public_export: Path | None,
) -> dict[str, str]:
    asset_path = task_dir / relative_asset
    exists = asset_path.exists()
    release_task = metadata.get("acceptance_status") in RELEASE_STATUSES
    public_export_expected = release_task and asset_role in {"prompt", "metadata", "public"}
    exported = export_path_for(task_dir, relative_asset, public_export)
    public_export_exists = bool(exported and exported.exists())
    record = {
        "task_id": str(metadata.get("task_id", "")),
        "split": str(metadata.get("split", "")),
        "acceptance_status": str(metadata.get("acceptance_status", "")),
        "family": str(metadata.get("family", "")),
        "asset_role": asset_role,
        "relative_path": asset_path.relative_to(ROOT).as_posix(),
        "metadata_listed_public_file": str(listed_public).lower(),
        "public_export_expected": str(public_export_expected).lower(),
        "public_export_exists": str(public_export_exists).lower(),
        "exists": str(exists).lower(),
        "bytes": "",
        "sha256": "",
        "line_count": "",
    }
    if exists:
        record["bytes"] = str(asset_path.stat().st_size)
        record["sha256"] = sha256(asset_path)
        record["line_count"] = str(line_count(asset_path))
    return record


def build_rows(public_export: Path | None) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for task_dir in discover_tasks():
        metadata = read_json(task_dir / "metadata.json")
        public_files = list(dict.fromkeys(metadata.get("public_files", ["Task.lean"])))
        rows.append(asset_row(task_dir, metadata, "metadata", "metadata.json", False, public_export))
        rows.append(asset_row(task_dir, metadata, "prompt", "Prompt.md", False, public_export))
        for public_file in public_files:
            rows.append(asset_row(task_dir, metadata, "public", public_file, True, public_export))
        rows.append(asset_row(task_dir, metadata, "hidden_reference", "hidden/Reference.lean", False, public_export))
        rows.append(asset_row(task_dir, metadata, "hidden_pincheck", "hidden/PinCheck.lean", False, public_export))
        wrong_dir = task_dir / "wrong"
        for wrong_file in sorted(wrong_dir.glob("*.lean")) if wrong_dir.exists() else []:
            rows.append(asset_row(task_dir, metadata, "wrong_submission", wrong_file.relative_to(task_dir).as_posix(), False, public_export))
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row["acceptance_status"] for row in rows if row["asset_role"] == "metadata")
    role_counts = Counter(row["asset_role"] for row in rows)
    missing = [row for row in rows if row["exists"] != "true"]
    release_public = [row for row in rows if row["public_export_expected"] == "true"]
    missing_export = [row for row in release_public if row["public_export_exists"] != "true"]
    hidden_exported = [
        row for row in rows
        if row["asset_role"].startswith("hidden") or row["asset_role"] == "wrong_submission"
        if row["public_export_exists"] == "true"
    ]
    accepted_tasks = sorted({row["task_id"] for row in rows if row["acceptance_status"] == "accepted_v0"})
    wrong_counts = Counter(row["task_id"] for row in rows if row["asset_role"] == "wrong_submission")
    accepted_wrong_gaps = [task_id for task_id in accepted_tasks if wrong_counts.get(task_id, 0) < 2]
    accepted_hidden_ref_gaps = sorted({
        row["task_id"] for row in rows
        if row["acceptance_status"] == "accepted_v0" and row["asset_role"] == "hidden_reference" and row["exists"] != "true"
    })
    accepted_pin_gaps = sorted({
        row["task_id"] for row in rows
        if row["acceptance_status"] == "accepted_v0" and row["asset_role"] == "hidden_pincheck" and row["exists"] != "true"
    })

    accepted_lines = [
        "| task | public assets | wrong submissions | hidden reference | hidden pincheck |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for task_id in accepted_tasks:
        task_rows = [row for row in rows if row["task_id"] == task_id]
        public_count = sum(1 for row in task_rows if row["asset_role"] in {"metadata", "prompt", "public"})
        hidden_reference = next((row for row in task_rows if row["asset_role"] == "hidden_reference"), {})
        hidden_pincheck = next((row for row in task_rows if row["asset_role"] == "hidden_pincheck"), {})
        accepted_lines.append(
            f"| `{task_id}` | {public_count} | {wrong_counts.get(task_id, 0)} | "
            f"{hidden_reference.get('exists', 'missing')} | {hidden_pincheck.get('exists', 'missing')} |"
        )

    lines = [
        "# Task Asset Manifest",
        "",
        "This generated manifest records task-asset paths and hashes without embedding hidden proof contents. It supports reproducibility review, public-export checks, and future version-freeze decisions.",
        "",
        "## Summary",
        "",
        f"- task count: `{len({row['task_id'] for row in rows})}`",
        f"- asset rows: `{len(rows)}`",
        f"- task statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- asset roles: `{compact_json(dict(sorted(role_counts.items())))}`",
        f"- missing task assets: `{len(missing)}`",
        f"- release public assets missing from public export: `{len(missing_export)}`",
        f"- hidden/wrong assets present in public export: `{len(hidden_exported)}`",
        f"- accepted tasks with fewer than two wrong submissions: `{len(accepted_wrong_gaps)}`",
        f"- accepted hidden reference gaps: `{len(accepted_hidden_ref_gaps)}`",
        f"- accepted hidden pincheck gaps: `{len(accepted_pin_gaps)}`",
        "",
        "## Accepted Task Asset Coverage",
        "",
        "\n".join(accepted_lines),
        "",
        "## Hash Ledger",
        "",
        "The full CSV at `data/task_asset_manifest.csv` contains one row per asset with byte count, line count, and SHA-256 hash. Hidden proof and pin contents are not copied into this report.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-export", type=Path, default=None)
    args = parser.parse_args()
    public_export = args.public_export.resolve() if args.public_export else None
    rows = build_rows(public_export)
    write_csv(ROOT / "data" / "task_asset_manifest.csv", rows)
    write_markdown(ROOT / "reports" / "task_asset_manifest.md", rows)
    print(f"wrote data/task_asset_manifest.csv and reports/task_asset_manifest.md with {len(rows)} asset rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
