"""Deterministic offline-fixture adapters for model + search.

These adapters are the canonical Phase 5 transport. They make the
entire pipeline runnable in CI without API keys and without network
access. Real Anthropic / OpenAI / search adapters land later (Phase
6 / Phase 7) and conform to the same protocols.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path

from .facade import (
    ModelAdapter,
    ModelRequest,
    ModelResponse,
    ProviderError,
    SearchAdapter,
    SearchHit,
    SearchRequest,
    SearchResponse,
)


def _hashed_token_count(text: str, salt: int = 0) -> int:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return (int(digest[:8], 16) + salt) % 512 + 1


class FixtureModelAdapter(ModelAdapter):
    """Deterministic model adapter backed by a fixture directory or in-memory dict."""

    name = "fixture-model"

    def __init__(
        self,
        *,
        fixtures: dict[str, ModelResponse] | None = None,
        fixture_root: Path | None = None,
        default_text: str = "{}",
        model_id: str = "fixture-haiku-4-5",
    ) -> None:
        self._fixtures = dict(fixtures or {})
        self._fixture_root = fixture_root
        self._default_text = default_text
        self._model_id = model_id

    def _lookup(self, key: str) -> ModelResponse | None:
        if key in self._fixtures:
            return self._fixtures[key]
        if self._fixture_root is None:
            return None
        candidate = self._fixture_root / f"{key}.json"
        if not candidate.exists():
            return None
        payload = json.loads(candidate.read_text(encoding="utf-8"))
        return ModelResponse(
            text=payload.get("text", self._default_text),
            tokens_in=int(payload.get("tokens_in", 0)),
            tokens_out=int(payload.get("tokens_out", 0)),
            latency_ms=float(payload.get("latency_ms", 0.0)),
            model_id=str(payload.get("model_id", self._model_id)),
            finish_reason=str(payload.get("finish_reason", "stop")),
        )

    def complete(self, request: ModelRequest) -> ModelResponse:
        if not request.prompt:
            raise ProviderError("empty prompt", retriable=False)
        key = request.metadata.get("fixture_key", request.model_class)
        cached = self._lookup(key)
        if cached is not None:
            return cached
        return ModelResponse(
            text=self._default_text,
            tokens_in=_hashed_token_count(request.prompt),
            tokens_out=_hashed_token_count(self._default_text, salt=7),
            latency_ms=1.0,
            model_id=self._model_id,
            finish_reason="stop",
        )


class FixtureSearchAdapter(SearchAdapter):
    """Deterministic search adapter sourced from the configured manifest."""

    name = "fixture-search"

    def __init__(self, hits: Iterable[SearchHit] | None = None) -> None:
        self._hits = list(hits or [])

    def search(self, request: SearchRequest) -> SearchResponse:
        if not request.query:
            raise ProviderError("empty search query", retriable=False)
        query_lc = request.query.lower()
        matched = [
            h
            for h in self._hits
            if query_lc in h.title.lower()
            or query_lc in h.snippet.lower()
            or (h.arxiv_id and query_lc == h.arxiv_id.lower())
        ]
        return SearchResponse(hits=matched[: request.max_results], latency_ms=1.0)


class DisabledSearchAdapter(SearchAdapter):
    """Search adapter for locked-context live runs where discovery is forbidden."""

    name = "disabled-search"

    def search(self, request: SearchRequest) -> SearchResponse:
        del request
        raise ProviderError(
            "live Phase 6 search is disabled; run consumes only locked source context",
            retriable=False,
        )
