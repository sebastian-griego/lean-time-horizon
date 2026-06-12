from __future__ import annotations

import csv
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "audit_benchmark_package.py"
SPEC = importlib.util.spec_from_file_location("audit_benchmark_package", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
audit_benchmark_package = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = audit_benchmark_package
SPEC.loader.exec_module(audit_benchmark_package)


class BenchmarkPackageAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "tasks" / "dev" / "lt-001-demo" / "hidden").mkdir(parents=True)
        (self.root / "tasks" / "dev" / "lt-001-demo" / "wrong").mkdir(parents=True)
        (self.root / "data").mkdir()
        (self.root / "reports").mkdir()
        self.task = self.root / "tasks" / "dev" / "lt-001-demo"
        self.metadata = {
            "task_id": "lt-001",
            "title": "demo task",
            "split": "dev",
            "family": "demo",
            "domain": "lists",
            "source_type": "authored",
            "human_time_bucket": "T1",
            "human_minutes_p50": 20,
            "human_minutes_p90": 40,
            "human_estimate_confidence": "medium",
            "skills": ["induction"],
            "scaffolds": ["one-shot"],
            "expected_failure_modes": ["target weakening"],
            "scaffold_sensitivity": "low",
            "qa_status": "local_only",
            "acceptance_status": "calibration_only",
            "difficulty_review_status": "manual_review_complete",
            "difficulty_review_notes": "retained as a calibration task",
            "public_files": ["Task.lean"],
            "submission_file": "Task.lean",
            "entry_file": "Task.lean",
            "axiom_audit_declarations": ["Demo.answer"],
            "extra_forbidden": [],
            "timeout_seconds": 60,
        }
        self.write_task_files()
        self.write_schema()
        self.write_metadata_csv()
        self.write_export()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_task_files(self) -> None:
        (self.task / "metadata.json").write_text(json.dumps(self.metadata, indent=2), encoding="utf-8")
        (self.task / "Prompt.md").write_text("Prove the theorem in Task.lean.\n", encoding="utf-8")
        (self.task / "Task.lean").write_text("namespace Demo\n\ntheorem answer : True := by trivial\n\nend Demo\n", encoding="utf-8")
        (self.task / "hidden" / "Reference.lean").write_text("import Task\nnamespace Demo\nend Demo\n", encoding="utf-8")
        (self.task / "hidden" / "PinCheck.lean").write_text("import Task\nnamespace Demo\nend Demo\n", encoding="utf-8")
        (self.task / "wrong" / "WrongA.lean").write_text("namespace Demo\nend Demo\n", encoding="utf-8")
        (self.task / "wrong" / "WrongB.lean").write_text("namespace Demo\nend Demo\n", encoding="utf-8")

    def write_schema(self) -> None:
        schema = {
            "required": [
                "task_id",
                "title",
                "split",
                "family",
                "domain",
                "source_type",
                "human_time_bucket",
                "human_minutes_p50",
                "human_minutes_p90",
                "human_estimate_confidence",
                "skills",
                "scaffolds",
                "expected_failure_modes",
                "scaffold_sensitivity",
                "qa_status",
                "acceptance_status",
                "difficulty_review_status",
                "difficulty_review_notes",
                "public_files",
                "axiom_audit_declarations",
                "extra_forbidden",
                "timeout_seconds",
            ],
            "properties": {
                "task_id": {"type": "string"},
                "title": {"type": "string"},
                "split": {"enum": ["dev", "test", "candidates"]},
                "human_time_bucket": {"enum": ["T0", "T1", "T2", "T3", "T4"]},
                "human_minutes_p50": {"type": "integer", "minimum": 1},
                "human_minutes_p90": {"type": "integer", "minimum": 1},
                "skills": {"type": "array", "items": {"type": "string"}},
                "scaffolds": {"type": "array", "items": {"enum": ["one-shot", "lookup", "lookup_unlimited"]}},
                "expected_failure_modes": {"type": "array", "items": {"type": "string"}},
                "acceptance_status": {"enum": ["accepted_v0", "calibration_only", "candidate_review_pending"]},
                "public_files": {"type": "array", "items": {"type": "string"}},
                "axiom_audit_declarations": {"type": "array", "items": {"type": "string"}},
                "extra_forbidden": {"type": "array", "items": {"type": "string"}},
                "timeout_seconds": {"type": "integer", "minimum": 1},
            },
        }
        (self.root / "data" / "task_metadata_schema.json").write_text(json.dumps(schema), encoding="utf-8")

    def write_metadata_csv(self) -> None:
        rows = audit_benchmark_package.expected_metadata_projection([(self.task, self.metadata)])
        with (self.root / "data" / "task_metadata.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=audit_benchmark_package.METADATA_PROJECTION_FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def write_export(self) -> None:
        export_task = self.root / "public_tasks" / "dev" / "lt-001-demo"
        export_task.mkdir(parents=True)
        for name in ["Prompt.md", "metadata.json", "Task.lean"]:
            shutil.copyfile(self.task / name, export_task / name)

    def row_status(self, rows: list[dict[str, str]], check_id: str) -> str:
        return next(row["status"] for row in rows if row["check_id"] == check_id)

    def test_clean_package_passes(self) -> None:
        rows = audit_benchmark_package.build_rows(self.root, self.root / "public_tasks")
        self.assertTrue(all(row["status"] == "pass" for row in rows), rows)

    def test_stale_metadata_csv_fails(self) -> None:
        csv_path = self.root / "data" / "task_metadata.csv"
        text = csv_path.read_text(encoding="utf-8")
        csv_path.write_text(text.replace("demo task", "stale title"), encoding="utf-8")

        rows = audit_benchmark_package.build_rows(self.root, self.root / "public_tasks")

        self.assertEqual(self.row_status(rows, "task_metadata_csv_projection"), "fail")

    def test_exported_hidden_material_fails(self) -> None:
        export_hidden = self.root / "public_tasks" / "dev" / "lt-001-demo" / "hidden"
        export_hidden.mkdir()
        (export_hidden / "Reference.lean").write_text("hidden proof\n", encoding="utf-8")

        rows = audit_benchmark_package.build_rows(self.root, self.root / "public_tasks")

        self.assertEqual(self.row_status(rows, "public_export_bundle"), "fail")

    def test_release_task_with_one_wrong_submission_fails(self) -> None:
        (self.task / "wrong" / "WrongB.lean").unlink()

        rows = audit_benchmark_package.build_rows(self.root, self.root / "public_tasks")

        self.assertEqual(self.row_status(rows, "task_source_structure"), "fail")


if __name__ == "__main__":
    unittest.main()
