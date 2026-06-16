from __future__ import annotations

import pytest

from agentic_publishing_pipeline.crews import LiveAdapterUnavailable, run_cli
from agentic_publishing_pipeline.crews.live_cli import _live_facade
from agentic_publishing_pipeline.providers import ProviderConfig, ProviderError, SearchRequest


def test_live_mode_unsupported_provider_does_not_fall_back_to_fixture() -> None:
    with pytest.raises(LiveAdapterUnavailable):
        run_cli(
            [
                "--mode",
                "live",
                "--i-understand-this-makes-paid-calls",
            ],
            env={"OPENAI_API_KEY": "present", "APP_LLM_PROVIDER": "anthropic"},
        )


def test_live_facade_uses_disabled_search_adapter_not_fixture() -> None:
    config = ProviderConfig("openai", "gpt-4.1-mini", "fixture", 4, 1.0, 30.0)
    facade = _live_facade(config=config, env={"OPENAI_API_KEY": "present"})
    assert facade.search_name == "disabled-search"
    with pytest.raises(ProviderError, match="locked source context"):
        facade.search(SearchRequest(query="reasoning"))
