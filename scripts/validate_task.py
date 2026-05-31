from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(ROOT / "harness"))
from forbidden_constructs import find_forbidden, load_forbidden  # noqa: E402


def run(cmd: list[str], cwd: Path, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    existing = env.get("LEAN_PATH", "")
    env["LEAN_PATH"] = str(cwd) + (os.pathsep + existing if existing else "")
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        env=env,
    )


def load_metadata(task_dir: Path) -> dict:
    path = task_dir / "metadata.json"
    if not path.exists():
        raise FileNotFoundError(f"missing metadata: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def copy_submission(task_dir: Path, submission: Path, tmp: Path) -> None:
    shutil.copyfile(submission, tmp / "Task.lean")
    pin = task_dir / "hidden" / "PinCheck.lean"
    if not pin.exists():
        raise FileNotFoundError(f"missing hidden pin check: {pin}")
    shutil.copyfile(pin, tmp / "PinCheck.lean")


def check_forbidden(path: Path, metadata_path: Path) -> list[dict[str, object]]:
    src = path.read_text(encoding="utf-8")
    return find_forbidden(src, load_forbidden(metadata_path))


def audit_axioms(tmp: Path, declarations: list[str]) -> tuple[bool, str]:
    lines = ["import Task", "set_option pp.all false"]
    for decl in declarations:
        lines.append(f"#print axioms {decl}")
    audit_file = tmp / "AxiomAudit.lean"
    audit_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = run(["lake", "env", "lean", "AxiomAudit.lean"], cwd=tmp)
    if result.returncode != 0:
        return False, result.stdout

    bad: list[str] = []
    for line in result.stdout.splitlines():
        if "depends on axioms:" not in line:
            continue
        axiom_text = line.split("depends on axioms:", 1)[1].strip()
        if axiom_text in {"[]", ""}:
            continue
        names = [x.strip().strip("[]") for x in axiom_text.strip("[]").split(",") if x.strip()]
        for name in names:
            if name not in ALLOWED_AXIOMS:
                bad.append(name)
    if bad:
        return False, "Disallowed axioms: " + ", ".join(sorted(set(bad))) + "\n" + result.stdout
    return True, result.stdout


def validate_submission(task_dir: Path, submission: Path, expect_pass: bool) -> dict:
    metadata = load_metadata(task_dir)
    metadata_path = task_dir / "metadata.json"
    with tempfile.TemporaryDirectory(prefix=f"{metadata['task_id']}-", dir=ROOT / "tmp") as td:
        tmp = Path(td)
        copy_submission(task_dir, submission, tmp)

        forbidden = check_forbidden(tmp / "Task.lean", metadata_path)
        if forbidden:
            ok = False
            detail = json.dumps({"forbidden": forbidden}, indent=2)
        else:
            build = run(
                ["lake", "env", "lean", "-o", "Task.olean", "-i", "Task.ilean", "Task.lean"],
                cwd=tmp,
                timeout=metadata.get("timeout_seconds", 60),
            )
            if build.returncode != 0:
                ok = False
                detail = build.stdout
            else:
                pins = run(
                    ["lake", "env", "lean", "-o", "PinCheck.olean", "-i", "PinCheck.ilean", "PinCheck.lean"],
                    cwd=tmp,
                    timeout=metadata.get("timeout_seconds", 60),
                )
                if pins.returncode != 0:
                    ok = False
                    detail = pins.stdout
                else:
                    ok, detail = audit_axioms(tmp, metadata.get("axiom_audit_declarations", []))

    return {
        "task_id": metadata["task_id"],
        "submission": str(submission),
        "expected": "pass" if expect_pass else "fail",
        "ok": ok,
        "accepted": ok == expect_pass,
        "detail": detail,
    }


def write_result_row(path: Path, metadata: dict, ok: bool, submission_kind: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "task_id",
                "split",
                "family",
                "scaffold",
                "model",
                "model_version",
                "job_id",
                "attempts_total",
                "attempts_completed",
                "successes_out_of_10",
                "timeout_count",
                "infra_fail_count",
                "score_values",
                "transcript_link",
                "failure_label",
                "qa_stage",
                "qa_findings_status",
            ],
        )
        if not exists:
            writer.writeheader()
        writer.writerow(
            {
                "task_id": metadata["task_id"],
                "split": metadata["split"],
                "family": metadata["family"],
                "scaffold": "one-shot",
                "model": submission_kind,
                "model_version": "lean-4.28.0",
                "job_id": f"local-{submission_kind}-{metadata['task_id']}",
                "attempts_total": 1,
                "attempts_completed": 1,
                "successes_out_of_10": 10 if ok else 0,
                "timeout_count": 0,
                "infra_fail_count": 0,
                "score_values": "1.0" if ok else "0.0",
                "transcript_link": f"local/{submission_kind}/{metadata['task_id']}",
                "failure_label": "none" if ok else "hidden_pin_failure",
                "qa_stage": "local_qa",
                "qa_findings_status": "passed" if ok else "failed",
            }
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_dir", type=Path)
    parser.add_argument("--submission", type=Path)
    parser.add_argument("--expect", choices=["pass", "fail"], default="pass")
    parser.add_argument("--record", type=Path)
    parser.add_argument("--kind", default="manual")
    args = parser.parse_args()

    task_dir = args.task_dir.resolve()
    submission = (args.submission or (task_dir / "hidden" / "Reference.lean")).resolve()
    result = validate_submission(task_dir, submission, args.expect == "pass")
    print(json.dumps({k: v for k, v in result.items() if k != "detail"}, indent=2))
    if not result["accepted"]:
        print(result["detail"])
    if args.record:
        write_result_row(args.record, load_metadata(task_dir), result["ok"], args.kind)
    return 0 if result["accepted"] else 1


if __name__ == "__main__":
    sys.exit(main())
