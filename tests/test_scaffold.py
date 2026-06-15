"""Smoke tests for the scaffold.

These deliberately only verify that the package and its subpackages import
cleanly. They do **not** exercise any CrewAI / LLM / search functionality —
none exists yet.
"""

from __future__ import annotations

import importlib

import pytest

SUBPACKAGES = [
    "agents",
    "bibliography",
    "tasks",
    "crews",
    "tools",
    "latex",
    "validation",
    "visualization",
]


def test_root_package_imports() -> None:
    pkg = importlib.import_module("agentic_publishing_pipeline")
    assert pkg.__version__ == "0.0.0"


@pytest.mark.parametrize("name", SUBPACKAGES)
def test_subpackage_imports(name: str) -> None:
    importlib.import_module(f"agentic_publishing_pipeline.{name}")
