from __future__ import annotations

from pathlib import Path

from agentic_publishing_pipeline.agents.factory import build_agents
from agentic_publishing_pipeline.contracts import BiDiSection, ChapterDraft, ChapterDrafts
from agentic_publishing_pipeline.runtime import load_registry
from agentic_publishing_pipeline.tasks import REQUIRED_CHAPTER_IDS
from agentic_publishing_pipeline.tasks.completeness import run_manuscript_preflight
from agentic_publishing_pipeline.tasks.factory import build_manuscript_tasks

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_task_factory_builds_seven_pre_review_tasks() -> None:
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
    assert len(tasks) == 7
    assert [task.output_pydantic.__name__ for task in tasks] == [
        "ResearchNotes",
        "Outline",
        "ChapterDrafts",
        "AssetSpecs",
        "BiDiSection",
        "BibliographyBundle",
        "ReviewerSignal",
    ]
    assert all(task.agent is not agents["latex"] for task in tasks)


def test_complete_manuscript_preflight_passes() -> None:
    keys = tuple(f"k{i}" for i in range(8))
    hebrew = " ".join(["זיכרון", "סוכן", "reasoning", "יציב"] * 12)
    chapters = []
    for index, chapter_id in enumerate(REQUIRED_CHAPTER_IDS):
        body = f"# {chapter_id}\n\nword " * 20 + f"\n<!-- CITATION: {keys[index]} -->\n"
        if chapter_id == "memory":
            body += hebrew
        chapters.append(ChapterDraft(chapter_id=chapter_id, heading=chapter_id, body_markdown=body))
    drafts = ChapterDrafts(run_id="r", chapters=chapters)
    bidi = BiDiSection(
        run_id="r",
        chapter_id="memory",
        hebrew_body=hebrew,
        inline_english_terms=["reasoning"],
    )
    report = run_manuscript_preflight(
        drafts,
        bidi=bidi,
        required_chapter_ids=REQUIRED_CHAPTER_IDS,
        manifest_keys=keys,
        min_words_per_chapter=5,
        min_total_words=40,
    )
    assert report.passed
    assert report.missing_source_keys == ()


def test_preflight_rejects_missing_citation() -> None:
    drafts = ChapterDrafts(
        run_id="r",
        chapters=[
            ChapterDraft(chapter_id="introduction", heading="x", body_markdown="# Intro\n\nwords")
        ],
    )
    bidi = BiDiSection(
        run_id="r",
        chapter_id="memory",
        hebrew_body=" ".join(["זיכרון"] * 40),
        inline_english_terms=["LLM"],
    )
    report = run_manuscript_preflight(
        drafts,
        bidi=bidi,
        required_chapter_ids=("introduction",),
        manifest_keys=("missing",),
        min_words_per_chapter=1,
        min_total_words=1,
    )
    assert not report.passed
    assert "locked sources not cited" in " ".join(report.errors)
