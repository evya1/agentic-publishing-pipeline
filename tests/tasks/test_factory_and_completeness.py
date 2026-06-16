from __future__ import annotations

from pathlib import Path

from agentic_publishing_pipeline.agents.factory import build_agents
from agentic_publishing_pipeline.contracts import (
    AssetSpec,
    AssetSpecs,
    BibEntry,
    BibliographyBundle,
    BiDiSection,
    ChapterDraft,
    ChapterDrafts,
)
from agentic_publishing_pipeline.runtime import load_registry
from agentic_publishing_pipeline.services.source_context import SourceContext, SourceRecord
from agentic_publishing_pipeline.tasks import REQUIRED_CHAPTER_IDS
from agentic_publishing_pipeline.tasks.completeness import run_manuscript_preflight
from agentic_publishing_pipeline.tasks.factory import build_manuscript_tasks

REPO_ROOT = Path(__file__).resolve().parents[2]
HEBREW = " ".join(["זיכרון", "סוכן", "תכנון", "הקשר"] * 12)
BIDI_BODY = f"{HEBREW} reasoning retrieval"


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


def _drafts(body: str | None = None) -> ChapterDrafts:
    text = body or (
        "# Memory\n\n"
        "This chapter has enough words for the configured floor and links assets. "
        "<!-- FIGURE: memory/figure --> <!-- TABLE: memory/table --> "
        "<!-- EQUATION: memory/equation --> <!-- CITATION: k1 -->\n\n"
        f"{BIDI_BODY}\n"
    )
    return ChapterDrafts(
        run_id="r",
        chapters=[ChapterDraft(chapter_id="memory", heading="Memory", body_markdown=text)],
    )


def _bidi(body: str = BIDI_BODY, terms: list[str] | None = None) -> BiDiSection:
    return BiDiSection(
        run_id="r",
        chapter_id="memory",
        hebrew_body=body,
        inline_english_terms=terms or ["reasoning", "retrieval"],
    )


def _assets(extra: list[AssetSpec] | None = None) -> AssetSpecs:
    specs = [
        AssetSpec(kind="image", slot="memory/figure-1", chapter_id="memory"),
        AssetSpec(kind="table", slot="memory/table-2", chapter_id="memory"),
        AssetSpec(kind="equation", slot="memory/equation-3", chapter_id="memory"),
    ]
    return AssetSpecs(run_id="r", assets=specs + list(extra or []))


def _bibliography(entries: list[BibEntry] | None = None) -> BibliographyBundle:
    return BibliographyBundle(
        run_id="r",
        entries=entries
        or [
            BibEntry(
                citation_key="k1",
                entry_type="article",
                title="Locked Source",
                year=2025,
                authors=["A. Author"],
                arxiv_id="2501.00001",
                verification_status="verified",
            )
        ],
        placeholder_resolution={"k1": "k1"},
        manifest_coverage=["k1"],
    )


def _source_context() -> SourceContext:
    return SourceContext(
        manifest_path=REPO_ROOT / "config" / "article_sources.yaml",
        records=(
            SourceRecord(
                citation_key="k1",
                title="Locked Source",
                authors=("A. Author",),
                year="2025",
                arxiv_id="2501.00001",
                doi=None,
                trusted_summary="Trusted locked context.",
            ),
        ),
    )


def _preflight(**overrides: object):
    params = {
        "drafts": _drafts(),
        "bidi": _bidi(),
        "required_chapter_ids": ("memory",),
        "manifest_keys": ("k1",),
        "min_words_per_chapter": 5,
        "min_total_words": 5,
        "assets": _assets(),
        "bibliography": _bibliography(),
        "source_context": _source_context(),
    }
    params.update(overrides)
    drafts = params.pop("drafts")
    return run_manuscript_preflight(drafts, **params)


def test_complete_manuscript_preflight_passes_all_rules() -> None:
    report = _preflight()
    assert report.passed
    assert report.missing_source_keys == ()
    assert report.warnings == ()


def test_preflight_rejects_missing_required_chapter() -> None:
    report = _preflight(required_chapter_ids=REQUIRED_CHAPTER_IDS)
    assert not report.passed
    assert "missing required chapters" in " ".join(report.errors)


def test_preflight_rejects_low_word_count_and_total() -> None:
    report = _preflight(min_words_per_chapter=500, min_total_words=500)
    assert not report.passed
    assert "chapter memory has" in " ".join(report.errors)
    assert "manuscript has" in " ".join(report.errors)


def test_preflight_rejects_missing_placeholder_kind() -> None:
    report = _preflight(
        drafts=_drafts("# Memory\n\nwords words <!-- CITATION: k1 -->\n\n" + BIDI_BODY)
    )
    assert not report.passed
    assert "missing placeholder kinds" in " ".join(report.errors)


def test_preflight_validates_asset_slots_and_rejects_orphans_duplicates() -> None:
    duplicate = AssetSpec(kind="image", slot="memory/figure-1", chapter_id="memory")
    orphan = AssetSpec(kind="table", slot="memory/table-99", chapter_id="memory")
    report = _preflight(assets=_assets([duplicate, orphan]))
    assert not report.passed
    assert "duplicate asset slot" in " ".join(report.errors)
    assert "orphan asset slot" in " ".join(report.errors)


def test_preflight_rejects_asset_kind_mismatch() -> None:
    bad = AssetSpecs(
        run_id="r",
        assets=[
            AssetSpec(kind="table", slot="memory/figure-1", chapter_id="memory"),
            AssetSpec(kind="table", slot="memory/table-2", chapter_id="memory"),
            AssetSpec(kind="equation", slot="memory/equation-3", chapter_id="memory"),
        ],
    )
    report = _preflight(assets=bad)
    assert not report.passed
    assert "does not match FIGURE" in " ".join(report.errors)


def test_preflight_rejects_unknown_and_missing_citations() -> None:
    body = "# Memory\n\nwords words <!-- CITATION: not_locked -->\n\n" + BIDI_BODY
    report = _preflight(drafts=_drafts(body), manifest_keys=("k1",))
    assert not report.passed
    assert "unknown citation keys" in " ".join(report.errors)
    assert "locked sources not cited" in " ".join(report.errors)


def test_preflight_rejects_bibliography_inconsistency() -> None:
    entry = BibEntry(
        citation_key="k1",
        entry_type="article",
        title="Locked Source",
        year=2025,
        verification_status="unverified",
    )
    report = _preflight(bibliography=_bibliography([entry]))
    assert not report.passed
    assert "not verified" in " ".join(report.errors)


def test_preflight_rejects_source_provenance_drift() -> None:
    entry = BibEntry(
        citation_key="k1",
        entry_type="article",
        title="Fabricated Title",
        year=2025,
        arxiv_id="2501.00001",
        verification_status="verified",
    )
    report = _preflight(bibliography=_bibliography([entry]))
    assert not report.passed
    assert "title drift" in " ".join(report.errors)


def test_preflight_rejects_unembedded_or_insufficient_bidi_as_error() -> None:
    report = _preflight(
        drafts=_drafts("# Memory\n\nwords words <!-- CITATION: k1 -->"),
        min_hebrew_tokens=50,
        min_embedded_english_terms=3,
    )
    assert not report.passed
    text = " ".join(report.errors)
    assert "Hebrew tokens" in text
    assert "embedded English terms" in text
    assert "not embedded verbatim" in text


def test_preflight_rejects_bibliography_duplicates_and_resolution_drift() -> None:
    duplicate = BibEntry(
        citation_key="k2",
        entry_type="article",
        title="Other",
        year=2025,
        verification_status="verified",
    )
    bibliography = BibliographyBundle(
        run_id="r",
        entries=[duplicate, duplicate],
        placeholder_resolution={"p": "not_locked"},
        manifest_coverage=[],
    )
    report = _preflight(bibliography=bibliography)
    text = " ".join(report.errors)
    assert "duplicate bibliography entries" in text
    assert "outside locked manifest" in text
    assert "missing bibliography entries" in text
    assert "manifest coverage mismatch" in text
    assert "citation resolutions outside locked manifest" in text


def test_preflight_rejects_source_context_identifier_drift() -> None:
    source_context = SourceContext(
        manifest_path=REPO_ROOT / "config" / "article_sources.yaml",
        records=(
            SourceRecord(
                citation_key="k1",
                title="Locked Source",
                authors=("A. Author",),
                year="2026",
                arxiv_id="2501.99999",
                doi="10.1/locked",
                trusted_summary="Trusted locked context.",
            ),
        ),
    )
    report = _preflight(source_context=source_context)
    text = " ".join(report.errors)
    assert "year drift" in text
    assert "arXiv drift" in text
    assert "DOI drift" in text


def test_preflight_rejects_bad_heading_extra_chapter_and_bidi_target() -> None:
    body = "Memory\n\nwords <!-- CITATION: k1 -->\n\n" + BIDI_BODY
    drafts = ChapterDrafts(
        run_id="r",
        chapters=[
            ChapterDraft(chapter_id="memory", heading="Memory", body_markdown=body),
            ChapterDraft(chapter_id="extra", heading="Extra", body_markdown="# Extra\n\nword"),
        ],
    )
    bidi = _bidi()
    report = _preflight(drafts=drafts, bidi=bidi, assets=AssetSpecs(run_id="r"))
    assert not report.passed
    assert report.warnings
    assert "must begin with one H1" in " ".join(report.errors)


def test_preflight_rejects_missing_bidi_host_and_absent_inline_term() -> None:
    report = _preflight(
        drafts=ChapterDrafts(
            run_id="r",
            chapters=[
                ChapterDraft(
                    chapter_id="introduction",
                    heading="Intro",
                    body_markdown="# Intro\n\nword <!-- CITATION: k1 -->",
                )
            ],
        ),
        required_chapter_ids=("introduction",),
        bidi=_bidi(terms=["absent"]),
        assets=AssetSpecs(run_id="r"),
    )
    text = " ".join(report.errors)
    assert "BiDi inline English terms absent" in text
    assert "BiDi host memory chapter is missing" in text
