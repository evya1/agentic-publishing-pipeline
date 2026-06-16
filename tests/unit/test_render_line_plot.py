"""Focused tests for the legacy line-plot helper used in smoke runs."""

from __future__ import annotations

import json
from pathlib import Path

from agentic_publishing_pipeline.tools import FileIO
from agentic_publishing_pipeline.visualization import LinePlotSpec, render_line_plot

from .conftest import make_run_context


def test_render_line_plot_creates_png_and_json(tmp_path: Path) -> None:
    target = render_line_plot(
        LinePlotSpec(series_label="accuracy", x_values=[1.0, 2.0], y_values=[0.7, 0.8]),
        fileio=FileIO(make_run_context(tmp_path)),
        relative_target="latex_project/figures/demo.png",
    )
    assert target.exists()
    provenance = target.with_suffix(".png.prov.json")
    assert json.loads(provenance.read_text(encoding="utf-8"))["kind"] == "line_plot"


def test_render_line_plot_records_audit_event(tmp_path: Path) -> None:
    ctx = make_run_context(tmp_path)
    render_line_plot(
        LinePlotSpec(series_label="accuracy", x_values=[1.0, 2.0], y_values=[0.7, 0.8]),
        fileio=FileIO(ctx),
        relative_target="latex_project/figures/demo.png",
    )
    events = [event for event in ctx.events.read_all() if event["kind"] == "graph.rendered"]
    assert events[-1]["payload"]["path"] == "latex_project/figures/demo.png"
