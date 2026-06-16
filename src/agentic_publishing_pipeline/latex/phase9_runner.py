"""Phase 9 orchestration that stops before compilation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..runtime import PipelineRunContext
from ..tools.fileio import FileIO
from .approval_loader import load_approved_manuscript
from .config_loader import load_phase9_config, resolve_repo_path
from .materialize import materialize_plan
from .preflight import Phase9PreflightReport, run_phase9_preflight
from .project_renderer import build_project_plan
from .project_spec import build_project_spec


class Phase9InputNotReady(RuntimeError):
    """Raised when approved upstream artifacts cannot satisfy Phase 9."""


@dataclass(frozen=True)
class Phase9Result:
    project_root: Path
    manuscript_revision: str
    file_count: int
    preflight: Phase9PreflightReport


def assemble_phase9_project(
    *, context: PipelineRunContext, repo_root: Path, config_path: Path
) -> Phase9Result:
    """Validate approved inputs, assemble sources, and never compile a PDF."""
    config = load_phase9_config(config_path)
    source = config.source
    md_root = resolve_repo_path(repo_root, source.markdown_root)
    log_root = resolve_repo_path(repo_root, source.review_log_root)
    bibliography = resolve_repo_path(repo_root, source.bibliography_path)
    graph = resolve_repo_path(repo_root, source.graph_path)
    outline = resolve_repo_path(repo_root, source.outline_path)
    manuscript = load_approved_manuscript(
        generated_md_root=md_root,
        run_log_root=log_root,
        chapter_order=tuple(config.chapter_order),
    )
    report = run_phase9_preflight(
        manuscript=manuscript,
        config=config,
        outline_path=outline,
        bibliography_path=bibliography,
        graph_path=graph,
    )
    _write_preflight(context, report)
    if not report.passed:
        raise Phase9InputNotReady("; ".join(report.errors))
    spec = build_project_spec(run_id=context.run_id, manuscript=manuscript, config=config)
    _write_spec(context, spec.model_dump(mode="json"))
    plan = build_project_plan(
        manuscript=manuscript,
        config=config,
        bibliography_path=bibliography,
        graph_path=graph,
    )
    written = materialize_plan(context=context, plan=plan)
    context.events.append("phase9.assembly_completed", {"file_count": len(written)})
    return Phase9Result(
        project_root=context.paths.child("latex_project"),
        manuscript_revision=manuscript.revision,
        file_count=len(written),
        preflight=report,
    )


def _write_preflight(context: PipelineRunContext, report: Phase9PreflightReport) -> None:
    io = FileIO(context)
    relative = "validation/phase9_input_preflight.json"
    io.write_json(relative, report.to_json())
    context.register_artifact(
        artifact_id="phase9.input-preflight",
        contract="Phase9PreflightReport",
        contract_version="v1",
        relative_path=relative,
        produced_by_task="phase9-preflight",
        consumed_by_tasks=["phase9-assemble"],
    )


def _write_spec(context: PipelineRunContext, payload: object) -> None:
    io = FileIO(context)
    relative = "artifacts/latex_project_spec.v1.json"
    io.write_json(relative, payload)
    context.register_artifact(
        artifact_id="latex-project-spec.v1",
        contract="LaTeXProjectSpec",
        contract_version="v1",
        relative_path=relative,
        produced_by_task="phase9-assemble",
        consumed_by_tasks=["phase10-build", "phase11-validate"],
    )
