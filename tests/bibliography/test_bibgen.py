"""Tests for the P7-I04 verified ``references.bib`` generator."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from agentic_publishing_pipeline.bibliography import (
    SourceManifest,
    SourceRecord,
    VerificationRecord,
    load_source_manifest,
)
from agentic_publishing_pipeline.bibliography.bibgen import (
    BibGenError,
    render_bib,
    render_entry,
)

REFERENCES_BIB = Path("latex_project/references.bib")
MANIFEST = Path("config/article_sources.yaml")


def _record(**overrides: object) -> SourceRecord:
    base: dict[str, object] = {
        "citation_key": "smith2024demo",
        "title": "Some Paper",
        "authors": ("Smith, Ada", "Doe, Jane"),
        "year": 2024,
        "arxiv_id": "1234.5678",
        "arxiv_url": "https://arxiv.org/abs/1234.5678",
        "doi": None,
        "source_archive": "data/sources/arxiv/source_zips/x.zip",
        "intended_use": "demo",
        "verification": VerificationRecord("verified", "arxiv_api", "now", "id:acct"),
        "notes": None,
    }
    base.update(overrides)
    return SourceRecord(**base)  # type: ignore[arg-type]


def test_render_entry_emits_required_biblatex_fields() -> None:
    rendered = render_entry(_record())
    assert rendered.startswith("@online{smith2024demo,")
    for field in ("author", "title", "date", "eprint", "eprinttype", "url"):
        assert re.search(rf"\b{field}\s+= \{{", rendered), field
    assert "eprinttype   = {arxiv}" in rendered
    assert "and Doe, Jane" in rendered  # multi-author handling


def test_render_entry_refuses_unverified_record() -> None:
    record = _record(verification=VerificationRecord("unverified", "arxiv_api", None, None))
    with pytest.raises(BibGenError, match="not verified"):
        render_entry(record)


def test_render_entry_requires_arxiv_identifiers() -> None:
    record = _record(arxiv_id=None, arxiv_url=None)
    with pytest.raises(BibGenError, match="arXiv identifiers"):
        render_entry(record)


def test_render_entry_escapes_latex_specials() -> None:
    rendered = render_entry(_record(title="50% off & a $$$ sale_now!"))
    assert "50\\% off \\& a \\$\\$\\$ sale\\_now!" in rendered


def test_render_entry_includes_doi_only_when_set() -> None:
    no_doi = render_entry(_record(doi=None))
    assert "doi          = " not in no_doi
    with_doi = render_entry(_record(doi="10.1234/example"))
    assert "doi          = {10.1234/example}," in with_doi


def test_render_entry_requires_family_given_authors() -> None:
    record = _record(authors=("Mononym",))
    with pytest.raises(BibGenError, match="Family, Given"):
        render_entry(record)


def test_committed_references_bib_matches_generator() -> None:
    """The committed file must match a fresh render — generator is the truth."""

    manifest = load_source_manifest(MANIFEST)
    from agentic_publishing_pipeline.bibliography.run_bibgen import _primary_categories

    cats = _primary_categories(Path("results/run_logs/p7i02_verification.json"))
    fresh = render_bib(manifest, primary_categories=cats)
    committed = REFERENCES_BIB.read_text(encoding="utf-8")
    assert committed == fresh


def test_committed_references_bib_has_one_entry_per_verified_record() -> None:
    text = REFERENCES_BIB.read_text(encoding="utf-8")
    entry_starts = re.findall(r"^@online\{([^,]+),", text, re.MULTILINE)
    manifest = load_source_manifest(MANIFEST)
    verified_keys = {
        r.citation_key for r in manifest.records if r.verification.status == "verified"
    }
    assert set(entry_starts) == verified_keys


def test_no_provisional_key_remains_in_bib() -> None:
    text = REFERENCES_BIB.read_text(encoding="utf-8")
    assert "tbd2" not in text, "provisional tbd... keys must not appear in references.bib"


def test_no_unverified_or_rejected_record_appears() -> None:
    text = REFERENCES_BIB.read_text(encoding="utf-8")
    manifest = load_source_manifest(MANIFEST)
    for record in manifest.records:
        if record.verification.status != "verified":
            assert f"@online{{{record.citation_key}," not in text


def test_render_bib_refuses_empty_verified_set() -> None:
    record = _record(verification=VerificationRecord("rejected", "arxiv_api", None, None))
    manifest = SourceManifest(records=(record,))
    with pytest.raises(BibGenError, match="no verified entries"):
        render_bib(manifest)


def test_render_is_deterministic() -> None:
    manifest = load_source_manifest(MANIFEST)
    first = render_bib(manifest)
    second = render_bib(manifest)
    assert first == second


def test_run_bibgen_check_mode_reports_in_sync() -> None:
    from agentic_publishing_pipeline.bibliography.run_bibgen import main

    assert main(["--check"]) == 0


def test_biber_tool_mode_validates_when_available(tmp_path: Path) -> None:
    """If biber is on PATH, biber --tool --validate-datamodel must succeed."""

    import shutil
    import subprocess

    biber = shutil.which("biber")
    if biber is None:
        pytest.skip("biber not available on PATH")
    work_bib = tmp_path / "references.bib"
    work_bib.write_text(REFERENCES_BIB.read_text(encoding="utf-8"), encoding="utf-8")
    result = subprocess.run(
        [biber, "--tool", "--validate-datamodel", "--quiet", "references.bib"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr or result.stdout
