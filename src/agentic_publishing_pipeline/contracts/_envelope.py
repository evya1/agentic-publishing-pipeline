"""Shared envelope mixin for every versioned artifact contract.

Every named/versioned contract in ``docs/architecture/artifact_contracts.md``
carries the same envelope: ``run_id``, ``contract_version``, and
``produced_at``. Defining the envelope once keeps the per-contract modules
focused on their domain fields and gives the bounded-repair helper a
single place to introspect the version tag.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ContractVersion = Literal["v1"]


def _utcnow() -> datetime:
    return datetime.now(UTC)


class ContractEnvelope(BaseModel):
    """Required envelope fields shared by every v1 contract."""

    model_config = ConfigDict(extra="forbid", frozen=False)

    run_id: str = Field(min_length=1)
    contract_version: ContractVersion = "v1"
    produced_at: datetime = Field(default_factory=_utcnow)
