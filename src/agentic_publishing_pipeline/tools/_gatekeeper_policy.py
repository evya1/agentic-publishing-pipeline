"""Policy primitives for the API Gatekeeper.

Split from :mod:`.gatekeeper` so each module stays under the 150-LOC
project cap and the policy types are independently testable.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RequestIdentity:
    """Identity carried by every Gatekeeper request for usage attribution."""

    agent_id: str
    task_id: str
    attempt: int

    def __post_init__(self) -> None:
        assert self.attempt >= 1, "attempt must be >= 1"
        assert self.agent_id, "agent_id must be non-empty"
        assert self.task_id, "task_id must be non-empty"


@dataclass
class BudgetState:
    """Per-run budget accounting used by :class:`ApiGatekeeper`."""

    requests_used: int = 0
    cost_used_usd: float = 0.0

    def would_exceed(
        self,
        *,
        max_requests: int,
        max_cost: float,
        next_cost: float,
    ) -> str | None:
        if self.requests_used + 1 > max_requests:
            return "max_requests"
        if self.cost_used_usd + next_cost > max_cost:
            return "max_cost"
        return None

    def charge(self, *, cost: float) -> None:
        assert cost >= 0.0, "cost must be non-negative"
        self.requests_used += 1
        self.cost_used_usd += cost


def estimate_cost(
    model_id: str,
    tokens_in: int,
    tokens_out: int,
    *,
    mode: str,
) -> float:
    """Estimate per-call cost in USD; 0 for offline-fixture/dry-run."""

    if mode in {"offline-fixture", "dry-run"}:
        return 0.0
    rate = 0.000003 if "haiku" in model_id else 0.000015
    return round((tokens_in + tokens_out) * rate, 6)
