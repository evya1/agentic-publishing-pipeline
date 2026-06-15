"""Provider facade and offline-fixture adapter tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_publishing_pipeline.providers import (
    FixtureModelAdapter,
    FixtureSearchAdapter,
    ModelRequest,
    ModelResponse,
    ProviderError,
    ProviderFacade,
    SearchHit,
    SearchRequest,
    load_provider_config,
)


def test_load_provider_config_defaults() -> None:
    cfg = load_provider_config({})
    assert cfg.llm_provider == "fixture"
    assert cfg.is_offline_fixture is True
    assert cfg.gatekeeper_max_requests == 64
    assert cfg.gatekeeper_max_cost_usd == pytest.approx(2.50)


def test_load_provider_config_overrides() -> None:
    cfg = load_provider_config(
        {
            "APP_LLM_PROVIDER": "anthropic",
            "APP_LLM_MODEL_CLASS": "writer",
            "APP_GATEKEEPER_MAX_REQUESTS": "128",
            "APP_GATEKEEPER_MAX_COST_USD": "5.0",
        }
    )
    assert cfg.llm_provider == "anthropic"
    assert cfg.is_offline_fixture is False
    assert cfg.gatekeeper_max_requests == 128


def test_load_provider_config_rejects_bad_int() -> None:
    with pytest.raises(ValueError):
        load_provider_config({"APP_GATEKEEPER_MAX_REQUESTS": "not-a-number"})


def test_fixture_model_adapter_uses_in_memory_fixture() -> None:
    response = ModelResponse(
        text='{"ok": true}', tokens_in=12, tokens_out=34,
        latency_ms=2.0, model_id="fixture-test",
    )
    adapter = FixtureModelAdapter(fixtures={"research": response})
    request = ModelRequest(model_class="research", prompt="hi")
    out = adapter.complete(request)
    assert out is response


def test_fixture_model_adapter_falls_back_to_default_text() -> None:
    adapter = FixtureModelAdapter(default_text='{"x":1}')
    out = adapter.complete(ModelRequest(model_class="research", prompt="x"))
    assert out.text == '{"x":1}'
    assert out.tokens_in > 0
    assert out.latency_ms >= 0.0


def test_fixture_model_adapter_rejects_empty_prompt() -> None:
    adapter = FixtureModelAdapter()
    with pytest.raises(ProviderError):
        adapter.complete(ModelRequest(model_class="research", prompt=""))


def test_fixture_model_adapter_reads_disk_fixtures(tmp_path: Path) -> None:
    payload = tmp_path / "writer.json"
    payload.write_text('{"text": "out", "tokens_in": 3, "tokens_out": 4}', encoding="utf-8")
    adapter = FixtureModelAdapter(fixture_root=tmp_path)
    request = ModelRequest(
        model_class="ignored", prompt="hi", metadata={"fixture_key": "writer"}
    )
    out = adapter.complete(request)
    assert out.text == "out"
    assert out.tokens_in == 3


def test_fixture_search_adapter_filters_by_query() -> None:
    adapter = FixtureSearchAdapter(
        hits=[
            SearchHit(title="Reasoning Survey", url="u1", arxiv_id="2504.09037"),
            SearchHit(title="Other", url="u2", arxiv_id="0000"),
        ]
    )
    out = adapter.search(SearchRequest(query="reasoning"))
    assert len(out.hits) == 1
    assert out.hits[0].arxiv_id == "2504.09037"


def test_fixture_search_adapter_matches_arxiv_id() -> None:
    adapter = FixtureSearchAdapter(
        hits=[SearchHit(title="Survey", url="u1", arxiv_id="2504.09037")]
    )
    out = adapter.search(SearchRequest(query="2504.09037", max_results=2))
    assert len(out.hits) == 1


def test_fixture_search_adapter_rejects_empty_query() -> None:
    adapter = FixtureSearchAdapter()
    with pytest.raises(ProviderError):
        adapter.search(SearchRequest(query=""))


def test_provider_facade_routes_to_adapters() -> None:
    facade = ProviderFacade(
        model=FixtureModelAdapter(default_text='{"y":2}'),
        search=FixtureSearchAdapter(hits=[SearchHit(title="x", url="u")]),
    )
    assert facade.model_name == "fixture-model"
    assert facade.search_name == "fixture-search"
    mr = facade.complete(ModelRequest(model_class="research", prompt="hi"))
    assert mr.text == '{"y":2}'
    sr = facade.search(SearchRequest(query="x"))
    assert len(sr.hits) == 1
