"""Deterministic-friendly run-ID generation.

A run ID is a time-prefixed token that sorts lexicographically by
creation time and contains enough randomness to avoid collisions
across parallel runs. The format is::

    RUN-YYYYMMDD-HHMMSS-<8 hex chars>

The randomness source is :mod:`secrets`. For tests, the
``frozen_clock`` and ``frozen_random`` parameters make the result
deterministic without affecting production behavior.
"""

from __future__ import annotations

import secrets
from collections.abc import Callable
from datetime import UTC, datetime

RUN_ID_PREFIX = "RUN"
_RANDOM_HEX_LEN = 8


def generate_run_id(
    *,
    now: Callable[[], datetime] | None = None,
    rand_hex: Callable[[int], str] | None = None,
) -> str:
    """Return a fresh run ID.

    The optional callables exist to make tests deterministic; they
    are not a runtime configuration knob.
    """

    clock = now or (lambda: datetime.now(UTC))
    rand = rand_hex or secrets.token_hex
    stamp = clock().strftime("%Y%m%d-%H%M%S")
    suffix = rand(_RANDOM_HEX_LEN // 2)
    assert len(suffix) == _RANDOM_HEX_LEN, "rand_hex must produce 8 hex chars"
    return f"{RUN_ID_PREFIX}-{stamp}-{suffix}"


def is_well_formed_run_id(candidate: str) -> bool:
    """Return ``True`` if ``candidate`` matches the documented shape."""

    parts = candidate.split("-")
    if len(parts) != 4:
        return False
    prefix, date, time, suffix = parts
    if prefix != RUN_ID_PREFIX:
        return False
    if len(date) != 8 or not date.isdigit():
        return False
    if len(time) != 6 or not time.isdigit():
        return False
    if len(suffix) != _RANDOM_HEX_LEN:
        return False
    return all(ch in "0123456789abcdef" for ch in suffix)
