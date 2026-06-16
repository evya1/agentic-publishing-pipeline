"""Source verification (P7-I02) — compare manifest records with arXiv metadata.

The module is pure: it takes a typed :class:`SourceRecord` plus the
parsed :class:`ArxivMetadata` for the same arXiv ID and returns a
:class:`VerificationResult` enumerating every check that ran. Live
HTTP fetching lives in :mod:`._arxiv_fetch` so tests can drive this
logic from committed XML fixtures.

The comparison rules implement
``docs/PRD_bibliography_and_citations.md`` §7.1: status flips to
``verified`` only when every check passes; otherwise the record is
marked ``rejected`` and the rationale is recorded.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ._arxiv_parse import ArxivMetadata, to_surname_given
from .manifest import SourceRecord


@dataclass(frozen=True)
class VerificationResult:
    """Outcome of cross-checking one manifest record against arXiv."""

    citation_key: str
    arxiv_id: str
    status: str  # "verified" | "rejected"
    title_match: bool
    year_match: bool
    arxiv_id_match: bool
    populated_authors: tuple[str, ...]
    mismatches: tuple[str, ...]


def _normalize_title(text: str) -> str:
    lowered = text.lower()
    return re.sub(r"\s+", " ", lowered).strip(" .:;,!?")


def _title_matches(manifest_title: str, arxiv_title: str) -> bool:
    return _normalize_title(manifest_title) == _normalize_title(arxiv_title)


def verify_record(record: SourceRecord, metadata: ArxivMetadata) -> VerificationResult:
    """Cross-check a manifest record against authoritative arXiv metadata."""

    assert record.arxiv_id is not None, (
        f"verify_record requires an arXiv source; {record.citation_key!r} has none"
    )
    mismatches: list[str] = []
    arxiv_id_match = record.arxiv_id == metadata.arxiv_id
    if not arxiv_id_match:
        mismatches.append(
            f"arxiv_id mismatch: manifest={record.arxiv_id!r} arxiv={metadata.arxiv_id!r}"
        )
    title_match = _title_matches(record.title, metadata.title)
    if not title_match:
        mismatches.append(f"title mismatch: manifest={record.title!r} arxiv={metadata.title!r}")
    year_match = record.year == metadata.published_year
    if not year_match:
        mismatches.append(f"year mismatch: manifest={record.year} arxiv={metadata.published_year}")
    authors = tuple(to_surname_given(name) for name in metadata.authors)
    if not authors:
        mismatches.append("authoritative response had no authors")
    status = "rejected" if mismatches else "verified"
    return VerificationResult(
        citation_key=record.citation_key,
        arxiv_id=record.arxiv_id,
        status=status,
        title_match=title_match,
        year_match=year_match,
        arxiv_id_match=arxiv_id_match,
        populated_authors=authors,
        mismatches=tuple(mismatches),
    )
