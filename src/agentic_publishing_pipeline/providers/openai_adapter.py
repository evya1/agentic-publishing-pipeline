"""OpenAI model adapter for live manuscript-generation runs."""

from __future__ import annotations

import time
from typing import Any

from openai import OpenAI, OpenAIError

from .facade import ModelAdapter, ModelRequest, ModelResponse, ProviderError


class OpenAIChatAdapter(ModelAdapter):
    """Translate repository model requests to OpenAI chat completions."""

    name = "openai-chat"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout: float,
        client: Any | None = None,
    ) -> None:
        if not api_key:
            raise ProviderError("OPENAI_API_KEY is required", retriable=False)
        if not model:
            raise ProviderError("APP_OPENAI_MODEL is required", retriable=False)
        self._model = model
        self._client = client or OpenAI(api_key=api_key, timeout=timeout)

    def complete(self, request: ModelRequest) -> ModelResponse:
        if not request.prompt:
            raise ProviderError("empty prompt", retriable=False)
        started = time.monotonic()
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=_messages(request),
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
        except OpenAIError as exc:
            raise ProviderError(str(exc), retriable=_is_retriable(exc)) from exc
        except Exception as exc:
            raise ProviderError(str(exc), retriable=False) from exc
        return ModelResponse(
            text=_content(response),
            tokens_in=_usage_int(response, "prompt_tokens"),
            tokens_out=_usage_int(response, "completion_tokens"),
            latency_ms=(time.monotonic() - started) * 1000.0,
            model_id=str(getattr(response, "model", self._model)),
            finish_reason=_finish_reason(response),
        )


def _messages(request: ModelRequest) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    if request.system_prompt:
        messages.append({"role": "system", "content": request.system_prompt})
    messages.append({"role": "user", "content": request.prompt})
    return messages


def _content(response: Any) -> str:
    choices = getattr(response, "choices", None) or []
    if not choices:
        raise ProviderError("OpenAI response had no choices", retriable=True)
    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", None)
    if isinstance(content, str) and content.strip():
        return content
    raise ProviderError("OpenAI response had empty content", retriable=True)


def _usage_int(response: Any, field: str) -> int:
    usage = getattr(response, "usage", None)
    value = getattr(usage, field, 0)
    return int(value or 0)


def _finish_reason(response: Any) -> str:
    choices = getattr(response, "choices", None) or []
    if not choices:
        return "unknown"
    return str(getattr(choices[0], "finish_reason", "unknown"))


def _is_retriable(exc: OpenAIError) -> bool:
    status = getattr(exc, "status_code", None)
    if status in {408, 409, 429, 500, 502, 503, 504}:
        return True
    name = type(exc).__name__.lower()
    return "timeout" in name or "connection" in name or "rate" in name
