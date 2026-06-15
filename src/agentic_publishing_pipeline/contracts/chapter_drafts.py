"""ChapterDrafts v1 — contract for edge E3 (Writer → many)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from ._common import Placeholder
from ._envelope import ContractEnvelope


class ChapterDraft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chapter_id: str = Field(min_length=1)
    heading: str = Field(min_length=1)
    body_markdown: str = Field(min_length=1)


class ChapterDrafts(ContractEnvelope):
    """Markdown chapter drafts produced by the Writer Agent for E3."""

    chapters: list[ChapterDraft] = Field(min_length=1)
    placeholder_index: list[Placeholder] = Field(default_factory=list)
