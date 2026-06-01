from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "task_id",
    "title",
    "split",
    "family",
    "acceptance_status",
    "pincheck_lines",
    "theorem_shape_checks",
    "positive_examples",
    "negative_examples",
    "parameterized_examples",
    "exact_eval_examples",
    "wrong_submission_count",
    "wrongs_failing_public_stage",
    "wrongs_failing_hidden_pin_stage",
    "wrongs_failing_mixed_stage",
    "wrongs_failing_unknown_stage",
    "wrong_stage_summary",
    "submission_surface",
    "same_signature_hidden_wrong_feasibility",
    "hidden_pin_role",
    "pin_coverage_grade",
    "review_note",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def discover_task_dirs() -> dict[str, Path]:
    out: dict[str, Path] = {}
    for split in ["dev", "test", "candidates"]:
        base = ROOT / "tasks" / split
        if not base.exists():
            continue
        for task_dir in sorted(base.iterdir()):
            metadata_path = task_dir / "metadata.json"
            if not metadata_path.exists():
                continue
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            out[str(metadata["task_id"])] = task_dir
    return out


def local_transcript_entries(task_id: str) -> list[dict[str, object]]:
    path = ROOT / "transcripts" / "local-qa" / f"{task_id}.jsonl"
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        entries.append(json.loads(line))
    return entries


def count_examples(src: str) -> dict[str, int]:
    example_lines = re.findall(r"^\s*example\b.*$", src, flags=re.MULTILINE)
    positive = 0
    negative = 0
    parameterized = 0
    exact_eval = 0
    for line in example_lines:
        if "\u00ac" in line or "False" in line:
            negative += 1
        else:
            positive += 1
        if re.match(r"^\s*example\s*\(", line):
            parameterized += 1
    current_is_example = False
    for line in src.splitlines():
        if re.match(r"^\s*example\b", line):
            current_is_example = True
        if current_is_example and re.search(r"\brfl\b", line):
            exact_eval += 1
            current_is_example = False
        if current_is_example and line.strip() == "":
            current_is_example = False
    return {
        "positive_examples": positive,
        "negative_examples": negative,
        "parameterized_examples": parameterized,
        "exact_eval_examples": exact_eval,
    }


def submission_surface(task_dir: Path | None, metadata: dict[str, str]) -> str:
    if not task_dir:
        return "missing_task_dir"
    submission_file = metadata.get("submission_file") or metadata.get("entry_file") or "Task.lean"
    public_path = task_dir / submission_file
    if not public_path.exists():
        return "missing_submission_file"
    src = public_path.read_text(encoding="utf-8", errors="replace")
    mutable_decl_count = len(re.findall(
        r"^\s*(?:def|abbrev|structure|inductive|class|instance)\b",
        src,
        flags=re.MULTILINE,
    ))
    theorem_count = len(re.findall(r"^\s*(?:theorem|lemma)\b", src, flags=re.MULTILINE))
    if mutable_decl_count == 0 and theorem_count > 0:
        return "proof_only_fixed_statements"
    if mutable_decl_count > 0 and theorem_count > 0:
        return "mutable_definitions_plus_theorems"
    if mutable_decl_count > 0:
        return "mutable_definitions_only"
    return "unclassified_surface"


def hidden_wrong_feasibility(surface: str) -> str:
    if surface == "proof_only_fixed_statements":
        return "structurally_infeasible_for_same_signature_proof_wrongs"
    if surface.startswith("mutable_definitions"):
        return "feasible_via_definition_semantics"
    return "unknown"


def hidden_pin_role(surface: str, shape_checks: int, positive: int, negative: int) -> str:
    if surface == "proof_only_fixed_statements":
        return "signature_and_downstream_use_guard"
    if negative > 0:
        return "semantic_positive_negative_guard"
    if positive > 0:
        return "semantic_positive_guard_only"
    if shape_checks > 0:
        return "signature_guard_only"
    return "weak_or_missing_guard"


def classify_failure_stage(entry: dict[str, object]) -> str:
    excerpt = str(entry.get("feedback_excerpt", ""))
    if not excerpt:
        return "unknown"
    has_pin = "PinCheck.lean" in excerpt
    has_task = "Task.lean" in excerpt
    has_forbidden = "forbidden" in excerpt.lower()
    has_axiom = "AxiomAudit.lean" in excerpt or "Disallowed axioms" in excerpt
    if has_forbidden:
        return "forbidden_scan"
    if has_axiom:
        return "axiom_audit"
    if has_pin and has_task:
        return "mixed"
    if has_pin:
        return "hidden_pin"
    if has_task:
        return "public_stage"
    return "unknown"


def pin_grade(shape_checks: int, positive: int, negative: int, parameterized: int, hidden_wrong: int, public_wrong: int) -> str:
    if negative > 0 and positive >= 2 and parameterized > 0 and hidden_wrong > 0:
        return "semantic_pins_exercised"
    if negative > 0 and positive > 0 and hidden_wrong > 0:
        return "semantic_examples_exercised"
    if shape_checks > 0 and hidden_wrong > 0:
        return "signature_plus_hidden_failure"
    if public_wrong > 0 and hidden_wrong == 0:
        return "pins_not_exercised_by_wrongs"
    return "weak_or_unclassified"


def review_note(
    status: str,
    grade: str,
    hidden_wrong: int,
    public_wrong: int,
    negative: int,
    feasibility: str,
    role: str,
) -> str:
    if (
        status == "accepted_v0"
        and grade == "pins_not_exercised_by_wrongs"
        and feasibility == "structurally_infeasible_for_same_signature_proof_wrongs"
    ):
        return "Accepted proof-only row: same-signature semantic wrong proofs are structurally infeasible once Lean accepts the fixed theorem; hidden pins guard signatures and downstream use."
    if status == "accepted_v0" and grade == "pins_not_exercised_by_wrongs":
        return "Accepted row needs a caveat: current wrong submissions fail before hidden pins run despite a mutable semantic surface."
    if status == "accepted_v0" and public_wrong > hidden_wrong:
        return "Accepted row has more public-stage wrong failures than hidden-pin failures; keep caveat visible."
    if status == "accepted_v0" and negative == 0:
        return f"Accepted row lacks negative hidden examples; current hidden-pin role is {role}."
    if status == "accepted_v0":
        return "Accepted row has at least one wrong submission reaching hidden pins and nontrivial examples."
    if status == "calibration_only":
        return "Calibration row; use as harness/pin regression evidence only."
    if status.startswith("rejected_"):
        return "Rejected archive row; retained as pruning evidence."
    return "Unclassified status; do not use for benchmark claims."


def build_rows() -> list[dict[str, str]]:
    metadata_rows = read_csv(ROOT / "data" / "task_metadata.csv")
    task_dirs = discover_task_dirs()
    rows: list[dict[str, str]] = []
    for metadata in metadata_rows:
        task_id = metadata["task_id"]
        task_dir = task_dirs.get(task_id)
        pin_src = ""
        if task_dir and (task_dir / "hidden" / "PinCheck.lean").exists():
            pin_src = (task_dir / "hidden" / "PinCheck.lean").read_text(encoding="utf-8", errors="replace")
        lines = [line for line in pin_src.splitlines() if line.strip()]
        shape_checks = len(re.findall(r"^\s*#check\b", pin_src, flags=re.MULTILINE))
        examples = count_examples(pin_src)
        surface = submission_surface(task_dir, metadata)
        feasibility = hidden_wrong_feasibility(surface)
        role = hidden_pin_role(
            surface,
            shape_checks,
            examples["positive_examples"],
            examples["negative_examples"],
        )
        wrong_entries = [
            entry for entry in local_transcript_entries(task_id)
            if str(entry.get("model", "")).startswith("plausible_wrong:")
        ]
        stage_counts = Counter(classify_failure_stage(entry) for entry in wrong_entries)
        hidden_wrong = stage_counts.get("hidden_pin", 0)
        public_wrong = stage_counts.get("public_stage", 0)
        mixed_wrong = stage_counts.get("mixed", 0)
        unknown_wrong = sum(
            count for stage, count in stage_counts.items()
            if stage not in {"hidden_pin", "public_stage", "mixed"}
        )
        grade = pin_grade(
            shape_checks,
            examples["positive_examples"],
            examples["negative_examples"],
            examples["parameterized_examples"],
            hidden_wrong,
            public_wrong,
        )
        rows.append({
            "task_id": task_id,
            "title": metadata.get("title", ""),
            "split": metadata.get("split", ""),
            "family": metadata.get("family", ""),
            "acceptance_status": metadata.get("acceptance_status", ""),
            "pincheck_lines": str(len(lines)),
            "theorem_shape_checks": str(shape_checks),
            "positive_examples": str(examples["positive_examples"]),
            "negative_examples": str(examples["negative_examples"]),
            "parameterized_examples": str(examples["parameterized_examples"]),
            "exact_eval_examples": str(examples["exact_eval_examples"]),
            "wrong_submission_count": str(len(wrong_entries)),
            "wrongs_failing_public_stage": str(public_wrong),
            "wrongs_failing_hidden_pin_stage": str(hidden_wrong),
            "wrongs_failing_mixed_stage": str(mixed_wrong),
            "wrongs_failing_unknown_stage": str(unknown_wrong),
            "wrong_stage_summary": json.dumps(dict(sorted(stage_counts.items())), sort_keys=True),
            "submission_surface": surface,
            "same_signature_hidden_wrong_feasibility": feasibility,
            "hidden_pin_role": role,
            "pin_coverage_grade": grade,
            "review_note": review_note(
                metadata.get("acceptance_status", ""),
                grade,
                hidden_wrong,
                public_wrong,
                examples["negative_examples"],
                feasibility,
                role,
            ),
        })
    return rows


def escaped(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ")


def accepted_table(rows: list[dict[str, str]]) -> str:
    accepted = [row for row in rows if row["acceptance_status"] == "accepted_v0"]
    if not accepted:
        return "_None._"
    lines = [
        "| task | grade | surface | feasibility | role | wrongs public | wrongs hidden | note |",
        "| --- | --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in accepted:
        lines.append(
            f"| `{row['task_id']}` | {row['pin_coverage_grade']} | {row['submission_surface']} | "
            f"{row['same_signature_hidden_wrong_feasibility']} | {row['hidden_pin_role']} | "
            f"{row['wrongs_failing_public_stage']} | "
            f"{row['wrongs_failing_hidden_pin_stage']} | {escaped(row['review_note'])} |"
        )
    return "\n".join(lines)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    grade_counts = Counter(row["pin_coverage_grade"] for row in rows)
    accepted = [row for row in rows if row["acceptance_status"] == "accepted_v0"]
    accepted_hidden = sum(int(row["wrongs_failing_hidden_pin_stage"]) for row in accepted)
    accepted_public = sum(int(row["wrongs_failing_public_stage"]) for row in accepted)
    accepted_with_hidden = sum(1 for row in accepted if int(row["wrongs_failing_hidden_pin_stage"]) > 0)
    feasibility_counts = Counter(row["same_signature_hidden_wrong_feasibility"] for row in accepted)
    role_counts = Counter(row["hidden_pin_role"] for row in accepted)
    lines = [
        "# Hidden Pin Coverage Audit",
        "",
        "This generated audit makes hidden-check evidence more transparent. It statically counts theorem-shape checks and examples in each `hidden/PinCheck.lean`, then uses deterministic local QA transcripts to classify whether plausible wrong submissions failed during public compilation/proof checking or after reaching hidden pins.",
        "",
        "A public-stage wrong failure can still be useful for proof-repair tasks, but it is weaker evidence for semantic-pin coverage than a wrong submission that compiles publicly and fails in `PinCheck.lean`.",
        "",
        "The audit now also classifies the submission surface. For proof-only fixed-statement tasks, a same-signature wrong proof that compiles publicly is structurally infeasible without forbidden constructs or disallowed axioms: Lean has already certified the fixed theorem. In those rows, hidden pins mainly guard theorem signatures and downstream usability rather than catching semantically wrong definitions.",
        "",
        "## Summary",
        "",
        f"- pin coverage grades: `{json.dumps(dict(sorted(grade_counts.items())), sort_keys=True)}`",
        f"- accepted-core tasks with at least one hidden-pin wrong failure: `{accepted_with_hidden}/{len(accepted)}`",
        f"- accepted-core wrong failures at public stage: `{accepted_public}`",
        f"- accepted-core wrong failures at hidden-pin stage: `{accepted_hidden}`",
        f"- accepted-core same-signature hidden-wrong feasibility: `{json.dumps(dict(sorted(feasibility_counts.items())), sort_keys=True)}`",
        f"- accepted-core hidden-pin roles: `{json.dumps(dict(sorted(role_counts.items())), sort_keys=True)}`",
        "",
        "## Accepted Core Pin Coverage",
        "",
        accepted_table(rows),
        "",
        "## Interpretation",
        "",
        "`semantic_pins_exercised` means the task has positive and negative examples, at least one parameterized example, and at least one plausible wrong submission that reaches hidden pins. `semantic_examples_exercised` means positive/negative examples and hidden-pin wrong failures exist, but the examples are less structurally rich by this heuristic. `pins_not_exercised_by_wrongs` means local wrong submissions fail before hidden pins run. That is a stronger concern for mutable-definition/formalization rows than for proof-only fixed-statement rows, where same-signature semantic wrong proofs are not a meaningful target.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_rows()
    csv_out = ROOT / "data" / "pin_coverage_audit.csv"
    md_out = ROOT / "reports" / "pin_coverage_audit.md"
    write_csv(csv_out, rows)
    write_markdown(md_out, rows)
    print(f"wrote {csv_out.relative_to(ROOT)} and {md_out.relative_to(ROOT)} with {len(rows)} task rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
