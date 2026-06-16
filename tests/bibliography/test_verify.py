"""Offline tests for the P7-I02 verifier using committed arXiv fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_publishing_pipeline.bibliography import load_source_manifest
from agentic_publishing_pipeline.bibliography._arxiv_parse import (
    ArxivParseError,
    parse_arxiv_feed,
    to_surname_given,
)
from agentic_publishing_pipeline.bibliography.verify import verify_record

FIXTURE_DIR = Path("tests/fixtures/arxiv")
MANIFEST = Path("config/article_sources.yaml")


def test_all_locked_manifest_records_verify_against_committed_fixtures() -> None:
    """Every locked source must verify against its committed authoritative response."""

    manifest = load_source_manifest(MANIFEST)
    for record in manifest.records:
        assert record.arxiv_id is not None, record.citation_key
        fixture = FIXTURE_DIR / f"{record.arxiv_id}.xml"
        assert fixture.is_file(), f"missing fixture for {record.citation_key!r}"
        metadata = parse_arxiv_feed(fixture.read_bytes(), expected_id=record.arxiv_id)
        result = verify_record(record, metadata)
        assert result.status == "verified", f"{record.citation_key!r}: {result.mismatches}"
        assert result.populated_authors, record.citation_key


def test_manifest_is_marked_verified_for_every_record() -> None:
    """P7-I02 must leave every manifest entry in the `verified` state."""

    manifest = load_source_manifest(MANIFEST)
    for record in manifest.records:
        assert record.verification.status == "verified", record.citation_key
        assert record.verification.method == "arxiv_api", record.citation_key
        assert record.verification.verified_at is not None, record.citation_key
        assert record.verification.verified_by is not None, record.citation_key
        assert ":" in record.verification.verified_by, record.citation_key
        assert record.authors, record.citation_key


def test_parser_rejects_unexpected_arxiv_id_in_response(tmp_path: Path) -> None:
    body = (FIXTURE_DIR / "2504.09037.xml").read_bytes()
    with pytest.raises(ArxivParseError, match="arXiv id mismatch"):
        parse_arxiv_feed(body, expected_id="1111.2222")


def test_parser_rejects_malformed_xml() -> None:
    with pytest.raises(ArxivParseError, match="valid XML"):
        parse_arxiv_feed(b"<<<not-xml>>>", expected_id="2504.09037")


def test_to_surname_given_round_trip() -> None:
    assert to_surname_given("Jane Doe") == "Doe, Jane"
    assert to_surname_given("Adam B. Smith") == "Smith, Adam B."
    # Already canonical form stays put.
    assert to_surname_given("Doe, Jane") == "Doe, Jane"
    # Single-token names are returned unchanged rather than fabricated.
    assert to_surname_given("Mononym") == "Mononym"


def test_verifier_flags_title_mismatch_as_rejected() -> None:
    """A manufactured title mismatch must be reported, not papered over."""

    manifest = load_source_manifest(MANIFEST)
    record = manifest.records[0]
    metadata = parse_arxiv_feed(
        (FIXTURE_DIR / f"{record.arxiv_id}.xml").read_bytes(),
        expected_id=record.arxiv_id,
    )
    # Replace the manifest title with a deliberate mismatch.
    sabotaged = record.__class__(
        citation_key=record.citation_key,
        title="Totally Different Title That Will Not Match",
        authors=record.authors,
        year=record.year,
        arxiv_id=record.arxiv_id,
        arxiv_url=record.arxiv_url,
        doi=record.doi,
        source_archive=record.source_archive,
        intended_use=record.intended_use,
        verification=record.verification,
        notes=record.notes,
    )
    result = verify_record(sabotaged, metadata)
    assert result.status == "rejected"
    assert any("title mismatch" in m for m in result.mismatches)


def test_verifier_requires_arxiv_id_on_record() -> None:
    manifest = load_source_manifest(MANIFEST)
    record = manifest.records[0]
    no_arxiv = record.__class__(
        citation_key=record.citation_key,
        title=record.title,
        authors=record.authors,
        year=record.year,
        arxiv_id=None,
        arxiv_url=None,
        doi=record.doi,
        source_archive=record.source_archive,
        intended_use=record.intended_use,
        verification=record.verification,
        notes=record.notes,
    )
    metadata = parse_arxiv_feed(
        (FIXTURE_DIR / f"{record.arxiv_id}.xml").read_bytes(),
        expected_id=record.arxiv_id,
    )
    with pytest.raises(AssertionError, match="arXiv source"):
        verify_record(no_arxiv, metadata)


def test_run_verification_does_not_import_during_unit_tests() -> None:
    """The run script must be importable without triggering network code."""

    import importlib

    module = importlib.import_module("agentic_publishing_pipeline.bibliography.run_verification")
    assert hasattr(module, "main")


def test_apply_verification_is_idempotent() -> None:
    """Re-applying the report against the current manifest must be a no-op."""

    import json

    from agentic_publishing_pipeline.bibliography.apply_verification import _apply

    report = json.loads(
        Path("results/run_logs/p7i02_verification.json").read_text(encoding="utf-8")
    )
    text = MANIFEST.read_text(encoding="utf-8")
    # Pull verified_at/verified_by from the current manifest so the
    # idempotency check does not flip them.
    manifest = load_source_manifest(MANIFEST)
    verified_at = manifest.records[0].verification.verified_at
    verified_by = manifest.records[0].verification.verified_by
    assert verified_at is not None and verified_by is not None
    # apply_verification joins on arxiv_id (stable across P7-I05 rekey).
    results = {r["arxiv_id"]: r for r in report["results"]}
    rewritten = _apply(text, results, verified_at=verified_at, verified_by=verified_by)
    assert rewritten == text
