"""Search tool — manifest-backed source-metadata verification.

Phase 5 scope is intentionally narrow: the tool returns
:class:`SearchHit` results derived from the **tracked source
manifest** (``config/article_sources.yaml``). It never opens a
socket. Real automatic source discovery is deferred beyond the MVP
per ``docs/PRD.md`` §21 / `docs/PRD_bibliography_and_citations.md`.

The tool is wrapped by the :class:`ApiGatekeeper` so the same usage
event and budget accounting that the live path uses are emitted in
offline-fixture and dry-run modes.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from ..providers.facade import SearchHit


class ManifestLoadError(RuntimeError):
    """Raised when the source manifest cannot be loaded."""


def _coerce_str(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ManifestLoadError(f"manifest entry missing required string field {field!r}")
    return value


def load_source_manifest_hits(manifest_path: Path) -> list[SearchHit]:
    """Read ``config/article_sources.yaml`` and return a SearchHit list."""

    if not manifest_path.is_file():
        raise ManifestLoadError(f"source manifest not found: {manifest_path}")
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ManifestLoadError("source manifest must be a mapping")
    sources = data.get("sources", [])
    if not isinstance(sources, list):
        raise ManifestLoadError("manifest 'sources' must be a list")
    hits: list[SearchHit] = []
    for entry in sources:
        if not isinstance(entry, dict):
            raise ManifestLoadError("source manifest entry must be a mapping")
        title = _coerce_str(entry.get("title"), field="title")
        arxiv_id = entry.get("arxiv_id")
        doi = entry.get("doi")
        url = entry.get("arxiv_url") or entry.get("doi_url") or entry.get("url") or ""
        snippet = entry.get("intended_use") or entry.get("summary") or ""
        hits.append(
            SearchHit(
                title=title,
                url=str(url),
                snippet=str(snippet),
                arxiv_id=str(arxiv_id) if arxiv_id else None,
                doi=str(doi) if doi else None,
            )
        )
    return hits


def verify_arxiv_id(hits: list[SearchHit], arxiv_id: str) -> SearchHit | None:
    """Return the matching manifest hit for ``arxiv_id`` or ``None``."""

    assert arxiv_id, "arxiv_id must be non-empty"
    for hit in hits:
        if hit.arxiv_id == arxiv_id:
            return hit
    return None


def manifest_coverage(hits: list[SearchHit]) -> set[str]:
    """Return the set of arXiv IDs present in the manifest."""

    return {h.arxiv_id for h in hits if h.arxiv_id}
