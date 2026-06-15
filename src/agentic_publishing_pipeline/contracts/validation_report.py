"""ValidationReport v1 — contract for edge E11 (Validator → Promotion)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ._envelope import ContractEnvelope

ValidationResult = Literal["pass", "fail"]
CheckStatus = Literal["pass", "fail", "skipped"]


class CheckOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    status: CheckStatus
    evidence: str = ""


class CitationCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    placeholder: str = Field(min_length=1)
    citation_key: str | None = None
    resolved: bool


class PageReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_pages: int = Field(ge=0)
    substantive_pages: int = Field(ge=0)
    page_budget_total_minimum: int = Field(default=15, ge=1)
    page_budget_substantive_minimum: int = Field(default=10, ge=1)

    @property
    def meets_total_minimum(self) -> bool:
        return self.total_pages >= self.page_budget_total_minimum

    @property
    def meets_substantive_minimum(self) -> bool:
        return self.substantive_pages >= self.page_budget_substantive_minimum


class ValidationReport(ContractEnvelope):
    """Deterministic validation outcome emitted by ValidatorService for E11."""

    result: ValidationResult
    checks: list[CheckOutcome] = Field(default_factory=list)
    page_report: PageReport | None = None
    citation_resolution: list[CitationCheck] = Field(default_factory=list)
