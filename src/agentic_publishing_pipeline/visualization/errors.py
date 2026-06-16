"""Shared visualization error and result types."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SpecIssue:
    path: str
    message: str


class SpecValidationError(ValueError):
    """Raised when a graph specification fails deterministic validation."""

    def __init__(self, issues: list[SpecIssue]) -> None:
        assert issues, "SpecValidationError requires at least one issue"
        self.issues = issues
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        first = self.issues[0]
        return f"{first.path}: {first.message} ({len(self.issues)} issue(s))"


@dataclass(frozen=True)
class AssetRenderResult:
    success: bool
    asset_id: str
    kind: str
    slot: str
    path: str | None = None
    provenance_path: str | None = None
    input_sha256: str | None = None
    output_sha256: str | None = None
    error_code: str | None = None
    message: str | None = None
