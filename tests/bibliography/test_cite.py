"""Tests for the P7-I06 citation resolver."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_publishing_pipeline.bibliography import (
    SourceManifest,
    SourceRecord,
    VerificationRecord,
    load_source_manifest,
)
from agentic_publishing_pipeline.bibliography.cite import (
    CitationResolutionError,
    CitationResolver,
)

MANIFEST = Path("config/article_sources.yaml")
GENERATED_MD = Path("results/generated_markdown")


def _record(key: str, *, status: str = "verified") -> SourceRecord:
    return SourceRecord(
        citation_key=key,
        title="t",
        authors=("Smith, A.",),
        year=2025,
        arxiv_id="1234.5678",
        arxiv_url="https://arxiv.org/abs/1234.5678",
        doi=None,
        source_archive=None,
        intended_use="demo",
        verification=VerificationRecord(status, "arxiv_api", None, None),
        notes=None,
    )


def _resolver(*records: SourceRecord) -> CitationResolver:
    return CitationResolver(SourceManifest(records=records))


def test_resolve_returns_verified_key_unchanged() -> None:
    resolver = _resolver(_record("ada2025x"))
    assert resolver.resolve_key("ada2025x") == "ada2025x"


def test_to_latex_cite_wraps_key() -> None:
    resolver = _resolver(_record("ada2025x"))
    assert resolver.to_latex_cite("ada2025x") == r"\cite{ada2025x}"


def test_rewrite_markdown_replaces_placeholders() -> None:
    resolver = _resolver(_record("ada2025x"))
    text = "intro<!-- CITATION: ada2025x -->outro"
    rewritten = resolver.rewrite_markdown(text)
    assert rewritten == r"intro\cite{ada2025x}outro"


def test_unknown_key_fails_loudly() -> None:
    resolver = _resolver(_record("ada2025x"))
    with pytest.raises(CitationResolutionError, match="unknown citation key"):
        resolver.resolve_key("missing2024nope")


def test_provisional_key_fails_loudly() -> None:
    resolver = _resolver(_record("ada2025x"))
    with pytest.raises(CitationResolutionError, match="provisional"):
        resolver.resolve_key("tbd2025something")


def test_rejected_key_fails_loudly() -> None:
    resolver = _resolver(_record("ada2025x"), _record("bad2024boom", status="rejected"))
    with pytest.raises(CitationResolutionError, match="rejected"):
        resolver.resolve_key("bad2024boom")


def test_empty_or_whitespace_key_fails() -> None:
    resolver = _resolver(_record("ada2025x"))
    with pytest.raises(CitationResolutionError, match="empty"):
        resolver.resolve_key("")
    with pytest.raises(CitationResolutionError, match="empty"):
        resolver.resolve_key("ada 2025x")


def test_rewrite_reports_source_in_error() -> None:
    resolver = _resolver(_record("ada2025x"))
    with pytest.raises(CitationResolutionError, match="research_notes.md"):
        resolver.rewrite_markdown(
            "<!-- CITATION: missing -->", source="research_notes.md"
        )


def test_extract_keys_preserves_order() -> None:
    resolver = _resolver(_record("ada2025x"), _record("bob2024y"))
    keys = resolver.extract_keys(
        "<!-- CITATION: bob2024y --> then <!-- CITATION: ada2025x -->"
    )
    assert keys == ["bob2024y", "ada2025x"]


def test_all_active_markdown_citations_resolve_against_manifest() -> None:
    """Every CITATION placeholder in generated_markdown/ resolves cleanly."""

    manifest = load_source_manifest(MANIFEST)
    resolver = CitationResolver(manifest)
    files = sorted(GENERATED_MD.rglob("*.md"))
    files = [f for f in files if f.name != "README.md"]
    for path in files:
        resolver.extract_keys(path.read_text(encoding="utf-8"), source=str(path))


def test_coverage_reports_uncited_evaluation_source() -> None:
    """`ye2024mirai` is a documented coverage gap (no Evaluation chapter)."""

    manifest = load_source_manifest(MANIFEST)
    resolver = CitationResolver(manifest)
    files = sorted(
        p for p in GENERATED_MD.rglob("*.md") if p.name != "README.md"
    )
    report = resolver.coverage(files)
    assert "ye2024mirai" in report.uncited_verified_keys
    assert set(report.cited_keys).issubset(resolver.verified_keys)


def test_ke2025reasoningfrontiers_is_now_cited() -> None:
    """The P7-I06 editorial addition truthfully cites the survey."""

    manifest = load_source_manifest(MANIFEST)
    resolver = CitationResolver(manifest)
    files = sorted(
        p for p in GENERATED_MD.rglob("*.md") if p.name != "README.md"
    )
    report = resolver.coverage(files)
    assert "ke2025reasoningfrontiers" in report.cited_keys


def test_run_citecheck_passes_without_full_coverage_flag() -> None:
    """The active Markdown tree resolves successfully end-to-end."""

    from agentic_publishing_pipeline.bibliography.run_citecheck import main

    assert main([]) == 0


def test_run_citecheck_with_full_coverage_flag_reports_gap() -> None:
    """`--require-full-coverage` returns non-zero while ye2024mirai is uncited."""

    from agentic_publishing_pipeline.bibliography.run_citecheck import main

    assert main(["--require-full-coverage"]) == 1


def test_invalid_fixture_fails_in_unit_test(tmp_path: Path) -> None:
    """A fabricated bad-key Markdown fixture must fail loudly, not silently."""

    resolver = _resolver(_record("ada2025x"))
    bad = tmp_path / "bad.md"
    bad.write_text("<!-- CITATION: invented2099yo -->\n", encoding="utf-8")
    with pytest.raises(CitationResolutionError, match="unknown citation key"):
        resolver.extract_keys(bad.read_text(encoding="utf-8"), source=str(bad))
