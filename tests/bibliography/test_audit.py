"""Tests for the P7-I03 reconstructable audit ledger."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_publishing_pipeline.bibliography import load_source_manifest
from agentic_publishing_pipeline.bibliography._audit_corrections import CORRECTIONS
from agentic_publishing_pipeline.bibliography.audit import (
    AuditInputs,
    build_audit_entries,
    render_mirror,
)

MANIFEST = Path("config/article_sources.yaml")
MIRROR = Path("results/run_logs/source_verification.json")
SOURCES_MD = Path("docs/SOURCES.md")


@pytest.fixture
def inputs() -> AuditInputs:
    return AuditInputs(
        manifest_path=MANIFEST,
        verification_report_path=Path("results/run_logs/p7i02_verification.json"),
        rekey_ledger_path=Path("results/run_logs/p7i05_rekey.json"),
        fixture_dir=Path("tests/fixtures/arxiv"),
        sources_md_path=SOURCES_MD,
        mirror_json_path=MIRROR,
    )


def test_audit_entries_cover_every_manifest_record(inputs: AuditInputs) -> None:
    entries = build_audit_entries(inputs)
    manifest = load_source_manifest(MANIFEST)
    assert len(entries) == len(manifest)
    by_key = {e["final_citation_key"]: e for e in entries}
    for record in manifest.records:
        assert record.citation_key in by_key, record.citation_key
        entry = by_key[record.citation_key]
        assert entry["arxiv_id"] == record.arxiv_id
        assert entry["previous_citation_key"].startswith("tbd")
        assert entry["verification"]["status"] == "verified"
        assert entry["local_archive"]["archive_inspection"] == "metadata_only"


def test_audit_mirror_matches_committed_payload(inputs: AuditInputs) -> None:
    """The committed mirror JSON must match a freshly generated one."""

    entries = build_audit_entries(inputs)
    expected = json.loads(render_mirror(entries))
    actual = json.loads(MIRROR.read_text(encoding="utf-8"))
    # The generated_at timestamp changes per run; compare everything else.
    expected.pop("generated_at", None)
    actual.pop("generated_at", None)
    assert expected == actual


def test_audit_mirror_has_summary_block(inputs: AuditInputs) -> None:
    payload = json.loads(MIRROR.read_text(encoding="utf-8"))
    assert payload["schema"] == "p7i03-source-audit/v1"
    summary = payload["summary"]
    assert summary["total"] == 10
    assert summary["verified"] == 10
    assert summary["rejected"] == 0


def test_audit_entries_record_placeholder_corrections(inputs: AuditInputs) -> None:
    """The three documented corrections must appear on the matching entries."""

    entries = build_audit_entries(inputs)
    corrected = {
        e["arxiv_id"]: e["correction_applied"]
        for e in entries
        if e["correction_applied"] is not None
    }
    assert set(corrected.keys()) == set(CORRECTIONS.keys())
    for arxiv_id, record in corrected.items():
        assert record["field"] in {"title", "year"}
        assert record["applied_at"] == ""
        assert "evya1" in record["applied_by"]


def test_audit_generation_is_deterministic(inputs: AuditInputs) -> None:
    """Two consecutive calls must produce identical entries (ignoring timestamp)."""

    first = build_audit_entries(inputs)
    second = build_audit_entries(inputs)
    assert first == second


def test_sources_md_contains_p7i03_section() -> None:
    text = SOURCES_MD.read_text(encoding="utf-8")
    assert "P7I03_SECTION_START" in text and "P7I03_SECTION_END" in text
    # Every final key must appear in the rendered Markdown.
    manifest = load_source_manifest(MANIFEST)
    for record in manifest.records:
        assert record.citation_key in text, record.citation_key


def test_audit_run_check_mode_reports_in_sync() -> None:
    """The committed audit ledger must already be in sync."""

    from agentic_publishing_pipeline.bibliography.run_audit import main

    assert main(["--check"]) == 0
