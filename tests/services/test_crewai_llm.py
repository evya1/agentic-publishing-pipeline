from __future__ import annotations

import pytest
from pydantic import BaseModel

from agentic_publishing_pipeline.providers import (
    DisabledSearchAdapter,
    FixtureModelAdapter,
    FixtureSearchAdapter,
    ModelRequest,
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


class SequenceModelAdapter:
    name = "sequence-model"

    def __init__(self, texts: list[str]) -> None:
        self._texts = list(texts)

    def complete(self, request: ModelRequest) -> ModelResponse:
        text = self._texts.pop(0)
        return ModelResponse(text, 1, 1, 1.0, "fixture-haiku-4-5")


def _llm(
    tmp_path,
    response: ModelResponse,
    *,
    max_attempts: int | None = None,
    max_repairs: int = 1,
) -> tuple[ControlledCrewLlm, PipelineRunContext]:
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
            max_attempts=max_attempts,
            max_repairs=max_repairs,
        )
    return llm, ctx


def _sequence_llm(
    tmp_path,
    texts: list[str],
    *,
    max_attempts: int | None = None,
    max_repairs: int = 1,
) -> tuple[ControlledCrewLlm, PipelineRunContext]:
    ctx = PipelineRunContext.create(
        results_root=tmp_path.resolve(),
        mode="offline-fixture",
        topic="test",
    )
    facade = ProviderFacade(model=SequenceModelAdapter(texts), search=DisabledSearchAdapter())
    config = ProviderConfig("fixture", "writer", "fixture", 10, 1.0, 30.0)
    gatekeeper = ApiGatekeeper(facade=facade, config=config, run_context=ctx)
    llm = ControlledCrewLlm(
        gatekeeper=gatekeeper,
        agent_id="writer",
        task_id="write",
        model_class="writer",
        run_id=ctx.run_id,
        prompt_version="v1",
        max_attempts=max_attempts,
        max_repairs=max_repairs,
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


def test_call_without_response_model_returns_text(tmp_path) -> None:
    response = ModelResponse("plain text", 1, 1, 1.0, "fixture-haiku-4-5")
    llm, _ = _llm(tmp_path, response)
    assert llm.call("prompt") == "plain text"
    assert not llm.supports_function_calling()


def test_retry_configuration_is_bounded(tmp_path) -> None:
    response = ModelResponse("{}", 1, 1, 1.0, "fixture-haiku-4-5")
    with pytest.raises(ValueError, match="max_repairs"):
        _llm(tmp_path, response, max_repairs=-1)
    with pytest.raises(ValueError, match="max_attempts"):
        _llm(tmp_path, response, max_attempts=0)


def test_empty_model_response_fails_clearly(tmp_path) -> None:
    response = ModelResponse("   ", 1, 1, 1.0, "fixture-haiku-4-5")
    llm, _ = _llm(tmp_path, response)
    with pytest.raises(CrewStructuredOutputError, match="empty model response"):
        llm.call("prompt")


def test_no_unbounded_repair_and_attempts_logged(tmp_path) -> None:
    response = ModelResponse('{"wrong": true}', 1, 1, 1.0, "fixture-haiku-4-5")
    llm, ctx = _llm(tmp_path, response)
    with pytest.raises(CrewStructuredOutputError):
        llm.call("prompt", response_model=Item)
    assert [row["attempt"] for row in ctx.usage.read_all()] == [1, 2]
    assert [row["purpose"] for row in ctx.usage.read_all()] == [
        "primary",
        "structured-repair",
    ]


def test_zero_repairs_exhausts_after_primary(tmp_path) -> None:
    llm, ctx = _sequence_llm(tmp_path, ['{"wrong": true}'], max_repairs=0)
    with pytest.raises(CrewStructuredOutputError, match="max_repairs=0"):
        llm.call("prompt", response_model=Item)
    assert [row["attempt"] for row in ctx.usage.read_all()] == [1]


def test_one_repair_can_recover(tmp_path) -> None:
    llm, ctx = _sequence_llm(tmp_path, ['{"wrong": true}', '{"value": 7}'])
    result = llm.call("prompt", response_model=Item)
    assert result.value == 7
    assert [row["attempt"] for row in ctx.usage.read_all()] == [1, 2]


def test_multiple_repairs_can_recover(tmp_path) -> None:
    llm, ctx = _sequence_llm(
        tmp_path,
        ['{"wrong": true}', '{"still_wrong": true}', '{"value": 8}'],
        max_attempts=3,
        max_repairs=2,
    )
    result = llm.call("prompt", response_model=Item)
    assert result.value == 8
    assert [row["attempt"] for row in ctx.usage.read_all()] == [1, 2, 3]


def test_exhausted_multiple_repairs_fails_bounded(tmp_path) -> None:
    llm, ctx = _sequence_llm(
        tmp_path,
        ['{"wrong": true}', '{"still_wrong": true}', '{"nope": true}'],
        max_attempts=3,
        max_repairs=2,
    )
    with pytest.raises(CrewStructuredOutputError, match="max_attempts=3"):
        llm.call("prompt", response_model=Item)
    assert [row["attempt"] for row in ctx.usage.read_all()] == [1, 2, 3]
