"""Typed CrewAI manuscript-task construction."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from crewai import Agent, Task

from ..contracts import (
    AssetSpecs,
    BibliographyBundle,
    BiDiSection,
    ChapterDrafts,
    Outline,
    ResearchNotes,
    ReviewerSignal,
)
from ..runtime.registry import PromptConfig, Registry
from .constants import REQUIRED_CHAPTER_IDS, TASK_PROMPT_IDS


class TaskFactoryError(ValueError):
    """Raised when the registry cannot construct the manuscript tasks."""


def build_manuscript_tasks(
    *,
    agents: Mapping[str, Agent],
    registry: Registry,
    topic: str,
    source_context_text: str,
    citation_keys: Sequence[str],
    target_pages: int,
    target_words: int,
) -> list[Task]:
    """Build deterministic-order manuscript tasks ending before human review."""
    allowed_keys = ", ".join(citation_keys)
    required_chapters = ", ".join(REQUIRED_CHAPTER_IDS)
    research = _task(
        registry,
        "research",
        agent=agents["researcher"],
        output=ResearchNotes,
        constraints=[
            f"Topic: {topic}",
            "Use only the locked source context below.",
            source_context_text,
        ],
    )
    outline = _task(
        registry,
        "outline",
        agent=agents["outline"],
        context=[research],
        output=Outline,
        constraints=[
            f"Required chapter IDs in order: {required_chapters}.",
            "The Memory chapter is the BiDi host.",
            f"Target total pages: {target_pages}.",
        ],
    )
    writer = _task(
        registry,
        "write",
        agent=agents["writer"],
        context=[research, outline],
        output=ChapterDrafts,
        constraints=[
            f"Return every required chapter: {required_chapters}.",
            f"Target at least {target_words} total words.",
            f"Use only these citation keys: {allowed_keys}.",
            "Every locked key must be cited at least once.",
            "Do not emit raw LaTeX or filesystem paths.",
        ],
    )
    assets = _task(
        registry,
        "asset",
        agent=agents["technical_asset"],
        context=[outline, writer],
        output=AssetSpecs,
        constraints=["Return semantic asset specs only; never trusted raw TeX."],
    )
    bidi = _task(
        registry,
        "bidi",
        agent=agents["bidi"],
        context=[outline, writer],
        output=BiDiSection,
        constraints=["Target chapter_id must be memory; do not output raw TeX."],
    )
    bibliography = _task(
        registry,
        "bibliography",
        agent=agents["bibliography"],
        context=[research, writer, bidi],
        output=BibliographyBundle,
        constraints=[f"Allowed citation keys: {allowed_keys}."],
    )
    reviewer = _task(
        registry,
        "review",
        agent=agents["reviewer"],
        context=[research, outline, writer, assets, bidi, bibliography],
        output=ReviewerSignal,
        constraints=["This verdict is advisory only and is not human approval."],
    )
    return [research, outline, writer, assets, bidi, bibliography, reviewer]


def _task(
    registry: Registry,
    task_id: str,
    *,
    agent: Agent,
    output: type,
    constraints: Sequence[str],
    context: list[Task] | None = None,
) -> Task:
    config = _lookup_task_config(registry, task_id)
    description = _description(config, constraints)
    expected = str(config.prompt.get("expected_output", "")).strip()
    return Task(
        description=description,
        expected_output=expected or f"Valid {output.__name__}.v1 JSON only",
        agent=agent,
        context=context,
        output_pydantic=output,
    )


def _lookup_task_config(registry: Registry, task_id: str) -> PromptConfig:
    try:
        return registry.get_task(TASK_PROMPT_IDS[task_id])
    except KeyError as exc:
        raise TaskFactoryError(f"unknown task id: {task_id!r}") from exc
    except Exception as exc:
        raise TaskFactoryError(f"registry has no prompt entry for {task_id!r}") from exc


def _description(config: PromptConfig, constraints: Sequence[str]) -> str:
    base = str(config.prompt.get("description", "")).strip()
    if not base:
        raise TaskFactoryError(f"{config.id} prompt missing description")
    joined = "\n".join(f"- {value}" for value in constraints if value)
    return f"{base}\n\nRun constraints:\n{joined}"
