"""Materialize and register a Phase 9 file plan through current runtime seams."""

from __future__ import annotations

from pathlib import Path

from ..runtime import PipelineRunContext
from ..tools.fileio import FileIO
from .file_plan import LaTeXFilePlan


def materialize_plan(*, context: PipelineRunContext, plan: LaTeXFilePlan) -> tuple[Path, ...]:
    io = FileIO(context)
    written: list[Path] = []
    for item in plan.text_files:
        relative = f"latex_project/{item.relative_path}"
        path = io.write_text(relative, item.content)
        _register(context, relative, _artifact_id(item.relative_path), "text/plain")
        written.append(path)
    for item in plan.binary_files:
        relative = f"latex_project/{item.relative_path}"
        path = io.write_bytes(relative, item.content)
        _register(
            context,
            relative,
            _artifact_id(item.relative_path),
            "application/octet-stream",
        )
        written.append(path)
    return tuple(written)


def _register(context: PipelineRunContext, relative: str, artifact_id: str, contract: str) -> None:
    context.register_artifact(
        artifact_id=artifact_id,
        contract=contract,
        contract_version="v1",
        relative_path=relative,
        produced_by_task="phase9-assemble",
        consumed_by_tasks=["phase10-build", "phase11-validate"],
    )


def _artifact_id(relative: str) -> str:
    safe = relative.replace("/", ".").replace("_", "-")
    return f"phase9.{safe}"
