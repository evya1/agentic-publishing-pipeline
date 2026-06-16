"""Deterministic composition of typed CrewAI manuscript outputs."""

from __future__ import annotations

from dataclasses import replace

from ..contracts import ChapterDraft, ChapterDrafts
from .result_parser import ManuscriptOutputs


class ManuscriptCompositionError(RuntimeError):
    """Raised when typed task outputs cannot be composed deterministically."""


def compose_manuscript_outputs(outputs: ManuscriptOutputs) -> ManuscriptOutputs:
    """Merge the validated BiDi section into the Memory chapter draft."""
    chapters = _merge_bidi_into_memory(outputs.chapters, outputs.bidi.hebrew_body)
    return replace(outputs, chapters=chapters)


def _merge_bidi_into_memory(drafts: ChapterDrafts, bidi_body: str) -> ChapterDrafts:
    if not bidi_body.strip():
        raise ManuscriptCompositionError("BiDi section body is empty")
    composed: list[ChapterDraft] = []
    found_memory = False
    for chapter in drafts.chapters:
        if chapter.chapter_id != "memory":
            composed.append(chapter)
            continue
        found_memory = True
        body = chapter.body_markdown.rstrip()
        if bidi_body.strip() not in body:
            body = "\n\n".join((body, "## Hebrew/English BiDi Section", bidi_body.strip()))
        composed.append(
            chapter.model_copy(update={"body_markdown": body.rstrip() + "\n"})
        )
    if not found_memory:
        raise ManuscriptCompositionError("BiDi section targets missing memory chapter")
    return drafts.model_copy(update={"chapters": composed})
