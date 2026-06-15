"""Graph renderer tests against a real run workspace."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_publishing_pipeline.contracts import AssetSpec
from agentic_publishing_pipeline.runtime import PipelineRunContext, generate_run_id
from agentic_publishing_pipeline.tools import FileIO
from agentic_publishing_pipeline.visualization import (
    GraphRenderError,
    LinePlotSpec,
    render_line_plot,
    render_python_graph_asset,
)


def _ctx(tmp_path: Path) -> PipelineRunContext:
    return PipelineRunContext(
        run_id=generate_run_id(),
        results_root=tmp_path / "results",
        mode="offline-fixture",
        env={},
    )


def test_render_line_plot_writes_png_and_provenance(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    fio = FileIO(ctx)
    spec = LinePlotSpec(
        series_label="accuracy",
        x_values=[1.0, 2.0, 3.0],
        y_values=[0.6, 0.75, 0.82],
        title="accuracy vs round",
    )
    target = render_line_plot(spec, fileio=fio, relative_target="latex_project/figures/demo.png")
    assert target.exists()
    assert target.stat().st_size > 0
    provenance = target.with_suffix(target.suffix + ".prov.json")
    assert provenance.exists()


def test_line_plot_rejects_uneven_lengths() -> None:
    with pytest.raises(GraphRenderError):
        LinePlotSpec(series_label="x", x_values=[1.0, 2.0], y_values=[1.0])


def test_line_plot_rejects_empty_inputs() -> None:
    with pytest.raises(GraphRenderError):
        LinePlotSpec(series_label="x", x_values=[], y_values=[])


def test_render_python_graph_asset_happy_path(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    fio = FileIO(ctx)
    asset = AssetSpec(
        kind="python_graph",
        slot="evaluation/accuracy-1",
        chapter_id="evaluation",
        caption="Accuracy vs round",
        payload={
            "series_label": "accuracy",
            "x_values": [1.0, 2.0, 3.0, 4.0],
            "y_values": [0.6, 0.7, 0.8, 0.85],
            "x_label": "round",
            "y_label": "accuracy",
        },
    )
    target = render_python_graph_asset(asset, fileio=fio)
    assert target.name == "evaluation_accuracy-1.png"
    assert target.parent.name == "figures"


def test_render_python_graph_asset_rejects_wrong_kind(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    fio = FileIO(ctx)
    asset = AssetSpec(kind="image", slot="x", chapter_id="c")
    with pytest.raises(GraphRenderError):
        render_python_graph_asset(asset, fileio=fio)


def test_render_emits_audit_event(tmp_path: Path) -> None:
    ctx = _ctx(tmp_path)
    fio = FileIO(ctx)
    spec = LinePlotSpec(
        series_label="x", x_values=[0.0, 1.0], y_values=[0.0, 1.0]
    )
    render_line_plot(spec, fileio=fio, relative_target="latex_project/figures/x.png")
    events = [e for e in ctx.events.read_all() if e["kind"] == "graph.rendered"]
    assert events
