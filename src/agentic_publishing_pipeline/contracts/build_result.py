"""BuildResult v1 — contract for edge E10 (Compiler → Validator)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ._envelope import ContractEnvelope


class BuildPass(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command: list[str] = Field(min_length=1)
    exit_code: int
    duration_seconds: float = Field(ge=0.0)
    log_excerpt: str = ""


class BuildResult(ContractEnvelope):
    """Outcome of the multi-pass LuaLaTeX + biber build for E10."""

    engine: Literal["lualatex"] = "lualatex"
    passes: list[BuildPass] = Field(default_factory=list)
    pdf_path: str | None = None
    parsed_warnings: list[str] = Field(default_factory=list)
    parsed_errors: list[str] = Field(default_factory=list)

    @property
    def succeeded(self) -> bool:
        return (
            self.pdf_path is not None
            and bool(self.passes)
            and all(p.exit_code == 0 for p in self.passes)
            and not self.parsed_errors
        )
