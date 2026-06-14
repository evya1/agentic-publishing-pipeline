"""ResearchNotes v1 — contract for edge E1 (Research → Outline)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ._common import CandidateReference, GlossaryTerm
from ._envelope import ContractEnvelope

ReasoningDimension = Literal[
    "planning",
    "memory",
    "retrieval",
    "tool_use",
    "multimodal",
]


class ResearchDimensionNote(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dimension: ReasoningDimension
    summary: str = Field(min_length=1)
    key_points: list[str] = Field(default_factory=list)


class ResearchNotes(ContractEnvelope):
    """Structured notes the Research Agent emits for E1."""

    topic: str = Field(min_length=1)
    dimensions: list[ResearchDimensionNote] = Field(min_length=1)
    candidate_references: list[CandidateReference] = Field(default_factory=list)
    glossary: list[GlossaryTerm] = Field(default_factory=list)
