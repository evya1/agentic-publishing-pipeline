"""Helper factories and writers used by the live manuscript runner."""

from __future__ import annotations

from collections.abc import Callable

from ..agents.factory import AGENT_PROMPT_IDS
from ..runtime import PipelineRunContext, Registry
from ..services.crewai_llm import ControlledCrewLlm
from ..tasks.completeness import ManuscriptPreflightReport
from ..tasks.constants import TASK_PROMPT_IDS
from ..tools.gatekeeper import ApiGatekeeper


def llm_factory(
    *,
    registry: Registry,
    gatekeeper: ApiGatekeeper,
    run_id: str,
    llm_builder: Callable[..., ControlledCrewLlm],
) -> Callable[[str, str, str], ControlledCrewLlm]:
    def build(agent_id: str, task_id: str, model_class: str) -> ControlledCrewLlm:
        prompt_id = AGENT_PROMPT_IDS[agent_id]
        prompt_version = registry.get_agent(prompt_id).version
        task_config = registry.get_task(TASK_PROMPT_IDS.get(task_id, TASK_PROMPT_IDS["review"]))
        max_repairs = int(task_config.config.get("repair_attempts_allowed", 1))
        return llm_builder(
            gatekeeper=gatekeeper,
            agent_id=agent_id,
            task_id=task_id,
            model_class=model_class,
            run_id=run_id,
            prompt_version=prompt_version,
            max_attempts=max_repairs + 1,
            max_repairs=max_repairs,
        )

    return build


def write_raw_result(context: PipelineRunContext, result: object) -> None:
    text = repr(result)
    context.write_artifact_json("raw_outputs/crew_result.json", {"repr": text})
    context.write_artifact_json("raw/crew_result.json", {"repr": text})


def write_preflight_report(
    context: PipelineRunContext,
    report: ManuscriptPreflightReport,
) -> None:
    context.write_artifact_json(
        "preflight_report.json",
        {
            "passed": report.passed,
            "word_counts": report.word_counts,
            "total_words": report.total_words,
            "cited_keys": list(report.cited_keys),
            "missing_source_keys": list(report.missing_source_keys),
            "errors": list(report.errors),
            "warnings": list(report.warnings),
        },
    )
