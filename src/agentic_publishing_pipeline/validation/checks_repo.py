"""P11-I02: Required repository file and directory checks."""

from __future__ import annotations

from pathlib import Path

from .report import ValidationReport

_REQUIRED_FILES = [
    "README.md",
    "docs/PRD.md",
    "docs/PLAN.md",
    "docs/TODO.md",
    "docs/AI_USAGE.md",
    "docs/PROMPTS.md",
    ".env-example",
]

_REQUIRED_DIRS = [
    "src/agentic_publishing_pipeline",
    "tests",
    "config",
    "latex_project",
    "results/generated_markdown",
    "results/run_logs",
]

_REQUIRED_ARTIFACTS = [
    "results/final.pdf",
]


def run_repo_checks(repo_root: Path, report: ValidationReport) -> None:
    """Assert required repository files, directories, and artifacts exist."""
    for rel in _REQUIRED_FILES:
        path = repo_root / rel
        report.add(
            f"file:{rel}",
            path.is_file(),
            f"Found: {path}" if path.is_file() else f"Missing: {path}",
        )

    for rel in _REQUIRED_DIRS:
        path = repo_root / rel
        report.add(
            f"dir:{rel}",
            path.is_dir(),
            f"Found: {path}" if path.is_dir() else f"Missing directory: {path}",
        )

    for rel in _REQUIRED_ARTIFACTS:
        path = repo_root / rel
        exists = path.is_file() and path.stat().st_size > 0
        report.add(
            f"artifact:{rel}",
            exists,
            f"Found ({path.stat().st_size} bytes)" if exists else f"Missing or empty: {path}",
        )
