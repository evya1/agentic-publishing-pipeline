"""Search tool tests against the tracked manifest."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_publishing_pipeline.providers import FixtureSearchAdapter, SearchRequest
from agentic_publishing_pipeline.tools import (
    ManifestLoadError,
    load_source_manifest_hits,
    manifest_coverage,
    verify_arxiv_id,
)

MANIFEST_PATH = Path(__file__).resolve().parents[2] / "config" / "article_sources.yaml"


def test_load_manifest_returns_ten_canonical_sources() -> None:
    hits = load_source_manifest_hits(MANIFEST_PATH)
    assert len(hits) == 10


def test_manifest_coverage_includes_known_arxiv_ids() -> None:
    hits = load_source_manifest_hits(MANIFEST_PATH)
    coverage = manifest_coverage(hits)
    assert "2504.09037" in coverage
    assert "2407.01231" in coverage


def test_verify_arxiv_id_resolves_known_entry() -> None:
    hits = load_source_manifest_hits(MANIFEST_PATH)
    hit = verify_arxiv_id(hits, "2504.09037")
    assert hit is not None
    assert "Frontiers" in hit.title


def test_verify_arxiv_id_returns_none_for_unknown() -> None:
    hits = load_source_manifest_hits(MANIFEST_PATH)
    assert verify_arxiv_id(hits, "9999.99999") is None


def test_manifest_load_rejects_missing(tmp_path: Path) -> None:
    with pytest.raises(ManifestLoadError):
        load_source_manifest_hits(tmp_path / "nope.yaml")


def test_manifest_load_rejects_bad_root(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("hello", encoding="utf-8")
    with pytest.raises(ManifestLoadError):
        load_source_manifest_hits(bad)


def test_manifest_load_rejects_missing_title(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("sources:\n  - arxiv_id: '0000.00001'\n", encoding="utf-8")
    with pytest.raises(ManifestLoadError):
        load_source_manifest_hits(bad)


def test_search_adapter_can_consume_manifest_hits() -> None:
    hits = load_source_manifest_hits(MANIFEST_PATH)
    adapter = FixtureSearchAdapter(hits=hits)
    response = adapter.search(SearchRequest(query="2504.09037", max_results=3))
    assert len(response.hits) == 1
    assert response.hits[0].arxiv_id == "2504.09037"
