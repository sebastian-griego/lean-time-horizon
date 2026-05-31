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


def run(cmd: list[str], cwd: Path, timeout: int = 60, lean_path_dir: Path | None = None) -> subprocess.CompletedProcess[str]:
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
        timeout=timeout,
        env=env,
    )


def load_metadata(task_dir: Path) -> dict:
    path = task_dir / "metadata.json"
    if not path.exists():
        raise FileNotFoundError(f"missing metadata: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def metadata_public_files(metadata: dict) -> list[str]:
    return list(metadata.get("public_files", ["Task.lean"]))


def metadata_submission_file(metadata: dict) -> str:
    return str(metadata.get("submission_file", "Task.lean"))


def metadata_entry_file(metadata: dict) -> str:
    return str(metadata.get("entry_file", metadata_submission_file(metadata)))


def module_name(path: str) -> str:
    return Path(path).with_suffix("").as_posix().replace("/", ".")


def copy_submission(task_dir: Path, submission: Path, tmp: Path, metadata: dict) -> None:
    for public_file in metadata_public_files(metadata):
        src = task_dir / public_file
        dest = tmp / public_file
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not src.exists():
            raise FileNotFoundError(f"missing public file: {src}")
        shutil.copyfile(src, dest)
    submission_dest = tmp / metadata_submission_file(metadata)
    submission_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(submission, submission_dest)
    pin = task_dir / "hidden" / "PinCheck.lean"
    if not pin.exists():
        raise FileNotFoundError(f"missing hidden pin check: {pin}")
    shutil.copyfile(pin, tmp / "PinCheck.lean")


def check_forbidden(path: Path, metadata_path: Path) -> list[dict[str, object]]:
    src = path.read_text(encoding="utf-8")
    return find_forbidden(src, load_forbidden(metadata_path))


def audit_axioms(tmp: Path, import_module: str, declarations: list[str]) -> tuple[bool, str]:
    lines = [f"import {import_module}", "set_option pp.all false"]
    for decl in declarations:
        lines.append(f"#print axioms {decl}")
    audit_file = tmp / "AxiomAudit.lean"
    audit_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = run(["lake", "env", "lean", str(audit_file)], cwd=ROOT, lean_path_dir=tmp)
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
        copy_submission(task_dir, submission, tmp, metadata)
        submission_path = tmp / metadata_submission_file(metadata)
        entry_path = tmp / metadata_entry_file(metadata)
        entry_module = module_name(metadata_entry_file(metadata))

        forbidden = check_forbidden(submission_path, metadata_path)
        if forbidden:
            ok = False
            detail = json.dumps({"forbidden": forbidden}, indent=2)
        else:
            build_outputs: list[str] = []
            build_failed = False
            files_to_build = []
            for public_file in metadata_public_files(metadata):
                if public_file not in files_to_build:
                    files_to_build.append(public_file)
            if metadata_entry_file(metadata) not in files_to_build:
                files_to_build.append(metadata_entry_file(metadata))
            for lean_file in files_to_build:
                path = tmp / lean_file
                build = run(
                    ["lake", "env", "lean", "-o", str(path.with_suffix(".olean")), "-i", str(path.with_suffix(".ilean")), str(path)],
                    cwd=ROOT,
                    timeout=metadata.get("timeout_seconds", 60),
                    lean_path_dir=tmp,
                )
                build_outputs.append(build.stdout)
                if build.returncode != 0:
                    build_failed = True
                    break
            if build_failed:
                ok = False
                detail = "\n".join(build_outputs)
            else:
                pins = run(
                    [
                        "lake",
                        "env",
                        "lean",
                        "-o",
                        str((tmp / "PinCheck").with_suffix(".olean")),
                        "-i",
                        str((tmp / "PinCheck").with_suffix(".ilean")),
                        str(tmp / "PinCheck.lean"),
                    ],
                    cwd=ROOT,
                    timeout=metadata.get("timeout_seconds", 60),
                    lean_path_dir=tmp,
                )
                if pins.returncode != 0:
                    ok = False
                    detail = pins.stdout
                else:
                    ok, detail = audit_axioms(tmp, entry_module, metadata.get("axiom_audit_declarations", []))

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
                "k": 1,
                "successes_out_of_k": 1 if ok else 0,
                "pass_at_k": 1 if ok else 0,
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
