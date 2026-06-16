"""Deterministic composition of typed CrewAI manuscript outputs."""

from __future__ import annotations

from dataclasses import replace

from ..contracts import ChapterDraft, ChapterDrafts
from .result_parser import ManuscriptOutputs

BIDI_BEGIN_MARKER = "<!-- BIDI-SECTION:BEGIN -->"
BIDI_END_MARKER = "<!-- BIDI-SECTION:END -->"
BIDI_HEADING = "## Hebrew/English BiDi Section"


class ManuscriptCompositionError(RuntimeError):
    """Raised when typed task outputs cannot be composed deterministically."""


def compose_manuscript_outputs(outputs: ManuscriptOutputs) -> ManuscriptOutputs:
    """Merge the validated BiDi section into the Memory chapter draft."""
    chapters = _merge_bidi_into_memory(outputs.chapters, outputs.bidi.hebrew_body)
    return replace(outputs, chapters=chapters)


def _merge_bidi_into_memory(drafts: ChapterDrafts, bidi_body: str) -> ChapterDrafts:
    body = bidi_body.strip()
    if not body:
        raise ManuscriptCompositionError("BiDi section body is empty")
    section = (
        f"{BIDI_BEGIN_MARKER}\n{BIDI_HEADING}\n\n{body}\n{BIDI_END_MARKER}"
    )
    composed: list[ChapterDraft] = []
    found_memory = False
    for chapter in drafts.chapters:
        if chapter.chapter_id != "memory":
            composed.append(chapter)
            continue
        found_memory = True
        composed.append(
            chapter.model_copy(
                update={"body_markdown": _splice_section(chapter.body_markdown, section) + "\n"}
            )
        )
    if not found_memory:
        raise ManuscriptCompositionError("BiDi section targets missing memory chapter")
    return drafts.model_copy(update={"chapters": composed})


def _splice_section(body: str, section: str) -> str:
    trimmed = body.rstrip()
    begin_count = trimmed.count(BIDI_BEGIN_MARKER)
    end_count = trimmed.count(BIDI_END_MARKER)
    if begin_count != end_count:
        raise ManuscriptCompositionError(
            "memory chapter has unbalanced BiDi markers: "
            f"begin={begin_count} end={end_count}"
        )
    if begin_count > 1:
        raise ManuscriptCompositionError(
            f"memory chapter has duplicate BiDi-section markers ({begin_count})"
        )
    if begin_count == 0:
        return f"{trimmed}\n\n{section}".rstrip()
    begin_idx = trimmed.index(BIDI_BEGIN_MARKER)
    end_idx = trimmed.index(BIDI_END_MARKER) + len(BIDI_END_MARKER)
    if end_idx <= begin_idx:
        raise ManuscriptCompositionError(
            "memory chapter has BiDi end marker before begin marker"
        )
    prefix = trimmed[:begin_idx].rstrip()
    suffix = trimmed[end_idx:].lstrip()
    pieces = [prefix, section]
    if suffix:
        pieces.append(suffix)
    return "\n\n".join(piece for piece in pieces if piece).rstrip()
