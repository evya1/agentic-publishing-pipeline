"""Configuration snapshot with secret-shaped value redaction.

The snapshot captures the effective configuration at run start. It
records the **presence** of secret-shaped env variables but never
their values, so the snapshot can be safely included in the sanitized
final-run evidence bundle (P13-I05).
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path

REDACTED = "***redacted***"
PRESENT = "***present***"
ABSENT = "***absent***"

_SECRET_HINTS: tuple[str, ...] = (
    "KEY",
    "TOKEN",
    "SECRET",
    "PASSWORD",
    "API",
    "CREDENTIAL",
)


def _looks_like_secret(name: str) -> bool:
    upper = name.upper()
    return any(hint in upper for hint in _SECRET_HINTS)


def redact_env(env: Mapping[str, str]) -> dict[str, str]:
    """Return a copy of ``env`` where secret-shaped values are masked."""

    redacted: dict[str, str] = {}
    for name, value in env.items():
        if _looks_like_secret(name):
            redacted[name] = PRESENT if value else ABSENT
        else:
            redacted[name] = value
    return redacted


def build_snapshot(
    *,
    run_id: str,
    mode: str,
    topic: str | None,
    manifest_path: str | None,
    registry_version: str | None,
    env: Mapping[str, str],
    extra: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Compose the snapshot dictionary that is written to disk verbatim."""

    payload: dict[str, object] = {
        "snapshot_version": "v1",
        "run_id": run_id,
        "captured_at": datetime.now(UTC).isoformat(),
        "mode": mode,
        "topic": topic,
        "manifest_path": manifest_path,
        "registry_version": registry_version,
        "env": redact_env(env),
    }
    if extra:
        payload["extra"] = dict(extra)
    return payload


def write_snapshot(target: Path, snapshot: dict[str, object]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
