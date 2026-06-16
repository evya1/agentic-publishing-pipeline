"""Persistent run-stage state across the human-review pause."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..tools.fileio import FileIO


class PipelineStage(StrEnum):
    """Allowed manuscript run stages."""

    GENERATING = "generating"
    GENERATED = "generated"
    PREFLIGHT = "preflight"
    GENERATION_FAILED = "generation_failed"
    PARSING_FAILED = "parsing_failed"
    PERSISTENCE_FAILED = "persistence_failed"
    PREFLIGHT_FAILED = "preflight_failed"
    AWAITING_HUMAN_REVIEW = "awaiting_human_review"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    PROMOTED = "promoted"


_ALLOWED: dict[PipelineStage, frozenset[PipelineStage]] = {
    PipelineStage.GENERATING: frozenset(
        {
            PipelineStage.GENERATED,
            PipelineStage.GENERATION_FAILED,
            PipelineStage.PARSING_FAILED,
        }
    ),
    PipelineStage.GENERATED: frozenset(
        {PipelineStage.PREFLIGHT, PipelineStage.PERSISTENCE_FAILED}
    ),
    PipelineStage.PREFLIGHT: frozenset(
        {PipelineStage.AWAITING_HUMAN_REVIEW, PipelineStage.PREFLIGHT_FAILED}
    ),
    PipelineStage.GENERATION_FAILED: frozenset({PipelineStage.GENERATING}),
    PipelineStage.PARSING_FAILED: frozenset({PipelineStage.GENERATING}),
    PipelineStage.PERSISTENCE_FAILED: frozenset({PipelineStage.GENERATING}),
    PipelineStage.PREFLIGHT_FAILED: frozenset({PipelineStage.GENERATING}),
    PipelineStage.AWAITING_HUMAN_REVIEW: frozenset(
        {PipelineStage.APPROVED, PipelineStage.CHANGES_REQUESTED}
    ),
    PipelineStage.CHANGES_REQUESTED: frozenset({PipelineStage.GENERATING}),
    PipelineStage.APPROVED: frozenset({PipelineStage.PROMOTED}),
    PipelineStage.PROMOTED: frozenset(),
}


class StageTransitionError(RuntimeError):
    """Raised on an illegal stage transition."""


@dataclass(frozen=True)
class StageState:
    """Current stage persisted inside a run workspace."""

    stage: PipelineStage
    run_id: str
    detail: str = ""


def write_stage(file_io: FileIO, state: StageState) -> Path:
    """Persist a stable status file inside the run workspace."""
    payload = asdict(state)
    payload["stage"] = state.stage.value
    return file_io.write_json("status.json", payload)


def transition(
    file_io: FileIO,
    current: StageState,
    target: PipelineStage,
    *,
    detail: str = "",
) -> StageState:
    """Validate and persist one state transition."""
    if target not in _ALLOWED[current.stage]:
        raise StageTransitionError(
            f"illegal transition {current.stage.value} -> {target.value}"
        )
    updated = StageState(stage=target, run_id=current.run_id, detail=detail)
    write_stage(file_io, updated)
    return updated
