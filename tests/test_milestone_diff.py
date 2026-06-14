"""Structural diff tests for ``_milestones_core.compute_diff``.

Each test asserts both the categorised diff lists and the ``is_clean`` /
``has_blocking_conflict`` flags that ``apply`` consults before deciding
whether any write is allowed.
"""

from __future__ import annotations

from pathlib import Path

from _milestones_core import compute_diff, load_manifest

from .conftest import make_live


def test_diff_clean_when_state_matches(simple_manifest_path: Path) -> None:
    manifest = load_manifest(simple_manifest_path)
    live = [
        make_live("Phase A", "Alpha.", number=1),
        make_live("Phase B", "Beta.", number=2),
    ]
    diff = compute_diff(manifest, live)
    assert diff.is_clean
    assert not diff.has_blocking_conflict
    assert sorted(diff.matches) == ["Phase A", "Phase B"]


def test_diff_reports_missing(simple_manifest_path: Path) -> None:
    manifest = load_manifest(simple_manifest_path)
    diff = compute_diff(manifest, [make_live("Phase A", "Alpha.", number=1)])
    assert [em.title for em in diff.missing] == ["Phase B"]
    assert not diff.is_clean
    assert not diff.has_blocking_conflict


def test_diff_reports_description_conflict(simple_manifest_path: Path) -> None:
    manifest = load_manifest(simple_manifest_path)
    diff = compute_diff(
        manifest,
        [
            make_live("Phase A", "WRONG.", number=1),
            make_live("Phase B", "Beta.", number=2),
        ],
    )
    assert len(diff.conflicts) == 1
    assert diff.conflicts[0][0].title == "Phase A"
    assert diff.has_blocking_conflict


def test_diff_reports_unexpected_extra(simple_manifest_path: Path) -> None:
    manifest = load_manifest(simple_manifest_path)
    diff = compute_diff(
        manifest,
        [
            make_live("Phase A", "Alpha.", number=1),
            make_live("Phase B", "Beta.", number=2),
            make_live("Phase Z", "Bogus.", number=99),
        ],
    )
    assert [lm.title for lm in diff.extra] == ["Phase Z"]
    assert diff.has_blocking_conflict


def test_diff_reports_non_null_due_on(simple_manifest_path: Path) -> None:
    manifest = load_manifest(simple_manifest_path)
    diff = compute_diff(
        manifest,
        [
            make_live("Phase A", "Alpha.", number=1, due_on="2030-01-01T00:00:00Z"),
            make_live("Phase B", "Beta.", number=2),
        ],
    )
    assert [lm.title for lm in diff.bad_due_on] == ["Phase A"]
    assert diff.has_blocking_conflict


def test_diff_reports_duplicate_live_titles(simple_manifest_path: Path) -> None:
    manifest = load_manifest(simple_manifest_path)
    diff = compute_diff(
        manifest,
        [
            make_live("Phase A", "Alpha.", number=1),
            make_live("Phase A", "Alpha.", number=2),
            make_live("Phase B", "Beta.", number=3),
        ],
    )
    assert diff.duplicates == ["Phase A"]
    assert diff.has_blocking_conflict
