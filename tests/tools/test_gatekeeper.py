"""Gatekeeper policy tests: budget, timeout, usage emission, rejection."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from agentic_publishing_pipeline.providers import (
    FixtureModelAdapter,
    FixtureSearchAdapter,
    ModelRequest,
    ModelResponse,
    ProviderConfig,
    ProviderError,
    ProviderFacade,
    SearchHit,
    SearchRequest,
)
from agentic_publishing_pipeline.providers.facade import ModelAdapter
from agentic_publishing_pipeline.runtime import PipelineRunContext, generate_run_id
from agentic_publishing_pipeline.tools import (
    ApiGatekeeper,
    GatekeeperRejection,
    request_identity,
)


def _config(
    *,
    max_requests: int = 64,
    max_cost: float = 2.50,
    timeout: float = 30.0,
) -> ProviderConfig:
    return ProviderConfig(
        llm_provider="fixture",
        llm_model_class="research",
        search_provider="fixture",
        gatekeeper_max_requests=max_requests,
        gatekeeper_max_cost_usd=max_cost,
        gatekeeper_timeout_seconds=timeout,
    )


def _context(tmp_path: Path, *, mode: str = "offline-fixture") -> PipelineRunContext:
    return PipelineRunContext(
        run_id=generate_run_id(),
        results_root=tmp_path / "results",
        mode=mode,
        env={},
    )


def _facade(default_text: str = '{"ok":true}') -> ProviderFacade:
    return ProviderFacade(
        model=FixtureModelAdapter(default_text=default_text),
        search=FixtureSearchAdapter(hits=[SearchHit(title="x", url="u")]),
    )


def _stepping_clock(values: list[float]) -> Iterator[float]:
    iterator = iter(values)
    return iterator


def test_call_model_emits_usage_event(tmp_path: Path) -> None:
    ctx = _context(tmp_path)
    gk = ApiGatekeeper(facade=_facade(), config=_config(), run_context=ctx)
    response = gk.call_model(
        ModelRequest(model_class="research", prompt="hi"),
        identity=request_identity("research_agent", "T1"),
    )
    assert isinstance(response, ModelResponse)
    records = ctx.usage.read_all()
    assert len(records) == 1
    assert records[0]["status"] == "ok"
    assert records[0]["mode"] == "offline-fixture"
    assert records[0]["estimated_cost_usd"] == 0.0


def test_call_model_charges_budget_on_live_mode(tmp_path: Path) -> None:
    ctx = _context(tmp_path, mode="live")
    gk = ApiGatekeeper(facade=_facade(), config=_config(max_requests=2), run_context=ctx)
    gk.call_model(ModelRequest(model_class="r", prompt="a"), identity=request_identity("a", "t"))
    assert gk.budget.requests_used == 1
    assert gk.budget.cost_used_usd > 0.0


def test_call_model_rejects_when_request_budget_exceeded(tmp_path: Path) -> None:
    ctx = _context(tmp_path)
    gk = ApiGatekeeper(facade=_facade(), config=_config(max_requests=1), run_context=ctx)
    gk.call_model(ModelRequest(model_class="r", prompt="a"), identity=request_identity("a", "t"))
    with pytest.raises(GatekeeperRejection) as info:
        gk.call_model(
            ModelRequest(model_class="r", prompt="b"),
            identity=request_identity("a", "t"),
        )
    assert info.value.kind == "max_requests"


def test_call_model_rejects_when_cost_budget_exceeded(tmp_path: Path) -> None:
    ctx = _context(tmp_path, mode="live")
    gk = ApiGatekeeper(facade=_facade(), config=_config(max_cost=0.0), run_context=ctx)
    with pytest.raises(GatekeeperRejection) as info:
        gk.call_model(
            ModelRequest(model_class="r", prompt="hello world"),
            identity=request_identity("a", "t"),
        )
    assert info.value.kind == "max_cost"


def test_call_model_rejects_on_non_retriable_provider_error(tmp_path: Path) -> None:
    class BrokenAdapter(ModelAdapter):
        name = "broken"

        def complete(self, request: ModelRequest) -> ModelResponse:
            raise ProviderError("hard fail", retriable=False)

    ctx = _context(tmp_path)
    facade = ProviderFacade(model=BrokenAdapter(), search=FixtureSearchAdapter())
    gk = ApiGatekeeper(facade=facade, config=_config(), run_context=ctx)
    with pytest.raises(GatekeeperRejection) as info:
        gk.call_model(
            ModelRequest(model_class="r", prompt="x"),
            identity=request_identity("a", "t"),
        )
    assert info.value.kind == "non_retriable"
    records = ctx.usage.read_all()
    assert records[0]["status"] == "error"


def test_call_model_timeout_raises(tmp_path: Path) -> None:
    ctx = _context(tmp_path)
    clock_values = iter([0.0, 60.0])
    gk = ApiGatekeeper(
        facade=_facade(),
        config=_config(timeout=10.0),
        run_context=ctx,
        clock=lambda: next(clock_values),
    )
    with pytest.raises(GatekeeperRejection) as info:
        gk.call_model(
            ModelRequest(model_class="r", prompt="x"),
            identity=request_identity("a", "t"),
        )
    assert info.value.kind == "timeout"


def test_call_search_emits_event(tmp_path: Path) -> None:
    ctx = _context(tmp_path)
    gk = ApiGatekeeper(facade=_facade(), config=_config(), run_context=ctx)
    out = gk.call_search(SearchRequest(query="x"), identity=request_identity("b", "T6"))
    assert out.hits
    records = ctx.usage.read_all()
    assert records[0]["model"] == "fixture-search"


def test_offline_fixture_mode_emits_zero_cost(tmp_path: Path) -> None:
    ctx = _context(tmp_path, mode="offline-fixture")
    gk = ApiGatekeeper(facade=_facade(), config=_config(), run_context=ctx)
    gk.call_model(ModelRequest(model_class="r", prompt="x"), identity=request_identity("a", "t"))
    records = ctx.usage.read_all()
    assert records[0]["estimated_cost_usd"] == 0.0
