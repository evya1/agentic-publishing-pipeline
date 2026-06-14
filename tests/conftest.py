"""Shared test fixtures and helpers.

Centralises the ``scripts/`` import path setup and the in-memory
``FakeClient`` used by the milestone sync tests so each test module stays
focused on its own scenarios.
"""

from __future__ import annotations

import io
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from _milestones_core import LiveMilestone  # noqa: E402


@dataclass
class FakeClient:
    """Hermetic stand-in for the gh-backed milestone client."""

    live: list[LiveMilestone] = field(default_factory=list)
    list_calls: int = 0
    create_calls: list[tuple[str, str]] = field(default_factory=list)

    def list_milestones(self) -> list[LiveMilestone]:
        self.list_calls += 1
        return list(self.live)

    def create_milestone(self, title: str, description: str) -> LiveMilestone:
        self.create_calls.append((title, description))
        lm = LiveMilestone(
            number=1000 + len(self.create_calls),
            title=title,
            description=description,
            due_on=None,
            state="open",
        )
        self.live.append(lm)
        return lm


def make_live(
    title: str,
    description: str,
    *,
    number: int = 1,
    due_on: str | None = None,
    state: str = "open",
) -> LiveMilestone:
    return LiveMilestone(
        number=number, title=title, description=description, due_on=due_on, state=state
    )


def write_manifest(tmp_path: Path, milestones: list[dict], *, version: int = 1) -> Path:
    path = tmp_path / "milestones.json"
    path.write_text(
        json.dumps({"version": version, "milestones": milestones}), encoding="utf-8"
    )
    return path


SIMPLE_ENTRIES: list[dict] = [
    {"title": "Phase A", "description": "Alpha.", "due_on": None},
    {"title": "Phase B", "description": "Beta.", "due_on": None},
]


@pytest.fixture
def simple_manifest_entries() -> list[dict]:
    return [dict(entry) for entry in SIMPLE_ENTRIES]


@pytest.fixture
def io_buffers() -> tuple[io.StringIO, io.StringIO]:
    return io.StringIO(), io.StringIO()


@pytest.fixture
def simple_manifest_path(tmp_path: Path, simple_manifest_entries: list[dict]) -> Path:
    return write_manifest(tmp_path, simple_manifest_entries)
