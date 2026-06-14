"""Shared contract-test fixtures."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest


@pytest.fixture
def envelope_kwargs() -> dict[str, object]:
    return {
        "run_id": "RUN-TEST-0001",
        "contract_version": "v1",
        "produced_at": datetime(2026, 6, 15, tzinfo=UTC),
    }
