"""Typed bibliography source records and deterministic manifest loader.

Phase 7 (P7-I01) boundary between ``config/article_sources.yaml`` and
the rest of the Bibliography Agent. The loader yields an immutable
:class:`SourceManifest` with typed :class:`SourceRecord` entries. No
agent or tool should plumb raw manifest dicts past this boundary.

The loader is deterministic and offline: same YAML bytes produce an
equal :class:`SourceManifest`. Validation errors surface as
:class:`SourceManifestError` with the offending record index and
field name so misconfigurations are easy to locate.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import _manifest_validation as _v


class SourceManifestError(RuntimeError):
    """Raised when the source manifest cannot be parsed or validated."""


@dataclass(frozen=True)
class VerificationRecord:
    status: str
    method: str
    verified_at: str | None
    verified_by: str | None


@dataclass(frozen=True)
class SourceRecord:
    citation_key: str
    title: str
    authors: tuple[str, ...]
    year: int
    arxiv_id: str | None
    arxiv_url: str | None
    doi: str | None
    source_archive: str | None
    intended_use: str
    verification: VerificationRecord
    notes: str | None = None

    @property
    def is_arxiv_source(self) -> bool:
        return self.arxiv_id is not None or self.arxiv_url is not None


@dataclass(frozen=True)
class SourceManifest:
    records: tuple[SourceRecord, ...] = field(default_factory=tuple)

    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self):  # pragma: no cover - trivial passthrough
        return iter(self.records)

    @property
    def citation_keys(self) -> tuple[str, ...]:
        return tuple(r.citation_key for r in self.records)

    @property
    def arxiv_ids(self) -> tuple[str, ...]:
        return tuple(r.arxiv_id for r in self.records if r.arxiv_id)

    def by_citation_key(self, key: str) -> SourceRecord | None:
        for record in self.records:
            if record.citation_key == key:
                return record
        return None

    def by_arxiv_id(self, arxiv_id: str) -> SourceRecord | None:
        for record in self.records:
            if record.arxiv_id == arxiv_id:
                return record
        return None


def _build_record(entry: Mapping[str, object], idx: int) -> SourceRecord:
    arxiv_id = _v.optional_str(entry, "arxiv_id")
    arxiv_url = _v.optional_str(entry, "arxiv_url")
    if (arxiv_id is None) != (arxiv_url is None):
        raise _v._ValidationError(
            f"record #{idx} arxiv_id and arxiv_url must be set together"
        )
    status, method, verified_at, verified_by = _v.coerce_verification(entry, idx)
    return SourceRecord(
        citation_key=_v.require_str(entry, "citation_key", idx),
        title=_v.require_str(entry, "title", idx),
        authors=_v.coerce_authors(entry.get("authors"), idx),
        year=_v.coerce_year(entry, idx),
        arxiv_id=arxiv_id,
        arxiv_url=arxiv_url,
        doi=_v.optional_str(entry, "doi"),
        source_archive=_v.coerce_archive_path(entry, idx),
        intended_use=_v.require_str(entry, "intended_use", idx),
        verification=VerificationRecord(status, method, verified_at, verified_by),
        notes=_v.optional_str(entry, "notes"),
    )


def _reject_duplicates(records: list[SourceRecord]) -> None:
    seen_keys: dict[str, int] = {}
    seen_arxiv: dict[str, int] = {}
    seen_doi: dict[str, int] = {}
    for idx, record in enumerate(records):
        if record.citation_key in seen_keys:
            raise SourceManifestError(
                f"duplicate citation_key {record.citation_key!r} at records "
                f"#{seen_keys[record.citation_key]} and #{idx}"
            )
        seen_keys[record.citation_key] = idx
        if record.arxiv_id is not None:
            if record.arxiv_id in seen_arxiv:
                raise SourceManifestError(
                    f"duplicate arxiv_id {record.arxiv_id!r} at records "
                    f"#{seen_arxiv[record.arxiv_id]} and #{idx}"
                )
            seen_arxiv[record.arxiv_id] = idx
        if record.doi is not None:
            if record.doi in seen_doi:
                raise SourceManifestError(
                    f"duplicate doi {record.doi!r} at records "
                    f"#{seen_doi[record.doi]} and #{idx}"
                )
            seen_doi[record.doi] = idx


def load_source_manifest(manifest_path: Path) -> SourceManifest:
    """Read ``config/article_sources.yaml`` as a typed :class:`SourceManifest`."""

    assert isinstance(manifest_path, Path), "manifest_path must be a pathlib.Path"
    if not manifest_path.is_file():
        raise SourceManifestError(f"source manifest not found: {manifest_path}")
    raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise SourceManifestError("source manifest must be a mapping at the top level")
    sources = raw.get("sources", [])
    if not isinstance(sources, list):
        raise SourceManifestError("manifest 'sources' must be a list")
    records: list[SourceRecord] = []
    for idx, entry in enumerate(sources):
        if not isinstance(entry, Mapping):
            raise SourceManifestError(
                f"record #{idx} must be a mapping; got {type(entry).__name__}"
            )
        try:
            records.append(_build_record(entry, idx))
        except _v._ValidationError as exc:
            raise SourceManifestError(str(exc)) from exc
    _reject_duplicates(records)
    return SourceManifest(records=tuple(records))
