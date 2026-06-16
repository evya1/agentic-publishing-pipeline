"""Verify that all required documentation files are present.

Exits with code 1 and a clear message if any required file is missing.
"""

from __future__ import annotations

import sys
from pathlib import Path

REQUIRED: list[str] = [
    "README.md",
    "CONTRIBUTING.md",
    "CLAUDE.md",
    "docs/PRD.md",
    "docs/PLAN.md",
    "docs/TODO.md",
    "docs/HW3_REQUIREMENTS.md",
    "docs/AI_USAGE.md",
    "docs/PROMPTS.md",
    "docs/PRD_bibliography_and_citations.md",
    "docs/PRD_crewai_pipeline.md",
    "docs/PRD_latex_generation.md",
    "docs/PRD_pdf_validation.md",
    "SUBMISSION_CHECKLIST.md",
    "config/article_sources.yaml",
]


def main() -> int:
    repo_root = Path(__file__).parent.parent
    missing: list[str] = []

    for rel in REQUIRED:
        if not (repo_root / rel).exists():
            missing.append(rel)

    if missing:
        print("FAIL: missing required documentation files:")
        for path in missing:
            print(f"  - {path}")
        return 1

    print(f"OK: all {len(REQUIRED)} required documentation files present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
