"""Canonical spec -> workspace -> promotion pipeline for graph assets."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from ..runtime import PipelineRunContext, PromotionRefused, promote
from ..tools import FileIO
from .errors import AssetRenderResult, SpecValidationError
from .graph import render_grouped_bar_chart
from .models import GroupedBarChartSpec
from .naming import build_output_paths
from .provenance import build_provenance
from .validator import load_graph_spec, validate_graph_spec


def render_asset(
    spec: GroupedBarChartSpec,
    *,
    fileio: FileIO,
    input_sha256: str,
) -> AssetRenderResult:
    issues = validate_graph_spec(spec)
    if issues:
        raise SpecValidationError(issues)
    png_relative, provenance_relative = build_output_paths(spec, input_sha256=input_sha256)
    try:
        png_bytes = render_grouped_bar_chart(spec)
        output_sha256 = _sha256_bytes(png_bytes)
        fileio.write_bytes(png_relative, png_bytes)
        provenance = build_provenance(
            spec,
            input_sha256=input_sha256,
            output_sha256=output_sha256,
            relative_png_path=png_relative,
            commit_sha=_git_commit_sha(),
        )
        fileio.write_json(provenance_relative, provenance)
        fileio.record_event("graph.rendered", {"path": png_relative, "asset_id": spec.asset_id})
    except OSError as exc:
        return AssetRenderResult(
            success=False,
            asset_id=spec.asset_id,
            kind=spec.kind,
            slot=spec.slot,
            error_code="write_failed",
            message=str(exc),
        )
    return AssetRenderResult(
        success=True,
        asset_id=spec.asset_id,
        kind=spec.kind,
        slot=spec.slot,
        path=png_relative,
        provenance_path=provenance_relative,
        input_sha256=input_sha256,
        output_sha256=output_sha256,
    )


def generate_graph(
    *,
    spec_path: str | Path,
    output_root: str | Path,
    overwrite_existing: bool,
) -> AssetRenderResult:
    raw_spec = Path(spec_path).read_bytes()
    input_sha256 = _sha256_bytes(raw_spec)
    spec = load_graph_spec(spec_path)
    canonical_root = Path(output_root).resolve()
    ctx = PipelineRunContext.create(results_root=canonical_root / "results", mode="visualization")
    fileio = FileIO(ctx)
    spec_relative = f"artifacts/{spec.asset_id}.spec.yaml"
    fileio.write_bytes(spec_relative, raw_spec)
    _register_artifact(
        ctx,
        spec_relative,
        artifact_id=f"{spec.asset_id}_spec",
        contract="GraphSpec",
    )
    result = render_asset(spec, fileio=fileio, input_sha256=input_sha256)
    if not result.success:
        return result
    assert result.path and result.provenance_path
    _register_artifact(ctx, result.path, artifact_id=spec.asset_id, contract="RenderedGraphPNG")
    _register_artifact(
        ctx,
        result.provenance_path,
        artifact_id=f"{spec.asset_id}_provenance",
        contract="RenderedGraphProvenance",
    )
    fileio.write_json("validation/report.v1.json", {"result": "pass"})
    try:
        promote(
            workspace_root=ctx.paths.root,
            canonical_root=canonical_root,
            manifest_path=ctx.paths.child("manifest.v1.json"),
            validation_report_path=ctx.paths.child("validation/report.v1.json"),
            pairs=[(result.path, result.path), (result.provenance_path, result.provenance_path)],
            force=overwrite_existing,
            force_reason="visualization regeneration" if overwrite_existing else None,
        )
    except PromotionRefused as exc:
        return AssetRenderResult(
            success=False,
            asset_id=spec.asset_id,
            kind=spec.kind,
            slot=spec.slot,
            error_code="promotion_refused",
            message=str(exc),
            input_sha256=input_sha256,
            output_sha256=result.output_sha256,
        )
    return result


def _register_artifact(
    ctx: PipelineRunContext,
    relative_path: str,
    *,
    artifact_id: str,
    contract: str,
) -> None:
    ctx.register_artifact(
        artifact_id=artifact_id,
        contract=contract,
        contract_version="v1",
        relative_path=relative_path,
        produced_by_task="visualization",
    )


def _git_commit_sha() -> str | None:
    proc = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()
