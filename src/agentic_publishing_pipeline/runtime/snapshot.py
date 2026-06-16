"""Configuration snapshot with allowlisted effective settings.

The snapshot captures the effective configuration at run start. It
records supported non-secret application settings and the **presence**
of configured credentials, never credential values or unrelated process
environment.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path

PRESENT = "***present***"
ABSENT = "***absent***"

APPLICATION_SETTING_NAMES: tuple[str, ...] = (
    "APP_LLM_PROVIDER",
    "APP_LLM_MODEL_CLASS",
    "APP_LLM_MODEL_ID",
    "APP_SEARCH_PROVIDER",
    "APP_GATEKEEPER_MAX_REQUESTS",
    "APP_GATEKEEPER_MAX_COST_USD",
    "APP_GATEKEEPER_TIMEOUT_SECONDS",
    "APP_RESULTS_ROOT",
)

CREDENTIAL_NAMES: tuple[str, ...] = (
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "APP_SEARCH_API_KEY",
)


def snapshot_settings(env: Mapping[str, str]) -> dict[str, str]:
    """Return explicitly supported non-secret application settings."""

    return {
        name: env[name] for name in APPLICATION_SETTING_NAMES if name in env and env[name] != ""
    }


def credential_presence(env: Mapping[str, str]) -> dict[str, str]:
    """Return stable credential-presence markers without values."""

    return {name: PRESENT if env.get(name) else ABSENT for name in CREDENTIAL_NAMES}


def redact_env(env: Mapping[str, str]) -> dict[str, dict[str, str]]:
    """Backward-compatible name for the sanitized environment snapshot."""

    return {
        "settings": snapshot_settings(env),
        "credential_presence": credential_presence(env),
    }


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
        **redact_env(env),
    }
    if extra:
        payload["extra"] = dict(extra)
    return payload


def write_snapshot(target: Path, snapshot: dict[str, object]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(snapshot, indent=2, sort_keys=True), encoding="utf-8")
