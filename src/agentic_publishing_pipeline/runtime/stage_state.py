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
    PREFLIGHT_FAILED = "preflight_failed"
    AWAITING_HUMAN_REVIEW = "awaiting_human_review"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    PROMOTED = "promoted"


_ALLOWED: dict[PipelineStage, frozenset[PipelineStage]] = {
    PipelineStage.GENERATING: frozenset(
        {PipelineStage.PREFLIGHT_FAILED, PipelineStage.AWAITING_HUMAN_REVIEW}
    ),
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
