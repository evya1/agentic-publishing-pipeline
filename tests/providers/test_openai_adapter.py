"""OpenAI live adapter tests."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from agentic_publishing_pipeline.providers import (
    ModelRequest,
    OpenAIChatAdapter,
    ProviderError,
)


class _FakeCompletions:
    def __init__(self) -> None:
        self.last: dict[str, object] | None = None

    def create(self, **kwargs):
        self.last = kwargs
        return SimpleNamespace(
            model=kwargs["model"],
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content='{"ok": true}'),
                    finish_reason="stop",
                )
            ],
            usage=SimpleNamespace(prompt_tokens=11, completion_tokens=7),
        )


class _FakeClient:
    def __init__(self) -> None:
        self.completions = _FakeCompletions()
        self.chat = SimpleNamespace(completions=self.completions)


def test_openai_chat_adapter_maps_request_and_response() -> None:
    client = _FakeClient()
    adapter = OpenAIChatAdapter(
        api_key="test-key",
        model="test-model",
        timeout=10.0,
        client=client,
    )
    response = adapter.complete(
        ModelRequest(
            model_class="writer",
            system_prompt="system",
            prompt="user",
            max_tokens=123,
            temperature=0.4,
        )
    )
    assert response.text == '{"ok": true}'
    assert response.tokens_in == 11
    assert response.tokens_out == 7
    assert response.model_id == "test-model"
    assert client.completions.last == {
        "model": "test-model",
        "messages": [
            {"role": "system", "content": "system"},
            {"role": "user", "content": "user"},
        ],
        "max_tokens": 123,
        "temperature": 0.4,
    }


def test_openai_chat_adapter_rejects_empty_prompt() -> None:
    adapter = OpenAIChatAdapter(
        api_key="test-key",
        model="test-model",
        timeout=10.0,
        client=_FakeClient(),
    )
    with pytest.raises(ProviderError, match="empty prompt"):
        adapter.complete(ModelRequest(model_class="writer", prompt=""))


def test_openai_chat_adapter_rejects_empty_api_key() -> None:
    with pytest.raises(ProviderError, match="OPENAI_API_KEY is required"):
        OpenAIChatAdapter(api_key="", model="test-model", timeout=10.0, client=_FakeClient())


def test_openai_chat_adapter_rejects_whitespace_only_api_key() -> None:
    with pytest.raises(ProviderError, match="OPENAI_API_KEY is required"):
        OpenAIChatAdapter(api_key="   \t\n", model="test-model", timeout=10.0, client=_FakeClient())


def test_openai_chat_adapter_strips_api_key_whitespace_padding() -> None:
    client = _FakeClient()
    adapter = OpenAIChatAdapter(
        api_key="  sk-padded  ",
        model="test-model",
        timeout=10.0,
        client=client,
    )
    assert adapter._model == "test-model"
