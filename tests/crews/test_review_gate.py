"""Tests for the human Markdown review gate (P6-I02 / issue #19)."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_publishing_pipeline.crews._review_gate import (
    HumanReviewRequired,
    ReviewRecord,
    compute_draft_revision,
    enforce_review_gate,
    load_review_record,
    make_review_record,
    write_review_record,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATED_MD = REPO_ROOT / "results" / "generated_markdown"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_draft(md_root: Path, name: str = "ch.md") -> Path:
    p = md_root / "chapters" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("# Chapter\n<!-- CITATION: tbd2025planningperformance -->", encoding="utf-8")
    return p


def _human_record(md_root: Path) -> ReviewRecord:
    return make_review_record(
        reviewer="Alice Reviewer", generated_md_root=md_root, verdict="approved"
    )


# ---------------------------------------------------------------------------
# compute_draft_revision
# ---------------------------------------------------------------------------


def test_compute_draft_revision_is_deterministic(tmp_path: Path) -> None:
    md_root = tmp_path / "generated_markdown"
    _write_draft(md_root)
    sha1 = compute_draft_revision(md_root)
    sha2 = compute_draft_revision(md_root)
    assert sha1 == sha2


def test_compute_draft_revision_changes_when_draft_changes(tmp_path: Path) -> None:
    md_root = tmp_path / "generated_markdown"
    p = _write_draft(md_root)
    sha_before = compute_draft_revision(md_root)
    p.write_text("# Modified", encoding="utf-8")
    sha_after = compute_draft_revision(md_root)
    assert sha_before != sha_after


# ---------------------------------------------------------------------------
# write / load
# ---------------------------------------------------------------------------


def test_write_and_load_review_record_round_trips(tmp_path: Path) -> None:
    md_root = tmp_path / "generated_markdown"
    _write_draft(md_root)
    log_root = tmp_path / "run_logs"
    record = _human_record(md_root)
    write_review_record(record, log_root)
    loaded = load_review_record(log_root)
    assert loaded is not None
    assert loaded.reviewer == "Alice Reviewer"
    assert loaded.verdict == "approved"
    assert loaded.draft_sha256 == record.draft_sha256


def test_load_review_record_returns_none_when_absent(tmp_path: Path) -> None:
    assert load_review_record(tmp_path / "run_logs") is None


def test_load_review_record_raises_on_unknown_verdict(tmp_path: Path) -> None:
    log_root = tmp_path / "run_logs"
    log_root.mkdir()
    (log_root / "review_record.json").write_text(
        '{"reviewer":"Bob","draft_sha256":"abc","reviewed_at":"2026-01-01","verdict":"LGTM","notes":""}',
        encoding="utf-8",
    )
    with pytest.raises(HumanReviewRequired, match="unknown verdict"):
        load_review_record(log_root)


# ---------------------------------------------------------------------------
# enforce_review_gate — blocking cases
# ---------------------------------------------------------------------------


def test_missing_review_blocks(tmp_path: Path) -> None:
    md_root = tmp_path / "generated_markdown"
    _write_draft(md_root)
    with pytest.raises(HumanReviewRequired, match="No review record"):
        enforce_review_gate(md_root, tmp_path / "run_logs")


def test_llm_reviewer_blocks(tmp_path: Path) -> None:
    md_root = tmp_path / "generated_markdown"
    _write_draft(md_root)
    log_root = tmp_path / "run_logs"
    for llm_name in ("claude", "codex", "gpt", "Agent", "Reviewer Agent"):
        rec = ReviewRecord(
            reviewer=llm_name,
            draft_sha256=compute_draft_revision(md_root),
            reviewed_at="2026-01-01T00:00:00+00:00",
            verdict="approved",
        )
        write_review_record(rec, log_root)
        with pytest.raises(HumanReviewRequired, match="LLM/agent identity"):
            enforce_review_gate(md_root, log_root)


def test_changes_requested_blocks(tmp_path: Path) -> None:
    md_root = tmp_path / "generated_markdown"
    _write_draft(md_root)
    log_root = tmp_path / "run_logs"
    rec = make_review_record(
        reviewer="Alice Reviewer",
        generated_md_root=md_root,
        verdict="changes_requested",
        notes="Fix figure captions.",
    )
    write_review_record(rec, log_root)
    with pytest.raises(HumanReviewRequired, match="changes_requested"):
        enforce_review_gate(md_root, log_root)


def test_modified_draft_invalidates_approval(tmp_path: Path) -> None:
    md_root = tmp_path / "generated_markdown"
    draft = _write_draft(md_root)
    log_root = tmp_path / "run_logs"
    rec = _human_record(md_root)
    write_review_record(rec, log_root)
    draft.write_text("# Modified after approval", encoding="utf-8")
    with pytest.raises(HumanReviewRequired, match="changed since approval"):
        enforce_review_gate(md_root, log_root)


def test_stale_sha_blocks(tmp_path: Path) -> None:
    md_root = tmp_path / "generated_markdown"
    _write_draft(md_root)
    log_root = tmp_path / "run_logs"
    rec = ReviewRecord(
        reviewer="Alice Reviewer",
        draft_sha256="deadbeef" * 8,
        reviewed_at="2026-01-01T00:00:00+00:00",
        verdict="approved",
    )
    write_review_record(rec, log_root)
    with pytest.raises(HumanReviewRequired, match="changed since approval"):
        enforce_review_gate(md_root, log_root)


def test_empty_reviewer_blocks(tmp_path: Path) -> None:
    md_root = tmp_path / "generated_markdown"
    _write_draft(md_root)
    log_root = tmp_path / "run_logs"
    rec = ReviewRecord(
        reviewer="",
        draft_sha256=compute_draft_revision(md_root),
        reviewed_at="2026-01-01T00:00:00+00:00",
        verdict="approved",
    )
    write_review_record(rec, log_root)
    with pytest.raises(HumanReviewRequired, match="empty reviewer"):
        enforce_review_gate(md_root, log_root)


# ---------------------------------------------------------------------------
# enforce_review_gate — passing case
# ---------------------------------------------------------------------------


def test_matching_human_approval_passes(tmp_path: Path) -> None:
    md_root = tmp_path / "generated_markdown"
    _write_draft(md_root)
    log_root = tmp_path / "run_logs"
    rec = _human_record(md_root)
    write_review_record(rec, log_root)
    enforce_review_gate(md_root, log_root)


# ---------------------------------------------------------------------------
# CLI gate integration (compile-only blocks without approval)
# ---------------------------------------------------------------------------


def test_compile_only_blocked_without_review(tmp_path: Path) -> None:
    from agentic_publishing_pipeline.crews import run_cli

    results = tmp_path / "results"
    REPO_ROOT = Path(__file__).resolve().parents[2]
    registry = REPO_ROOT / "config" / "prompt_registry"
    manifest = REPO_ROOT / "config" / "article_sources.yaml"
    rc = run_cli(
        [
            "--mode",
            "offline-fixture",
            "--registry",
            str(registry),
            "--manifest",
            str(manifest),
            "--results-root",
            str(results),
        ],
        env={},
    )
    assert rc == 0
    run_id = next(p.name for p in results.iterdir() if p.name.startswith("RUN-"))
    (results / run_id / "latex_project" / "main.tex").write_text(
        "\\documentclass{article}\\begin{document}test\\end{document}",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit, match="human review gate"):
        run_cli(
            [
                "--mode",
                "compile-only",
                "--registry",
                str(registry),
                "--results-root",
                str(results),
                "--run-id",
                run_id,
            ],
            env={},
        )


def test_compile_only_passes_with_valid_review(tmp_path: Path) -> None:
    from agentic_publishing_pipeline.crews import run_cli

    results = tmp_path / "results"
    REPO_ROOT = Path(__file__).resolve().parents[2]
    registry = REPO_ROOT / "config" / "prompt_registry"
    manifest = REPO_ROOT / "config" / "article_sources.yaml"
    rc = run_cli(
        [
            "--mode",
            "offline-fixture",
            "--registry",
            str(registry),
            "--manifest",
            str(manifest),
            "--results-root",
            str(results),
        ],
        env={},
    )
    assert rc == 0
    run_id = next(p.name for p in results.iterdir() if p.name.startswith("RUN-"))
    (results / run_id / "latex_project" / "main.tex").write_text(
        "\\documentclass{article}\\begin{document}test\\end{document}",
        encoding="utf-8",
    )
    md_root = results / "generated_markdown"
    log_root = results / "run_logs"
    rec = make_review_record(
        reviewer="Alice Reviewer", generated_md_root=md_root, verdict="approved"
    )
    write_review_record(rec, log_root)
    rc2 = run_cli(
        [
            "--mode",
            "compile-only",
            "--registry",
            str(registry),
            "--results-root",
            str(results),
            "--run-id",
            run_id,
        ],
        env={},
    )
    assert rc2 == 0
