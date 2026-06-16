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
    BIDI_BEGIN_MARKER,
    BIDI_END_MARKER,
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


def _outputs(memory_body: str, hebrew: str | None = None) -> ManuscriptOutputs:
    body = hebrew if hebrew is not None else " ".join(["זיכרון"] * 40) + " reasoning"
    return ManuscriptOutputs(
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
                    body_markdown=memory_body,
                )
            ],
        ),
        assets=AssetSpecs(run_id="r"),
        bidi=BiDiSection(
            run_id="r",
            chapter_id="memory",
            hebrew_body=body,
            inline_english_terms=["reasoning"],
        ),
        bibliography=BibliographyBundle(run_id="r"),
        reviewer=ReviewerSignal(run_id="r", signal="pass"),
    )


def test_composition_is_idempotent_under_repeated_application() -> None:
    once = compose_manuscript_outputs(_outputs("# Memory\n\nWriter-only body."))
    twice = compose_manuscript_outputs(once)
    assert once.chapters.chapters[0].body_markdown == twice.chapters.chapters[0].body_markdown
    assert once.chapters.chapters[0].body_markdown.count(BIDI_BEGIN_MARKER) == 1
    assert once.chapters.chapters[0].body_markdown.count(BIDI_END_MARKER) == 1


def test_composition_replaces_existing_section_after_reformatting() -> None:
    composed = compose_manuscript_outputs(_outputs("# Memory\n\nWriter-only body."))
    body = composed.chapters.chapters[0].body_markdown
    reformatted = body.replace("\n\n", "\n\n   \n\n").rstrip() + "\n   \n"
    follow_up = _outputs(reformatted)
    final = compose_manuscript_outputs(follow_up)
    assert final.chapters.chapters[0].body_markdown.count(BIDI_BEGIN_MARKER) == 1
    assert final.chapters.chapters[0].body_markdown.count(BIDI_END_MARKER) == 1


def test_composition_replaces_truncated_existing_section() -> None:
    composed = compose_manuscript_outputs(_outputs("# Memory\n\nWriter-only body."))
    body = composed.chapters.chapters[0].body_markdown
    truncated = body[: body.index(BIDI_END_MARKER)] + BIDI_END_MARKER
    follow_up = _outputs(truncated)
    final = compose_manuscript_outputs(follow_up)
    assert final.chapters.chapters[0].body_markdown.count(BIDI_BEGIN_MARKER) == 1
    assert final.chapters.chapters[0].body_markdown.count(BIDI_END_MARKER) == 1


def test_composition_ignores_incidental_hebrew_in_prose() -> None:
    hebrew = " ".join(["זיכרון", "סוכן", "תכנון", "הקשר"] * 12) + " reasoning"
    memory = "# Memory\n\n" + hebrew + "\n\nMore writer prose follows."
    composed = compose_manuscript_outputs(_outputs(memory, hebrew=hebrew))
    body = composed.chapters.chapters[0].body_markdown
    assert body.count(BIDI_BEGIN_MARKER) == 1
    assert body.endswith("\n")


def test_composition_rejects_duplicate_markers() -> None:
    bad = (
        "# Memory\n\n"
        f"{BIDI_BEGIN_MARKER}\nold body\n{BIDI_END_MARKER}\n\n"
        f"{BIDI_BEGIN_MARKER}\nother\n{BIDI_END_MARKER}\n"
    )
    with pytest.raises(ManuscriptCompositionError, match="duplicate BiDi-section markers"):
        compose_manuscript_outputs(_outputs(bad))


def test_composition_rejects_unbalanced_markers() -> None:
    bad = f"# Memory\n\n{BIDI_BEGIN_MARKER}\nbody without end\n"
    with pytest.raises(ManuscriptCompositionError, match="unbalanced BiDi markers"):
        compose_manuscript_outputs(_outputs(bad))


def test_composition_rejects_empty_bidi_body_via_internal_helper() -> None:
    from agentic_publishing_pipeline.crews.composition import _merge_bidi_into_memory

    drafts = _outputs("# Memory\n\nbody").chapters
    with pytest.raises(ManuscriptCompositionError, match="empty"):
        _merge_bidi_into_memory(drafts, "   ")


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
