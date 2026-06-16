"""run-id format and workspace-path safety tests."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from agentic_publishing_pipeline.runtime import (
    PathSafetyError,
    WorkspacePaths,
    generate_run_id,
    is_well_formed_run_id,
)


def test_run_id_well_formed_shape() -> None:
    rid = generate_run_id(
        now=lambda: datetime(2026, 6, 15, 12, 30, 45, tzinfo=UTC),
        rand_hex=lambda n: "abcdabcd",
    )
    assert rid == "RUN-20260615-123045-abcdabcd"
    assert is_well_formed_run_id(rid)


def test_run_id_recognised_by_validator() -> None:
    rid = generate_run_id()
    assert is_well_formed_run_id(rid)


def test_run_id_validator_rejects_garbage() -> None:
    assert not is_well_formed_run_id("not-a-run")
    assert not is_well_formed_run_id("RUN--abcd")
    assert not is_well_formed_run_id("RUN-20260615-123045-XYZQQQQQ")


def test_workspace_paths_create_subdirs(tmp_path: Path) -> None:
    paths = WorkspacePaths(tmp_path / "RUN-1")
    paths.ensure_layout()
    for sub in WorkspacePaths.SUBDIRS:
        assert (paths.root / sub).is_dir()


def test_workspace_paths_resolve_relative(tmp_path: Path) -> None:
    paths = WorkspacePaths(tmp_path / "RUN-1")
    paths.ensure_layout()
    artifact = paths.child("artifacts/research_notes.v1.json")
    assert artifact.parent == paths.root / "artifacts"


def test_workspace_paths_refuses_traversal(tmp_path: Path) -> None:
    paths = WorkspacePaths(tmp_path / "RUN-1")
    paths.ensure_layout()
    with pytest.raises(PathSafetyError):
        paths.child("../escape.txt")
    with pytest.raises(PathSafetyError):
        paths.child("/etc/passwd")
