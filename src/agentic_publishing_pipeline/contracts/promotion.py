"""PromotionRecord v1 — contract for edge E12 (Promotion → canonical roots)."""

from __future__ import annotations

from pydantic import Field

from ._envelope import ContractEnvelope


class PromotionRecord(ContractEnvelope):
    """The record explicit promotion writes after a PASS run."""

    source_workspace: str = Field(min_length=1)
    canonical_paths_written: list[str] = Field(min_length=1)
    content_hashes: dict[str, str] = Field(min_length=1)
    validation_report_ref: str = Field(min_length=1)
    forced: bool = False
    force_reason: str | None = None
