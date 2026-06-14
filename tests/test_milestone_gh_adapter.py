"""Hermetic tests for the gh subprocess adapter.

These tests stub ``subprocess.run`` via ``monkeypatch`` so no test invokes
``gh`` and no test touches the network. They cover the success path plus the
explicit error mappings the adapter promises: nonzero exit, missing binary,
timeout, and unparseable JSON.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable

import pytest
from _milestones_core import LiveMilestone
from _milestones_gh import GhClient, GhError, resolve_repo


def _completed(
    stdout: str = "", stderr: str = "", returncode: int = 0
) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(
        args=["gh"], returncode=returncode, stdout=stdout, stderr=stderr
    )


def _patch_run(monkeypatch, fn: Callable) -> None:
    monkeypatch.setattr("_milestones_gh.subprocess.run", fn)


def test_list_milestones_parses_payload(monkeypatch) -> None:
    payload = json.dumps(
        [
            {
                "number": 1,
                "title": "A",
                "description": "Alpha.",
                "due_on": None,
                "state": "open",
            }
        ]
    )
    _patch_run(monkeypatch, lambda *a, **k: _completed(stdout=payload))
    result = GhClient("o/r").list_milestones()
    assert result == [
        LiveMilestone(
            number=1, title="A", description="Alpha.", due_on=None, state="open"
        )
    ]


def test_list_milestones_handles_empty_payload(monkeypatch) -> None:
    _patch_run(monkeypatch, lambda *a, **k: _completed(stdout="[]"))
    assert GhClient("o/r").list_milestones() == []


def test_list_milestones_raises_on_invalid_json(monkeypatch) -> None:
    _patch_run(monkeypatch, lambda *a, **k: _completed(stdout="not json"))
    with pytest.raises(GhError, match="unparseable JSON"):
        GhClient("o/r").list_milestones()


def test_list_milestones_raises_on_non_list_payload(monkeypatch) -> None:
    _patch_run(monkeypatch, lambda *a, **k: _completed(stdout=json.dumps({"x": 1})))
    with pytest.raises(GhError, match="non-list payload"):
        GhClient("o/r").list_milestones()


def test_run_raises_on_nonzero_exit_with_stderr(monkeypatch) -> None:
    _patch_run(
        monkeypatch, lambda *a, **k: _completed(returncode=1, stderr="boom")
    )
    with pytest.raises(GhError, match="boom"):
        GhClient("o/r").list_milestones()


def test_run_raises_when_gh_missing(monkeypatch) -> None:
    def _raise(*_a, **_k):
        raise FileNotFoundError("missing")

    _patch_run(monkeypatch, _raise)
    with pytest.raises(GhError, match="gh CLI not found"):
        GhClient("o/r").list_milestones()


def test_run_raises_on_timeout(monkeypatch) -> None:
    def _raise(*_a, **_k):
        raise subprocess.TimeoutExpired(cmd="gh", timeout=1)

    _patch_run(monkeypatch, _raise)
    with pytest.raises(GhError, match="timed out"):
        GhClient("o/r").list_milestones()


def test_create_milestone_returns_live(monkeypatch) -> None:
    payload = json.dumps(
        {"number": 42, "title": "T", "description": "D", "due_on": None, "state": "open"}
    )
    _patch_run(monkeypatch, lambda *a, **k: _completed(stdout=payload))
    lm = GhClient("o/r").create_milestone("T", "D")
    assert lm.number == 42
    assert lm.title == "T"
    assert lm.description == "D"
    assert lm.due_on is None


def test_create_milestone_raises_on_invalid_json(monkeypatch) -> None:
    _patch_run(monkeypatch, lambda *a, **k: _completed(stdout="oops"))
    with pytest.raises(GhError, match="unparseable JSON"):
        GhClient("o/r").create_milestone("t", "d")


def test_resolve_repo_success(monkeypatch) -> None:
    _patch_run(monkeypatch, lambda *a, **k: _completed(stdout="owner/name\n"))
    assert resolve_repo() == "owner/name"


def test_resolve_repo_failure_surfaces_stderr(monkeypatch) -> None:
    _patch_run(
        monkeypatch, lambda *a, **k: _completed(returncode=1, stderr="not a repo")
    )
    with pytest.raises(GhError, match="not a repo"):
        resolve_repo()


def test_resolve_repo_rejects_malformed_output(monkeypatch) -> None:
    _patch_run(monkeypatch, lambda *a, **k: _completed(stdout="not-a-repo"))
    with pytest.raises(GhError, match="unexpected repository name"):
        resolve_repo()


def test_resolve_repo_missing_gh(monkeypatch) -> None:
    def _raise(*_a, **_k):
        raise FileNotFoundError("missing")

    _patch_run(monkeypatch, _raise)
    with pytest.raises(GhError, match="gh CLI not found"):
        resolve_repo()


def test_resolve_repo_timeout(monkeypatch) -> None:
    def _raise(*_a, **_k):
        raise subprocess.TimeoutExpired(cmd="gh", timeout=1)

    _patch_run(monkeypatch, _raise)
    with pytest.raises(GhError, match="timed out"):
        resolve_repo()
