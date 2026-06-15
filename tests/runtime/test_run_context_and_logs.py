"""End-to-end PipelineRunContext + manifest + log tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_publishing_pipeline.runtime import (
    ArtifactManifest,
    PipelineRunContext,
    fresh_manifest,
    generate_run_id,
    sha256_of,
)


def _new_context(tmp_path: Path) -> PipelineRunContext:
    rid = generate_run_id()
    return PipelineRunContext(
        run_id=rid,
        results_root=tmp_path / "results",
        mode="offline-fixture",
        topic="Reasoning",
        manifest_path="config/article_sources.yaml",
        registry_version="v1",
        env={"OPENAI_API_KEY": "secret"},
    )


def test_context_bootstrap_creates_workspace_layout(tmp_path: Path) -> None:
    ctx = _new_context(tmp_path)
    root = ctx.paths.root
    assert root.is_dir()
    assert (root / "artifacts").is_dir()
    assert (root / "raw").is_dir()
    assert (root / "latex_project" / "chapters").is_dir()
    assert (root / "config_snapshot.json").is_file()
    assert (root / "manifest.v1.json").is_file()


def test_context_snapshot_is_redacted_on_disk(tmp_path: Path) -> None:
    ctx = _new_context(tmp_path)
    payload = json.loads((ctx.paths.root / "config_snapshot.json").read_text(encoding="utf-8"))
    assert payload["credential_presence"]["OPENAI_API_KEY"] == "***present***"
    assert "secret" not in json.dumps(payload)
    assert "env" not in payload


def test_context_event_log_records_creation(tmp_path: Path) -> None:
    ctx = _new_context(tmp_path)
    events = ctx.events.read_all()
    assert any(e["kind"] == "run.created" for e in events)


def test_register_artifact_records_hash(tmp_path: Path) -> None:
    ctx = _new_context(tmp_path)
    target = ctx.write_artifact_json("artifacts/research_notes.v1.json", {"hello": "world"})
    expected_hash = sha256_of(target)
    entry = ctx.register_artifact(
        artifact_id="research_notes",
        contract="ResearchNotes",
        contract_version="v1",
        relative_path="artifacts/research_notes.v1.json",
        produced_by_task="T1",
        consumed_by_tasks=["T2"],
    )
    assert entry.sha256 == expected_hash
    persisted = json.loads((ctx.paths.root / "manifest.v1.json").read_text(encoding="utf-8"))
    assert persisted["artifacts"][0]["sha256"] == expected_hash


def test_register_artifact_refuses_duplicate(tmp_path: Path) -> None:
    ctx = _new_context(tmp_path)
    ctx.write_artifact_json("artifacts/outline.v1.json", {})
    ctx.register_artifact(
        artifact_id="outline",
        contract="Outline",
        contract_version="v1",
        relative_path="artifacts/outline.v1.json",
        produced_by_task="T2",
    )
    with pytest.raises(AssertionError):
        ctx.register_artifact(
            artifact_id="outline",
            contract="Outline",
            contract_version="v1",
            relative_path="artifacts/outline.v1.json",
            produced_by_task="T2",
        )


def test_usage_log_appends_records(tmp_path: Path) -> None:
    ctx = _new_context(tmp_path)
    ctx.usage.append(
        agent_id="A1", task_id="T1", attempt=1, model="haiku-4-5",
        tokens_in=10, tokens_out=20, latency_ms=5.0, status="ok",
        estimated_cost_usd=0.0001, mode="offline-fixture",
    )
    records = ctx.usage.read_all()
    assert records[0]["agent_id"] == "A1"
    assert records[0]["tokens_in"] == 10


def test_manifest_verify_integrity_flags_tampered(tmp_path: Path) -> None:
    ctx = _new_context(tmp_path)
    ctx.write_artifact_json("artifacts/x.v1.json", {"k": 1})
    ctx.register_artifact(
        artifact_id="x", contract="X", contract_version="v1",
        relative_path="artifacts/x.v1.json", produced_by_task="T1",
    )
    (ctx.paths.root / "artifacts" / "x.v1.json").write_text("{}", encoding="utf-8")
    broken = ctx.manifest.verify_integrity(ctx.paths.root)
    assert broken == ["x"]


def test_fresh_manifest_envelope() -> None:
    manifest = fresh_manifest(
        run_id="RUN-20260615-000000-aaaaaaaa",
        mode="dry-run",
        config_snapshot_path="results/RUN/config_snapshot.json",
    )
    assert isinstance(manifest, ArtifactManifest)
    assert manifest.run_id.startswith("RUN-")
