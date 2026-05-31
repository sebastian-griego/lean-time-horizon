from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(ROOT / "scripts"))
from validate_task import validate_submission  # noqa: E402


FIELDS = [
    "task_id",
    "split",
    "family",
    "scaffold",
    "model",
    "model_version",
    "job_id",
    "attempts_total",
    "attempts_completed",
    "k",
    "successes_out_of_k",
    "pass_at_k",
    "timeout_count",
    "infra_fail_count",
    "score_values",
    "transcript_link",
    "failure_label",
    "qa_stage",
    "qa_findings_status",
]


def discover_tasks() -> list[Path]:
    tasks: list[Path] = []
    for split in ["dev", "test", "candidates"]:
        base = ROOT / "tasks" / split
        if base.exists():
            tasks.extend(sorted(p for p in base.iterdir() if (p / "metadata.json").exists()))
    return tasks


def row(metadata: dict, model: str, ok: bool, failure_label: str) -> dict[str, object]:
    return {
        "task_id": metadata["task_id"],
        "split": metadata["split"],
        "family": metadata["family"],
        "scaffold": "one-shot",
        "model": model,
        "model_version": "lean-4.28.0-local",
        "job_id": f"local-qa-{model}-{metadata['task_id']}",
        "attempts_total": 1,
        "attempts_completed": 1,
        "k": 1,
        "successes_out_of_k": 1 if ok else 0,
        "pass_at_k": "1.0" if ok else "0.0",
        "timeout_count": 0,
        "infra_fail_count": 0,
        "score_values": "1.0" if ok else "0.0",
        "transcript_link": f"transcripts/local-qa/{metadata['task_id']}.jsonl",
        "failure_label": failure_label,
        "qa_stage": "local_qa",
        "qa_findings_status": "passed" if ok else "expected_failure",
    }


def main() -> int:
    rows: list[dict[str, object]] = []
    transcript_dir = ROOT / "transcripts" / "local-qa"
    transcript_dir.mkdir(parents=True, exist_ok=True)
    for old in transcript_dir.glob("*.jsonl"):
        old.unlink()
    for task in discover_tasks():
        metadata = json.loads((task / "metadata.json").read_text(encoding="utf-8"))
        ref = validate_submission(task, task / "hidden" / "Reference.lean", True)
        ref_row = row(metadata, "reference_solution", bool(ref["ok"]), "none" if ref["ok"] else "grader_false_negative")
        rows.append(ref_row)
        with (transcript_dir / f"{metadata['task_id']}.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "task_id": metadata["task_id"],
                "split": metadata["split"],
                "scaffold": "one-shot",
                "model": "reference_solution",
                "attempt_index": 1,
                "score": 1 if ref["ok"] else 0,
                "primary_failure_label": ref_row["failure_label"],
                "feedback_excerpt": "" if ref["ok"] else str(ref["detail"])[-1000:],
                "timestamp_utc": int(time.time()),
            }) + "\n")
        wrongs = sorted((task / "wrong").glob("*.lean"))
        for wrong in wrongs:
            wrong_result = validate_submission(task, wrong, False)
            failed_as_expected = not bool(wrong_result["ok"])
            wrong_row = row(
                metadata,
                f"plausible_wrong:{wrong.stem}",
                not failed_as_expected,
                "hidden_pin_failure" if failed_as_expected else "grader_false_negative",
            )
            rows.append(wrong_row)
            with (transcript_dir / f"{metadata['task_id']}.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "task_id": metadata["task_id"],
                    "split": metadata["split"],
                    "scaffold": "one-shot",
                    "model": f"plausible_wrong:{wrong.stem}",
                    "attempt_index": 1,
                    "score": 0 if failed_as_expected else 1,
                    "primary_failure_label": wrong_row["failure_label"],
                    "feedback_excerpt": str(wrong_result["detail"])[-1000:],
                    "timestamp_utc": int(time.time()),
                }) + "\n")

    out = ROOT / "data" / "run_results.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {out.relative_to(ROOT)} with {len(rows)} local QA rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
