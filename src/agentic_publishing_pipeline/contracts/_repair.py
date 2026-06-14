"""Bounded-repair helper for contract validation.

Per ADR-0002 and FR-42, the runtime allows **at most one** repair
attempt per stage when a parse fails contract validation. This module
provides the single helper every stage uses, plus the structured error
type the orchestrator surfaces on exhaustion.

The helper is intentionally transport-agnostic: it accepts a ``parse``
callable that returns the validated model (or raises a
``pydantic.ValidationError``) and a ``repair`` callable that receives
the original payload plus the previous validation errors and returns a
new payload to retry. The bound is hard-coded to one repair attempt;
the bound is not a runtime knob — see ADR-0002.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Generic, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)
P = TypeVar("P")

REPAIR_ATTEMPTS_ALLOWED: int = 1


class ContractValidationError(Exception):
    """Raised when the bounded-repair attempt is exhausted."""

    def __init__(
        self,
        contract_name: str,
        attempts: int,
        validation_errors: list[ValidationError],
    ) -> None:
        self.contract_name = contract_name
        self.attempts = attempts
        self.validation_errors = list(validation_errors)
        msg = (
            f"Contract {contract_name!r} failed validation after "
            f"{attempts} attempt(s); repair budget exhausted."
        )
        super().__init__(msg)


@dataclass
class RepairLog(Generic[T]):
    """Structured record of how the parse arrived at a model."""

    contract_name: str
    attempts: int
    repaired: bool = False
    errors: list[ValidationError] = field(default_factory=list)


def parse_with_repair(
    contract_name: str,
    raw: P,
    parse: Callable[[P], T],
    repair: Callable[[P, ValidationError], P] | None = None,
) -> tuple[T, RepairLog[T]]:
    """Parse ``raw`` into ``T`` with at most one bounded repair attempt.

    The first parse is attempted directly. On ``ValidationError``, if a
    ``repair`` callable is provided, exactly one repair payload is
    produced and parsed once more. If the repaired payload also fails,
    ``ContractValidationError`` is raised with both error sets preserved.
    """

    assert contract_name, "contract_name must be a non-empty identifier"
    errors: list[ValidationError] = []
    try:
        model = parse(raw)
        return model, RepairLog(contract_name=contract_name, attempts=1, repaired=False)
    except ValidationError as exc:
        errors.append(exc)
        if repair is None:
            raise ContractValidationError(contract_name, 1, errors) from exc
        repaired_payload = repair(raw, exc)
        try:
            model = parse(repaired_payload)
        except ValidationError as exc2:
            errors.append(exc2)
            raise ContractValidationError(contract_name, 2, errors) from exc2
        return (
            model,
            RepairLog(
                contract_name=contract_name,
                attempts=2,
                repaired=True,
                errors=errors,
            ),
        )
