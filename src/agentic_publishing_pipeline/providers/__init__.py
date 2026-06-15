"""Controlled provider/service layer.

Every LLM and search call routes through this package. The
:class:`ProviderFacade` exposes one typed entry point per operation;
the concrete transport (Anthropic, OpenAI, deterministic fixture) is
hidden behind adapters that conform to the :class:`ModelAdapter` and
:class:`SearchAdapter` protocols.

Per ADR-0004, the facade is the *transport* layer; the API Gatekeeper
(:mod:`agentic_publishing_pipeline.tools.gatekeeper`) is the *policy*
layer. Agents and tasks call the Gatekeeper, which in turn calls the
facade. Offline-fixture mode resolves through the same Gatekeeper so
budget accounting, retry classification, and usage emission remain
identical to the live path.
"""

from __future__ import annotations

from .adapters import FixtureModelAdapter, FixtureSearchAdapter
from .config import ProviderConfig, load_provider_config
from .facade import (
    ModelAdapter,
    ModelRequest,
    ModelResponse,
    ProviderError,
    ProviderFacade,
    SearchAdapter,
    SearchHit,
    SearchRequest,
    SearchResponse,
)

__all__ = [
    "FixtureModelAdapter",
    "FixtureSearchAdapter",
    "ModelAdapter",
    "ModelRequest",
    "ModelResponse",
    "ProviderConfig",
    "ProviderError",
    "ProviderFacade",
    "SearchAdapter",
    "SearchHit",
    "SearchRequest",
    "SearchResponse",
    "load_provider_config",
]
