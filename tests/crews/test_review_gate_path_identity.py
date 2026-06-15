"""Regression tests for path-identity draft revision (P6-I02 follow-up).

The aggregate hash must bind each draft file's normalized POSIX relative
path together with its byte contents so that rename, directory move,
addition, removal, and content mutation all invalidate the revision —
while an unchanged tree remains deterministic.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_publishing_pipeline.crews._review_gate import (
    HumanReviewRequired,
    ReviewRecord,
    compute_draft_revision,
    enforce_review_gate,
    make_review_record,
    write_review_record,
)


def _seed_two_chapters(md_root: Path) -> tuple[Path, Path]:
    a = md_root / "chapters" / "alpha.md"
    b = md_root / "chapters" / "beta.md"
    a.parent.mkdir(parents=True, exist_ok=True)
    a.write_text("# Alpha\nbody-a\n", encoding="utf-8")
    b.write_text("# Beta\nbody-b\n", encoding="utf-8")
    return a, b


def test_unchanged_tree_is_deterministic(tmp_path: Path) -> None:
    md_root = tmp_path / "generated_markdown"
    _seed_two_chapters(md_root)
    assert compute_draft_revision(md_root) == compute_draft_revision(md_root)


def test_content_change_invalidates(tmp_path: Path) -> None:
    md_root = tmp_path / "generated_markdown"
    a, _ = _seed_two_chapters(md_root)
    sha_before = compute_draft_revision(md_root)
    a.write_text("# Alpha\nbody-a-MODIFIED\n", encoding="utf-8")
    assert compute_draft_revision(md_root) != sha_before


def test_basename_rename_invalidates(tmp_path: Path) -> None:
    md_root = tmp_path / "generated_markdown"
    a, _ = _seed_two_chapters(md_root)
    sha_before = compute_draft_revision(md_root)
    a.rename(a.with_name("alpha-renamed.md"))
    assert compute_draft_revision(md_root) != sha_before


def test_directory_move_invalidates(tmp_path: Path) -> None:
    """Moving same filename + content to another subdir must invalidate.

    This is the exact case Codex flagged: prior basename-only hashing
    produced equal aggregate revisions before and after the move.
    """
    md_root = tmp_path / "generated_markdown"
    a, _ = _seed_two_chapters(md_root)
    sha_before = compute_draft_revision(md_root)
    moved_dir = md_root / "research_notes"
    moved_dir.mkdir(parents=True, exist_ok=True)
    moved = moved_dir / a.name
    moved.write_bytes(a.read_bytes())
    a.unlink()
    assert compute_draft_revision(md_root) != sha_before


def test_addition_invalidates(tmp_path: Path) -> None:
    md_root = tmp_path / "generated_markdown"
    _seed_two_chapters(md_root)
    sha_before = compute_draft_revision(md_root)
    (md_root / "chapters" / "gamma.md").write_text("# Gamma\n", encoding="utf-8")
    assert compute_draft_revision(md_root) != sha_before


def test_removal_invalidates(tmp_path: Path) -> None:
    md_root = tmp_path / "generated_markdown"
    a, _ = _seed_two_chapters(md_root)
    sha_before = compute_draft_revision(md_root)
    a.unlink()
    assert compute_draft_revision(md_root) != sha_before


def test_readme_files_are_excluded(tmp_path: Path) -> None:
    md_root = tmp_path / "generated_markdown"
    _seed_two_chapters(md_root)
    sha_before = compute_draft_revision(md_root)
    (md_root / "README.md").write_text("layout doc\n", encoding="utf-8")
    (md_root / "chapters" / "README.md").write_text("more docs\n", encoding="utf-8")
    assert compute_draft_revision(md_root) == sha_before


def test_stale_recorded_sha_is_rejected(tmp_path: Path) -> None:
    md_root = tmp_path / "generated_markdown"
    _seed_two_chapters(md_root)
    log_root = tmp_path / "run_logs"
    rec = ReviewRecord(
        reviewer="Alice Reviewer",
        draft_sha256="deadbeef" * 8,
        reviewed_at="2026-01-01T00:00:00+00:00",
        verdict="approved",
    )
    write_review_record(rec, log_root)
    with pytest.raises(HumanReviewRequired, match="changed since approval"):
        enforce_review_gate(md_root, log_root)


def test_human_approval_passes_only_in_isolated_environment(tmp_path: Path) -> None:
    md_root = tmp_path / "generated_markdown"
    _seed_two_chapters(md_root)
    log_root = tmp_path / "run_logs"
    rec = make_review_record(
        reviewer="Alice Reviewer", generated_md_root=md_root, verdict="approved"
    )
    write_review_record(rec, log_root)
    enforce_review_gate(md_root, log_root)
