"""Typed provider facade — transport layer (ADR-0004).

Adapters implement the model/search protocols and return normalized
typed responses. No policy logic lives here; budget enforcement,
retry classification, and usage accounting belong to the API
Gatekeeper. Adapters must not write to disk and must not throw raw
SDK errors — they wrap them in :class:`ProviderError`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


class ProviderError(RuntimeError):
    """Wraps any adapter failure with a retry-classification hint."""

    def __init__(self, message: str, *, retriable: bool = False) -> None:
        super().__init__(message)
        self.retriable = retriable


@dataclass(frozen=True)
class ModelRequest:
    """Typed input to a model adapter."""

    model_class: str
    prompt: str
    system_prompt: str = ""
    max_tokens: int = 1024
    temperature: float = 0.2
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class ModelResponse:
    """Typed normalized response from a model adapter."""

    text: str
    tokens_in: int
    tokens_out: int
    latency_ms: float
    model_id: str
    finish_reason: str = "stop"


@dataclass(frozen=True)
class SearchHit:
    title: str
    url: str
    snippet: str = ""
    arxiv_id: str | None = None
    doi: str | None = None


@dataclass(frozen=True)
class SearchRequest:
    query: str
    max_results: int = 5
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchResponse:
    hits: list[SearchHit]
    latency_ms: float


class ModelAdapter(Protocol):
    """Protocol every model adapter implements."""

    name: str

    def complete(self, request: ModelRequest) -> ModelResponse: ...


class SearchAdapter(Protocol):
    """Protocol every search adapter implements."""

    name: str

    def search(self, request: SearchRequest) -> SearchResponse: ...


class ProviderFacade:
    """Holds the wired model + search adapters; no policy lives here."""

    def __init__(self, *, model: ModelAdapter, search: SearchAdapter) -> None:
        self._model = model
        self._search = search

    @property
    def model_name(self) -> str:
        return self._model.name

    @property
    def search_name(self) -> str:
        return self._search.name

    def complete(self, request: ModelRequest) -> ModelResponse:
        return self._model.complete(request)

    def search(self, request: SearchRequest) -> SearchResponse:
        return self._search.search(request)
