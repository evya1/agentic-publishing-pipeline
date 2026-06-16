"""Generate the human review packet for a candidate manuscript."""

from __future__ import annotations

import difflib
import hashlib
from pathlib import Path

from ..tasks.completeness import ManuscriptPreflightReport
from ..tools.fileio import FileIO
from ._review_gate import compute_draft_revision


def write_review_packet(
    *,
    file_io: FileIO,
    candidate_root: Path,
    previous_root: Path,
    report: ManuscriptPreflightReport,
    reviewer_instructions: str,
) -> Path:
    """Write paths, hashes, counts, coverage, diff, and response templates."""
    chapter_paths = sorted((candidate_root / "chapters").glob("*.md"))
    lines = [
        "# Phase 6 manuscript review packet",
        "",
        f"Aggregate SHA-256: `{compute_draft_revision(candidate_root)}`",
        "",
        "## Candidate files",
        "",
    ]
    lines.extend(_candidate_lines(candidate_root, chapter_paths, report))
    lines.extend(_coverage_lines(report))
    lines.extend(("", "## Diff from previous canonical revision", "", "```diff"))
    lines.extend(_tree_diff(previous_root, candidate_root))
    lines.extend(("```", "", "## Reviewer instructions", "", reviewer_instructions))
    return file_io.write_text("review_packet.md", "\n".join(lines).rstrip() + "\n")


def _candidate_lines(
    candidate_root: Path,
    chapter_paths: list[Path],
    report: ManuscriptPreflightReport,
) -> list[str]:
    lines: list[str] = []
    for path in chapter_paths:
        rel = path.relative_to(candidate_root).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"- `{rel}` — {report.word_counts.get(path.stem, 0)} words")
        lines.append(f"  - sha256: `{digest}`")
    return lines


def _coverage_lines(report: ManuscriptPreflightReport) -> list[str]:
    lines = [
        "",
        "## Citation coverage",
        "",
        f"Cited keys: {', '.join(report.cited_keys)}",
        f"Missing keys: {', '.join(report.missing_source_keys) or 'none'}",
        "",
        "## Preflight",
        "",
        f"Result: {'PASS' if report.passed else 'FAIL'}",
        f"Total words: {report.total_words}",
    ]
    lines.extend(f"- ERROR: {value}" for value in report.errors)
    lines.extend(f"- WARNING: {value}" for value in report.warnings)
    return lines


def _tree_diff(previous_root: Path, candidate_root: Path) -> list[str]:
    names = sorted(_markdown_names(previous_root) | _markdown_names(candidate_root))
    output: list[str] = []
    for name in names:
        before_path = previous_root / name
        after_path = candidate_root / name
        before = _read_lines(before_path)
        after = _read_lines(after_path)
        output.extend(
            difflib.unified_diff(
                before,
                after,
                fromfile=f"old/{name}",
                tofile=f"new/{name}",
                lineterm="",
            )
        )
    return output or ["No textual differences detected."]


def _markdown_names(root: Path) -> set[str]:
    if not root.exists():
        return set()
    return {path.relative_to(root).as_posix() for path in root.rglob("*.md")}


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []
