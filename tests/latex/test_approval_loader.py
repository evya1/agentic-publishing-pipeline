import hashlib
import json
from pathlib import Path

from agentic_publishing_pipeline.latex.approval_loader import load_approved_manuscript


def _revision(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*.md") if p.name != "README.md"):
        rel = path.resolve().relative_to(root.resolve()).as_posix().encode()
        content = path.read_bytes()
        digest.update(f"P:{len(rel)}:".encode() + rel)
        digest.update(f"C:{len(content)}:".encode() + content)
    return digest.hexdigest()


def test_loader_uses_existing_review_gate_and_preserves_order(
    tmp_path: Path,
) -> None:
    md_root = tmp_path / "generated_markdown"
    chapters = md_root / "chapters"
    logs = tmp_path / "run_logs"
    chapters.mkdir(parents=True)
    logs.mkdir()
    (chapters / "planning.md").write_text("# Planning\n", encoding="utf-8")
    (chapters / "memory.md").write_text("# Memory\n", encoding="utf-8")
    (logs / "review_record.json").write_text(
        json.dumps(
            {
                "reviewer": "Human Maintainer",
                "draft_sha256": _revision(md_root),
                "reviewed_at": "T00:00:00Z",
                "verdict": "approved",
                "schema_version": "v1",
            }
        ),
        encoding="utf-8",
    )
    result = load_approved_manuscript(
        generated_md_root=md_root,
        run_log_root=logs,
        chapter_order=("planning", "memory"),
    )
    assert [chapter.chapter_id for chapter in result.chapters] == ["planning", "memory"]


def test_loader_raises_on_missing_required_chapter(
    tmp_path: Path,
) -> None:
    import pytest

    md_root = tmp_path / "generated_markdown"
    chapters = md_root / "chapters"
    logs = tmp_path / "run_logs"
    chapters.mkdir(parents=True)
    logs.mkdir()
    (chapters / "planning.md").write_text("# Planning\n", encoding="utf-8")
    (logs / "review_record.json").write_text(
        json.dumps(
            {
                "reviewer": "Human Maintainer",
                "draft_sha256": _revision(md_root),
                "reviewed_at": "T00:00:00Z",
                "verdict": "approved",
                "schema_version": "v1",
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="missing required chapters"):
        load_approved_manuscript(
            generated_md_root=md_root,
            run_log_root=logs,
            chapter_order=("planning", "memory"),
        )
