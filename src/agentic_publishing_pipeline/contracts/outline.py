"""Outline v1 — contract for edge E2 (Outline → Writer)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from ._envelope import ContractEnvelope


class ChapterOutline(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chapter_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    is_bidi_host: bool = False
    planned_placeholders: list[str] = Field(default_factory=list)


class Outline(ContractEnvelope):
    """Article-level outline produced by the Outline Agent for E2."""

    chapters: list[ChapterOutline] = Field(min_length=1)
    target_total_pages: int = Field(ge=1)

    def bidi_host_chapter(self) -> ChapterOutline | None:
        for chapter in self.chapters:
            if chapter.is_bidi_host:
                return chapter
        return None
