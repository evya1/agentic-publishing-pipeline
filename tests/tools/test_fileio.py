"""Sandboxed FileIO tool tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_publishing_pipeline.runtime import (
    PathSafetyError,
    PipelineRunContext,
    generate_run_id,
)
from agentic_publishing_pipeline.tools import FileIO


def _ctx(tmp_path: Path) -> PipelineRunContext:
    return PipelineRunContext(
        run_id=generate_run_id(),
        results_root=tmp_path / "results",
        mode="offline-fixture",
        env={},
    )


def test_write_text_atomic_and_audited(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    fio = FileIO(ctx)
    target = fio.write_text("artifacts/note.txt", "hello\n")
    assert target.read_text(encoding="utf-8") == "hello\n"
    # No tmp leftovers
    assert list(target.parent.glob("*.tmp-fio")) == []
    events = [e for e in ctx.events.read_all() if e["kind"] == "fileio.wrote"]
    assert events[-1]["payload"]["path"] == "artifacts/note.txt"


def test_write_json_persists_dict(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    fio = FileIO(ctx)
    fio.write_json("artifacts/x.json", {"k": 1})
    assert fio.read_json("artifacts/x.json") == {"k": 1}


def test_write_bytes_audited(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    fio = FileIO(ctx)
    fio.write_bytes("artifacts/x.bin", b"abc")
    assert fio.exists("artifacts/x.bin") is True


def test_path_traversal_refused(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    fio = FileIO(ctx)
    with pytest.raises(PathSafetyError):
        fio.write_text("../escape.txt", "x")


def test_exists_returns_false_for_missing(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    fio = FileIO(ctx)
    assert fio.exists("artifacts/missing.json") is False


def test_exists_returns_false_for_traversal(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    fio = FileIO(ctx)
    assert fio.exists("../escape.json") is False
