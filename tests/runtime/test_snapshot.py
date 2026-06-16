"""Configuration snapshot tests — secret-shaped redaction."""

from __future__ import annotations

import json
from pathlib import Path

from agentic_publishing_pipeline.runtime import build_snapshot, redact_env, write_snapshot
from agentic_publishing_pipeline.runtime.snapshot import ABSENT, PRESENT


def test_redact_env_keeps_only_allowed_settings_and_credential_presence() -> None:
    redacted = redact_env(
        {
            "OPENAI_API_KEY": "sk-abc",
            "APP_SEARCH_API_KEY": "",
            "APP_LLM_PROVIDER": "fixture",
            "APP_GATEKEEPER_MAX_REQUESTS": "8",
            "HOME": "/Users/local",
            "PATH": "/bin",
            "CLAUDE_SESSION": "abc",
        }
    )
    assert redacted["settings"] == {
        "APP_LLM_PROVIDER": "fixture",
        "APP_GATEKEEPER_MAX_REQUESTS": "8",
    }
    assert redacted["credential_presence"]["OPENAI_API_KEY"] == PRESENT
    assert redacted["credential_presence"]["APP_SEARCH_API_KEY"] == ABSENT
    assert "HOME" not in redacted["settings"]
    assert "PATH" not in redacted["settings"]
    assert "CLAUDE_SESSION" not in redacted["settings"]


def test_redact_env_is_deterministic_for_equivalent_input() -> None:
    left = redact_env({"APP_LLM_PROVIDER": "fixture", "OPENAI_API_KEY": "secret"})
    right = redact_env({"OPENAI_API_KEY": "different", "APP_LLM_PROVIDER": "fixture"})
    assert left == right


def test_build_snapshot_includes_mode_and_topic() -> None:
    snap = build_snapshot(
        run_id="RUN-20260615-000000-aaaaaaaa",
        mode="offline-fixture",
        topic="Reasoning",
        manifest_path="config/article_sources.yaml",
        registry_version="v1",
        env={"OPENAI_API_KEY": "secret", "APP_SEARCH_PROVIDER": "fixture", "USER": "local"},
    )
    assert snap["mode"] == "offline-fixture"
    assert snap["topic"] == "Reasoning"
    assert snap["credential_presence"]["OPENAI_API_KEY"] == PRESENT
    assert snap["settings"]["APP_SEARCH_PROVIDER"] == "fixture"
    assert "USER" not in snap["settings"]
    assert "secret" not in json.dumps(snap)


def test_write_snapshot_persists_json(tmp_path: Path) -> None:
    snap = build_snapshot(
        run_id="RUN-X",
        mode="dry-run",
        topic=None,
        manifest_path=None,
        registry_version=None,
        env={},
    )
    target = tmp_path / "out" / "snap.json"
    write_snapshot(target, snap)
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded["mode"] == "dry-run"
