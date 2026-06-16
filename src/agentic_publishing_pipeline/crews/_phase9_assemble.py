"""CLI handler for assemble-phase9 mode."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from ..runtime import PipelineRunContext

_LATEX_CONFIG_DEFAULT = Path(__file__).resolve().parents[3] / "config/latex/phase9_project.yaml"


def run_phase9_assemble(ctx: PipelineRunContext, *, repo_root: Path) -> int:
    from ..latex import Phase9InputNotReady, assemble_phase9_project

    try:
        result = assemble_phase9_project(
            context=ctx, repo_root=repo_root, config_path=_LATEX_CONFIG_DEFAULT
        )
    except Phase9InputNotReady as exc:
        raise SystemExit(f"Phase 9 blocked: {exc}") from exc
    ctx.events.append("run.completed", {"mode": ctx.mode, "file_count": result.file_count})
    ctx.manifest.completed_at = datetime.now(UTC).isoformat()
    ctx.manifest.write(ctx.paths.child("manifest.v1.json"))
    ctx.manifest.write(ctx.paths.child("manifest.json"))
    return 0
