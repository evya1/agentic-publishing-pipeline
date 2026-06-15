"""Prompt/config registry loader and compatibility-check tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_publishing_pipeline.contracts import REQUIRED_CONTRACT_VERSIONS
from agentic_publishing_pipeline.runtime.registry import (
    RegistryError,
    load_registry,
    verify_compatibility,
)

REGISTRY_ROOT = Path(__file__).resolve().parents[2] / "config" / "prompt_registry"


def test_registry_loads_all_eight_agents() -> None:
    reg = load_registry(REGISTRY_ROOT)
    assert len(reg.agents) == 8
    assert "PROMPT-AGENT-RESEARCH-001" in reg.agents
    assert reg.get_agent("PROMPT-AGENT-RESEARCH-001").kind == "agent"


def test_registry_loads_all_eight_tasks() -> None:
    reg = load_registry(REGISTRY_ROOT)
    assert len(reg.tasks) == 8
    write_task = reg.get_task("PROMPT-TASK-WRITE-001")
    assert write_task.config["emits_contract"] == "ChapterDrafts.v1"


def test_registry_fingerprint_is_stable_between_loads() -> None:
    a = load_registry(REGISTRY_ROOT)
    b = load_registry(REGISTRY_ROOT)
    assert a.fingerprint == b.fingerprint


def test_compatibility_passes_for_required_contracts() -> None:
    reg = load_registry(REGISTRY_ROOT)
    verify_compatibility(reg, REQUIRED_CONTRACT_VERSIONS)


def test_compatibility_refuses_missing_contract() -> None:
    reg = load_registry(REGISTRY_ROOT)
    with pytest.raises(RegistryError):
        verify_compatibility(reg, (*REQUIRED_CONTRACT_VERSIONS, "FutureContract.v9"))


def test_registry_rejects_missing_root(tmp_path: Path) -> None:
    with pytest.raises((RegistryError, AssertionError)):
        load_registry(tmp_path / "nope")


def test_registry_rejects_malformed_entry(tmp_path: Path) -> None:
    root = tmp_path / "reg"
    (root / "agents").mkdir(parents=True)
    (root / "registry.v1.yaml").write_text(
        "registry_version: v1\n"
        "generated_at: 2026-01-01\n"
        "entries:\n  agents:\n    - id: BAD\n      path: agents/bad.v1.yaml\n      ledger_id: BAD\n"
        "  tasks: []\n"
        "compatibility:\n  contract_versions: []\n",
        encoding="utf-8",
    )
    (root / "agents" / "bad.v1.yaml").write_text("id: BAD\n", encoding="utf-8")
    with pytest.raises(RegistryError):
        load_registry(root)


def test_get_agent_unknown_raises() -> None:
    reg = load_registry(REGISTRY_ROOT)
    with pytest.raises(RegistryError):
        reg.get_agent("PROMPT-AGENT-NOPE")


def test_registry_root_directory_check(tmp_path: Path) -> None:
    bogus = tmp_path / "file.txt"
    bogus.write_text("x", encoding="utf-8")
    with pytest.raises(AssertionError):
        load_registry(bogus)
