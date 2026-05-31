from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

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

PROVIDER_COMMAND_ENV = {
    "openai": "OPENAI_LEAN_RUNNER",
    "anthropic": "ANTHROPIC_LEAN_RUNNER",
    "gemini": "GEMINI_LEAN_RUNNER",
    "command": "LEAN_MODEL_RUNNER",
}


def discover_tasks(split: str | None, task_id: str | None) -> list[Path]:
    tasks: list[Path] = []
    splits = [split] if split else ["dev", "test", "candidates"]
    for sp in splits:
        base = ROOT / "tasks" / sp
        if base.exists():
            tasks.extend(sorted(p for p in base.iterdir() if (p / "metadata.json").exists()))
    if task_id:
        tasks = [p for p in tasks if json.loads((p / "metadata.json").read_text(encoding="utf-8"))["task_id"] == task_id]
    return tasks


def build_prompt(task: Path, scaffold: str, feedback: str = "") -> str:
    metadata = json.loads((task / "metadata.json").read_text(encoding="utf-8"))
    prompt = (task / "Prompt.md").read_text(encoding="utf-8")
    scaffold_text = {
        "one-shot": "One submission. No lookup tools are available.",
        "lookup": "One submission. Read-only Lean/Std lookup is available.",
        "lookup_unlimited": "Iterative compile/debug attempts are available; use feedback from previous attempts.",
    }[scaffold]
    public_parts = []
    for public_file in metadata.get("public_files", ["Task.lean"]):
        public_parts.extend([
            f"File: {public_file}",
            "```lean",
            (task / public_file).read_text(encoding="utf-8"),
            "```",
            "",
        ])
    parts = [
        prompt,
        "",
        f"Scaffold: {scaffold}",
        scaffold_text,
        "",
        f"Return the complete contents of {metadata.get('submission_file', 'Task.lean')} only.",
        "",
        *public_parts,
    ]
    if feedback:
        parts.extend(["", "Previous grader feedback:", "```text", feedback[-4000:], "```"])
    return "\n".join(parts)


def call_provider(provider: str, model: str, prompt: str, task: Path, job_dir: Path, attempt: int) -> str:
    if provider == "local_reference":
        return (task / "hidden" / "Reference.lean").read_text(encoding="utf-8")
    env_name = PROVIDER_COMMAND_ENV.get(provider)
    if not env_name:
        raise ValueError(f"unknown provider: {provider}")
    command = os.environ.get(env_name)
    if not command:
        raise RuntimeError(
            f"{provider} adapter expects {env_name} to name an executable command. "
            "The command receives PROMPT_PATH, MODEL, TASK_ID, and ATTEMPT_INDEX in the environment "
            "and must print a complete Lean file to stdout."
        )
    prompt_path = job_dir / f"attempt-{attempt}-prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")
    metadata = json.loads((task / "metadata.json").read_text(encoding="utf-8"))
    env = os.environ.copy()
    env.update(
        {
            "PROMPT_PATH": str(prompt_path),
            "MODEL": model,
            "TASK_ID": metadata["task_id"],
            "ATTEMPT_INDEX": str(attempt),
        }
    )
    proc = subprocess.run(command, shell=True, text=True, encoding="utf-8", errors="replace", env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout)
    return proc.stdout


def classify_failure(detail: str) -> str:
    if "forbidden" in detail:
        return "reward_hack_attempt"
    if "PinCheck" in detail:
        return "hidden_pin_failure"
    if "unknown constant" in detail or "unknown identifier" in detail:
        return "library_search"
    if "unsolved goals" in detail or "tactic" in detail:
        return "proof_debugging"
    return "proof_debugging"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["local_reference", "command", "openai", "anthropic", "gemini"], required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--scaffold", choices=["one-shot", "lookup", "lookup_unlimited"], required=True)
    parser.add_argument("--split", choices=["dev", "test", "candidates"])
    parser.add_argument("--task-id")
    parser.add_argument("--attempts", type=int, default=1)
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "run_results.csv")
    args = parser.parse_args()

    tasks = discover_tasks(args.split, args.task_id)
    job_id = f"{args.provider}-{args.model}-{args.scaffold}-{int(time.time())}".replace("/", "_")
    transcript_root = ROOT / "transcripts" / job_id
    transcript_root.mkdir(parents=True, exist_ok=True)
    rows = []

    for task in tasks:
        metadata = json.loads((task / "metadata.json").read_text(encoding="utf-8"))
        successes = 0
        completed = 0
        labels: list[str] = []
        feedback = ""
        transcript_path = transcript_root / f"{metadata['task_id']}.jsonl"
        attempts_allowed = args.attempts if args.scaffold == "lookup_unlimited" else min(args.attempts, 1)
        with tempfile.TemporaryDirectory(prefix=f"{metadata['task_id']}-", dir=ROOT / "tmp") as td:
            job_dir = Path(td)
            for attempt in range(1, attempts_allowed + 1):
                prompt = build_prompt(task, args.scaffold, feedback)
                try:
                    solution = call_provider(args.provider, args.model, prompt, task, job_dir, attempt)
                    submission = job_dir / f"attempt-{attempt}.lean"
                    submission.write_text(solution, encoding="utf-8")
                    result = validate_submission(task, submission, True)
                    completed += 1
                    if result["ok"]:
                        successes += 1
                        label = "none"
                        feedback = ""
                    else:
                        feedback = str(result["detail"])
                        label = classify_failure(feedback)
                    labels.append(label)
                except Exception as exc:
                    completed += 1
                    label = "infra_failure"
                    feedback = str(exc)
                    labels.append(label)
                with transcript_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps({
                        "task_id": metadata["task_id"],
                        "split": metadata["split"],
                        "scaffold": args.scaffold,
                        "model": args.model,
                        "attempt_index": attempt,
                        "score": 1 if labels[-1] == "none" else 0,
                        "primary_failure_label": labels[-1],
                        "feedback_excerpt": feedback[-1000:],
                        "timestamp_utc": int(time.time()),
                    }) + "\n")
                if labels[-1] == "none":
                    break

        rows.append(
            {
                "task_id": metadata["task_id"],
                "split": metadata["split"],
                "family": metadata["family"],
                "scaffold": args.scaffold,
                "model": args.provider,
                "model_version": args.model,
                "job_id": job_id,
                "attempts_total": attempts_allowed,
                "attempts_completed": completed,
                "k": attempts_allowed,
                "successes_out_of_k": successes,
                "pass_at_k": f"{(1.0 if successes > 0 else 0.0):.1f}",
                "timeout_count": 0,
                "infra_fail_count": labels.count("infra_failure"),
                "score_values": ",".join("1" if label == "none" else "0" for label in labels),
                "transcript_link": str(transcript_path.relative_to(ROOT)),
                "failure_label": "none" if any(label == "none" for label in labels) else (labels[-1] if labels else "infra_failure"),
                "qa_stage": "model_sweep",
                "qa_findings_status": "unreviewed",
            }
        )

    exists = args.out.exists()
    with args.out.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
