"""Byte-for-byte regeneration of all four committed candidate files."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_publishing_pipeline.crews._phase6_generate import (
    CANONICAL_MD,
    run_phase6_generate,
)
from agentic_publishing_pipeline.crews._phase6_static import write_static_templates
from agentic_publishing_pipeline.crews._review_gate import compute_draft_revision

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / "config" / "article_sources.yaml"
COMMITTED_MD = REPO_ROOT / "results" / "generated_markdown"
CANDIDATE_RELS = (
    "chapters/planning.md",
    "chapters/memory.md",
    "outline.md",
    "research_notes.md",
)


def test_regen_in_clean_tmp_matches_committed_bytes(tmp_path: Path) -> None:
    record = run_phase6_generate(tmp_path.resolve(), MANIFEST)
    assert sorted(record.chapters_written) == sorted(
        [
            f"{CANONICAL_MD}/chapters/planning.md",
            f"{CANONICAL_MD}/chapters/memory.md",
        ]
    )
    assert sorted(record.static_files_written) == sorted(
        [
            f"{CANONICAL_MD}/outline.md",
            f"{CANONICAL_MD}/research_notes.md",
        ]
    )
    md_root = tmp_path / CANONICAL_MD
    for rel in CANDIDATE_RELS:
        regen = (md_root / rel).read_bytes()
        committed = (COMMITTED_MD / rel).read_bytes()
        assert regen == committed, f"{rel} bytes differ from committed copy"


def test_regen_aggregate_revision_matches_committed(tmp_path: Path) -> None:
    run_phase6_generate(tmp_path.resolve(), MANIFEST)
    md_root = tmp_path / CANONICAL_MD
    assert compute_draft_revision(md_root) == compute_draft_revision(COMMITTED_MD)


def test_static_templates_reject_unknown_citation_key(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not in manifest"):
        write_static_templates(tmp_path, manifest_keys=["only_one_known_key"])


def test_static_templates_no_latex_artifact(tmp_path: Path) -> None:
    run_phase6_generate(tmp_path.resolve(), MANIFEST)
    forbidden = (
        list(tmp_path.rglob("*.tex"))
        + list(tmp_path.rglob("*.bib"))
        + list(tmp_path.rglob("*.pdf"))
    )
    assert forbidden == []


# ---------------------------------------------------------------------------
# Atomic validation across the static-template set
# ---------------------------------------------------------------------------


def test_invalid_later_template_writes_nothing_in_clean_root(
    tmp_path: Path,
) -> None:
    """outline.md carries no CITATION markers; research_notes.md carries 10.

    Passing an empty manifest validates outline.md trivially but fails on
    research_notes.md. The atomic implementation must reject the whole
    operation before either file is written.
    """
    md_root = tmp_path / CANONICAL_MD
    with pytest.raises(ValueError, match="research_notes.md.*not in manifest"):
        write_static_templates(md_root, manifest_keys=[])
    assert not (md_root / "outline.md").exists()
    assert not (md_root / "research_notes.md").exists()
    tmp_residue = list(md_root.rglob("*.tmp-p6")) if md_root.exists() else []
    assert tmp_residue == []


def test_invalid_validation_preserves_existing_targets(tmp_path: Path) -> None:
    md_root = tmp_path / CANONICAL_MD
    md_root.mkdir(parents=True)
    outline_target = md_root / "outline.md"
    research_target = md_root / "research_notes.md"
    outline_sentinel = b"PRE-EXISTING OUTLINE SENTINEL\n"
    research_sentinel = b"PRE-EXISTING RESEARCH SENTINEL\n"
    outline_target.write_bytes(outline_sentinel)
    research_target.write_bytes(research_sentinel)
    with pytest.raises(ValueError, match="not in manifest"):
        write_static_templates(md_root, manifest_keys=[])
    assert outline_target.read_bytes() == outline_sentinel
    assert research_target.read_bytes() == research_sentinel
    tmp_residue = list(md_root.rglob("*.tmp-p6"))
    assert tmp_residue == []


def test_valid_generation_reports_full_citation_union(tmp_path: Path) -> None:
    md_root = tmp_path / CANONICAL_MD
    from agentic_publishing_pipeline.crews._phase6_generate import (
        extract_manifest_keys,
    )

    keys = extract_manifest_keys(MANIFEST)
    written, cites = write_static_templates(md_root, manifest_keys=keys)
    assert written == ["outline.md", "research_notes.md"]
    assert (md_root / "outline.md").read_bytes() == (COMMITTED_MD / "outline.md").read_bytes()
    assert (md_root / "research_notes.md").read_bytes() == (
        COMMITTED_MD / "research_notes.md"
    ).read_bytes()
    # Post-P7-I05 final keys (authorYYYYkey).
    expected_cites = {
        "correa2025planningperformance",
        "wei2026agenticreasoning",
        "huang2025licomemory",
        "chen2025telemem",
        "wu2025agenticreasoningtools",
        "wang2025proactiveretrievalmedical",
        "liu2025agenticmath",
        "yao2025multimodalsurvey",
    }
    assert expected_cites.issubset(set(cites))
