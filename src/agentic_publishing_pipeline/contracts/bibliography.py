"""BibliographyBundle v1 — contract for edge E6 (Bibliography → many)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ._envelope import ContractEnvelope

VerificationStatus = Literal["unverified", "verified", "rejected"]
EntryType = Literal["article", "misc", "techreport", "inproceedings", "book"]


class BibEntry(BaseModel):
    """One bibliography entry; no fabricated sources allowed (CLAUDE.md)."""

    model_config = ConfigDict(extra="forbid")

    citation_key: str = Field(min_length=1)
    entry_type: EntryType
    title: str = Field(min_length=1)
    year: int = Field(ge=1900, le=2100)
    authors: list[str] = Field(default_factory=list)
    arxiv_id: str | None = None
    doi: str | None = None
    url: str | None = None
    verification_status: VerificationStatus = "unverified"


class BibliographyBundle(ContractEnvelope):
    """The complete bibliography state for a run, used by LaTeX and Validator."""

    entries: list[BibEntry] = Field(default_factory=list)
    placeholder_resolution: dict[str, str] = Field(default_factory=dict)
    manifest_coverage: list[str] = Field(default_factory=list)
