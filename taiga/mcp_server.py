from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Any

REPO_ROOT = Path(os.environ.get("LEAN_TIME_HORIZON_ROOT", Path(__file__).resolve().parents[1]))
DEFAULT_WORKDIR = Path("/workdir") if os.name != "nt" else REPO_ROOT / "tmp" / "taiga_workdir"
WORKDIR = Path(os.environ.get("TAIGA_WORKDIR", DEFAULT_WORKDIR))
PUBLIC_TASKS = REPO_ROOT / "public_tasks"
HIDDEN_BUNDLE_PATH = Path(os.environ.get("TAIGA_HIDDEN_BUNDLE", "/opt/lean-time-horizon-private/hidden_bundle.json"))
DELETE_HIDDEN_BUNDLE = os.environ.get("TAIGA_DELETE_HIDDEN_BUNDLE", "1") != "0"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from validate_task import (  # noqa: E402
    audit_axioms,
    check_forbidden,
    load_metadata,
    metadata_entry_file,
    metadata_public_files,
    metadata_submission_file,
    module_name,
    run,
    validate_submission,
)


FENCE_RE = re.compile(r"```(?:lean|lean4)?\s*\n(?P<code>.*?)```", re.IGNORECASE | re.DOTALL)


def _load_hidden_bundle() -> dict[str, str]:
    if not HIDDEN_BUNDLE_PATH.exists():
        return {}
    payload = json.loads(HIDDEN_BUNDLE_PATH.read_text(encoding="utf-8"))
    tasks = payload.get("tasks", {})
    pins = {
        str(task_id): str(task_data.get("pincheck_lean", ""))
        for task_id, task_data in tasks.items()
        if isinstance(task_data, dict) and task_data.get("pincheck_lean")
    }
    if DELETE_HIDDEN_BUNDLE:
        HIDDEN_BUNDLE_PATH.unlink(missing_ok=True)
    return pins


HIDDEN_PINCHECKS = _load_hidden_bundle()


def _metadata_paths(base: Path) -> list[Path]:
    if not base.exists():
        return []
    return sorted(base.rglob("metadata.json"))


def _find_task_dir(task_id: str, base: Path) -> Path:
    for metadata_path in _metadata_paths(base):
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if metadata.get("task_id") == task_id:
            return metadata_path.parent
    raise FileNotFoundError(f"unknown task_id {task_id!r} under {base}")


def _source_task_dir(task_id: str) -> Path:
    for split in ("dev", "test", "candidates"):
        base = REPO_ROOT / "tasks" / split
        if not base.exists():
            continue
        try:
            return _find_task_dir(task_id, base)
        except FileNotFoundError:
            continue
    raise FileNotFoundError(f"unknown source task_id {task_id!r}")


def _public_task_dir(task_id: str) -> Path:
    return _find_task_dir(task_id, PUBLIC_TASKS)


def _problem_workdir(task_id: str) -> Path:
    return WORKDIR / "problems" / task_id


def _copy_public_task(task_id: str) -> tuple[Path, dict[str, Any]]:
    public_dir = _public_task_dir(task_id)
    metadata = load_metadata(public_dir)
    dest = _problem_workdir(task_id)
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    for name in ["Prompt.md", "metadata.json", *metadata_public_files(metadata)]:
        src = public_dir / name
        target = dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
    return dest, metadata


def _validate_with_hidden_pin_bundle(public_dir: Path, submission: Path, pincheck_text: str) -> dict[str, Any]:
    metadata = load_metadata(public_dir)
    metadata_path = public_dir / "metadata.json"
    tmp_root = WORKDIR / "grader_tmp"
    tmp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"{metadata['task_id']}-", dir=tmp_root) as td:
        tmp = Path(td)
        for public_file in metadata_public_files(metadata):
            src = public_dir / public_file
            dest = tmp / public_file
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
        submission_dest = tmp / metadata_submission_file(metadata)
        submission_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(submission, submission_dest)
        (tmp / "PinCheck.lean").write_text(pincheck_text, encoding="utf-8")

        forbidden = check_forbidden(submission_dest, metadata_path)
        if forbidden:
            ok = False
            detail = json.dumps({"forbidden": forbidden}, indent=2)
        else:
            build_outputs: list[str] = []
            build_failed = False
            files_to_build = list(dict.fromkeys([*metadata_public_files(metadata), metadata_entry_file(metadata)]))
            for lean_file in files_to_build:
                path = tmp / lean_file
                build = run(
                    [
                        "lake",
                        "env",
                        "lean",
                        "-o",
                        str(path.with_suffix(".olean")),
                        "-i",
                        str(path.with_suffix(".ilean")),
                        str(path),
                    ],
                    cwd=REPO_ROOT,
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
                    cwd=REPO_ROOT,
                    timeout=metadata.get("timeout_seconds", 60),
                    lean_path_dir=tmp,
                )
                if pins.returncode != 0:
                    ok = False
                    detail = pins.stdout
                else:
                    ok, detail = audit_axioms(
                        tmp,
                        module_name(metadata_entry_file(metadata)),
                        metadata.get("axiom_audit_declarations", []),
                    )
    return {
        "task_id": metadata["task_id"],
        "submission": str(submission),
        "expected": "pass",
        "ok": ok,
        "accepted": ok,
        "detail": detail,
    }


def setup_problem(problem_id: str, use_hinted_problem: bool = False, extra_fields: dict[str, Any] | None = None) -> dict[str, Any]:
    task_dir, metadata = _copy_public_task(problem_id)
    submission_file = metadata_submission_file(metadata)
    prompt = (task_dir / "Prompt.md").read_text(encoding="utf-8", errors="replace")
    public_files = ", ".join(metadata_public_files(metadata))
    instructions = f"""

You are working on Lean task `{problem_id}`.

The public task files have been copied to `{task_dir}`.
Editable submission file: `{task_dir / submission_file}`.
Public files: {public_files}.

Use the available shell/editor tools to edit the submission file. The grader will
run the repository Lean validator with hidden checks that are not present in this
directory. Do not use forbidden constructs, axioms outside the documented policy,
or hidden-material assumptions.
"""
    return {
        "prompt": prompt + instructions,
        "metadata": {
            "task_id": problem_id,
            "workdir": str(task_dir),
            "submission_file": submission_file,
            "use_hinted_problem": use_hinted_problem,
            "extra_fields": extra_fields or {},
        },
    }


def _last_fenced_lean(transcript: str) -> str | None:
    matches = list(FENCE_RE.finditer(transcript or ""))
    if not matches:
        return None
    return matches[-1].group("code").strip() + "\n"


def _submission_from_workdir_or_transcript(task_id: str, metadata: dict[str, Any], transcript: str) -> tuple[Path, str]:
    submission = _problem_workdir(task_id) / metadata_submission_file(metadata)
    if submission.exists():
        return submission, "workdir_file"
    code = _last_fenced_lean(transcript)
    if code is None:
        raise FileNotFoundError(
            f"no submission file found at {submission} and no fenced Lean block was present in transcript"
        )
    extracted = WORKDIR / "extracted_submissions" / task_id / metadata_submission_file(metadata)
    extracted.parent.mkdir(parents=True, exist_ok=True)
    extracted.write_text(code, encoding="utf-8")
    return extracted, "transcript_fence"


def grade_problem(problem_id: str, transcript: str, extra_fields: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        public_dir = _public_task_dir(problem_id)
        metadata = load_metadata(public_dir)
        submission, submission_source = _submission_from_workdir_or_transcript(problem_id, metadata, transcript)
        if problem_id in HIDDEN_PINCHECKS:
            result = _validate_with_hidden_pin_bundle(public_dir, submission, HIDDEN_PINCHECKS[problem_id])
            hidden_bundle_used = True
        else:
            source_dir = _source_task_dir(problem_id)
            result = validate_submission(source_dir, submission, expect_pass=True)
            hidden_bundle_used = False
        ok = bool(result["ok"])
        return {
            "subscores": {"lean_validation": 1.0 if ok else 0.0},
            "weights": {"lean_validation": 1.0},
            "metadata": {
                "task_id": problem_id,
                "submission": str(submission),
                "submission_source": submission_source,
                "hidden_bundle_used": hidden_bundle_used,
                "accepted": bool(result["accepted"]),
                "validator_ok": ok,
                "detail_excerpt": str(result.get("detail", ""))[:4000],
                "extra_fields": extra_fields or {},
            },
            "env_internal_failure": False,
            "env_internal_failure_logs": None,
            "penalties": None,
            "allow_unbounded": False,
        }
    except Exception as exc:  # pragma: no cover - defensive hosted wrapper path
        return {
            "subscores": {"lean_validation": 0.0},
            "weights": {"lean_validation": 1.0},
            "metadata": {"task_id": problem_id, "error": repr(exc), "extra_fields": extra_fields or {}},
            "env_internal_failure": True,
            "env_internal_failure_logs": traceback.format_exc().splitlines(),
            "penalties": None,
            "allow_unbounded": False,
        }


def _dispatch(request: dict[str, Any]) -> dict[str, Any]:
    method = request.get("method")
    params = request.get("params") or {}
    if method == "initialize":
        result = {
            "name": "lean-time-horizon-taiga-wrapper",
            "capabilities": ["setup_problem", "grade_problem"],
        }
    elif method == "setup_problem":
        result = setup_problem(
            str(params["problem_id"]),
            bool(params.get("use_hinted_problem", False)),
            params.get("extra_fields") or {},
        )
    elif method == "grade_problem":
        result = grade_problem(
            str(params["problem_id"]),
            str(params.get("transcript", "")),
            params.get("extra_fields") or {},
        )
    elif method == "list_problems":
        result = {
            "problem_ids": [
                json.loads(path.read_text(encoding="utf-8")).get("task_id")
                for path in _metadata_paths(PUBLIC_TASKS)
            ]
        }
    else:
        raise ValueError(f"unknown method {method!r}")
    return {"jsonrpc": "2.0", "id": request.get("id"), "result": result}


def main() -> int:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            response = _dispatch(json.loads(line))
        except Exception as exc:  # pragma: no cover - defensive stdio path
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"message": repr(exc), "traceback": traceback.format_exc().splitlines()},
            }
        print(json.dumps(response), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
