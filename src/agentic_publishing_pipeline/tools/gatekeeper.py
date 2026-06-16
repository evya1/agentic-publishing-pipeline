"""API Gatekeeper — the policy seam between Crew and ProviderFacade.

Per ADR-0004, the provider facade is the *transport* layer and the
Gatekeeper is the *policy* layer. Every provider call (live or
fixture) flows through the Gatekeeper so that budget accounting,
timeout/retry classification, and structured usage/cost emission are
identical regardless of mode.

The Gatekeeper does not silently fall back to a different model or
to a different mode; it raises :class:`GatekeeperRejection` on
budget exhaustion, timeout, or non-retriable provider failure.
"""

from __future__ import annotations

import time
from collections.abc import Callable

from ..providers import (
    ModelRequest,
    ModelResponse,
    ProviderError,
    ProviderFacade,
    SearchRequest,
    SearchResponse,
)
from ..providers.config import ProviderConfig
from ..runtime import PipelineRunContext
from ._gatekeeper_policy import BudgetState, RequestIdentity, estimate_cost


class GatekeeperRejection(RuntimeError):
    """Raised when policy denies a request (budget, timeout, non-retriable)."""

    def __init__(self, reason: str, *, kind: str) -> None:
        super().__init__(reason)
        self.kind = kind


def request_identity(agent_id: str, task_id: str, attempt: int = 1) -> RequestIdentity:
    return RequestIdentity(agent_id=agent_id, task_id=task_id, attempt=attempt)


class ApiGatekeeper:
    """Policy gate enforcing budget, timeout, and usage emission."""

    def __init__(
        self,
        *,
        facade: ProviderFacade,
        config: ProviderConfig,
        run_context: PipelineRunContext,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self._facade = facade
        self._config = config
        self._ctx = run_context
        self._clock = clock or time.monotonic
        self._budget = BudgetState()

    @property
    def budget(self) -> BudgetState:
        return self._budget

    def _check_budget(self, *, projected_cost: float) -> None:
        breach = self._budget.would_exceed(
            max_requests=self._config.gatekeeper_max_requests,
            max_cost=self._config.gatekeeper_max_cost_usd,
            next_cost=projected_cost,
        )
        if breach is not None:
            self._ctx.events.append("provider.rejected", {"reason": breach})
            raise GatekeeperRejection(f"budget would exceed {breach}", kind=breach)

    def call_model(
        self,
        request: ModelRequest,
        *,
        identity: RequestIdentity,
    ) -> ModelResponse:
        self._check_budget(projected_cost=0.0)
        started = self._clock()
        try:
            response = self._facade.complete(request)
        except ProviderError as exc:
            elapsed_ms = (self._clock() - started) * 1000.0
            self._ctx.usage.append(
                agent_id=identity.agent_id,
                task_id=identity.task_id,
                attempt=identity.attempt,
                model=self._facade.model_name,
                tokens_in=0,
                tokens_out=0,
                latency_ms=elapsed_ms,
                status="error",
                estimated_cost_usd=0.0,
                mode=self._ctx.mode,
            )
            if not exc.retriable:
                raise GatekeeperRejection(str(exc), kind="non_retriable") from exc
            raise
        elapsed_ms = (self._clock() - started) * 1000.0
        if elapsed_ms / 1000.0 > self._config.gatekeeper_timeout_seconds:
            self._ctx.events.append("provider.rejected", {"reason": "timeout"})
            raise GatekeeperRejection("timeout", kind="timeout")
        cost = estimate_cost(
            response.model_id,
            response.tokens_in,
            response.tokens_out,
            mode=self._ctx.mode,
        )
        self._check_budget(projected_cost=cost)
        self._budget.charge(cost=cost)
        self._ctx.usage.append(
            agent_id=identity.agent_id,
            task_id=identity.task_id,
            attempt=identity.attempt,
            model=response.model_id,
            tokens_in=response.tokens_in,
            tokens_out=response.tokens_out,
            latency_ms=elapsed_ms,
            status="ok",
            estimated_cost_usd=cost,
            mode=self._ctx.mode,
        )
        return response

    def call_search(
        self,
        request: SearchRequest,
        *,
        identity: RequestIdentity,
    ) -> SearchResponse:
        self._check_budget(projected_cost=0.0)
        started = self._clock()
        response = self._facade.search(request)
        elapsed_ms = (self._clock() - started) * 1000.0
        self._budget.charge(cost=0.0)
        self._ctx.usage.append(
            agent_id=identity.agent_id,
            task_id=identity.task_id,
            attempt=identity.attempt,
            model=self._facade.search_name,
            tokens_in=0,
            tokens_out=len(response.hits),
            latency_ms=elapsed_ms,
            status="ok",
            estimated_cost_usd=0.0,
            mode=self._ctx.mode,
        )
        return response
