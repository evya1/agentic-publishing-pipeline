"""Sequential CrewAI crew for pre-review manuscript generation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from crewai import Agent, Crew, Process, Task


class ManuscriptCrewError(ValueError):
    """Raised when the manuscript crew graph is incomplete."""


def build_manuscript_crew(
    *,
    agents: Mapping[str, Agent],
    tasks: Sequence[Task],
    verbose: bool = False,
) -> Crew:
    """Return a real sequential Crew that stops before LaTeX assembly."""
    if not tasks:
        raise ManuscriptCrewError("manuscript crew requires at least one task")
    used = _unique_task_agents(tasks)
    if agents.get("latex") in used:
        raise ManuscriptCrewError(
            "LaTeX agent must not execute before the human-review gate"
        )
    return Crew(
        agents=used,
        tasks=list(tasks),
        process=Process.sequential,
        verbose=verbose,
    )


def _unique_task_agents(tasks: Sequence[Task]) -> list[Agent]:
    used: list[Agent] = []
    identities: set[int] = set()
    for task in tasks:
        if task.agent is None:
            raise ManuscriptCrewError("every task must have an owning agent")
        identity = id(task.agent)
        if identity not in identities:
            used.append(task.agent)
            identities.add(identity)
    return used
