#!/usr/bin/env python3
"""Fail when common secrets or local identifiers appear in publishable files."""

from __future__ import annotations

import re
import sys
from pathlib import Path


IGNORED_DIRS = {".git", ".venv", "__pycache__"}
TEXT_SUFFIXES = {".md", ".txt", ".py", ".yaml", ".yml", ".json", ".toml", ".example", ""}
PATTERNS = {
    "macOS home path": re.compile(r"/Users/(?!用户名(?:/|$)|example(?:/|$))[^/\s]+/"),
    "private IPv4 address": re.compile(
        r"\b(?:"
        r"10(?:\.\d{1,3}){3}|"
        r"192\.168(?:\.\d{1,3}){2}|"
        r"172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}"
        r")\b"
    ),
    "Feishu chat id": re.compile(r"\boc_[A-Za-z0-9]{8,}\b"),
    "common secret assignment": re.compile(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}"),
}


def iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name.startswith(".env"):
            yield path


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    findings: list[str] = []
    for path in iter_text_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings.append(f"{path.relative_to(root)}:{line}: {label}")
    if findings:
        print("Privacy scan failed:")
        print("\n".join(findings))
        return 1
    print("Privacy scan passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
