from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from crewai import Process

from agentic_publishing_pipeline.agents.factory import build_agents
from agentic_publishing_pipeline.contracts import (
    AssetSpecs,
    BibliographyBundle,
    BiDiSection,
    ChapterDraft,
    ChapterDrafts,
    Outline,
    ResearchNotes,
    ReviewerSignal,
)
from agentic_publishing_pipeline.crews.composition import (
    ManuscriptCompositionError,
    compose_manuscript_outputs,
)
from agentic_publishing_pipeline.crews.manuscript_crew import build_manuscript_crew
from agentic_publishing_pipeline.crews.result_parser import (
    CrewResultError,
    ManuscriptOutputs,
    parse_manuscript_outputs,
)
from agentic_publishing_pipeline.runtime import load_registry
from agentic_publishing_pipeline.tasks.factory import build_manuscript_tasks

REPO_ROOT = Path(__file__).resolve().parents[2]


def _tasks():
    registry = load_registry(REPO_ROOT / "config" / "prompt_registry")
    agents = build_agents(registry=registry, llm_factory=lambda a, t, m: "fixture")
    tasks = build_manuscript_tasks(
        agents=agents,
        registry=registry,
        topic="Reasoning",
        source_context_text="citation_key: k",
        citation_keys=["k"],
        target_pages=15,
        target_words=1000,
    )
    return agents, tasks


def test_crew_is_real_sequential_and_pre_review_only() -> None:
    agents, tasks = _tasks()
    crew = build_manuscript_crew(agents=agents, tasks=tasks)
    assert crew.process == Process.sequential
    assert len(crew.tasks) == 7
    assert all(task.agent is not agents["latex"] for task in crew.tasks)


def test_parse_manuscript_outputs_validates_order_and_types() -> None:
    hebrew = " ".join(["זיכרון"] * 40)
    values = [
        ResearchNotes(
            run_id="r",
            topic="t",
            dimensions=[{"dimension": "planning", "summary": "s"}],
        ),
        Outline(
            run_id="r",
            chapters=[{"chapter_id": "c", "title": "t", "summary": "s"}],
            target_total_pages=1,
        ),
        ChapterDrafts(
            run_id="r",
            chapters=[ChapterDraft(chapter_id="c", heading="h", body_markdown="# H")],
        ),
        AssetSpecs(run_id="r"),
        BiDiSection(
            run_id="r",
            chapter_id="memory",
            hebrew_body=hebrew,
            inline_english_terms=["LLM"],
        ),
        BibliographyBundle(run_id="r"),
        ReviewerSignal(run_id="r", signal="pass"),
    ]
    result = SimpleNamespace(tasks_output=[SimpleNamespace(pydantic=value) for value in values])
    assert parse_manuscript_outputs(result).reviewer.signal == "pass"


def test_parse_manuscript_outputs_rejects_missing_output() -> None:
    with pytest.raises(CrewResultError):
        parse_manuscript_outputs(SimpleNamespace(tasks_output=[]))


def test_composition_merges_bidi_into_memory_chapter() -> None:
    hebrew = " ".join(["זיכרון", "סוכן", "תכנון", "הקשר"] * 12) + " reasoning"
    outputs = ManuscriptOutputs(
        research=ResearchNotes(
            run_id="r",
            topic="t",
            dimensions=[{"dimension": "memory", "summary": "s"}],
        ),
        outline=Outline(
            run_id="r",
            chapters=[{"chapter_id": "memory", "title": "Memory", "summary": "s"}],
            target_total_pages=1,
        ),
        chapters=ChapterDrafts(
            run_id="r",
            chapters=[
                ChapterDraft(
                    chapter_id="memory",
                    heading="Memory",
                    body_markdown="# Memory\n\nWriter-only body.",
                )
            ],
        ),
        assets=AssetSpecs(run_id="r"),
        bidi=BiDiSection(
            run_id="r",
            chapter_id="memory",
            hebrew_body=hebrew,
            inline_english_terms=["reasoning"],
        ),
        bibliography=BibliographyBundle(run_id="r"),
        reviewer=ReviewerSignal(run_id="r", signal="pass"),
    )
    composed = compose_manuscript_outputs(outputs)
    assert hebrew in composed.chapters.chapters[0].body_markdown
    assert hebrew not in outputs.chapters.chapters[0].body_markdown


def test_composition_rejects_missing_memory_chapter() -> None:
    hebrew = " ".join(["זיכרון"] * 40) + " reasoning"
    outputs = ManuscriptOutputs(
        research=ResearchNotes(
            run_id="r",
            topic="t",
            dimensions=[{"dimension": "memory", "summary": "s"}],
        ),
        outline=Outline(
            run_id="r",
            chapters=[{"chapter_id": "planning", "title": "Planning", "summary": "s"}],
            target_total_pages=1,
        ),
        chapters=ChapterDrafts(
            run_id="r",
            chapters=[ChapterDraft(chapter_id="planning", heading="Planning", body_markdown="# P")],
        ),
        assets=AssetSpecs(run_id="r"),
        bidi=BiDiSection(
            run_id="r",
            chapter_id="memory",
            hebrew_body=hebrew,
            inline_english_terms=["reasoning"],
        ),
        bibliography=BibliographyBundle(run_id="r"),
        reviewer=ReviewerSignal(run_id="r", signal="pass"),
    )
    with pytest.raises(ManuscriptCompositionError, match="missing memory"):
        compose_manuscript_outputs(outputs)
