"""Structured provider usage / cost log (`usage.jsonl`).

The log captures one record per Gatekeeper-gated call. The Gatekeeper
is the only writer; deterministic services do not emit usage events.
Required fields follow ``docs/architecture/c4_views.md`` §2 and
ADR-0004.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

UsageStatus = Literal["ok", "rejected", "error"]


class UsageLog:
    """Append-only JSON-Lines usage log written by :class:`ApiGatekeeper`."""

    def __init__(self, path: Path, run_id: str) -> None:
        assert path.is_absolute(), "usage log path must be absolute"
        self._path = path
        self._run_id = run_id

    @property
    def path(self) -> Path:
        return self._path

    def append(
        self,
        *,
        agent_id: str,
        task_id: str,
        attempt: int,
        model: str,
        tokens_in: int,
        tokens_out: int,
        latency_ms: float,
        status: UsageStatus,
        estimated_cost_usd: float,
        mode: str,
        purpose: str = "",
    ) -> dict[str, object]:
        assert attempt >= 1, "attempt must be >= 1"
        assert tokens_in >= 0 and tokens_out >= 0, "token counts must be non-negative"
        assert latency_ms >= 0.0, "latency must be non-negative"
        record: dict[str, object] = {
            "ts": datetime.now(UTC).isoformat(),
            "run_id": self._run_id,
            "agent_id": agent_id,
            "task_id": task_id,
            "attempt": attempt,
            "model": model,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "latency_ms": latency_ms,
            "status": status,
            "estimated_cost_usd": estimated_cost_usd,
            "mode": mode,
            "purpose": purpose,
        }
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True))
            handle.write("\n")
        self._mirror_to_logs(record)
        return record

    def read_all(self) -> list[dict[str, object]]:
        if not self._path.exists():
            return []
        return [
            json.loads(line)
            for line in self._path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def _mirror_to_logs(self, record: dict[str, object]) -> None:
        mirror = self._path.parent / "logs" / self._path.name
        if mirror == self._path:
            return
        mirror.parent.mkdir(parents=True, exist_ok=True)
        with mirror.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True))
            handle.write("\n")
