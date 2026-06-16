"""Tests for the CLI ``main`` dispatcher.

``main`` is exercised both for its preflight error paths (invalid
manifest, ``resolve_repo`` failure, ``GhError`` during the operation) and
for its success dispatch by monkey-patching ``sync_milestones.GhClient``
with a factory that returns a ``FakeClient``.
"""

from __future__ import annotations

from pathlib import Path

import sync_milestones
from _milestones_gh import GhError
from sync_milestones import EXIT_DIVERGED, EXIT_GH_ERROR, EXIT_MANIFEST_INVALID, EXIT_OK, main

from .conftest import FakeClient, make_live


def _patch_gh_client(monkeypatch, live: list, captured: dict | None = None) -> None:
    def _factory(repo: str, timeout: int = 60) -> FakeClient:
        client = FakeClient(live=list(live))
        if captured is not None:
            captured["repo"] = repo
            captured["client"] = client
        return client

    monkeypatch.setattr(sync_milestones, "GhClient", _factory)


def test_main_rejects_malformed_manifest_path(tmp_path: Path, capsys) -> None:
    missing_path = tmp_path / "nope.json"
    rc = main(["verify", "--manifest", str(missing_path), "--repo", "owner/name"])
    assert rc == EXIT_MANIFEST_INVALID
    assert "Manifest invalid" in capsys.readouterr().err


def test_main_handles_resolve_repo_failure(simple_manifest_path: Path, monkeypatch, capsys) -> None:
    def _fail() -> str:
        raise GhError("no repo here")

    monkeypatch.setattr(sync_milestones, "resolve_repo", _fail)
    rc = main(["verify", "--manifest", str(simple_manifest_path)])
    assert rc == EXIT_GH_ERROR
    assert "no repo here" in capsys.readouterr().err


def test_main_dispatches_verify_with_explicit_repo(
    simple_manifest_path: Path, monkeypatch, capsys
) -> None:
    captured: dict = {}
    _patch_gh_client(
        monkeypatch,
        [
            make_live("Phase A", "Alpha.", number=1),
            make_live("Phase B", "Beta.", number=2),
        ],
        captured,
    )
    rc = main(["verify", "--manifest", str(simple_manifest_path), "--repo", "owner/name"])
    assert rc == EXIT_OK
    assert captured["repo"] == "owner/name"
    out = capsys.readouterr().out
    assert "Repository: owner/name" in out
    assert "matches: 2" in out
    assert captured["client"].create_calls == []


def test_main_dispatches_dry_run(simple_manifest_path: Path, monkeypatch, capsys) -> None:
    captured: dict = {}
    _patch_gh_client(monkeypatch, [make_live("Phase A", "Alpha.", number=1)], captured)
    rc = main(["dry-run", "--manifest", str(simple_manifest_path), "--repo", "o/r"])
    assert rc == EXIT_DIVERGED
    assert "Would create: Phase B" in capsys.readouterr().out
    assert captured["client"].create_calls == []


def test_main_dispatches_apply_with_confirm(
    simple_manifest_path: Path, monkeypatch, capsys
) -> None:
    captured: dict = {}
    _patch_gh_client(monkeypatch, [make_live("Phase A", "Alpha.", number=1)], captured)
    rc = main(
        [
            "apply",
            "--confirm",
            "--manifest",
            str(simple_manifest_path),
            "--repo",
            "o/r",
        ]
    )
    assert rc == EXIT_OK
    assert captured["client"].create_calls == [("Phase B", "Beta.")]


def test_main_surfaces_gh_error_during_operation(
    simple_manifest_path: Path, monkeypatch, capsys
) -> None:
    def _boom(repo: str, timeout: int = 60):
        class _BoomClient:
            def list_milestones(self):
                raise GhError("api down")

            def create_milestone(self, title, description):
                raise AssertionError("must not be called")

        return _BoomClient()

    monkeypatch.setattr(sync_milestones, "GhClient", _boom)
    rc = main(["verify", "--manifest", str(simple_manifest_path), "--repo", "o/r"])
    assert rc == EXIT_GH_ERROR
    assert "gh error" in capsys.readouterr().err
