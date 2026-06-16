"""Structured run event log (`events.jsonl`).

The log is append-only JSON-Lines. Every entry includes ``run_id``
and a UTC ``ts`` so external tooling can sort and filter without
parsing structured payloads.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path


class EventLog:
    """Append-only JSON-Lines event log."""

    def __init__(self, path: Path, run_id: str) -> None:
        assert path.is_absolute(), "event log path must be absolute"
        self._path = path
        self._run_id = run_id

    @property
    def path(self) -> Path:
        return self._path

    def append(self, kind: str, payload: Mapping[str, object] | None = None) -> dict[str, object]:
        assert kind, "event kind must be non-empty"
        record: dict[str, object] = {
            "ts": datetime.now(UTC).isoformat(),
            "run_id": self._run_id,
            "kind": kind,
        }
        if payload:
            record["payload"] = dict(payload)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True))
            handle.write("\n")
        self._mirror_to_logs(record)
        return record

    def read_all(self) -> list[dict[str, object]]:
        if not self._path.exists():
            return []
        records: list[dict[str, object]] = []
        for line in self._path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            records.append(json.loads(line))
        return records

    def _mirror_to_logs(self, record: dict[str, object]) -> None:
        mirror = self._path.parent / "logs" / self._path.name
        if mirror == self._path:
            return
        mirror.parent.mkdir(parents=True, exist_ok=True)
        with mirror.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True))
            handle.write("\n")
