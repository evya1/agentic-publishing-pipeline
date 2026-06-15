"""ReviewerSignal v1 — contract for edge E8 (Reviewer → Validator).

Per FR-40 and NFR-19, the Reviewer Agent is **advisory only**. Its
signal does not gate canonical writes; the deterministic
ValidatorService does. This contract captures the advisory verdict
plus itemized notes so the Validator can use them as hints.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ._envelope import ContractEnvelope

ReviewVerdict = Literal["pass", "flag"]
Severity = Literal["info", "warning", "blocker"]


class ReviewNote(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target: str = Field(min_length=1)
    severity: Severity = "info"
    message: str = Field(min_length=1)


class ReviewerSignal(ContractEnvelope):
    """Advisory pass/flag verdict the Reviewer Agent emits for E8."""

    signal: ReviewVerdict
    notes: list[ReviewNote] = Field(default_factory=list)
