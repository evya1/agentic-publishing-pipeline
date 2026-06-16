from __future__ import annotations

from pathlib import Path

import pytest

from agentic_publishing_pipeline.latex.approval_loader import (
    ApprovedChapter,
    ApprovedManuscript,
)
from agentic_publishing_pipeline.latex.config_models import Phase9Config


@pytest.fixture
def config() -> Phase9Config:
    return Phase9Config.model_validate(
        {
            "metadata": {
                "title": "Agent Systems",
                "subtitle": "A deterministic test",
                "authors": ["Ada Example"],
                "group_code": "group-01",
                "course": "Orchestration",
                "date_text": "2026",
            },
            "chapter_order": ["planning", "memory"],
            "minimum_hebrew_words": 2,
            "minimum_words_per_chapter": 2,
            "minimum_total_words": 8,
            "require_all_bibliography_entries": False,
            "chapter_citation_requirements": {},
            "macros": ["AgentState", "ToolCall"],
            "nomenclature": [["LLM", "Large language model"], ["RAG", "Retrieval"]],
            "english_index": [{"term": "agent", "chapter_id": "planning"}],
            "hebrew_index": [{"term": "זיכרון", "chapter_id": "memory"}],
            "assets": [
                {
                    "kind": "image",
                    "asset_id": "graph",
                    "chapter_id": "planning",
                    "caption": "Graph",
                    "label": "graph",
                    "payload": {"width": 0.8},
                },
                {
                    "kind": "table",
                    "asset_id": "table",
                    "chapter_id": "planning",
                    "caption": "Table",
                    "label": "table",
                    "payload": {"columns": ["A", "B"], "rows": [["1", "2"]]},
                },
                {
                    "kind": "equation",
                    "asset_id": "equation",
                    "chapter_id": "planning",
                    "label": "score",
                    "payload": {"template": "weighted-sum"},
                },
                {
                    "kind": "equation_ref",
                    "asset_id": "equation_ref",
                    "chapter_id": "memory",
                    "label": "score-ref",
                    "payload": {"target": "score", "sentence": "[EQUATION] is reused."},
                },
                {
                    "kind": "theorem",
                    "asset_id": "definition",
                    "chapter_id": "memory",
                    "label": "state",
                    "payload": {"kind": "definition", "statement": "State is bounded."},
                },
                {
                    "kind": "tikz",
                    "asset_id": "loop",
                    "chapter_id": "planning",
                    "caption": "Loop",
                    "label": "loop",
                    "payload": {
                        "nodes": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}],
                        "edges": [["a", "b"]],
                    },
                },
            ],
        }
    )


@pytest.fixture
def manuscript(tmp_path: Path) -> ApprovedManuscript:
    chapter_root = tmp_path / "chapters"
    chapter_root.mkdir()
    planning = chapter_root / "planning.md"
    memory = chapter_root / "memory.md"
    planning.write_text(
        "# Planning\n\nAgents plan steps and cite \\cite{known}.\n", encoding="utf-8"
    )
    memory.write_text("# Memory\n\nזיכרון סוכנים with LLM state.\n", encoding="utf-8")
    return ApprovedManuscript(
        root=tmp_path,
        revision="abc123",
        chapters=(
            ApprovedChapter("planning", planning, planning.read_text(encoding="utf-8")),
            ApprovedChapter("memory", memory, memory.read_text(encoding="utf-8")),
        ),
    )
