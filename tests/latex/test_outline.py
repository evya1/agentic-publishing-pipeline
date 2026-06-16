from pathlib import Path

from agentic_publishing_pipeline.latex.outline import load_outline_chapter_ids


def test_outline_supports_explicit_phase6_ids(tmp_path: Path) -> None:
    path = tmp_path / "outline.md"
    path.write_text(
        "1. Intro (`chapter_id: introduction`)\n2. Tool (`chapter_id: tool_use`)\n",
        encoding="utf-8",
    )
    assert load_outline_chapter_ids(path) == ("introduction", "tool_use")


def test_outline_supports_generated_h2_headings(tmp_path: Path) -> None:
    path = tmp_path / "outline.md"
    path.write_text(
        "# Outline\n\n## Introduction\n\nSummary\n\n## Tool Use\n\nSummary\n",
        encoding="utf-8",
    )
    assert load_outline_chapter_ids(path) == ("introduction", "tool_use")
