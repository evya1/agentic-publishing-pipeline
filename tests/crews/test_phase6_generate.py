"""Tests for Phase 6 Markdown-first generation (P6-I01 / issue #18)."""

from __future__ import annotations

import json
import socket
from pathlib import Path

import pytest

from agentic_publishing_pipeline.crews._phase6_generate import (
    Phase6RunRecord,
    extract_manifest_keys,
    run_phase6_generate,
)
from agentic_publishing_pipeline.tools.markdown import has_placeholder

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / "config" / "article_sources.yaml"
GENERATED_MD = REPO_ROOT / "results" / "generated_markdown"


def test_extract_manifest_keys_returns_all_ten() -> None:
    keys = extract_manifest_keys(MANIFEST)
    assert len(keys) == 10
    assert "tbd2025planningperformance" in keys
    assert "tbd2026agenticreasoning" in keys
    assert "tbd2025licomemory" in keys
    assert "tbd2026telemem" in keys
    assert "tbd2025reasoningfrontiers" in keys


def test_run_phase6_generate_creates_chapters(tmp_path: Path) -> None:
    record = run_phase6_generate(tmp_path.resolve(), MANIFEST)
    assert isinstance(record, Phase6RunRecord)
    assert len(record.chapters_written) >= 1
    for rel in record.chapters_written:
        assert (tmp_path / rel).exists(), f"missing chapter: {rel}"


def test_run_phase6_generate_canonical_path(tmp_path: Path) -> None:
    run_phase6_generate(tmp_path.resolve(), MANIFEST)
    chapters_dir = tmp_path / "generated_markdown" / "chapters"
    assert chapters_dir.is_dir()
    md_files = list(chapters_dir.glob("*.md"))
    assert len(md_files) >= 1


def test_run_phase6_generate_all_placeholder_kinds(tmp_path: Path) -> None:
    record = run_phase6_generate(tmp_path.resolve(), MANIFEST)
    assert set(record.all_placeholder_kinds) >= {"FIGURE", "TABLE", "EQUATION", "CITATION"}
    md_root = tmp_path / "generated_markdown"
    body = " ".join(
        p.read_text(encoding="utf-8") for p in md_root.rglob("*.md")
    )
    for kind in ("FIGURE", "TABLE", "EQUATION", "CITATION"):
        assert has_placeholder(body, kind=kind), f"missing {kind} placeholder"  # type: ignore[arg-type]


def test_run_phase6_generate_citation_keys_resolve(tmp_path: Path) -> None:
    manifest_keys = set(extract_manifest_keys(MANIFEST))
    record = run_phase6_generate(tmp_path.resolve(), MANIFEST)
    for key in record.citation_keys_used:
        assert key in manifest_keys, (
            f"CITATION placeholder {key!r} not in manifest. "
            f"Valid keys: {sorted(manifest_keys)}"
        )


def test_run_phase6_generate_run_log_created(tmp_path: Path) -> None:
    record = run_phase6_generate(tmp_path.resolve(), MANIFEST)
    log_file = tmp_path / "run_logs" / f"{record.run_id}.jsonl"
    assert log_file.exists()
    entry = json.loads(log_file.read_text(encoding="utf-8"))
    assert entry["kind"] == "phase6.generate.completed"
    assert entry["run_id"] == record.run_id
    assert len(entry["manifest_citation_keys"]) == 10


def test_run_phase6_generate_no_latex_artifact(tmp_path: Path) -> None:
    run_phase6_generate(tmp_path.resolve(), MANIFEST)
    latex_files = list(tmp_path.rglob("*.tex")) + list(tmp_path.rglob("*.bib"))
    assert not latex_files, f"unexpected LaTeX artifacts: {latex_files}"


def test_run_phase6_generate_safe_output_path(tmp_path: Path) -> None:
    record = run_phase6_generate(tmp_path.resolve(), MANIFEST)
    for rel in record.chapters_written:
        absolute = (tmp_path / rel).resolve()
        absolute.relative_to(tmp_path.resolve())


def test_run_phase6_generate_no_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = socket.socket.connect

    def fail(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("phase6 generate opened a socket")

    monkeypatch.setattr(socket.socket, "connect", fail)
    try:
        run_phase6_generate(tmp_path.resolve(), MANIFEST)
    finally:
        monkeypatch.setattr(socket.socket, "connect", original)


def test_run_phase6_generate_no_api_key_needed(tmp_path: Path) -> None:
    import os
    env_backup = {
        k: os.environ.pop(k)
        for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY")
        if k in os.environ
    }
    try:
        run_phase6_generate(tmp_path.resolve(), MANIFEST)
    finally:
        os.environ.update(env_backup)


def test_committed_chapter_planning_has_all_placeholders() -> None:
    planning = GENERATED_MD / "chapters" / "planning.md"
    assert planning.exists(), "committed planning.md not found"
    body = planning.read_text(encoding="utf-8")
    for kind in ("FIGURE", "TABLE", "EQUATION", "CITATION"):
        assert has_placeholder(body, kind=kind), f"planning.md missing {kind}"  # type: ignore[arg-type]


def test_committed_chapter_memory_has_all_placeholders() -> None:
    memory = GENERATED_MD / "chapters" / "memory.md"
    assert memory.exists(), "committed memory.md not found"
    body = memory.read_text(encoding="utf-8")
    for kind in ("FIGURE", "TABLE", "EQUATION", "CITATION"):
        assert has_placeholder(body, kind=kind), f"memory.md missing {kind}"  # type: ignore[arg-type]


def test_committed_citation_keys_resolve_to_manifest() -> None:
    manifest_keys = set(extract_manifest_keys(MANIFEST))
    from agentic_publishing_pipeline.tools.markdown import _PLACEHOLDER_RE
    for md_file in GENERATED_MD.rglob("*.md"):
        if md_file.name == "README.md":
            continue
        body = md_file.read_text(encoding="utf-8")
        for match in _PLACEHOLDER_RE.finditer(body):
            if match.group(1).upper() == "CITATION":
                key = match.group("desc").strip()
                assert key in manifest_keys, (
                    f"{md_file.name}: CITATION {key!r} not in manifest"
                )
