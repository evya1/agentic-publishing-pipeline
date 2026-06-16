"""Load exactly the canonical Markdown approved by the existing review gate."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..crews._review_gate import compute_draft_revision, enforce_review_gate


@dataclass(frozen=True)
class ApprovedChapter:
    chapter_id: str
    path: Path
    markdown: str


@dataclass(frozen=True)
class ApprovedManuscript:
    root: Path
    revision: str
    chapters: tuple[ApprovedChapter, ...]


def load_approved_manuscript(
    *,
    generated_md_root: Path,
    run_log_root: Path,
    chapter_order: tuple[str, ...],
) -> ApprovedManuscript:
    """Enforce approval, then load the exact configured chapter set."""
    enforce_review_gate(generated_md_root, run_log_root)
    chapter_root = generated_md_root / "chapters"
    by_id = {path.stem: path for path in chapter_root.glob("*.md")}
    if not by_id:
        raise ValueError(f"approved chapter directory is empty: {chapter_root}")
    if missing := sorted(set(chapter_order) - set(by_id)):
        raise ValueError(
            f"approved chapter directory is missing required chapters: {missing}"
        )
    ordered = list(chapter_order)
    ordered.extend(sorted(set(by_id) - set(chapter_order)))
    chapters = tuple(
        ApprovedChapter(
            chapter_id=chapter_id,
            path=by_id[chapter_id],
            markdown=by_id[chapter_id].read_text(encoding="utf-8"),
        )
        for chapter_id in ordered
    )
    return ApprovedManuscript(
        root=generated_md_root,
        revision=compute_draft_revision(generated_md_root),
        chapters=chapters,
    )
