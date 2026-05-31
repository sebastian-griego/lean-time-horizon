from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TACTICS = [
    "rfl",
    "simp",
    "omega",
    "cases",
    "induction",
    "rw",
    "exact",
    "unfold",
    "split",
    "constructor",
    "intro",
    "rcases",
    "ext",
    "aesop",
]


def discover_tasks() -> list[Path]:
    tasks: list[Path] = []
    for split in ["dev", "test", "candidates"]:
        base = ROOT / "tasks" / split
        if base.exists():
            tasks.extend(sorted(p for p in base.iterdir() if (p / "metadata.json").exists()))
    return tasks


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def proof_text(reference: str) -> str:
    lines = []
    in_proof = False
    for line in reference.splitlines():
        stripped = line.strip()
        if re.match(r"^(theorem|lemma)\b", stripped):
            in_proof = True
        if in_proof:
            lines.append(line)
    return "\n".join(lines)


def count_reference_lines(reference: str) -> int:
    text = proof_text(reference)
    return sum(1 for line in text.splitlines() if line.strip() and not line.strip().startswith("--"))


def tactic_profile(reference: str) -> Counter[str]:
    text = proof_text(reference)
    counts: Counter[str] = Counter()
    for tactic in TACTICS:
        counts[tactic] = len(re.findall(rf"\b{re.escape(tactic)}\b", text))
    return Counter({k: v for k, v in counts.items() if v})


def declaration_count(text: str) -> int:
    return len(re.findall(r"^\s*(def|theorem|lemma|structure|inductive)\b", text, flags=re.MULTILINE))


def capability_flags(metadata: dict) -> dict[str, bool]:
    skills = " ".join(metadata.get("skills", [])).lower()
    family = metadata.get("family", "")
    public_files = metadata.get("public_files", ["Task.lean"])
    return {
        "requires_library_search": "library search" in skills or "mathlib" in skills or family == "direct_theorem_proving",
        "requires_decomposition": any(s in skills for s in ["induction", "recursive", "library construction", "decomposition", "helper"]),
        "requires_semantic_formalization": family == "informal_spec_to_formal" or "semantic formalization" in skills,
        "requires_proof_debugging": "debug" in skills or "repair" in family,
        "requires_codebase_navigation": family == "proof_repair_codebase" or "codebase navigation" in skills or len(public_files) > 1,
        "requires_invariant_design": family == "invariant_verification_ml_optimization" or "invariant design" in skills,
        "requires_long_horizon_construction": "library construction" in skills or "helper lemma" in skills or family == "small_formal_library_construction",
    }


def hidden_pin_assessment(task_dir: Path) -> tuple[str, int, int]:
    pins = read_text(task_dir / "hidden" / "PinCheck.lean")
    check_count = pins.count("#check")
    example_count = len(re.findall(r"^\s*example\b", pins, flags=re.MULTILINE))
    if example_count >= 3 and check_count >= 1:
        return "semantic", check_count, example_count
    if example_count >= 1 and check_count >= 1:
        return "mixed", check_count, example_count
    if check_count >= 1:
        return "signature_only", check_count, example_count
    return "weak", check_count, example_count


def recommendation_label(metadata: dict) -> str:
    status = metadata.get("acceptance_status", "candidate_not_accepted")
    if status in {"accepted_v0", "calibration_only", "candidate_review_pending"}:
        return status
    if status.startswith("rejected_"):
        return status
    return "candidate_review_pending"


def row_for_task(task_dir: Path) -> dict[str, object]:
    metadata = json.loads((task_dir / "metadata.json").read_text(encoding="utf-8"))
    task_id = metadata["task_id"]
    public_files = metadata.get("public_files", ["Task.lean"])
    public_texts = [read_text(task_dir / name) for name in public_files]
    reference = read_text(task_dir / "hidden" / "Reference.lean")
    profile = tactic_profile(reference)
    total_tactics = sum(profile.values())
    auto_tactics = sum(profile.get(t, 0) for t in ["rfl", "simp", "omega", "cases"])
    automation_dominated = auto_tactics >= max(1, total_tactics * 0.6)
    hidden_strength, hidden_checks, hidden_examples = hidden_pin_assessment(task_dir)
    capabilities = capability_flags(metadata)
    wrong_count = len(list((task_dir / "wrong").glob("*.lean"))) if (task_dir / "wrong").exists() else 0
    return {
        "task_id": task_id,
        "title": metadata.get("title", ""),
        "split": metadata.get("split", ""),
        "family": metadata.get("family", ""),
        "acceptance_status": metadata.get("acceptance_status", ""),
        "difficulty_review_status": metadata.get("difficulty_review_status", ""),
        "audit_recommendation": recommendation_label(metadata),
        "mechanical_reference_proof_lines": count_reference_lines(reference),
        "mechanical_declaration_count": sum(declaration_count(text) for text in public_texts),
        "mechanical_file_count": len(public_files),
        "mechanical_public_lemma_count": sum(len(re.findall(r"^\s*(theorem|lemma)\b", text, flags=re.MULTILINE)) for text in public_texts),
        "mechanical_tactic_profile": json.dumps(dict(profile), sort_keys=True),
        "mechanical_automation_dominated": str(automation_dominated).lower(),
        "mechanical_mathlib_required": str(any("Mathlib" in text for text in public_texts + [reference])).lower(),
        "mechanical_multifile_context": str(len(public_files) > 1).lower(),
        "mechanical_hidden_pin_strength": hidden_strength,
        "mechanical_hidden_check_count": hidden_checks,
        "mechanical_hidden_example_count": hidden_examples,
        "mechanical_wrong_submission_count": wrong_count,
        "manual_time_bucket": metadata.get("human_time_bucket", ""),
        "manual_human_minutes_p50": metadata.get("human_minutes_p50", ""),
        "manual_human_minutes_p90": metadata.get("human_minutes_p90", ""),
        "manual_frontier_model_one_shot_likelihood": metadata.get("frontier_model_one_shot_likelihood", "unknown"),
        "manual_diagnostic_value": metadata.get("diagnostic_value", "unknown"),
        "manual_scaffold_sensitivity": metadata.get("scaffold_sensitivity", ""),
        "manual_final_reason": metadata.get("difficulty_review_notes", ""),
        **{k: str(v).lower() for k, v in capabilities.items()},
    }


def write_markdown(rows: list[dict[str, object]]) -> None:
    report = ROOT / "reports" / "difficulty_audit.md"
    accepted = [r for r in rows if r["acceptance_status"] == "accepted_v0"]
    calibration = [r for r in rows if r["acceptance_status"] == "calibration_only"]
    rejected = [r for r in rows if str(r["acceptance_status"]).startswith("rejected_")]
    pending = [r for r in rows if r["acceptance_status"] == "candidate_review_pending"]
    bucket_counts = Counter(str(r["manual_time_bucket"]) for r in accepted + calibration)
    family_counts = Counter(str(r["family"]) for r in accepted)

    def table(rs: list[dict[str, object]]) -> str:
        if not rs:
            return "_None._"
        lines = [
            "| task | status | bucket | proof lines | hidden pins | wrongs | automation dominated | diagnostic value | review note |",
            "| --- | --- | --- | ---: | --- | ---: | --- | --- | --- |",
        ]
        for r in rs:
            note = str(r["manual_final_reason"]).replace("|", "/")
            lines.append(
                f"| {r['task_id']} | {r['acceptance_status']} | {r['manual_time_bucket']} | "
                f"{r['mechanical_reference_proof_lines']} | {r['mechanical_hidden_pin_strength']} | "
                f"{r['mechanical_wrong_submission_count']} | {r['mechanical_automation_dominated']} | "
                f"{r['manual_diagnostic_value']} | {note} |"
            )
        return "\n".join(lines)

    report.write_text(
        "# Difficulty Audit\n\n"
        "This audit separates mechanical signals from manual benchmark judgments. "
        "Mechanical signals are generated from the task files and hidden references; "
        "manual judgments live in each task's `metadata.json` and are regenerated into the CSV.\n\n"
        "## Summary\n\n"
        f"- Accepted v0 core tasks: {len(accepted)}\n"
        f"- Calibration-only release tasks: {len(calibration)}\n"
        f"- Rejected tasks retained in archive: {len(rejected)}\n"
        f"- Candidate review pending: {len(pending)}\n"
        f"- Accepted/calibration buckets: {dict(sorted(bucket_counts.items()))}\n"
        f"- Accepted core families: {dict(sorted(family_counts.items()))}\n\n"
        "## Accepted v0 Core Tasks\n\n"
        + table(accepted)
        + "\n\n## Calibration-Only Release Tasks\n\n"
        + table(calibration)
        + "\n\n## Rejected Archive\n\n"
        + table(rejected)
        + "\n\n## Pending Candidates\n\n"
        + table(pending)
        + "\n\n## Method\n\n"
        "The script counts reference proof lines, declarations, public files, public theorem/lemma statements, tactic-token profiles, "
        "Mathlib imports, multi-file context, hidden pin shape, and wrong-submission count. "
        "Manual fields record likely frontier one-shot solvability, human p50/p90, diagnostic value, and the keep/revise/reject rationale. "
        "Tasks dominated by `rfl`, `simp`, `omega`, or `cases` are only accepted as calibration unless their metadata records a specific diagnostic role.\n",
        encoding="utf-8",
    )


def main() -> int:
    rows = [row_for_task(task_dir) for task_dir in discover_tasks()]
    out = ROOT / "data" / "difficulty_audit.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    write_markdown(rows)
    print(f"wrote {out.relative_to(ROOT)} and reports/difficulty_audit.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
