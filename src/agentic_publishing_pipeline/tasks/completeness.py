"""Deterministic completeness checks for candidate Markdown manuscripts."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..contracts import AssetSpecs, BibliographyBundle, BiDiSection, ChapterDrafts
from ..contracts._common import PlaceholderKind
from ..services.source_context import SourceContext
from ._preflight_assets import check_asset_specs
from ._preflight_sources import (
    check_bibliography,
    check_citation_set,
    check_source_provenance,
)
from ._preflight_text import (
    check_bidi_embedding,
    check_chapter_set,
    check_placeholder_requirements,
    check_placeholder_slots,
    collect_chapter_text,
)

_DEFAULT_PLACEHOLDER_KINDS: tuple[PlaceholderKind, ...] = (
    "FIGURE",
    "TABLE",
    "EQUATION",
    "CITATION",
)


@dataclass(frozen=True)
class ManuscriptPreflightReport:
    """Machine-verifiable completeness report for a candidate run."""

    passed: bool
    word_counts: dict[str, int]
    total_words: int
    cited_keys: tuple[str, ...]
    missing_source_keys: tuple[str, ...]
    errors: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)


def run_manuscript_preflight(
    drafts: ChapterDrafts,
    *,
    bidi: BiDiSection,
    required_chapter_ids: tuple[str, ...],
    manifest_keys: tuple[str, ...],
    min_words_per_chapter: int,
    min_total_words: int,
    min_hebrew_tokens: int = 40,
    min_embedded_english_terms: int = 1,
    required_placeholder_kinds: tuple[PlaceholderKind, ...] = _DEFAULT_PLACEHOLDER_KINDS,
    assets: AssetSpecs | None = None,
    bibliography: BibliographyBundle | None = None,
    source_context: SourceContext | None = None,
) -> ManuscriptPreflightReport:
    """Reject incomplete, unsafe, or source-drifting manuscript output."""
    errors: list[str] = []
    warnings: list[str] = []
    by_id = {chapter.chapter_id: chapter for chapter in drafts.chapters}
    if len(by_id) != len(drafts.chapters):
        errors.append("duplicate chapter_id in ChapterDrafts")
    check_chapter_set(by_id, required_chapter_ids, errors, warnings)
    word_counts, cited, placeholders = collect_chapter_text(
        by_id,
        required_chapter_ids,
        min_words_per_chapter=min_words_per_chapter,
        errors=errors,
    )
    total_words = sum(word_counts.values())
    if total_words < min_total_words:
        errors.append(f"manuscript has {total_words} words")
    check_placeholder_requirements(placeholders, required_placeholder_kinds, errors)
    check_placeholder_slots(placeholders, errors)
    if assets is not None:
        check_asset_specs(placeholders, assets, errors)
    missing_keys = check_citation_set(cited, manifest_keys, errors)
    if bibliography is not None:
        check_bibliography(cited, manifest_keys, bibliography, errors)
    if source_context is not None:
        check_source_provenance(manifest_keys, bibliography, source_context, errors)
    check_bidi_embedding(
        bidi,
        by_id.get("memory"),
        min_hebrew_tokens=min_hebrew_tokens,
        min_embedded_english_terms=min_embedded_english_terms,
        errors=errors,
    )
    return ManuscriptPreflightReport(
        passed=not errors,
        word_counts=word_counts,
        total_words=total_words,
        cited_keys=tuple(sorted(cited)),
        missing_source_keys=missing_keys,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
