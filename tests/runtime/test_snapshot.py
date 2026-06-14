"""Configuration snapshot tests — secret-shaped redaction."""

from __future__ import annotations

import json
from pathlib import Path

from agentic_publishing_pipeline.runtime import build_snapshot, redact_env, write_snapshot
from agentic_publishing_pipeline.runtime.snapshot import ABSENT, PRESENT


def test_redact_env_masks_secret_shaped_present_values() -> None:
    redacted = redact_env(
        {
            "OPENAI_API_KEY": "sk-abc",
            "ANTHROPIC_TOKEN": "tok",
            "USER_HOME": "/Users/x",
            "MODEL_NAME": "claude-haiku-4-5",
        }
    )
    assert redacted["OPENAI_API_KEY"] == PRESENT
    assert redacted["ANTHROPIC_TOKEN"] == PRESENT
    assert redacted["USER_HOME"] == "/Users/x"
    assert redacted["MODEL_NAME"] == "claude-haiku-4-5"


def test_redact_env_marks_secret_shaped_empty_values_absent() -> None:
    redacted = redact_env({"OPENAI_API_KEY": ""})
    assert redacted["OPENAI_API_KEY"] == ABSENT


def test_build_snapshot_includes_mode_and_topic() -> None:
    snap = build_snapshot(
        run_id="RUN-20260615-000000-aaaaaaaa",
        mode="offline-fixture",
        topic="Reasoning",
        manifest_path="config/article_sources.yaml",
        registry_version="v1",
        env={"PROVIDER_API_KEY": "secret"},
    )
    assert snap["mode"] == "offline-fixture"
    assert snap["topic"] == "Reasoning"
    assert snap["env"]["PROVIDER_API_KEY"] == PRESENT


def test_write_snapshot_persists_json(tmp_path: Path) -> None:
    snap = build_snapshot(
        run_id="RUN-X", mode="dry-run", topic=None, manifest_path=None,
        registry_version=None, env={}
    )
    target = tmp_path / "out" / "snap.json"
    write_snapshot(target, snap)
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded["mode"] == "dry-run"
