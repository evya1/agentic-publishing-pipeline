"""Provider configuration loaded from environment variables.

Secrets are never read from source files. The env-variable contract
is documented in ``.env.example``.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderConfig:
    """Effective provider configuration captured at run start."""

    llm_provider: str
    llm_model_class: str
    search_provider: str
    gatekeeper_max_requests: int
    gatekeeper_max_cost_usd: float
    gatekeeper_timeout_seconds: float
    llm_model_id: str = "gpt-4.1-mini"

    @property
    def is_offline_fixture(self) -> bool:
        return self.llm_provider.lower() == "fixture"


def _as_int(value: str | None, *, default: int, name: str) -> int:
    if value is None or value == "":
        return default
    try:
        result = int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer; got {value!r}") from exc
    assert result >= 0, f"{name} must be non-negative"
    return result


def _as_float(value: str | None, *, default: float, name: str) -> float:
    if value is None or value == "":
        return default
    try:
        result = float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a float; got {value!r}") from exc
    assert result >= 0.0, f"{name} must be non-negative"
    return result


def load_provider_config(env: Mapping[str, str]) -> ProviderConfig:
    """Build a :class:`ProviderConfig` from an environment mapping."""

    return ProviderConfig(
        llm_provider=env.get("APP_LLM_PROVIDER", "fixture"),
        llm_model_class=env.get("APP_LLM_MODEL_CLASS", "research"),
        llm_model_id=env.get("APP_LLM_MODEL_ID", "gpt-4.1-mini"),
        search_provider=env.get("APP_SEARCH_PROVIDER", "fixture"),
        gatekeeper_max_requests=_as_int(
            env.get("APP_GATEKEEPER_MAX_REQUESTS"),
            default=64,
            name="APP_GATEKEEPER_MAX_REQUESTS",
        ),
        gatekeeper_max_cost_usd=_as_float(
            env.get("APP_GATEKEEPER_MAX_COST_USD"),
            default=2.50,
            name="APP_GATEKEEPER_MAX_COST_USD",
        ),
        gatekeeper_timeout_seconds=_as_float(
            env.get("APP_GATEKEEPER_TIMEOUT_SECONDS"),
            default=30.0,
            name="APP_GATEKEEPER_TIMEOUT_SECONDS",
        ),
    )
