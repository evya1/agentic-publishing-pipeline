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
    assert sorted(record.chapters_written) == sorted([
        f"{CANONICAL_MD}/chapters/planning.md",
        f"{CANONICAL_MD}/chapters/memory.md",
    ])
    assert sorted(record.static_files_written) == sorted([
        f"{CANONICAL_MD}/outline.md",
        f"{CANONICAL_MD}/research_notes.md",
    ])
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
