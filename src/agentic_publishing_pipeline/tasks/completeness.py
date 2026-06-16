"""Deterministic completeness checks for candidate Markdown manuscripts."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..contracts import BiDiSection, ChapterDrafts
from ..tools.markdown import parse_placeholders

_CITE_RE = re.compile(r"\\cite\{(?P<keys>[^}]+)\}")


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
) -> ManuscriptPreflightReport:
    """Reject incomplete, unsafe, or source-drifting manuscript output."""
    errors: list[str] = []
    warnings: list[str] = []
    by_id = {chapter.chapter_id: chapter for chapter in drafts.chapters}
    if len(by_id) != len(drafts.chapters):
        errors.append("duplicate chapter_id in ChapterDrafts")
    _check_chapter_set(by_id, required_chapter_ids, errors, warnings)
    word_counts: dict[str, int] = {}
    cited: set[str] = set()
    placeholder_slots: set[str] = set()
    for chapter_id in required_chapter_ids:
        chapter = by_id.get(chapter_id)
        if chapter is None:
            continue
        body = chapter.body_markdown
        count = _word_count(body)
        word_counts[chapter_id] = count
        if count < min_words_per_chapter:
            errors.append(f"chapter {chapter_id} has {count} words")
        if not body.lstrip().startswith("# "):
            errors.append(f"chapter {chapter_id} must begin with one H1 heading")
        _collect_placeholders(chapter_id, body, placeholder_slots, cited, errors)
        cited.update(_cite_commands(body))
    total_words = sum(word_counts.values())
    if total_words < min_total_words:
        errors.append(f"manuscript has {total_words} words")
    missing_keys = _check_citation_set(cited, manifest_keys, errors)
    _check_bidi_embedding(bidi, by_id.get("memory"), errors, warnings)
    return ManuscriptPreflightReport(
        passed=not errors,
        word_counts=word_counts,
        total_words=total_words,
        cited_keys=tuple(sorted(cited)),
        missing_source_keys=missing_keys,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def _check_chapter_set(
    by_id: dict[str, object],
    required: tuple[str, ...],
    errors: list[str],
    warnings: list[str],
) -> None:
    missing = [value for value in required if value not in by_id]
    extra = [value for value in by_id if value not in required]
    if missing:
        errors.append(f"missing required chapters: {missing}")
    if extra:
        warnings.append(f"unexpected chapters: {extra}")


def _collect_placeholders(
    chapter_id: str,
    body: str,
    seen_slots: set[str],
    cited: set[str],
    errors: list[str],
) -> None:
    for placeholder in parse_placeholders(body, chapter_id=chapter_id):
        if placeholder.slot in seen_slots:
            errors.append(f"duplicate placeholder slot: {placeholder.slot}")
        seen_slots.add(placeholder.slot)
        if placeholder.kind == "CITATION":
            cited.update(key.strip() for key in placeholder.description.split(","))


def _check_citation_set(
    cited: set[str],
    manifest_keys: tuple[str, ...],
    errors: list[str],
) -> tuple[str, ...]:
    allowed = set(manifest_keys)
    unknown = sorted(cited - allowed)
    if unknown:
        errors.append(f"unknown citation keys: {unknown}")
    missing = tuple(sorted(allowed - cited))
    if missing:
        errors.append(f"locked sources not cited: {list(missing)}")
    return missing


def _check_bidi_embedding(
    bidi: BiDiSection,
    memory_chapter: object | None,
    errors: list[str],
    warnings: list[str],
) -> None:
    if bidi.chapter_id != "memory":
        errors.append("BiDi section must target the Memory chapter")
    memory_body = getattr(memory_chapter, "body_markdown", "")
    if bidi.hebrew_body not in memory_body:
        warnings.append("BiDi contract text is not embedded verbatim in memory.md")


def _cite_commands(markdown: str) -> set[str]:
    keys: set[str] = set()
    for match in _CITE_RE.finditer(markdown):
        keys.update(key.strip() for key in match.group("keys").split(","))
    return keys


def _word_count(markdown: str) -> int:
    without_comments = re.sub(r"<!--.*?-->", " ", markdown, flags=re.DOTALL)
    without_commands = _CITE_RE.sub(" ", without_comments)
    return len(re.findall(r"\b[\w'-]+\b", without_commands, flags=re.UNICODE))
