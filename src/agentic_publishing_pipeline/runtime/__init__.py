"""Run-lifecycle deterministic services.

Owns run-ID generation, isolated workspace creation, configuration
snapshot redaction, the structured event/usage logs, the artifact
manifest, and the explicit promotion operation. See
``docs/architecture/run_lifecycle.md``.
"""

from __future__ import annotations

from .event_log import EventLog
from .manifest import ArtifactManifest, ManifestEntry, fresh_manifest, sha256_of
from .paths import PathSafetyError, WorkspacePaths
from .promotion import PromotionRefused, promote
from .registry import (
    PromptConfig,
    Registry,
    RegistryError,
    load_registry,
    verify_compatibility,
)
from .run_context import PipelineRunContext
from .run_id import RUN_ID_PREFIX, generate_run_id, is_well_formed_run_id
from .snapshot import build_snapshot, redact_env, write_snapshot
from .stage_state import (
    PipelineStage,
    StageState,
    StageTransitionError,
    transition,
    write_stage,
)
from .usage_log import UsageLog, UsageStatus

__all__ = [
    "ArtifactManifest",
    "EventLog",
    "ManifestEntry",
    "PathSafetyError",
    "PipelineRunContext",
    "PipelineStage",
    "PromotionRefused",
    "PromptConfig",
    "RUN_ID_PREFIX",
    "Registry",
    "RegistryError",
    "StageState",
    "StageTransitionError",
    "UsageLog",
    "UsageStatus",
    "WorkspacePaths",
    "build_snapshot",
    "fresh_manifest",
    "generate_run_id",
    "is_well_formed_run_id",
    "load_registry",
    "promote",
    "redact_env",
    "sha256_of",
    "transition",
    "verify_compatibility",
    "write_snapshot",
    "write_stage",
]
