"""Pure-function tests for ``verify`` and ``dry_run``.

These exercise the read-only operations against a ``FakeClient`` without
going through the ``main`` dispatcher, so they assert directly that no
``create_milestone`` call is ever issued during read-only paths.
"""

from __future__ import annotations

from pathlib import Path

from _milestones_core import load_manifest
from sync_milestones import EXIT_DIVERGED, EXIT_OK, dry_run, verify

from .conftest import FakeClient, make_live


def test_verify_returns_ok_when_state_matches(simple_manifest_path: Path, io_buffers) -> None:
    manifest = load_manifest(simple_manifest_path)
    client = FakeClient(
        live=[
            make_live("Phase A", "Alpha.", number=1),
            make_live("Phase B", "Beta.", number=2),
        ]
    )
    out, err = io_buffers
    assert verify(manifest, client, out=out, err=err) == EXIT_OK
    assert client.create_calls == []
    assert "matches: 2" in out.getvalue()


def test_verify_returns_diverged_when_state_differs(simple_manifest_path: Path, io_buffers) -> None:
    manifest = load_manifest(simple_manifest_path)
    client = FakeClient(live=[make_live("Phase A", "Alpha.", number=1)])
    out, err = io_buffers
    assert verify(manifest, client, out=out, err=err) == EXIT_DIVERGED
    assert client.create_calls == []


def test_dry_run_performs_zero_writes(simple_manifest_path: Path, io_buffers) -> None:
    manifest = load_manifest(simple_manifest_path)
    client = FakeClient(live=[make_live("Phase A", "Alpha.", number=1)])
    out, err = io_buffers
    assert dry_run(manifest, client, out=out, err=err) == EXIT_DIVERGED
    assert client.create_calls == []
    assert "Would create: Phase B" in out.getvalue()


def test_dry_run_succeeds_when_state_matches(simple_manifest_path: Path, io_buffers) -> None:
    manifest = load_manifest(simple_manifest_path)
    client = FakeClient(
        live=[
            make_live("Phase A", "Alpha.", number=1),
            make_live("Phase B", "Beta.", number=2),
        ]
    )
    out, err = io_buffers
    assert dry_run(manifest, client, out=out, err=err) == EXIT_OK
    assert client.create_calls == []
    assert "No actions required." in out.getvalue()
