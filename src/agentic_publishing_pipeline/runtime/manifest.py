"""Run-scoped artifact manifest with SHA-256 integrity.

The manifest is the single source of truth for "what did this run
produce". It is required for promotion (ADR-0005), resumption, and
the sanitized evidence bundle (P13-I05).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass
class ManifestEntry:
    artifact_id: str
    contract: str
    contract_version: str
    path: str
    sha256: str
    produced_by_task: str
    consumed_by_tasks: list[str] = field(default_factory=list)


@dataclass
class ArtifactManifest:
    """In-memory artifact manifest, persisted to ``manifest.v1.json``."""

    manifest_version: str
    run_id: str
    started_at: str
    mode: str
    config_snapshot_path: str
    registry_version: str | None = None
    completed_at: str | None = None
    artifacts: list[ManifestEntry] = field(default_factory=list)
    build_result_ref: str | None = None
    validation_report_ref: str | None = None
    promotion_ref: str | None = None

    def register(self, entry: ManifestEntry) -> None:
        assert all(e.artifact_id != entry.artifact_id for e in self.artifacts), (
            f"Artifact {entry.artifact_id!r} already registered."
        )
        self.artifacts.append(entry)

    def find(self, artifact_id: str) -> ManifestEntry | None:
        for entry in self.artifacts:
            if entry.artifact_id == artifact_id:
                return entry
        return None

    def to_json(self) -> dict[str, object]:
        return asdict(self)

    def write(self, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_json(), indent=2, sort_keys=True), encoding="utf-8")

    def verify_integrity(self, workspace_root: Path) -> list[str]:
        """Return a list of artifact IDs whose recorded hash disagrees with disk."""

        broken: list[str] = []
        for entry in self.artifacts:
            target = (workspace_root / entry.path).resolve()
            try:
                target.relative_to(workspace_root.resolve())
            except ValueError:
                target = Path(entry.path)
            if not target.exists():
                broken.append(entry.artifact_id)
                continue
            if sha256_of(target) != entry.sha256:
                broken.append(entry.artifact_id)
        return broken


def fresh_manifest(*, run_id: str, mode: str, config_snapshot_path: str) -> ArtifactManifest:
    return ArtifactManifest(
        manifest_version="v1",
        run_id=run_id,
        started_at=datetime.now(UTC).isoformat(),
        mode=mode,
        config_snapshot_path=config_snapshot_path,
    )
