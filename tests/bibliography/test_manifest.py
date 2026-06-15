"""Tests for the P7-I01 typed source manifest loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_publishing_pipeline.bibliography import (
    SourceManifest,
    SourceManifestError,
    SourceRecord,
    VerificationRecord,
    load_source_manifest,
)

REAL_MANIFEST = Path("config/article_sources.yaml")


def _write(tmp_path: Path, content: str) -> Path:
    target = tmp_path / "sources.yaml"
    target.write_text(content, encoding="utf-8")
    return target


def test_loads_real_locked_manifest_with_10_records() -> None:
    manifest = load_source_manifest(REAL_MANIFEST)
    assert isinstance(manifest, SourceManifest)
    assert len(manifest) == 10
    for record in manifest.records:
        assert isinstance(record, SourceRecord)
        # Post-P7-I05 keys: lowercase ASCII, no `tbd` prefix.
        assert not record.citation_key.startswith("tbd"), record.citation_key
        assert record.citation_key == record.citation_key.lower()
        assert record.citation_key.isascii()
        # P7-I02 flips status to verified.
        assert record.verification.status == "verified"
        assert record.is_arxiv_source
        assert record.source_archive is not None


def test_load_is_deterministic_for_same_bytes() -> None:
    first = load_source_manifest(REAL_MANIFEST)
    second = load_source_manifest(REAL_MANIFEST)
    assert first == second
    assert first.citation_keys == second.citation_keys


def test_missing_manifest_path_rejected(tmp_path: Path) -> None:
    with pytest.raises(SourceManifestError, match="not found"):
        load_source_manifest(tmp_path / "nope.yaml")


def test_loader_requires_pathlib_path() -> None:
    with pytest.raises(AssertionError, match="pathlib.Path"):
        load_source_manifest("config/article_sources.yaml")  # type: ignore[arg-type]


def test_non_mapping_top_level_rejected(tmp_path: Path) -> None:
    path = _write(tmp_path, "- not: a-mapping\n")
    with pytest.raises(SourceManifestError, match="mapping"):
        load_source_manifest(path)


def test_sources_must_be_list(tmp_path: Path) -> None:
    path = _write(tmp_path, "sources: {}\n")
    with pytest.raises(SourceManifestError, match="'sources' must be a list"):
        load_source_manifest(path)


def _minimal_yaml(**overrides: object) -> str:
    base: dict[str, object] = {
        "citation_key": "smith2024abc",
        "title": "Some Paper",
        "authors": ["Smith, A."],
        "year": 2024,
        "arxiv_id": "1234.5678",
        "arxiv_url": "https://arxiv.org/abs/1234.5678",
        "source_archive": "data/sources/arxiv/source_zips/1234.5678.zip",
        "intended_use": "demo",
        "verification": {
            "status": "unverified",
            "method": "arxiv_url",
            "verified_at": None,
            "verified_by": None,
        },
    }
    base.update(overrides)
    import yaml as _y

    return _y.safe_dump({"sources": [base]}, sort_keys=False)


def test_minimal_valid_record_loads(tmp_path: Path) -> None:
    manifest = load_source_manifest(_write(tmp_path, _minimal_yaml()))
    record = manifest.records[0]
    assert record.citation_key == "smith2024abc"
    assert record.authors == ("Smith, A.",)
    assert record.verification == VerificationRecord(
        status="unverified", method="arxiv_url", verified_at=None, verified_by=None
    )


def test_missing_required_field_rejected(tmp_path: Path) -> None:
    raw = _minimal_yaml()
    raw_yaml = raw.replace("title: Some Paper", "title: ''")
    with pytest.raises(SourceManifestError, match="title"):
        load_source_manifest(_write(tmp_path, raw_yaml))


def test_invalid_year_rejected(tmp_path: Path) -> None:
    with pytest.raises(SourceManifestError, match="year"):
        load_source_manifest(_write(tmp_path, _minimal_yaml(year=42)))


def test_invalid_authors_member_rejected(tmp_path: Path) -> None:
    with pytest.raises(SourceManifestError, match="authors"):
        load_source_manifest(_write(tmp_path, _minimal_yaml(authors=["Ok", 42])))


def test_arxiv_id_without_url_rejected(tmp_path: Path) -> None:
    with pytest.raises(SourceManifestError, match="arxiv_id and arxiv_url"):
        load_source_manifest(_write(tmp_path, _minimal_yaml(arxiv_url=None)))


def test_unsafe_archive_path_rejected(tmp_path: Path) -> None:
    with pytest.raises(SourceManifestError, match="safe repo-relative"):
        load_source_manifest(
            _write(tmp_path, _minimal_yaml(source_archive="../../etc/passwd"))
        )


def test_absolute_archive_path_rejected(tmp_path: Path) -> None:
    with pytest.raises(SourceManifestError, match="safe repo-relative"):
        load_source_manifest(
            _write(tmp_path, _minimal_yaml(source_archive="/etc/passwd"))
        )


def test_invalid_verification_status_rejected(tmp_path: Path) -> None:
    raw = _minimal_yaml(
        verification={
            "status": "approved",
            "method": "arxiv_url",
            "verified_at": None,
            "verified_by": None,
        }
    )
    with pytest.raises(SourceManifestError, match="verification.status"):
        load_source_manifest(_write(tmp_path, raw))


def test_verified_at_without_verified_by_rejected(tmp_path: Path) -> None:
    raw = _minimal_yaml(
        verification={
            "status": "verified",
            "method": "arxiv_api",
            "verified_at": "2026-06-16T00:00:00Z",
            "verified_by": None,
        }
    )
    with pytest.raises(SourceManifestError, match="set together"):
        load_source_manifest(_write(tmp_path, raw))


def test_duplicate_citation_key_rejected(tmp_path: Path) -> None:
    import yaml as _y

    one = _y.safe_load(_minimal_yaml())["sources"][0]
    two = dict(one)
    two["arxiv_id"] = "9999.9999"
    two["arxiv_url"] = "https://arxiv.org/abs/9999.9999"
    text = _y.safe_dump({"sources": [one, two]}, sort_keys=False)
    with pytest.raises(SourceManifestError, match="duplicate citation_key"):
        load_source_manifest(_write(tmp_path, text))


def test_duplicate_arxiv_id_rejected(tmp_path: Path) -> None:
    import yaml as _y

    one = _y.safe_load(_minimal_yaml())["sources"][0]
    two = dict(one)
    two["citation_key"] = "smith2024def"
    text = _y.safe_dump({"sources": [one, two]}, sort_keys=False)
    with pytest.raises(SourceManifestError, match="duplicate arxiv_id"):
        load_source_manifest(_write(tmp_path, text))


def test_ordering_independence_preserves_records(tmp_path: Path) -> None:
    """The loader's lookups must work regardless of manifest order."""

    import yaml as _y

    one = _y.safe_load(_minimal_yaml())["sources"][0]
    two = dict(one)
    two["citation_key"] = "smith2024def"
    two["arxiv_id"] = "9999.9999"
    two["arxiv_url"] = "https://arxiv.org/abs/9999.9999"
    text_a = _y.safe_dump({"sources": [one, two]}, sort_keys=False)
    text_b = _y.safe_dump({"sources": [two, one]}, sort_keys=False)
    path_a = tmp_path / "a.yaml"
    path_b = tmp_path / "b.yaml"
    path_a.write_text(text_a, encoding="utf-8")
    path_b.write_text(text_b, encoding="utf-8")
    a = load_source_manifest(path_a)
    b = load_source_manifest(path_b)
    assert {r.citation_key for r in a.records} == {r.citation_key for r in b.records}
    assert a.by_citation_key("smith2024abc") is not None
    assert b.by_citation_key("smith2024abc") is not None


def test_lookups_return_none_for_unknown(tmp_path: Path) -> None:
    manifest = load_source_manifest(REAL_MANIFEST)
    assert manifest.by_citation_key("nope") is None
    assert manifest.by_arxiv_id("0000.0000") is None
    assert manifest.by_citation_key(manifest.records[0].citation_key) is not None
    assert manifest.by_arxiv_id(manifest.records[0].arxiv_id) is not None


def test_arxiv_ids_property() -> None:
    manifest = load_source_manifest(REAL_MANIFEST)
    ids = manifest.arxiv_ids
    assert len(ids) == 10
    assert "2504.09037" in ids
