"""Happy-path parse tests for each E1..E12 contract."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from agentic_publishing_pipeline.contracts import (
    AssetSpecs,
    BibliographyBundle,
    BiDiSection,
    BuildResult,
    ChapterDrafts,
    LaTeXProjectSpec,
    Outline,
    PromotionRecord,
    ResearchNotes,
    ReviewerSignal,
    ValidationReport,
)

RUN_ID = "RUN-TEST-CONTRACTS"


def _envelope(**extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"run_id": RUN_ID}
    payload.update(extra)
    return payload


def test_research_notes_minimal() -> None:
    payload = _envelope(
        topic="Reasoning",
        dimensions=[{"dimension": "planning", "summary": "Plans matter."}],
    )
    model = ResearchNotes.model_validate(payload)
    assert model.dimensions[0].dimension == "planning"


def test_outline_requires_at_least_one_chapter() -> None:
    payload = _envelope(target_total_pages=15, chapters=[])
    with pytest.raises(ValidationError):
        Outline.model_validate(payload)


def test_outline_bidi_host_lookup() -> None:
    payload = _envelope(
        target_total_pages=18,
        chapters=[
            {"chapter_id": "intro", "title": "Intro", "summary": "x"},
            {"chapter_id": "memory", "title": "Memory", "summary": "x", "is_bidi_host": True},
        ],
    )
    outline = Outline.model_validate(payload)
    host = outline.bidi_host_chapter()
    assert host is not None and host.chapter_id == "memory"


def test_chapter_drafts_accepts_placeholders() -> None:
    payload = _envelope(
        chapters=[
            {"chapter_id": "intro", "heading": "Intro", "body_markdown": "Hello."},
        ],
        placeholder_index=[
            {"kind": "CITATION", "slot": "intro/cite-1", "chapter_id": "intro"},
        ],
    )
    drafts = ChapterDrafts.model_validate(payload)
    assert drafts.placeholder_index[0].kind == "CITATION"


def test_asset_specs_accepts_theorem_like() -> None:
    payload = _envelope(
        assets=[
            {
                "kind": "equation",
                "slot": "intro/eq-1",
                "chapter_id": "intro",
                "caption": "Demo",
                "theorem_like_kind": "definition",
            },
        ],
    )
    specs = AssetSpecs.model_validate(payload)
    assert specs.assets[0].theorem_like_kind == "definition"


def test_bidi_section_enforces_token_count() -> None:
    payload = _envelope(
        chapter_id="memory",
        hebrew_body="טקסט ",
        inline_english_terms=["LLM"],
    )
    with pytest.raises(ValidationError):
        BiDiSection.model_validate(payload)


def test_bidi_section_happy_path() -> None:
    payload = _envelope(
        chapter_id="memory",
        hebrew_body=" ".join(["טקסט"] * 60),
        inline_english_terms=["LLM"],
    )
    section = BiDiSection.model_validate(payload)
    assert len(section.inline_english_terms) == 1


def test_bibliography_bundle_empty_is_valid() -> None:
    bundle = BibliographyBundle.model_validate(_envelope())
    assert bundle.entries == []


def test_latex_project_spec_requires_minimum_pieces() -> None:
    payload = _envelope(
        chapters=[{"chapter_id": "intro", "file_stem": "intro"}],
        nomenclature={"symbols": [("alpha", "rate"), ("beta", "loss")]},
        index_entries={"hebrew_terms": ["זיכרון"], "english_terms": ["memory"]},
    )
    spec = LaTeXProjectSpec.model_validate(payload)
    assert spec.preamble.engine == "lualatex"


def test_reviewer_signal_pass() -> None:
    payload = _envelope(signal="pass")
    sig = ReviewerSignal.model_validate(payload)
    assert sig.signal == "pass"


def test_build_result_succeeded_property() -> None:
    payload = _envelope(
        passes=[{"command": ["lualatex", "main"], "exit_code": 0, "duration_seconds": 1.0}],
        pdf_path="results/RUN/build/main.pdf",
    )
    br = BuildResult.model_validate(payload)
    assert br.succeeded is True


def test_validation_report_fail_status() -> None:
    payload = _envelope(result="fail", checks=[{"name": "pages", "status": "fail"}])
    report = ValidationReport.model_validate(payload)
    assert report.result == "fail"


def test_promotion_record_requires_hash_map() -> None:
    payload = _envelope(
        source_workspace="results/RUN/",
        canonical_paths_written=["latex_project/main.tex"],
        content_hashes={"latex_project/main.tex": "abc"},
        validation_report_ref="results/RUN/validation/report.v1.json",
    )
    record = PromotionRecord.model_validate(payload)
    assert record.canonical_paths_written == ["latex_project/main.tex"]
