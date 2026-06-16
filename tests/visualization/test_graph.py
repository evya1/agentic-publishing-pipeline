"""Low-level renderer tests for visualization graphs."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pytest

from agentic_publishing_pipeline.runtime import PipelineRunContext, generate_run_id
from agentic_publishing_pipeline.tools import FileIO
from agentic_publishing_pipeline.visualization import (
    GraphRenderError,
    GroupedBarChartSpec,
    LinePlotSpec,
    render_grouped_bar_chart,
    render_line_plot,
)


def _ctx(tmp_path: Path) -> PipelineRunContext:
    return PipelineRunContext(
        run_id=generate_run_id(),
        results_root=tmp_path / "results",
        mode="visualization",
        env={},
    )


def test_render_grouped_bar_chart_returns_png_bytes() -> None:
    spec = GroupedBarChartSpec.model_validate(
        {
            "schema_version": 1,
            "asset_id": "planning_benchmark_comparison",
            "kind": "grouped_bar_chart",
            "slot": "planning_benchmark_comparison",
            "chapter_id": "planning",
            "output_dir": "latex_project/figures",
            "title": "Planning benchmark coverage",
            "caption": "Grouped benchmark comparison.",
            "x_label": "Method",
            "y_label": "Solved tasks (out of 360)",
            "metric": {"name": "solved_tasks", "unit": "tasks", "direction": "higher_is_better"},
            "data": {
                "categories": ["Planner", "GPT-5"],
                "series": [
                    {"label": "Standard tasks", "values": [234, 205]},
                    {"label": "Obfuscated tasks", "values": [234, 142]},
                ],
            },
            "source": {
                "citation_key": "correa2025planningperformance",
                "identifier": "arXiv:2511.09378v2",
                "publication_url_or_doi": "https://doi.org/10.48550/arXiv.2511.09378",
                "locator": {
                    "page": None,
                    "table": "Tables 1 and 2",
                    "figure": None,
                    "rows": ["Sum (360)"],
                },
                "notes": "Selected totals.",
            },
            "transformations": [],
            "render": {"width_inches": 7.2, "height_inches": 4.2, "dpi": 200, "seed": 0},
        }
    )
    png_bytes = render_grouped_bar_chart(spec)
    assert png_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    assert plt.get_fignums() == []


def test_render_line_plot_writes_png_and_provenance(tmp_path: Path) -> None:
    fio = FileIO(_ctx(tmp_path))
    spec = LinePlotSpec(series_label="accuracy", x_values=[1.0, 2.0], y_values=[0.7, 0.8])
    target = render_line_plot(spec, fileio=fio, relative_target="latex_project/figures/demo.png")
    assert target.exists()
    assert target.stat().st_size > 0
    assert target.with_suffix(".png.prov.json").exists()


def test_render_line_plot_is_deterministic(tmp_path: Path) -> None:
    spec = LinePlotSpec(series_label="det", x_values=[1.0, 2.0], y_values=[1.0, 4.0])
    first = render_line_plot(
        spec,
        fileio=FileIO(_ctx(tmp_path / "a")),
        relative_target="latex_project/figures/det.png",
    )
    second = render_line_plot(
        spec,
        fileio=FileIO(_ctx(tmp_path / "b")),
        relative_target="latex_project/figures/det.png",
    )
    assert first.read_bytes() == second.read_bytes()


def test_line_plot_rejects_invalid_lengths() -> None:
    with pytest.raises(GraphRenderError):
        LinePlotSpec(series_label="bad", x_values=[1.0, 2.0], y_values=[1.0])
