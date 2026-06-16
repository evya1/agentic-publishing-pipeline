"""Tests for ``apply``: idempotency and abort-before-write safety.

Each test asserts both the return code and ``client.create_calls`` so the
zero-write claim is directly observable rather than implied.
"""

from __future__ import annotations

from pathlib import Path

from _milestones_core import load_manifest
from sync_milestones import (
    EXIT_APPLY_ABORTED,
    EXIT_CONFIRM_REQUIRED,
    EXIT_DIVERGED,
    EXIT_OK,
    apply,
)

from .conftest import FakeClient, make_live


def test_apply_creates_only_missing_milestones(simple_manifest_path: Path, io_buffers) -> None:
    manifest = load_manifest(simple_manifest_path)
    client = FakeClient(live=[make_live("Phase A", "Alpha.", number=1)])
    out, err = io_buffers
    assert apply(manifest, client, confirm=True, out=out, err=err) == EXIT_OK
    assert client.create_calls == [("Phase B", "Beta.")]


def test_second_apply_is_zero_write_no_op(simple_manifest_path: Path, io_buffers) -> None:
    manifest = load_manifest(simple_manifest_path)
    client = FakeClient(
        live=[
            make_live("Phase A", "Alpha.", number=1),
            make_live("Phase B", "Beta.", number=2),
        ]
    )
    out, err = io_buffers
    assert apply(manifest, client, confirm=True, out=out, err=err) == EXIT_OK
    assert client.create_calls == []
    assert "Zero writes performed" in out.getvalue()


def test_apply_requires_confirm(simple_manifest_path: Path, io_buffers) -> None:
    manifest = load_manifest(simple_manifest_path)
    client = FakeClient(live=[])
    out, err = io_buffers
    assert apply(manifest, client, confirm=False, out=out, err=err) == EXIT_CONFIRM_REQUIRED
    assert client.create_calls == []


def test_apply_aborts_before_write_on_description_conflict(
    simple_manifest_path: Path, io_buffers
) -> None:
    manifest = load_manifest(simple_manifest_path)
    client = FakeClient(
        live=[
            make_live("Phase A", "WRONG.", number=1),
            make_live("Phase B", "Beta.", number=2),
        ]
    )
    out, err = io_buffers
    assert apply(manifest, client, confirm=True, out=out, err=err) == EXIT_APPLY_ABORTED
    assert client.create_calls == []
    assert "Aborting apply" in err.getvalue()


def test_apply_aborts_before_write_on_unexpected_extra(
    simple_manifest_path: Path, io_buffers
) -> None:
    manifest = load_manifest(simple_manifest_path)
    client = FakeClient(
        live=[
            make_live("Phase A", "Alpha.", number=1),
            make_live("Phase B", "Beta.", number=2),
            make_live("Phase Z", "Bogus.", number=99),
        ]
    )
    out, err = io_buffers
    assert apply(manifest, client, confirm=True, out=out, err=err) == EXIT_APPLY_ABORTED
    assert client.create_calls == []


def test_apply_aborts_before_write_on_non_null_due_on(
    simple_manifest_path: Path, io_buffers
) -> None:
    manifest = load_manifest(simple_manifest_path)
    client = FakeClient(
        live=[
            make_live("Phase A", "Alpha.", number=1, due_on="2030-01-01T00:00:00Z"),
            make_live("Phase B", "Beta.", number=2),
        ]
    )
    out, err = io_buffers
    assert apply(manifest, client, confirm=True, out=out, err=err) == EXIT_APPLY_ABORTED
    assert client.create_calls == []


def test_apply_aborts_before_write_on_duplicate_live_title(
    simple_manifest_path: Path, io_buffers
) -> None:
    manifest = load_manifest(simple_manifest_path)
    client = FakeClient(
        live=[
            make_live("Phase A", "Alpha.", number=1),
            make_live("Phase A", "Alpha.", number=2),
            make_live("Phase B", "Beta.", number=3),
        ]
    )
    out, err = io_buffers
    assert apply(manifest, client, confirm=True, out=out, err=err) == EXIT_APPLY_ABORTED
    assert client.create_calls == []


def test_apply_post_create_reverify_catches_divergence(
    simple_manifest_path: Path, io_buffers
) -> None:
    """If the gh layer claimed success but the live list still diverges
    afterwards, ``apply`` must surface the divergence with ``EXIT_DIVERGED``
    rather than silently exit 0."""

    manifest = load_manifest(simple_manifest_path)

    class _DroppingClient(FakeClient):
        def create_milestone(self, title: str, description: str):  # type: ignore[override]
            self.create_calls.append((title, description))
            return make_live(title, description, number=999)

    client = _DroppingClient(live=[make_live("Phase A", "Alpha.", number=1)])
    out, err = io_buffers
    assert apply(manifest, client, confirm=True, out=out, err=err) == EXIT_DIVERGED
    assert client.create_calls == [("Phase B", "Beta.")]
    assert "Post-apply verification failed." in err.getvalue()
