"""Run the real manuscript Crew and stop at the human-review boundary."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

from ..agents.factory import build_agents
from ..runtime import PipelineRunContext, Registry
from ..runtime.stage_state import PipelineStage, StageState, transition, write_stage
from ..services.crewai_llm import ControlledCrewLlm
from ..services.source_context import SourceContext
from ..tasks.completeness import ManuscriptPreflightReport, run_manuscript_preflight
from ..tasks.factory import REQUIRED_CHAPTER_IDS, build_manuscript_tasks
from ..tools.fileio import FileIO
from ..tools.gatekeeper import ApiGatekeeper
from ._live_helpers import llm_factory as _llm_factory
from ._live_helpers import write_preflight_report as _write_preflight_report
from ._live_helpers import write_raw_result as _write_raw_result
from .composition import compose_manuscript_outputs
from .manuscript_crew import build_manuscript_crew
from .persistence import persist_manuscript_outputs
from .result_parser import ManuscriptOutputs, parse_manuscript_outputs
from .review_packet import finalize_review_artifacts

__all__ = [
    "ManuscriptPreflightFailed",
    "_llm_factory",
    "run_live_manuscript",
]


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
    review_template_path: Path,
    previous_canonical_root: Path,
    min_hebrew_tokens: int = 40,
    min_embedded_english_terms: int = 1,
    source_context: SourceContext | None = None,
    llm_builder: Callable[..., ControlledCrewLlm] = ControlledCrewLlm,
) -> tuple[ManuscriptOutputs, ManuscriptPreflightReport, str]:
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
    try:
        result = build_manuscript_crew(agents=agents, tasks=tasks).kickoff(
            inputs={"topic": topic, "run_id": context.run_id}
        )
    except Exception as exc:
        transition(io, state, PipelineStage.GENERATION_FAILED, detail=str(exc))
        raise
    _write_raw_result(context, result)
    try:
        outputs = compose_manuscript_outputs(parse_manuscript_outputs(result))
    except Exception as exc:
        transition(io, state, PipelineStage.PARSING_FAILED, detail=str(exc))
        raise
    state = transition(io, state, PipelineStage.GENERATED)
    try:
        persist_manuscript_outputs(context=context, outputs=outputs)
    except Exception as exc:
        transition(io, state, PipelineStage.PERSISTENCE_FAILED, detail=str(exc))
        raise
    state = transition(io, state, PipelineStage.PREFLIGHT)
    try:
        report = run_manuscript_preflight(
            outputs.chapters,
            bidi=outputs.bidi,
            required_chapter_ids=REQUIRED_CHAPTER_IDS,
            manifest_keys=tuple(citation_keys),
            min_words_per_chapter=min_words_per_chapter,
            min_total_words=target_words,
            min_hebrew_tokens=min_hebrew_tokens,
            min_embedded_english_terms=min_embedded_english_terms,
            assets=outputs.assets,
            bibliography=outputs.bibliography,
            source_context=source_context,
        )
    except Exception as exc:
        transition(io, state, PipelineStage.PREFLIGHT_FAILED, detail=str(exc))
        raise
    if not report.passed:
        _write_preflight_report(context, report)
        transition(io, state, PipelineStage.PREFLIGHT_FAILED, detail="; ".join(report.errors))
        raise ManuscriptPreflightFailed("; ".join(report.errors))
    _write_preflight_report(context, report)
    state = transition(io, state, PipelineStage.REVIEW_FINALIZATION)
    try:
        aggregate = finalize_review_artifacts(
            context=context,
            io=io,
            report=report,
            review_template_path=review_template_path,
            previous_canonical_root=previous_canonical_root,
        )
    except Exception as exc:
        transition(io, state, PipelineStage.REVIEW_FINALIZATION_FAILED, detail=str(exc))
        raise
    transition(io, state, PipelineStage.AWAITING_HUMAN_REVIEW, detail=aggregate)
    return outputs, report, aggregate
