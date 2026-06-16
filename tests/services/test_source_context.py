from __future__ import annotations

from pathlib import Path

import pytest

from agentic_publishing_pipeline.services.source_context import (
    SourceContextError,
    load_source_context,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_load_source_context_current_manifest() -> None:
    context = load_source_context(REPO_ROOT / "config" / "article_sources.yaml")
    assert len(context.records) == 10
    assert "ye2024mirai" in context.citation_keys
    assert "citation_key: ye2024mirai" in context.as_prompt_text()


def test_duplicate_keys_rejected(tmp_path: Path) -> None:
    path = tmp_path / "sources.yaml"
    path.write_text(
        "sources:\n"
        "- citation_key: x\n  title: A\n  intended_use: one\n"
        "- citation_key: x\n  title: B\n  intended_use: two\n",
        encoding="utf-8",
    )
    with pytest.raises(SourceContextError, match="duplicate citation key"):
        load_source_context(path)


def test_context_path_traversal_rejected(tmp_path: Path) -> None:
    path = tmp_path / "sources.yaml"
    path.write_text(
        "sources:\n- citation_key: x\n  title: A\n  context_path: ../escape.txt\n",
        encoding="utf-8",
    )
    with pytest.raises(SourceContextError, match="escapes"):
        load_source_context(path)
