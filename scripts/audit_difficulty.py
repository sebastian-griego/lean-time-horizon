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

MANUAL = {
    "lt-001": ("calibration", "T1", "yes", "low", "likely", "Short induction; mostly simp/arithmetic cleanup."),
    "lt-002": ("calibration", "T1", "yes", "low", "likely", "Short induction plus Bool cases; useful smoke row."),
    "lt-003": ("calibration", "T1", "partial", "medium", "likely", "Codebase-repair shape, but the proof is a small generalized induction."),
    "lt-004": ("calibration", "T1", "yes", "medium", "likely", "Semantic formalization row, but the target relation is very small."),
    "lt-005": ("reject_or_T0", "T0", "yes", "low", "very_likely", "Solved by unfolding conditionals and omega/simp; weak long-horizon signal."),
    "lt-101": ("calibration", "T1", "yes", "medium", "likely", "Accumulator invariant gives some decomposition value but still short."),
    "lt-102": ("reject_or_T0", "T0", "yes", "low", "very_likely", "Option case split with simp/omega; too easy for final set."),
    "lt-103": ("calibration", "T1", "yes", "medium", "likely", "Tree induction and arithmetic normalization; good calibration only."),
    "lt-104": ("calibration", "T1", "partial", "medium", "likely", "Proof-repair shape overlaps heavily with lt-003."),
    "lt-105": ("borderline_candidate", "T1", "partial", "medium", "maybe", "Recursive API repair has some value but is still mainly induction+simp."),
    "lt-106": ("calibration", "T1", "yes", "medium", "likely", "Suffix formalization is semantically pinned but too compact."),
    "lt-107": ("borderline_candidate", "T1", "yes", "medium", "maybe", "Membership implication spec has semantic value; proof still short."),
    "lt-108": ("borderline_candidate", "T1", "yes", "medium", "maybe", "Recursive predicate design is useful; public lemmas are constructor-level."),
    "lt-109": ("reject_or_T0", "T0", "yes", "low", "very_likely", "Mostly nested if split plus omega."),
    "lt-110": ("reject_or_T0", "T0", "partial", "low", "very_likely", "Natural subtraction invariant is one arithmetic fact and transitivity."),
    "lt-111": ("reject_or_T1", "T1", "yes", "low", "likely", "Nested branch invariant, but reference is dominated by omega."),
    "lt-112": ("reject_or_T0", "T0", "yes", "low", "very_likely", "Structure cases and simp; not final-benchmark material."),
    "lt-113": ("calibration", "T1", "partial", "medium", "likely", "Small library wrapper has multiple lemmas but proofs are cases/simp."),
    "lt-114": ("reject_or_T0", "T0", "yes", "low", "very_likely", "Nearly all rfl; keep only as harness smoke if needed."),
    "lt-115": ("reject_or_T0", "T0", "partial", "low", "very_likely", "One obvious library lemma applied twice."),
    "lt-201": ("replacement_review_pending", "T2", "yes", "high", "maybe", "Multi-file repair requires reading Model.lean, preserving API meaning, and proving two generalized batch lemmas."),
    "lt-202": ("replacement_review_pending", "T2", "yes", "medium_high", "maybe", "Mathlib set/function package requires API fluency and witness merging; lookup sensitivity should be high."),
    "lt-203": ("replacement_review_pending", "T2", "yes", "high", "maybe", "Spec-to-formalization task uses hidden semantic pins to reject vacuous or duplicate-sensitive definitions."),
    "lt-204": ("replacement_review_pending", "T2", "yes", "high", "maybe", "Invariant package requires several helper lemmas before the final capped-list invariant."),
    "lt-205": ("replacement_review_pending", "T2", "yes", "high", "maybe", "Small library construction requires a coherent count-based bag interface across 5-10 lemmas."),
}


def discover_tasks() -> list[Path]:
    tasks: list[Path] = []
    for split in ["dev", "test", "candidates"]:
        base = ROOT / "tasks" / split
        if base.exists():
            tasks.extend(sorted(p for p in base.iterdir() if (p / "metadata.json").exists()))
    return tasks


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
    return sum(
        1
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("--")
    )


def tactic_profile(reference: str) -> Counter[str]:
    text = proof_text(reference)
    counts: Counter[str] = Counter()
    for tactic in TACTICS:
        counts[tactic] = len(re.findall(rf"\b{re.escape(tactic)}\b", text))
    return Counter({k: v for k, v in counts.items() if v})


def capability_flags(metadata: dict, recommendation: str) -> dict[str, bool]:
    skills = " ".join(metadata.get("skills", [])).lower()
    family = metadata.get("family", "")
    return {
        "requires_library_search": "library search" in skills or family == "direct_theorem_proving",
        "requires_decomposition": any(s in skills for s in ["induction", "recursive", "library construction", "decomposition", "helper"]),
        "requires_semantic_formalization": family == "informal_spec_to_formal" or "semantic formalization" in skills,
        "requires_proof_debugging": "debug" in skills or "repair" in family or recommendation.startswith("borderline"),
        "requires_codebase_navigation": family == "proof_repair_codebase" or "codebase navigation" in skills,
        "requires_invariant_design": family == "invariant_verification_ml_optimization" or "invariant design" in skills,
        "requires_long_horizon_construction": "library construction" in skills or "helper lemma" in skills or family == "small_formal_library_construction",
    }


def hidden_pin_assessment(task_dir: Path) -> str:
    pins = (task_dir / "hidden" / "PinCheck.lean").read_text(encoding="utf-8") if (task_dir / "hidden" / "PinCheck.lean").exists() else ""
    wrongs = list((task_dir / "wrong").glob("*.lean")) if (task_dir / "wrong").exists() else []
    has_type_pin = "#check" in pins
    has_examples = "example" in pins
    has_wrong = bool(wrongs)
    if has_type_pin and has_examples and has_wrong:
        return "yes"
    if has_type_pin and has_wrong:
        return "partial"
    return "weak"


def main() -> int:
    rows = []
    for task_dir in discover_tasks():
        metadata = json.loads((task_dir / "metadata.json").read_text(encoding="utf-8"))
        task_id = metadata["task_id"]
        reference_path = task_dir / "hidden" / "Reference.lean"
        reference = reference_path.read_text(encoding="utf-8") if reference_path.exists() else ""
        profile = tactic_profile(reference)
        dominant_auto = sum(profile.get(t, 0) for t in ["rfl", "simp", "omega", "cases"]) >= max(1, sum(profile.values()) * 0.6)
        manual = MANUAL.get(task_id, ("new_replacement_candidate", metadata.get("human_time_bucket", "T2"), "manual_review_required", "high", "unknown", "Replacement candidate requires separate manual review."))
        capabilities = capability_flags(metadata, manual[0])
        rows.append(
            {
                "task_id": task_id,
                "title": metadata.get("title", ""),
                "split": metadata.get("split", ""),
                "family": metadata.get("family", ""),
                "reference_proof_lines": count_reference_lines(reference),
                "tactic_profile": json.dumps(dict(profile), sort_keys=True),
                "rfl_simp_omega_cases_dominant": str(dominant_auto).lower(),
                "audit_recommendation": manual[0],
                "audited_time_bucket": manual[1],
                "only_t0_t1_calibration": "yes" if manual[0] == "calibration" else "no",
                "hidden_pins_prevent_definition_changes_or_weakening": hidden_pin_assessment(task_dir),
                "requires_library_search": str(capabilities["requires_library_search"]).lower(),
                "requires_decomposition": str(capabilities["requires_decomposition"]).lower(),
                "requires_semantic_formalization": str(capabilities["requires_semantic_formalization"]).lower(),
                "requires_proof_debugging": str(capabilities["requires_proof_debugging"]).lower(),
                "requires_codebase_navigation": str(capabilities["requires_codebase_navigation"]).lower(),
                "requires_invariant_design": str(capabilities["requires_invariant_design"]).lower(),
                "requires_long_horizon_construction": str(capabilities["requires_long_horizon_construction"]).lower(),
                "diagnostic_value": manual[3],
                "frontier_model_one_shot_likelihood": manual[4],
                "notes": manual[5],
            }
        )

    out = ROOT / "data" / "difficulty_audit.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    report = ROOT / "reports" / "difficulty_audit.md"
    old_rows = [r for r in rows if not r["task_id"].startswith("lt-2")]
    replacement_rows = [r for r in rows if r["audit_recommendation"].startswith("replacement") or r["audit_recommendation"] == "new_replacement_candidate"]
    rejected = [r for r in old_rows if r["audit_recommendation"].startswith("reject")]
    calibration = [r for r in old_rows if r["audit_recommendation"] == "calibration"]
    borderline = [r for r in old_rows if r["audit_recommendation"] == "borderline_candidate"]
    report.write_text(
        "# Difficulty Audit\n\n"
        "The original 20 tasks are now treated as candidates, not final accepted tasks. "
        "This audit applies the playbook criterion that diagnostic validity matters more than raw difficulty.\n\n"
        "## Summary\n\n"
        f"- Original candidate tasks audited: {len(old_rows)}\n"
        f"- Reject or downgrade to smoke/calibration: {len(rejected)}\n"
        f"- T0/T1 calibration only: {len(calibration)}\n"
        f"- Borderline candidates needing stronger review: {len(borderline)}\n"
        f"- New replacement candidates present: {len(replacement_rows)}\n\n"
        "## Original Candidate Decisions\n\n"
        "| task | recommendation | bucket | proof lines | tactic profile | simp/omega/rfl/cases dominant | hidden pins | model one-shot | notes |\n"
        "| --- | --- | --- | ---: | --- | --- | --- | --- | --- |\n"
        + "\n".join(
            f"| {r['task_id']} | {r['audit_recommendation']} | {r['audited_time_bucket']} | {r['reference_proof_lines']} | `{r['tactic_profile']}` | {r['rfl_simp_omega_cases_dominant']} | {r['hidden_pins_prevent_definition_changes_or_weakening']} | {r['frontier_model_one_shot_likelihood']} | {r['notes']} |"
            for r in old_rows
        )
        + "\n\n## T0/T1 Calibration-Only Items\n\n"
        + ", ".join(f"`{r['task_id']}`" for r in calibration)
        + "\n\n## Reject Or Smoke-Only Items\n\n"
        + ", ".join(f"`{r['task_id']}`" for r in rejected)
        + "\n\n## Borderline Items Needing Stronger Review\n\n"
        + ", ".join(f"`{r['task_id']}`" for r in borderline)
        + "\n\n## Replacement Candidate Notes\n\n"
        + (
            "\n".join(
                f"- `{r['task_id']}`: {r['title']} ({r['family']}), proof lines {r['reference_proof_lines']}, profile `{r['tactic_profile']}`; "
                f"library_search={r['requires_library_search']}, decomposition={r['requires_decomposition']}, "
                f"semantic_formalization={r['requires_semantic_formalization']}, proof_debugging={r['requires_proof_debugging']}, "
                f"codebase_navigation={r['requires_codebase_navigation']}, invariant_design={r['requires_invariant_design']}, "
                f"hidden_pins={r['hidden_pins_prevent_definition_changes_or_weakening']}, one_shot={r['frontier_model_one_shot_likelihood']}. "
                f"{r['notes']}"
                for r in replacement_rows
            )
            if replacement_rows
            else "No replacement candidates have been added yet."
        )
        + "\n\n## Method\n\n"
        "The script counts reference proof lines and tactic-token profiles mechanically, then combines those counts with manual review fields for diagnostic value, likely frontier one-shot success, and final recommendation. "
        "Rows dominated by `rfl`, `simp`, `omega`, or `cases`, or by one obvious library lemma, are downgraded unless they serve a narrow calibration purpose.\n",
        encoding="utf-8",
    )
    print(f"wrote {out.relative_to(ROOT)} and {report.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
