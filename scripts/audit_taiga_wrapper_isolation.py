from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "check_id",
    "area",
    "status",
    "evidence",
    "limitation",
    "next_action",
]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def row(
    check_id: str,
    area: str,
    status: str,
    evidence: str,
    limitation: str,
    next_action: str,
) -> dict[str, str]:
    return {
        "check_id": check_id,
        "area": area,
        "status": status,
        "evidence": evidence,
        "limitation": limitation,
        "next_action": next_action,
    }


def read_bundle(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_bundle_smoke(bundle_path: Path, workdir: Path) -> dict[str, object]:
    child = r'''
import json
import os
import shutil
from pathlib import Path

root = Path(os.environ["LEAN_TIME_HORIZON_ROOT"])
bundle_path = Path(os.environ["TAIGA_HIDDEN_BUNDLE"])

import taiga.mcp_server as server

source_fallback_calls = []

def blocked_source_task_dir(task_id):
    source_fallback_calls.append(task_id)
    raise RuntimeError("source task fallback was accessed")

server._source_task_dir = blocked_source_task_dir

setup = server.setup_problem("lt-001")
workdir = Path(setup["metadata"]["workdir"])
public_hidden_or_wrong = [
    str(path.relative_to(workdir))
    for path in workdir.rglob("*")
    if "hidden" in path.parts or "wrong" in path.parts
]

fail_grade = server.grade_problem("lt-001", "")
shutil.copyfile(
    root / "tasks" / "dev" / "lt-001-sum-append" / "hidden" / "Reference.lean",
    workdir / "Task.lean",
)
pass_grade = server.grade_problem("lt-001", "")

print(json.dumps({
    "bundle_deleted": not bundle_path.exists(),
    "hidden_bundle_count": len(server.HIDDEN_PINCHECKS),
    "public_hidden_or_wrong_count": len(public_hidden_or_wrong),
    "public_hidden_or_wrong_examples": public_hidden_or_wrong[:5],
    "unedited_score": fail_grade["subscores"]["lean_validation"],
    "unedited_hidden_bundle_used": bool(fail_grade["metadata"].get("hidden_bundle_used")),
    "reference_score": pass_grade["subscores"]["lean_validation"],
    "reference_hidden_bundle_used": bool(pass_grade["metadata"].get("hidden_bundle_used")),
    "source_fallback_calls": source_fallback_calls,
}))
'''
    env = os.environ.copy()
    env["LEAN_TIME_HORIZON_ROOT"] = str(ROOT)
    env["TAIGA_HIDDEN_BUNDLE"] = str(bundle_path)
    env["TAIGA_DELETE_HIDDEN_BUNDLE"] = "1"
    env["TAIGA_WORKDIR"] = str(workdir)
    result = subprocess.run(
        [sys.executable, "-c", child],
        cwd=ROOT,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=180,
    )
    if result.returncode != 0:
        return {"returncode": result.returncode, "stdout": result.stdout}
    return json.loads(result.stdout)


def build_rows() -> list[dict[str, str]]:
    tmp = ROOT / "tmp" / "taiga_wrapper_isolation"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True, exist_ok=True)
    bundle_path = tmp / "hidden_bundle.json"
    workdir = tmp / "workdir"

    generate = subprocess.run(
        [
            sys.executable,
            "scripts/generate_taiga_hidden_bundle.py",
            "--out",
            str(bundle_path),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=120,
    )
    bundle = read_bundle(bundle_path) if bundle_path.exists() else {}
    tasks = bundle.get("tasks", {}) if isinstance(bundle.get("tasks"), dict) else {}
    bundle_entries = len(tasks)
    bundle_contains_reference = any("Reference.lean" in json.dumps(task_data) for task_data in tasks.values())
    bundle_contains_pincheck = all(
        isinstance(task_data, dict) and bool(task_data.get("pincheck_lean"))
        for task_data in tasks.values()
    )

    rows: list[dict[str, str]] = []
    rows.append(row(
        "hidden_bundle_generation",
        "bundle_generation",
        "pass" if generate.returncode == 0 and bundle_entries == 14 and bundle_contains_pincheck and not bundle_contains_reference else "fail",
        (
            f"returncode={generate.returncode}; bundle_entries={bundle_entries}; "
            f"bundle_contains_pincheck={bundle_contains_pincheck}; bundle_contains_reference={bundle_contains_reference}; "
            f"stdout={generate.stdout.strip()[:240]}"
        ),
        "This checks the committed local bundle generator, not a built uploaded container image.",
        "Keep the bundle limited to hidden PinCheck text and verify count changes whenever public release tasks change.",
    ))

    smoke = run_bundle_smoke(bundle_path, workdir) if bundle_path.exists() else {"missing_bundle": True}
    smoke_ok = (
        smoke.get("bundle_deleted") is True
        and smoke.get("hidden_bundle_count") == 14
        and smoke.get("public_hidden_or_wrong_count") == 0
        and smoke.get("unedited_score") == 0.0
        and smoke.get("reference_score") == 1.0
        and smoke.get("unedited_hidden_bundle_used") is True
        and smoke.get("reference_hidden_bundle_used") is True
        and smoke.get("source_fallback_calls") == []
    )
    rows.append(row(
        "bundle_runtime_grading_smoke",
        "wrapper_runtime",
        "pass" if smoke_ok else "fail",
        compact_json(smoke),
        "This is a local subprocess smoke test. It proves the wrapper can use the bundle path without source-task fallback, but it is not hosted filesystem-tool isolation evidence.",
        "Run Taiga preflight and Env Linter on the uploaded image to prove the model cannot inspect hidden material.",
    ))

    docker = (ROOT / "taiga" / "Dockerfile").read_text(encoding="utf-8", errors="replace")
    mcp = (ROOT / "taiga" / "mcp_server.py").read_text(encoding="utf-8", errors="replace")
    static_ok = (
        "generate_taiga_hidden_bundle.py" in docker
        and "rm -rf tasks transcripts tmp" in docker
        and "TAIGA_HIDDEN_BUNDLE" in docker
        and "HIDDEN_BUNDLE_PATH.unlink" in mcp
        and "_validate_with_hidden_pin_bundle" in mcp
    )
    rows.append(row(
        "docker_static_isolation_controls",
        "static_packaging",
        "pass" if static_ok else "fail",
        (
            f"bundle_generation_in_docker={'generate_taiga_hidden_bundle.py' in docker}; "
            f"task_sources_removed={'rm -rf tasks transcripts tmp' in docker}; "
            f"bundle_env={'TAIGA_HIDDEN_BUNDLE' in docker}; "
            f"bundle_deleted_on_import={'HIDDEN_BUNDLE_PATH.unlink' in mcp}; "
            f"bundle_validator={'_validate_with_hidden_pin_bundle' in mcp}"
        ),
        "Static controls can drift from hosted runtime behavior and do not replace uploaded-image inspection.",
        "Keep this audit passing and add hosted evidence rows after upload.",
    ))
    return rows


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    status_counts = Counter(row_data["status"] for row_data in rows)
    area_counts = Counter(row_data["area"] for row_data in rows)
    lines = [
        "# Taiga Wrapper Isolation Audit",
        "",
        "This generated audit exercises the local Taiga wrapper hidden-bundle path. It is mitigation evidence only: hosted filesystem-tool isolation, image digest pinning, preflight, Full Env QA, and Env Linter evidence are still required before hosted-QA claims can be made.",
        "",
        "## Summary",
        "",
        f"- checks: `{len(rows)}`",
        f"- statuses: `{compact_json(dict(sorted(status_counts.items())))}`",
        f"- areas: `{compact_json(dict(sorted(area_counts.items())))}`",
        "",
        "## Check Table",
        "",
        "| check | area | status | evidence | limitation | next action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row_data in rows:
        lines.append(
            f"| `{row_data['check_id']}` | {row_data['area']} | {row_data['status']} | "
            f"{row_data['evidence'].replace('|', '/')} | {row_data['limitation'].replace('|', '/')} | "
            f"{row_data['next_action'].replace('|', '/')} |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "`pass` means the local wrapper mitigation is internally exercised. It does not mean hidden material is unreachable to a model in Taiga; that requires hosted preflight and Env Linter evidence on the exact uploaded image/problem versions.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    write_csv(ROOT / "data" / "taiga_wrapper_isolation_audit.csv", rows)
    write_markdown(ROOT / "reports" / "taiga_wrapper_isolation_audit.md", rows)
    failures = sum(1 for row_data in rows if row_data["status"] == "fail")
    print(
        "wrote data/taiga_wrapper_isolation_audit.csv and "
        f"reports/taiga_wrapper_isolation_audit.md with {len(rows)} checks; failures={failures}"
    )
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
