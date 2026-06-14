"""Pagination and pre-write safety tests for milestone sync."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from _milestones_core import load_manifest
from _milestones_gh import GhClient, GhError
from sync_milestones import EXIT_APPLY_ABORTED, EXIT_OK, apply

from .conftest import FakeClient, make_live


def _completed(stdout: str) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=["gh"], returncode=0, stdout=stdout, stderr="")


def test_gh_client_combines_multiple_milestone_pages(monkeypatch) -> None:
    seen: dict[str, list[str]] = {}
    pages = [
        [{"number": 1, "title": "Phase A", "description": "Alpha.", "due_on": None}],
        [{"number": 2, "title": "Phase B", "description": "Beta.", "due_on": None}],
    ]

    def _run(cmd: list[str], **_kwargs):
        seen["cmd"] = cmd
        return _completed(json.dumps(pages))

    monkeypatch.setattr("_milestones_gh.subprocess.run", _run)
    live = GhClient("owner/repo").list_milestones()
    assert [m.title for m in live] == ["Phase A", "Phase B"]
    assert "--paginate" in seen["cmd"]
    assert "--slurp" in seen["cmd"]


def test_gh_client_rejects_malformed_paginated_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "_milestones_gh.subprocess.run",
        lambda *_args, **_kwargs: _completed(json.dumps([[{"number": 1}], "bad"])),
    )
    with pytest.raises(GhError, match="non-list page"):
        GhClient("owner/repo").list_milestones()


def test_expected_milestone_on_later_page_is_detected(
    simple_manifest_path: Path, io_buffers
) -> None:
    manifest = load_manifest(simple_manifest_path)
    client = FakeClient(
        live=[
            make_live("Phase A", "Alpha.", number=1),
            make_live("Phase B", "Beta.", number=101),
        ]
    )
    out, err = io_buffers
    assert apply(manifest, client, confirm=True, out=out, err=err) == EXIT_OK
    assert client.create_calls == []
    assert "matching milestones (2):" in out.getvalue()


def test_later_page_extra_blocks_apply_with_zero_writes(
    simple_manifest_path: Path, io_buffers
) -> None:
    manifest = load_manifest(simple_manifest_path)
    client = FakeClient(
        live=[
            make_live("Phase A", "Alpha.", number=1),
            make_live("Phase B", "Beta.", number=2),
            make_live("Phase C", "Extra.", number=101),
        ]
    )
    out, err = io_buffers
    assert apply(manifest, client, confirm=True, out=out, err=err) == EXIT_APPLY_ABORTED
    assert client.create_calls == []
    assert "Phase C" in err.getvalue()


def test_duplicate_title_across_pages_blocks_apply_with_zero_writes(
    simple_manifest_path: Path, io_buffers
) -> None:
    manifest = load_manifest(simple_manifest_path)
    client = FakeClient(
        live=[
            make_live("Phase A", "Alpha.", number=1),
            make_live("Phase B", "Beta.", number=2),
            make_live("Phase A", "Alpha.", number=101),
        ]
    )
    out, err = io_buffers
    assert apply(manifest, client, confirm=True, out=out, err=err) == EXIT_APPLY_ABORTED
    assert client.create_calls == []
    assert "duplicate live titles" in err.getvalue()


def test_preapply_diff_is_printed_before_first_write(
    simple_manifest_path: Path, io_buffers
) -> None:
    manifest = load_manifest(simple_manifest_path)
    out, err = io_buffers

    class _CheckingClient(FakeClient):
        def create_milestone(self, title: str, description: str):
            printed = out.getvalue()
            assert "Accepted pre-apply diff:" in printed
            assert "matching milestones (1):" in printed
            assert "missing milestones to create (1):" in printed
            assert "unexpected extras: none" in printed
            assert "description conflicts: none" in printed
            assert "duplicate live titles: none" in printed
            assert "non-null due_on: none" in printed
            return super().create_milestone(title, description)

    client = _CheckingClient(live=[make_live("Phase A", "Alpha.", number=1)])
    assert apply(manifest, client, confirm=True, out=out, err=err) == EXIT_OK
    assert client.create_calls == [("Phase B", "Beta.")]
