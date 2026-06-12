# QA Checklist

Use `python scripts/validate_all.py` before accepting or promoting a task.

For each accepted task candidate:

- reference solution passes public build, hidden pins, forbidden scan, and axiom audit
- at least one plausible wrong solution fails
- public prompt names editable files, allowed scaffolds, and forbidden constructs
- metadata is complete and agrees with `data/task_metadata.csv`
- hidden files are not referenced from public prompts or scaffolds
- task is human-solvable in the stated time bucket

For release:

- `python scripts/validate_all.py`
- `python scripts/audit_difficulty.py`
- `python scripts/export_public_tasks.py --out public_tasks`
- `python scripts/audit_benchmark_package.py --public-export public_tasks`
- `python scripts/generate_report.py`
- generated figures and report are committed
- README commands match the current scripts
- limitations are documented in `reports/metr_style_report.md`
