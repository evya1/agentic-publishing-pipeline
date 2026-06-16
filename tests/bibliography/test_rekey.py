"""Tests for the P7-I05 provisional → final citation-key migration."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_publishing_pipeline.bibliography import (
    SourceManifest,
    SourceRecord,
    VerificationRecord,
    load_source_manifest,
)
from agentic_publishing_pipeline.bibliography.rekey import (
    RekeyError,
    apply_key_map,
    build_key_map,
    derive_final_key,
)

MANIFEST = Path("config/article_sources.yaml")


def _verified(**overrides: object) -> SourceRecord:
    base: dict[str, object] = {
        "citation_key": "tbd2025foo",
        "title": "X",
        "authors": ("Smith, A.",),
        "year": 2025,
        "arxiv_id": "1234.5678",
        "arxiv_url": "https://arxiv.org/abs/1234.5678",
        "doi": None,
        "source_archive": "data/sources/arxiv/source_zips/1234.5678.zip",
        "intended_use": "demo",
        "verification": VerificationRecord("verified", "arxiv_api", "now", "id:acct"),
        "notes": None,
    }
    base.update(overrides)
    return SourceRecord(**base)  # type: ignore[arg-type]


def test_derive_final_key_lowercases_and_strips_diacritics() -> None:
    record = _verified(authors=("Corrêa, Augusto B.",), citation_key="tbd2025planning")
    assert derive_final_key(record) == "correa2025planning"


def test_derive_final_key_requires_verified_status() -> None:
    record = _verified(verification=VerificationRecord("unverified", "arxiv_api", None, None))
    with pytest.raises(RekeyError, match="not verified"):
        derive_final_key(record)


def test_derive_final_key_requires_authors() -> None:
    record = _verified(authors=())
    with pytest.raises(RekeyError, match="no authors"):
        derive_final_key(record)


def test_derive_final_key_requires_family_given_form() -> None:
    record = _verified(authors=("Mononym",))
    with pytest.raises(RekeyError, match="Family, Given"):
        derive_final_key(record)


def test_build_key_map_rejects_collisions() -> None:
    record_a = _verified(
        citation_key="tbd2025alpha",
        arxiv_id="1111.1111",
        arxiv_url="https://arxiv.org/abs/1111.1111",
    )
    record_b = _verified(
        citation_key="tbd2025alpha",
        arxiv_id="2222.2222",
        arxiv_url="https://arxiv.org/abs/2222.2222",
    )
    manifest = SourceManifest(records=(record_a, record_b))
    with pytest.raises(RekeyError, match="collision"):
        build_key_map(manifest)


def test_apply_key_map_uses_word_boundaries() -> None:
    """Keys must not partially match longer keys."""

    key_map = {
        "tbd2026agenticreasoning": "wei2026agenticreasoning",
        "tbd2025agenticreasoningtools": "wu2025agenticreasoningtools",
    }
    text = "see tbd2025agenticreasoningtools and tbd2026agenticreasoning today."
    rewritten, count = apply_key_map(text, key_map)
    assert count == 2
    assert "wu2025agenticreasoningtools" in rewritten
    assert "wei2026agenticreasoning" in rewritten
    # No accidental over-replacement that would corrupt the longer key.
    assert "wei2026agenticreasoningtools" not in rewritten


def test_apply_key_map_returns_zero_when_no_match() -> None:
    rewritten, count = apply_key_map("nothing to see", {"tbd2025x": "y2025x"})
    assert count == 0
    assert rewritten == "nothing to see"


def test_build_key_map_matches_committed_manifest() -> None:
    """Sanity-check that the real manifest's keys round-trip through the deriver."""

    manifest = load_source_manifest(MANIFEST)
    # The current manifest already contains final keys post-P7-I05.
    # Re-deriving from itself must reproduce each key.
    for record in manifest.records:
        # Slug derivation expects the provisional `tbd…` prefix; verify
        # that a synthetic provisional key matching the current slug
        # reproduces the same final key.
        year_str = str(record.year)
        if year_str not in record.citation_key:
            continue
        slug = record.citation_key.split(year_str, 1)[1]
        if not slug:
            continue
        synthetic = _verified(
            citation_key=f"tbd{record.year}{slug}",
            title=record.title,
            authors=record.authors,
            year=record.year,
            arxiv_id=record.arxiv_id,
            arxiv_url=record.arxiv_url,
            source_archive=record.source_archive,
            intended_use=record.intended_use,
            verification=record.verification,
        )
        assert derive_final_key(synthetic) == record.citation_key, record.citation_key


def test_rekey_ledger_records_migration() -> None:
    """The committed ledger must record the key map and the SHA delta."""

    import json

    ledger = json.loads(Path("results/run_logs/p7i05_rekey.json").read_text(encoding="utf-8"))
    assert ledger["schema"] == "p7i05-rekey/v1"
    assert ledger["previous_draft_sha256"] != ledger["new_draft_sha256"]
    assert len(ledger["key_map"]) == 10
    # Every value is a valid post-P7-I05 key.
    for old, new in ledger["key_map"].items():
        assert old.startswith("tbd"), old
        assert not new.startswith("tbd"), new
        assert new.isascii() and new == new.lower()


def test_phase6_review_record_no_longer_matches_current_markdown() -> None:
    """The Phase 6 review gate must refuse to proceed after the rekey."""

    import json

    record = json.loads(Path("results/run_logs/review_record.json").read_text(encoding="utf-8"))
    from agentic_publishing_pipeline.crews._review_gate import (
        compute_draft_revision,
    )

    current = compute_draft_revision(Path("results/generated_markdown"))
    assert record["draft_sha256"] != current, (
        "Phase 6 approved hash unexpectedly matches migrated markdown; "
        "the migration would silently bypass the review gate."
    )
