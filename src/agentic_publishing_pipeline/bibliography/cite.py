"""Resolve Markdown citation placeholders to LaTeX ``\\cite{...}`` (P7-I06).

The resolver is the narrow Phase 7 boundary between the Markdown
drafts produced by Phase 6 and the LaTeX project assembled by
Phase 9. It does **not** convert any other Markdown construct; the
broader Markdown→LaTeX conversion remains in
:mod:`agentic_publishing_pipeline.tools.markdown`.

Behaviour (per ``docs/PRD_bibliography_and_citations.md`` §7.4):

- a placeholder of the form ``<!-- CITATION: key -->`` is replaced
  by ``\\cite{key}`` iff ``key`` is in the verified manifest;
- unknown, provisional (``tbd…``), or rejected keys raise
  :class:`CitationResolutionError` with the source location;
- the resolver also provides a coverage report so callers can
  detect verified manifest entries that are not cited anywhere.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from .manifest import SourceManifest

_CITATION_RE = re.compile(
    r"<!--\s*CITATION\s*:\s*(?P<key>[^>\s-][^>]*?)\s*-->",
    re.IGNORECASE,
)


class CitationResolutionError(RuntimeError):
    """Raised when a Markdown citation placeholder cannot be resolved."""


@dataclass(frozen=True)
class CoverageReport:
    cited_keys: tuple[str, ...]
    uncited_verified_keys: tuple[str, ...]
    files: tuple[Path, ...]
    citations_per_file: dict[Path, int] = field(default_factory=dict)


class CitationResolver:
    """Resolve Markdown citation keys against the verified manifest."""

    def __init__(self, manifest: SourceManifest) -> None:
        self._verified_keys: set[str] = {
            r.citation_key for r in manifest.records if r.verification.status == "verified"
        }
        self._rejected_keys: set[str] = {
            r.citation_key for r in manifest.records if r.verification.status == "rejected"
        }

    @property
    def verified_keys(self) -> frozenset[str]:
        return frozenset(self._verified_keys)

    def resolve_key(self, key: str, *, source: str | None = None) -> str:
        """Validate ``key`` against the manifest; return it unchanged."""

        location = f" (in {source})" if source else ""
        if not key or any(ch.isspace() for ch in key):
            raise CitationResolutionError(
                f"empty or whitespace-bearing citation key{location}: {key!r}"
            )
        if key.startswith("tbd"):
            raise CitationResolutionError(
                f"provisional citation key {key!r} reached resolution{location}; "
                "P7-I05 rekey must complete first"
            )
        if key in self._rejected_keys:
            raise CitationResolutionError(f"rejected source {key!r} cannot be cited{location}")
        if key not in self._verified_keys:
            raise CitationResolutionError(
                f"unknown citation key {key!r}{location}; not in the verified manifest"
            )
        return key

    def to_latex_cite(self, key: str, *, source: str | None = None) -> str:
        """Return ``\\cite{<key>}`` after validating ``key``."""

        return rf"\cite{{{self.resolve_key(key, source=source)}}}"

    def rewrite_markdown(self, text: str, *, source: str | None = None) -> str:
        """Replace every ``<!-- CITATION: key -->`` with ``\\cite{key}``."""

        def _sub(match: re.Match[str]) -> str:
            raw = match.group("key").strip()
            return self.to_latex_cite(raw, source=source)

        return _CITATION_RE.sub(_sub, text)

    def extract_keys(self, text: str, *, source: str | None = None) -> list[str]:
        """Return the validated citation keys in order of appearance."""

        keys: list[str] = []
        for match in _CITATION_RE.finditer(text):
            raw = match.group("key").strip()
            keys.append(self.resolve_key(raw, source=source))
        return keys

    def coverage(self, markdown_files: Iterable[Path]) -> CoverageReport:
        """Return citation coverage across ``markdown_files``."""

        per_file: dict[Path, int] = {}
        all_keys: list[str] = []
        files_seen: list[Path] = []
        for path in markdown_files:
            text = path.read_text(encoding="utf-8")
            keys = self.extract_keys(text, source=str(path))
            per_file[path] = len(keys)
            all_keys.extend(keys)
            files_seen.append(path)
        cited = tuple(sorted(set(all_keys)))
        uncited = tuple(sorted(self._verified_keys - set(cited)))
        return CoverageReport(
            cited_keys=cited,
            uncited_verified_keys=uncited,
            files=tuple(files_seen),
            citations_per_file=per_file,
        )
