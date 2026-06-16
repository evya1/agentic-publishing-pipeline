"""Deterministic readiness checks before any Markdown-to-LaTeX conversion."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path

from ..tools.markdown import parse_placeholders
from .approval_loader import ApprovedManuscript
from .bibliography import load_bibliography_keys
from .config_models import Phase9Config
from .outline import load_outline_chapter_ids

_CITE_RE = re.compile(r"\\cite\{([^}]+)\}")
_HEBREW_RE = re.compile(r"[\u0590-\u05FF]+")
_WORD_RE = re.compile(r"\b[\w'-]+\b", re.UNICODE)


@dataclass(frozen=True)
class Phase9PreflightReport:
    passed: bool
    manuscript_revision: str
    chapter_word_counts: dict[str, int]
    total_words: int
    hebrew_words: int
    citation_keys: tuple[str, ...]
    placeholder_counts: dict[str, int]
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_json(self) -> dict[str, object]:
        return asdict(self)


def run_phase9_preflight(
    *,
    manuscript: ApprovedManuscript,
    config: Phase9Config,
    outline_path: Path,
    bibliography_path: Path,
    graph_path: Path,
) -> Phase9PreflightReport:
    errors: list[str] = []
    actual = tuple(chapter.chapter_id for chapter in manuscript.chapters)
    outlined = load_outline_chapter_ids(outline_path)
    _check_metadata(config, errors)
    if actual != tuple(config.chapter_order):
        errors.append(f"approved chapter order differs from configuration: {actual}")
    if outlined != tuple(config.chapter_order):
        errors.append(f"outline/config chapter order mismatch: outline={outlined}")
    bib_keys = set(load_bibliography_keys(bibliography_path))
    if not graph_path.is_file():
        errors.append(f"Phase 8 graph missing: {graph_path}")
    counts, cited, chapter_citations, placeholders, hebrew = _inspect_chapters(
        manuscript, config, errors
    )
    _check_citations(config, bib_keys, cited, chapter_citations, errors)
    total = sum(counts.values())
    if total < config.minimum_total_words:
        errors.append(
            f"approved manuscript has {total} words; minimum is {config.minimum_total_words}"
        )
    if hebrew < config.minimum_hebrew_words:
        errors.append(
            f"approved manuscript has {hebrew} Hebrew words; minimum is "
            f"{config.minimum_hebrew_words}"
        )
    return Phase9PreflightReport(
        passed=not errors,
        manuscript_revision=manuscript.revision,
        chapter_word_counts=counts,
        total_words=total,
        hebrew_words=hebrew,
        citation_keys=tuple(sorted(cited)),
        placeholder_counts=placeholders,
        errors=tuple(errors),
        warnings=(),
    )


def _check_metadata(config: Phase9Config, errors: list[str]) -> None:
    if not config.metadata.authors:
        errors.append("title-page authors are not configured")
    if not config.metadata.group_code.strip():
        errors.append("title-page group_code is not configured")


def _inspect_chapters(
    manuscript: ApprovedManuscript,
    config: Phase9Config,
    errors: list[str],
) -> tuple[dict[str, int], set[str], dict[str, set[str]], dict[str, int], int]:
    counts: dict[str, int] = {}
    cited: set[str] = set()
    chapter_citations: dict[str, set[str]] = {}
    placeholders: dict[str, int] = {}
    hebrew = 0
    for chapter in manuscript.chapters:
        count = len(_WORD_RE.findall(chapter.markdown))
        counts[chapter.chapter_id] = count
        if count < config.minimum_words_per_chapter:
            errors.append(
                f"{chapter.chapter_id}: {count} words; minimum is "
                f"{config.minimum_words_per_chapter}"
            )
        hebrew += len(_HEBREW_RE.findall(chapter.markdown))
        chapter_keys = _citation_keys(chapter.markdown)
        chapter_citations[chapter.chapter_id] = chapter_keys
        cited.update(chapter_keys)
        parsed = parse_placeholders(chapter.markdown, chapter_id=chapter.chapter_id)
        placeholders[chapter.chapter_id] = len(parsed)
        if parsed:
            slots = [placeholder.slot for placeholder in parsed]
            errors.append(f"{chapter.chapter_id}: unresolved Markdown placeholders: {slots}")
        if not chapter.markdown.lstrip().startswith("# "):
            errors.append(f"{chapter.chapter_id}: chapter must begin with one H1")
    return counts, cited, chapter_citations, placeholders, hebrew


def _check_citations(
    config: Phase9Config,
    bib_keys: set[str],
    cited: set[str],
    by_chapter: dict[str, set[str]],
    errors: list[str],
) -> None:
    if not cited:
        errors.append("approved manuscript contains no resolved citation commands")
    if unknown := sorted(cited - bib_keys):
        errors.append(f"citations absent from verified bibliography: {unknown}")
    if config.require_all_bibliography_entries and (missing := sorted(bib_keys - cited)):
        errors.append(f"verified bibliography entries not cited: {missing}")
    for chapter_id, required in config.chapter_citation_requirements.items():
        if missing := sorted(set(required) - by_chapter.get(chapter_id, set())):
            errors.append(f"{chapter_id}: required citations missing: {missing}")


def _citation_keys(markdown: str) -> set[str]:
    result: set[str] = set()
    for match in _CITE_RE.finditer(markdown):
        result.update(value.strip() for value in match.group(1).split(",") if value.strip())
    return result
