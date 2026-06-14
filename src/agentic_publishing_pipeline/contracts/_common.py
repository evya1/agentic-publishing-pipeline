"""Common nested types shared across multiple contracts.

Placeholders link Writer/BiDi/Asset/Bibliography artifacts together;
keeping them in one module avoids cyclic imports between per-contract
files.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PlaceholderKind = Literal["FIGURE", "TABLE", "EQUATION", "CITATION"]


class Placeholder(BaseModel):
    """A semantic slot in Markdown that downstream agents/renderers fill."""

    model_config = ConfigDict(extra="forbid")

    kind: PlaceholderKind
    slot: str = Field(min_length=1)
    chapter_id: str = Field(min_length=1)
    description: str = ""


class CandidateReference(BaseModel):
    """A candidate source surfaced during research; verified later."""

    model_config = ConfigDict(extra="forbid")

    arxiv_id: str | None = None
    doi: str | None = None
    title: str = Field(min_length=1)


class GlossaryTerm(BaseModel):
    model_config = ConfigDict(extra="forbid")

    term: str = Field(min_length=1)
    definition: str = Field(min_length=1)
    language: Literal["en", "he"] = "en"
