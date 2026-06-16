from __future__ import annotations

import pytest
from pydantic import BaseModel

from agentic_publishing_pipeline.providers import (
    FixtureModelAdapter,
    FixtureSearchAdapter,
    ModelResponse,
    ProviderConfig,
    ProviderFacade,
)
from agentic_publishing_pipeline.runtime import PipelineRunContext
from agentic_publishing_pipeline.services import (
    ControlledCrewLlm,
    CrewStructuredOutputError,
    extract_json_value,
    split_messages,
)
from agentic_publishing_pipeline.tools import ApiGatekeeper


class Item(BaseModel):
    value: int


def _llm(tmp_path, response: ModelResponse) -> tuple[ControlledCrewLlm, PipelineRunContext]:
    ctx = PipelineRunContext.create(
        results_root=tmp_path.resolve(),
        mode="offline-fixture",
        topic="test",
    )
    facade = ProviderFacade(
        model=FixtureModelAdapter(fixtures={"writer": response}),
        search=FixtureSearchAdapter(),
    )
    config = ProviderConfig("fixture", "writer", "fixture", 4, 1.0, 30.0)
    gatekeeper = ApiGatekeeper(facade=facade, config=config, run_context=ctx)
    llm = ControlledCrewLlm(
        gatekeeper=gatekeeper,
        agent_id="writer",
        task_id="write",
        model_class="writer",
        run_id=ctx.run_id,
        prompt_version="v1",
    )
    return llm, ctx


def test_split_messages() -> None:
    system, user = split_messages(
        [{"role": "system", "content": "S"}, {"role": "user", "content": "U"}]
    )
    assert system == "S"
    assert user == "U"


def test_extract_json_value_from_fence() -> None:
    assert extract_json_value('```json\n{"value": 4}\n```') == '{"value": 4}'


def test_call_parses_pydantic(tmp_path) -> None:
    response = ModelResponse('{"value": 42}', 1, 1, 1.0, "fixture-haiku-4-5")
    llm, _ = _llm(tmp_path, response)
    result = llm.call("prompt", response_model=Item)
    assert isinstance(result, Item)
    assert result.value == 42


def test_no_unbounded_repair_and_attempts_logged(tmp_path) -> None:
    response = ModelResponse('{"wrong": true}', 1, 1, 1.0, "fixture-haiku-4-5")
    llm, ctx = _llm(tmp_path, response)
    with pytest.raises(CrewStructuredOutputError):
        llm.call("prompt", response_model=Item)
    assert [row["attempt"] for row in ctx.usage.read_all()] == [1, 2]
