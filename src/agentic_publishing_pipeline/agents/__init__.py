"""CrewAI agent definitions.

Factory helpers build the configured PRD agents from the prompt registry.
"""

from __future__ import annotations

from .factory import AGENT_PROMPT_IDS, AGENT_TASK_IDS, AgentFactoryError, build_agents

__all__ = [
    "AGENT_PROMPT_IDS",
    "AGENT_TASK_IDS",
    "AgentFactoryError",
    "build_agents",
]
