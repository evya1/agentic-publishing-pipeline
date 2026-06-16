"""Run the real manuscript Crew and stop at the human-review boundary."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from ..agents.factory import AGENT_PROMPT_IDS, build_agents
from ..runtime import PipelineRunContext, Registry
from ..runtime.stage_state import PipelineStage, StageState, transition, write_stage
from ..services.crewai_llm import ControlledCrewLlm
from ..tasks.completeness import ManuscriptPreflightReport, run_manuscript_preflight
from ..tasks.factory import REQUIRED_CHAPTER_IDS, build_manuscript_tasks
from ..tools.fileio import FileIO
from ..tools.gatekeeper import ApiGatekeeper
from .manuscript_crew import build_manuscript_crew
from .persistence import persist_manuscript_outputs
from .result_parser import ManuscriptOutputs, parse_manuscript_outputs


class ManuscriptPreflightFailed(RuntimeError):
    """Raised when typed task outputs fail deterministic completeness."""


def run_live_manuscript(
    *,
    context: PipelineRunContext,
    registry: Registry,
    gatekeeper: ApiGatekeeper,
    topic: str,
    source_context_text: str,
    citation_keys: Sequence[str],
    target_pages: int,
    target_words: int,
    min_words_per_chapter: int,
    llm_builder: Callable[..., ControlledCrewLlm] = ControlledCrewLlm,
) -> tuple[ManuscriptOutputs, ManuscriptPreflightReport]:
    """Kick off the real Crew, persist candidates, and await human review."""
    io = FileIO(context)
    state = StageState(PipelineStage.GENERATING, context.run_id)
    write_stage(io, state)
    agents = build_agents(
        registry=registry,
        llm_factory=_llm_factory(
            registry=registry,
            gatekeeper=gatekeeper,
            run_id=context.run_id,
            llm_builder=llm_builder,
        ),
    )
    tasks = build_manuscript_tasks(
        agents=agents,
        registry=registry,
        topic=topic,
        source_context_text=source_context_text,
        citation_keys=citation_keys,
        target_pages=target_pages,
        target_words=target_words,
    )
    result = build_manuscript_crew(agents=agents, tasks=tasks).kickoff(
        inputs={"topic": topic, "run_id": context.run_id}
    )
    outputs = parse_manuscript_outputs(result)
    persist_manuscript_outputs(context=context, outputs=outputs)
    report = run_manuscript_preflight(
        outputs.chapters,
        bidi=outputs.bidi,
        required_chapter_ids=REQUIRED_CHAPTER_IDS,
        manifest_keys=tuple(citation_keys),
        min_words_per_chapter=min_words_per_chapter,
        min_total_words=target_words,
    )
    if not report.passed:
        transition(io, state, PipelineStage.PREFLIGHT_FAILED, detail="; ".join(report.errors))
        raise ManuscriptPreflightFailed("; ".join(report.errors))
    transition(io, state, PipelineStage.AWAITING_HUMAN_REVIEW)
    return outputs, report


def _llm_factory(
    *,
    registry: Registry,
    gatekeeper: ApiGatekeeper,
    run_id: str,
    llm_builder: Callable[..., ControlledCrewLlm],
):
    def build(agent_id: str, task_id: str, model_class: str) -> ControlledCrewLlm:
        prompt_id = AGENT_PROMPT_IDS[agent_id]
        prompt_version = registry.get_agent(prompt_id).version
        return llm_builder(
            gatekeeper=gatekeeper,
            agent_id=agent_id,
            task_id=task_id,
            model_class=model_class,
            run_id=run_id,
            prompt_version=prompt_version,
        )

    return build
