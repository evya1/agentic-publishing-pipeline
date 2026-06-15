"""Regression tests for unsafe chapter_id rejection (P6-I01 follow-up)."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_publishing_pipeline.crews._phase6_generate import (
    CANONICAL_CHAPTERS_SUBDIR,
    CANONICAL_MD,
    UnsafeChapterIdError,
    _write_chapter,
    run_phase6_generate,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / "config" / "article_sources.yaml"


def _md_root(tmp_path: Path) -> Path:
    return tmp_path / CANONICAL_MD


def test_safe_slug_writes_under_chapters_root(tmp_path: Path) -> None:
    md_root = _md_root(tmp_path)
    target = _write_chapter(md_root, "planning", "body\n")
    chapters_root = (md_root / CANONICAL_CHAPTERS_SUBDIR).resolve()
    assert target == (chapters_root / "planning.md").resolve()
    assert target.read_text(encoding="utf-8") == "body\n"


@pytest.mark.parametrize(
    "bad_id",
    [
        "",
        ".",
        "..",
        "/etc/passwd",
        "/tmp/phase6_escape_probe",
        "../escape",
        "../../escape",
        "chapters/../escape",
        "foo/bar",
        "foo\\bar",
        "~root",
        "C:foo",
        "C:\\Windows\\foo",
        "with space",
        "with.dot",
        "with$dollar",
        "with\x00nul",
        "-leading-dash",
        "_leading-underscore",
    ],
)
def test_unsafe_chapter_ids_rejected_without_writing(
    tmp_path: Path, bad_id: str
) -> None:
    md_root = _md_root(tmp_path)
    sibling_witness = tmp_path / "escape_witness"
    sibling_witness.mkdir()
    before_repo = {p for p in tmp_path.rglob("*")}
    with pytest.raises(UnsafeChapterIdError):
        _write_chapter(md_root, bad_id, "body\n")
    after_repo = {p for p in tmp_path.rglob("*")}
    new_files = after_repo - before_repo
    assert new_files == set(), f"unsafe write created files: {new_files}"
    chapters_root = md_root / CANONICAL_CHAPTERS_SUBDIR
    assert not chapters_root.exists() or not any(chapters_root.iterdir())


def test_absolute_chapter_id_does_not_escape_repo(tmp_path: Path) -> None:
    """An absolute path probe must never reach the global filesystem."""
    md_root = _md_root(tmp_path)
    probe = "/tmp/phase6_escape_probe_xyz_4242"
    with pytest.raises(UnsafeChapterIdError):
        _write_chapter(md_root, probe, "should never be written")
    assert not Path(probe + ".md").exists()
    assert not Path(probe).exists()


def test_non_string_chapter_id_rejected(tmp_path: Path) -> None:
    md_root = _md_root(tmp_path)
    with pytest.raises(UnsafeChapterIdError):
        _write_chapter(md_root, 17, "body\n")  # type: ignore[arg-type]


def test_normal_offline_flow_still_succeeds(tmp_path: Path) -> None:
    record = run_phase6_generate(tmp_path.resolve(), MANIFEST)
    chapters_root = (
        tmp_path / CANONICAL_MD / CANONICAL_CHAPTERS_SUBDIR
    ).resolve()
    for rel in record.chapters_written:
        target = (tmp_path / rel).resolve()
        target.relative_to(chapters_root)
        assert target.exists()
