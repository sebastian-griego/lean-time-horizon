from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


DEFAULT_FORBIDDEN = [
    "sorry",
    "admit",
    "axiom",
    "constant",
    "opaque",
    "unsafe",
    "macro",
    "macro_rules",
    "syntax",
    "elab",
    "run_cmd",
    "run_tac",
    "Lean.addDecl",
    "#eval",
    "#exit",
]


def strip_comments_and_strings(src: str) -> str:
    """Remove Lean comments and string/char literals while preserving line count."""
    out: list[str] = []
    i = 0
    block_depth = 0
    n = len(src)
    while i < n:
        c = src[i]
        nxt = src[i : i + 2]

        if block_depth > 0:
            if nxt == "/-":
                block_depth += 1
                out.append("  ")
                i += 2
            elif nxt == "-/":
                block_depth -= 1
                out.append("  ")
                i += 2
            else:
                out.append("\n" if c == "\n" else " ")
                i += 1
            continue

        if nxt == "/-":
            block_depth = 1
            out.append("  ")
            i += 2
            continue

        if nxt == "--":
            while i < n and src[i] != "\n":
                out.append(" ")
                i += 1
            continue

        if c == '"':
            out.append(" ")
            i += 1
            while i < n:
                if src[i] == "\\":
                    out.append(" ")
                    if i + 1 < n:
                        out.append("\n" if src[i + 1] == "\n" else " ")
                    i += 2
                    continue
                if src[i] == '"':
                    out.append(" ")
                    i += 1
                    break
                out.append("\n" if src[i] == "\n" else " ")
                i += 1
            continue

        if c == "'":
            out.append(" ")
            i += 1
            while i < n:
                if src[i] == "\\":
                    out.append(" ")
                    if i + 1 < n:
                        out.append("\n" if src[i + 1] == "\n" else " ")
                    i += 2
                    continue
                if src[i] == "'":
                    out.append(" ")
                    i += 1
                    break
                if src[i] == "\n":
                    break
                out.append(" ")
                i += 1
            continue

        out.append(c)
        i += 1

    return "".join(out)


def find_forbidden(src: str, forbidden: list[str]) -> list[dict[str, object]]:
    stripped = strip_comments_and_strings(src)
    findings: list[dict[str, object]] = []
    for term in forbidden:
        if re.match(r"^[A-Za-z_][A-Za-z0-9_'.]*$", term):
            pattern = re.compile(rf"(?<![A-Za-z0-9_'.]){re.escape(term)}(?![A-Za-z0-9_'.])")
        else:
            pattern = re.compile(re.escape(term))
        for match in pattern.finditer(stripped):
            line = stripped.count("\n", 0, match.start()) + 1
            col = match.start() - stripped.rfind("\n", 0, match.start())
            findings.append({"term": term, "line": line, "column": col})
    return sorted(findings, key=lambda f: (int(f["line"]), int(f["column"]), str(f["term"])))


def load_forbidden(metadata_path: Path | None) -> list[str]:
    forbidden = list(DEFAULT_FORBIDDEN)
    if metadata_path and metadata_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        for term in metadata.get("extra_forbidden", []):
            if term not in forbidden:
                forbidden.append(term)
    return forbidden


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    src = args.path.read_text(encoding="utf-8")
    findings = find_forbidden(src, load_forbidden(args.metadata))
    if args.json:
        print(json.dumps({"ok": not findings, "findings": findings}, indent=2))
    elif findings:
        for finding in findings:
            print(f"{args.path}:{finding['line']}:{finding['column']}: forbidden {finding['term']}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
