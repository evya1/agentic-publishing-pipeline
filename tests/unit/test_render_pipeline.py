"""Pipeline tests for canonical graph generation."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from agentic_publishing_pipeline.tools import FileIO
from agentic_publishing_pipeline.visualization import (
    AssetRenderResult,
    SpecValidationError,
    generate_graph,
    load_graph_spec,
    render_asset,
)

from .conftest import make_run_context, valid_graph_spec_payload


def _write_spec(tmp_path: Path, payload: dict[str, object]) -> Path:
    path = tmp_path / "graph.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def test_render_asset_success(tmp_path: Path) -> None:
    spec_path = _write_spec(tmp_path, valid_graph_spec_payload())
    spec = load_graph_spec(spec_path)
    result = render_asset(
        spec,
        fileio=FileIO(make_run_context(tmp_path)),
        input_sha256="a" * 64,
    )
    assert result == AssetRenderResult(
        success=True,
        asset_id=spec.asset_id,
        kind=spec.kind,
        slot=spec.slot,
        path="latex_project/figures/planning_benchmark_comparison_aaaaaaaa.png",
        provenance_path="latex_project/figures/planning_benchmark_comparison_aaaaaaaa.png.prov.json",
        input_sha256="a" * 64,
        output_sha256=result.output_sha256,
    )


def test_render_asset_invalid_spec_never_reaches_renderer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    spec = load_graph_spec(_write_spec(tmp_path, valid_graph_spec_payload()))
    object.__setattr__(spec, "slot", "../escape")
    called = False

    def _boom(*args, **kwargs):  # noqa: ANN002, ANN003
        nonlocal called
        called = True
        raise AssertionError("renderer should not be called")

    monkeypatch.setattr(
        "agentic_publishing_pipeline.visualization.render_pipeline.render_grouped_bar_chart",
        _boom,
    )
    with pytest.raises(SpecValidationError):
        render_asset(spec, fileio=FileIO(make_run_context(tmp_path)), input_sha256="a" * 64)
    assert called is False


def test_render_asset_write_failure_returns_structured_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    spec = load_graph_spec(_write_spec(tmp_path, valid_graph_spec_payload()))

    def _fail(*args, **kwargs):  # noqa: ANN002, ANN003
        raise OSError("disk full")

    monkeypatch.setattr(FileIO, "write_bytes", _fail)
    result = render_asset(spec, fileio=FileIO(make_run_context(tmp_path)), input_sha256="a" * 64)
    assert not result.success
    assert result.error_code == "write_failed"


def test_render_asset_unexpected_errors_are_not_swallowed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    spec = load_graph_spec(_write_spec(tmp_path, valid_graph_spec_payload()))
    monkeypatch.setattr(
        "agentic_publishing_pipeline.visualization.render_pipeline.render_grouped_bar_chart",
        lambda _spec: (_ for _ in ()).throw(RuntimeError("bug")),
    )
    with pytest.raises(RuntimeError, match="bug"):
        render_asset(spec, fileio=FileIO(make_run_context(tmp_path)), input_sha256="a" * 64)


def test_generate_graph_requires_overwrite_for_existing_artifacts(tmp_path: Path) -> None:
    spec_path = _write_spec(tmp_path, valid_graph_spec_payload())
    first = generate_graph(spec_path=spec_path, output_root=tmp_path, overwrite_existing=True)
    assert first.success
    second = generate_graph(spec_path=spec_path, output_root=tmp_path, overwrite_existing=False)
    assert not second.success
    assert second.error_code == "promotion_refused"


def test_generate_graph_is_deterministic_across_output_roots(tmp_path: Path) -> None:
    spec_path = _write_spec(tmp_path, valid_graph_spec_payload())
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first = generate_graph(spec_path=spec_path, output_root=first_root, overwrite_existing=True)
    second = generate_graph(spec_path=spec_path, output_root=second_root, overwrite_existing=True)
    assert first.success and second.success
    assert (first_root / first.path).read_bytes() == (second_root / second.path).read_bytes()
    assert (first_root / first.provenance_path).read_bytes() == (
        second_root / second.provenance_path
    ).read_bytes()
