"""Text, placeholder, and BiDi rules for manuscript preflight."""

from __future__ import annotations

import re

from ..contracts import BiDiSection
from ..contracts._common import Placeholder, PlaceholderKind
from ..tools.markdown import parse_placeholders

_CITE_RE = re.compile(r"\\cite\{(?P<keys>[^}]+)\}")
_HEBREW_TOKEN_RE = re.compile(r"[\u0590-\u05ff]+")


def collect_chapter_text(
    by_id: dict[str, object],
    required_chapter_ids: tuple[str, ...],
    *,
    min_words_per_chapter: int,
    errors: list[str],
) -> tuple[dict[str, int], set[str], list[Placeholder]]:
    word_counts: dict[str, int] = {}
    cited: set[str] = set()
    placeholders: list[Placeholder] = []
    for chapter_id in required_chapter_ids:
        chapter = by_id.get(chapter_id)
        if chapter is None:
            continue
        body = str(getattr(chapter, "body_markdown", ""))
        count = _word_count(body)
        word_counts[chapter_id] = count
        if count < min_words_per_chapter:
            errors.append(f"chapter {chapter_id} has {count} words")
        if not body.lstrip().startswith("# "):
            errors.append(f"chapter {chapter_id} must begin with one H1 heading")
        chapter_placeholders = parse_placeholders(body, chapter_id=chapter_id)
        placeholders.extend(chapter_placeholders)
        cited.update(citation_keys(chapter_placeholders))
        cited.update(cite_commands(body))
    return word_counts, cited, placeholders


def check_chapter_set(
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


def check_placeholder_requirements(
    placeholders: list[Placeholder],
    required: tuple[PlaceholderKind, ...],
    errors: list[str],
) -> None:
    present = {placeholder.kind for placeholder in placeholders}
    missing = [kind for kind in required if kind not in present]
    if missing:
        errors.append(f"missing placeholder kinds: {missing}")


def check_placeholder_slots(placeholders: list[Placeholder], errors: list[str]) -> None:
    seen: set[str] = set()
    for placeholder in placeholders:
        if placeholder.slot in seen:
            errors.append(f"duplicate placeholder slot: {placeholder.slot}")
        seen.add(placeholder.slot)


def check_bidi_embedding(
    bidi: BiDiSection,
    memory_chapter: object | None,
    *,
    min_hebrew_tokens: int,
    min_embedded_english_terms: int,
    errors: list[str],
) -> None:
    if bidi.chapter_id != "memory":
        errors.append("BiDi section must target the Memory chapter")
    hebrew_tokens = len(_HEBREW_TOKEN_RE.findall(bidi.hebrew_body))
    if hebrew_tokens < min_hebrew_tokens:
        errors.append(f"BiDi section has {hebrew_tokens} Hebrew tokens")
    if len(bidi.inline_english_terms) < min_embedded_english_terms:
        errors.append(
            f"BiDi section has {len(bidi.inline_english_terms)} embedded English terms"
        )
    missing_terms = [
        term for term in bidi.inline_english_terms if term and term not in bidi.hebrew_body
    ]
    if missing_terms:
        errors.append(f"BiDi inline English terms absent from body: {missing_terms}")
    memory_body = getattr(memory_chapter, "body_markdown", "")
    if not memory_body:
        errors.append("BiDi host memory chapter is missing")
    elif bidi.hebrew_body.strip() not in memory_body:
        errors.append("BiDi contract text is not embedded verbatim in memory.md")


def citation_keys(placeholders: list[Placeholder]) -> set[str]:
    keys: set[str] = set()
    for placeholder in placeholders:
        if placeholder.kind == "CITATION":
            keys.update(key.strip() for key in placeholder.description.split(",") if key.strip())
    return keys


def cite_commands(markdown: str) -> set[str]:
    keys: set[str] = set()
    for match in _CITE_RE.finditer(markdown):
        keys.update(key.strip() for key in match.group("keys").split(",") if key.strip())
    return keys


def _word_count(markdown: str) -> int:
    without_comments = re.sub(r"<!--.*?-->", " ", markdown, flags=re.DOTALL)
    without_commands = _CITE_RE.sub(" ", without_comments)
    return len(re.findall(r"\b[\w'-]+\b", without_commands, flags=re.UNICODE))
