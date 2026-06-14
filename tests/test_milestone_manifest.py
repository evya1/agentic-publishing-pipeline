"""Manifest parsing and validation tests for ``_milestones_core.load_manifest``.

Covers JSON shape, version, duplicate titles, due_on rejection, missing
fields, non-object entries, and the project-tracked manifest itself.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from _milestones_core import ExpectedMilestone, ManifestError, load_manifest

from .conftest import write_manifest


def test_valid_manifest_parses(simple_manifest_path: Path) -> None:
    manifest = load_manifest(simple_manifest_path)
    assert manifest.version == 1
    assert manifest.milestones == (
        ExpectedMilestone("Phase A", "Alpha."),
        ExpectedMilestone("Phase B", "Beta."),
    )


def test_repository_manifest_loads_with_thirteen_entries() -> None:
    repo_manifest = (
        Path(__file__).resolve().parent.parent / "config" / "milestones.json"
    )
    manifest = load_manifest(repo_manifest)
    titles = [m.title for m in manifest.milestones]
    assert len(titles) == 13
    assert titles[0] == "Phase 2 — Project management setup"
    assert titles[-1] == "Phase 14 — Final submission packaging"
    assert len(set(titles)) == 13
    assert all("docs/PLAN.md" in m.description for m in manifest.milestones)


def test_duplicate_manifest_titles_rejected(
    tmp_path: Path, simple_manifest_entries: list[dict]
) -> None:
    entries = simple_manifest_entries + [
        {"title": "Phase A", "description": "Alpha duplicate.", "due_on": None}
    ]
    path = write_manifest(tmp_path, entries)
    with pytest.raises(ManifestError, match="Duplicate milestone title"):
        load_manifest(path)


def test_unsupported_manifest_version_rejected(
    tmp_path: Path, simple_manifest_entries: list[dict]
) -> None:
    path = write_manifest(tmp_path, simple_manifest_entries, version=999)
    with pytest.raises(ManifestError, match="Unsupported manifest version"):
        load_manifest(path)


def test_non_null_due_on_in_manifest_rejected(tmp_path: Path) -> None:
    entries = [{"title": "X", "description": "x", "due_on": "2030-01-01T00:00:00Z"}]
    path = write_manifest(tmp_path, entries)
    with pytest.raises(ManifestError, match="due_on must be null"):
        load_manifest(path)


def test_malformed_manifest_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ManifestError, match="not valid JSON"):
        load_manifest(path)


def test_empty_milestone_list_rejected(tmp_path: Path) -> None:
    path = write_manifest(tmp_path, [])
    with pytest.raises(ManifestError, match="non-empty list"):
        load_manifest(path)


def test_missing_required_field_rejected(tmp_path: Path) -> None:
    path = write_manifest(tmp_path, [{"title": "Only title"}])
    with pytest.raises(ManifestError, match="description must be a string"):
        load_manifest(path)


def test_non_object_entry_rejected(tmp_path: Path) -> None:
    path = write_manifest(tmp_path, ["not an object"])
    with pytest.raises(ManifestError, match="must be an object"):
        load_manifest(path)


def test_non_dict_root_rejected(tmp_path: Path) -> None:
    path = tmp_path / "list_root.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(ManifestError, match="root must be a JSON object"):
        load_manifest(path)


def test_empty_title_rejected(tmp_path: Path) -> None:
    path = write_manifest(
        tmp_path, [{"title": "", "description": "x", "due_on": None}]
    )
    with pytest.raises(ManifestError, match="non-empty string"):
        load_manifest(path)
