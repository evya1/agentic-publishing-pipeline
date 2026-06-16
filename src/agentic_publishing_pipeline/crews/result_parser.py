"""Strict extraction of typed outputs from a CrewAI kickoff result."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from pydantic import BaseModel

from ..contracts import (
    AssetSpecs,
    BibliographyBundle,
    BiDiSection,
    ChapterDrafts,
    Outline,
    ResearchNotes,
    ReviewerSignal,
)


class CrewResultError(RuntimeError):
    """Raised when kickoff does not return the expected typed task outputs."""


@dataclass(frozen=True)
class ManuscriptOutputs:
    """Typed outputs produced by the pre-review manuscript crew."""

    research: ResearchNotes
    outline: Outline
    chapters: ChapterDrafts
    assets: AssetSpecs
    bidi: BiDiSection
    bibliography: BibliographyBundle
    reviewer: ReviewerSignal


_EXPECTED: tuple[type[BaseModel], ...] = (
    ResearchNotes,
    Outline,
    ChapterDrafts,
    AssetSpecs,
    BiDiSection,
    BibliographyBundle,
    ReviewerSignal,
)


def parse_manuscript_outputs(result: Any) -> ManuscriptOutputs:
    """Validate task count, order, and every Pydantic output."""
    outputs = list(getattr(result, "tasks_output", ()) or ())
    if len(outputs) != len(_EXPECTED):
        raise CrewResultError(
            f"expected {len(_EXPECTED)} task outputs; received {len(outputs)}"
        )
    parsed: list[BaseModel] = []
    for index, (output, expected) in enumerate(zip(outputs, _EXPECTED, strict=True)):
        value = getattr(output, "pydantic", None)
        if not isinstance(value, expected):
            observed = type(value).__name__ if value is not None else "None"
            raise CrewResultError(
                f"task output {index} expected {expected.__name__}; got {observed}"
            )
        parsed.append(value)
    return ManuscriptOutputs(
        research=cast(ResearchNotes, parsed[0]),
        outline=cast(Outline, parsed[1]),
        chapters=cast(ChapterDrafts, parsed[2]),
        assets=cast(AssetSpecs, parsed[3]),
        bidi=cast(BiDiSection, parsed[4]),
        bibliography=cast(BibliographyBundle, parsed[5]),
        reviewer=cast(ReviewerSignal, parsed[6]),
    )
