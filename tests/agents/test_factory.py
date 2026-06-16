from __future__ import annotations

from pathlib import Path

import pytest

from agentic_publishing_pipeline.agents.factory import AgentFactoryError, build_agents
from agentic_publishing_pipeline.runtime import load_registry

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_build_agents_constructs_all_eight_without_model_call() -> None:
    registry = load_registry(REPO_ROOT / "config" / "prompt_registry")
    calls: list[tuple[str, str, str]] = []

    def llm_factory(agent_id: str, task_id: str, model_class: str) -> str:
        calls.append((agent_id, task_id, model_class))
        return "fixture-llm"

    agents = build_agents(registry=registry, llm_factory=llm_factory)
    assert sorted(agents) == [
        "bibliography",
        "bidi",
        "latex",
        "outline",
        "researcher",
        "reviewer",
        "technical_asset",
        "writer",
    ]
    assert "validator" not in agents
    assert all(not agent.allow_delegation for agent in agents.values())
    assert len(calls) == 8


def test_missing_registry_entry_fails_clearly() -> None:
    registry = load_registry(REPO_ROOT / "config" / "prompt_registry")
    broken = registry.__class__(
        registry_version=registry.registry_version,
        generated_at=registry.generated_at,
        agents={},
        tasks=registry.tasks,
        contract_versions=registry.contract_versions,
        fingerprint=registry.fingerprint,
    )
    with pytest.raises(AgentFactoryError):
        build_agents(registry=broken, llm_factory=lambda a, t, m: "fixture")
