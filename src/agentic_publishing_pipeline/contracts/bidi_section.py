"""BiDiSection v1 — contract for edge E5 (Hebrew/BiDi → many)."""

from __future__ import annotations

from pydantic import Field, field_validator

from ._common import Placeholder
from ._envelope import ContractEnvelope

MIN_HEBREW_TOKEN_COUNT: int = 40
MIN_INLINE_ENGLISH_TERMS: int = 1


class BiDiSection(ContractEnvelope):
    """Hebrew/English BiDi section authored by the BiDi Agent for E5."""

    chapter_id: str = Field(min_length=1)
    hebrew_body: str = Field(min_length=1)
    inline_english_terms: list[str] = Field(default_factory=list)
    placeholders: list[Placeholder] = Field(default_factory=list)

    @field_validator("hebrew_body")
    @classmethod
    def _enforce_min_hebrew_tokens(cls, value: str) -> str:
        token_count = len(value.split())
        assert token_count >= MIN_HEBREW_TOKEN_COUNT, (
            f"hebrew_body has {token_count} tokens; minimum is {MIN_HEBREW_TOKEN_COUNT}."
        )
        return value

    @field_validator("inline_english_terms")
    @classmethod
    def _enforce_min_english_terms(cls, value: list[str]) -> list[str]:
        assert len(value) >= MIN_INLINE_ENGLISH_TERMS, (
            f"inline_english_terms requires at least {MIN_INLINE_ENGLISH_TERMS} entr(y/ies)."
        )
        return value
