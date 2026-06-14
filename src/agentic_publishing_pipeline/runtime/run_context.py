"""PipelineRunContext — the deterministic owner of a single run.

The context creates the run ID, the isolated workspace, the
configuration snapshot, the structured event/usage logs, and the
artifact manifest. All workspace writes route through this object so
that the deterministic layer remains the only writer of run state.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

from .event_log import EventLog
from .manifest import ArtifactManifest, ManifestEntry, fresh_manifest, sha256_of
from .paths import WorkspacePaths
from .run_id import generate_run_id, is_well_formed_run_id
from .snapshot import build_snapshot, write_snapshot
from .usage_log import UsageLog


class PipelineRunContext:
    """Per-run deterministic state owner."""

    def __init__(
        self,
        *,
        run_id: str,
        results_root: Path,
        mode: str,
        topic: str | None = None,
        manifest_path: str | None = None,
        registry_version: str | None = None,
        env: Mapping[str, str] | None = None,
    ) -> None:
        assert is_well_formed_run_id(run_id), f"malformed run_id: {run_id!r}"
        assert results_root.is_absolute(), "results_root must be absolute"
        self._run_id = run_id
        self._mode = mode
        self.paths = WorkspacePaths(results_root / run_id)
        self.paths.ensure_layout()
        config_snapshot_path = self.paths.child("config_snapshot.json")
        snapshot = build_snapshot(
            run_id=run_id,
            mode=mode,
            topic=topic,
            manifest_path=manifest_path,
            registry_version=registry_version,
            env=env or {},
        )
        write_snapshot(config_snapshot_path, snapshot)
        self.events = EventLog(self.paths.child("events.jsonl"), run_id)
        self.usage = UsageLog(self.paths.child("usage.jsonl"), run_id)
        self._manifest_path = self.paths.child("manifest.v1.json")
        self._manifest: ArtifactManifest = fresh_manifest(
            run_id=run_id,
            mode=mode,
            config_snapshot_path=str(config_snapshot_path.relative_to(results_root)),
        )
        if registry_version:
            self._manifest.registry_version = registry_version
        self._persist_manifest()
        self.events.append("run.created", {"mode": mode, "topic": topic})

    @classmethod
    def create(
        cls,
        *,
        results_root: Path,
        mode: str,
        topic: str | None = None,
        manifest_path: str | None = None,
        registry_version: str | None = None,
        env: Mapping[str, str] | None = None,
    ) -> PipelineRunContext:
        return cls(
            run_id=generate_run_id(),
            results_root=results_root,
            mode=mode,
            topic=topic,
            manifest_path=manifest_path,
            registry_version=registry_version,
            env=env,
        )

    @property
    def run_id(self) -> str:
        return self._run_id

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def manifest(self) -> ArtifactManifest:
        return self._manifest

    def _persist_manifest(self) -> None:
        self._manifest.write(self._manifest_path)

    def register_artifact(
        self,
        *,
        artifact_id: str,
        contract: str,
        contract_version: str,
        relative_path: str,
        produced_by_task: str,
        consumed_by_tasks: list[str] | None = None,
    ) -> ManifestEntry:
        target = self.paths.child(relative_path)
        assert target.exists(), f"cannot register missing artifact: {relative_path}"
        entry = ManifestEntry(
            artifact_id=artifact_id,
            contract=contract,
            contract_version=contract_version,
            path=relative_path,
            sha256=sha256_of(target),
            produced_by_task=produced_by_task,
            consumed_by_tasks=list(consumed_by_tasks or []),
        )
        self._manifest.register(entry)
        self._persist_manifest()
        self.events.append("artifact.registered", {"artifact_id": artifact_id})
        return entry

    def write_artifact_json(self, relative_path: str, payload: object) -> Path:
        target = self.paths.child(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(payload, indent=2, sort_keys=True, default=str),
            encoding="utf-8",
        )
        return target
