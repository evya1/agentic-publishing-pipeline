"""CrewAI Agent construction from the versioned prompt registry."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from crewai import Agent

from ..runtime.registry import PromptConfig, Registry
from ..services.crewai_llm import ControlledCrewLlm

AgentLlmFactory = Callable[[str, str, str], ControlledCrewLlm]

AGENT_PROMPT_IDS: dict[str, str] = {
    "researcher": "PROMPT-AGENT-RESEARCH-001",
    "outline": "PROMPT-AGENT-OUTLINE-001",
    "writer": "PROMPT-AGENT-WRITER-001",
    "technical_asset": "PROMPT-AGENT-ASSET-001",
    "bidi": "PROMPT-AGENT-BIDI-001",
    "bibliography": "PROMPT-AGENT-BIBLIOGRAPHY-001",
    "reviewer": "PROMPT-AGENT-REVIEWER-001",
    "latex": "PROMPT-AGENT-LATEX-001",
}

AGENT_TASK_IDS: dict[str, str] = {
    "researcher": "research",
    "outline": "outline",
    "writer": "write",
    "technical_asset": "asset",
    "bidi": "bidi",
    "bibliography": "bibliography",
    "reviewer": "review",
    "latex": "latex-plan",
}


class AgentFactoryError(ValueError):
    """Raised when the registry cannot construct the required agent set."""


def build_agents(
    *,
    registry: Registry,
    llm_factory: AgentLlmFactory,
    tool_map: Mapping[str, Sequence[Any]] | None = None,
    verbose: bool = False,
) -> dict[str, Agent]:
    """Build the eight PRD agents without performing model calls."""
    tools = tool_map or {}
    built: dict[str, Agent] = {}
    for agent_id, prompt_id in AGENT_PROMPT_IDS.items():
        config = _lookup_agent_config(registry, prompt_id)
        task_id = AGENT_TASK_IDS[agent_id]
        model_class = str(config.config.get("model_class", agent_id))
        llm = llm_factory(agent_id, task_id, model_class)
        built[agent_id] = Agent(
            role=_required(config, "role", agent_id),
            goal=_required(config, "goal", agent_id),
            backstory=_backstory(config),
            llm=llm,
            tools=list(tools.get(agent_id, ())),
            verbose=verbose,
            allow_delegation=False,
            max_iter=int(config.config.get("max_iter", 3)),
            max_tokens=_optional_int(config.config.get("max_tokens")),
        )
    return built


def _lookup_agent_config(registry: Registry, prompt_id: str) -> PromptConfig:
    try:
        return registry.get_agent(prompt_id)
    except Exception as exc:
        raise AgentFactoryError(f"registry has no prompt entry for {prompt_id!r}") from exc


def _required(config: PromptConfig, field: str, agent_id: str) -> str:
    value = str(config.prompt.get(field, "")).strip()
    if not value:
        raise AgentFactoryError(f"{agent_id} prompt missing {field}")
    return value


def _backstory(config: PromptConfig) -> str:
    parts = [
        str(config.prompt.get(name, "")).strip()
        for name in ("backstory", "instructions", "role")
    ]
    return "\n\n".join(part for part in parts if part)


def _optional_int(value: object) -> int | None:
    return int(value) if value is not None else None
