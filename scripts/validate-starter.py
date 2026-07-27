#!/usr/bin/env python3
"""Validate an exported learner starter using only the Python standard library."""

from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
IGNORED_LINK_PREFIXES = ("http://", "https://", "mailto:", "#")
REQUIRED = [
    "README.md",
    "STARTER_SCOPE.md",
    "VALIDATION_REPORT.md",
    "PUBLISH_TO_GITHUB.md",
    "COURSE_MAP.md",
    "VERSION_MATRIX.md",
    "compose.yaml",
    "compose.test.yaml",
    ".env.example",
    ".github/workflows/ci.yml",
    ".github/workflows/deploy-gcp.yml",
    "backend/pyproject.toml",
    "backend/app/main.py",
    "backend/tests/test_health.py",
    "frontend/package.json",
    "frontend/nuxt.config.ts",
    "workshop/00-orientation-and-definition-of-done.md",
    "workshop/19-final-capstone-and-production-readiness.md",
    "learner/START_HERE.md",
    "instructor/RUBRIC.md",
    "references/OFFICIAL_REFERENCES.md",
    "infrastructure/gcp/README.md",
]
FORBIDDEN_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "node_modules",
    ".nuxt",
    ".output",
    ".terraform",
    "playwright-report",
    "test-results",
}
FORBIDDEN_NAMES = {".env", ".coverage", "terraform.tfvars", "workboard.tfplan"}


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    failures: list[str] = []

    for relative in REQUIRED:
        if not (root / relative).exists():
            failures.append(f"Missing required starter file: {relative}")

    modules = sorted((root / "workshop").glob("[0-9][0-9]-*.md"))
    if [item.name[:2] for item in modules] != [f"{index:02d}" for index in range(20)]:
        failures.append("Workshop modules must be a complete 00-19 sequence")

    for path in root.rglob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            failures.append(f"Invalid JSON {path.relative_to(root)}: {exc}")

    for path in root.rglob("*.toml"):
        try:
            tomllib.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            failures.append(f"Invalid TOML {path.relative_to(root)}: {exc}")

    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.strip().split("#", 1)[0]
            if not target or target.startswith(IGNORED_LINK_PREFIXES):
                continue
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            candidate = (path.parent / target).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                failures.append(
                    f"Markdown link escapes starter: {path.relative_to(root)} -> {raw_target}"
                )
                continue
            if not candidate.exists():
                failures.append(
                    f"Broken Markdown link: {path.relative_to(root)} -> {raw_target}"
                )

    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in FORBIDDEN_PARTS for part in relative.parts[:-1]):
            continue
        if path.is_dir() and path.name in FORBIDDEN_PARTS:
            failures.append(f"Generated directory must not ship: {relative}")
            continue
        if path.is_file() and (
            path.name in FORBIDDEN_NAMES
            or path.suffix in {".pyc", ".pyo", ".tfstate"}
            or ".tfstate." in path.name
        ):
            failures.append(f"Generated or secret file must not ship: {relative}")

    if failures:
        print("Starter validation failed:")
        for failure in sorted(set(failures)):
            print(f" - {failure}")
        return 1

    print(
        "Starter structure, module sequence, JSON/TOML, local Markdown links, "
        "and release hygiene are valid."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
