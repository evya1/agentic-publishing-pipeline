"""Deterministic graph-generation pipeline for canonical visualization assets."""

from __future__ import annotations

from .errors import AssetRenderResult, SpecIssue, SpecValidationError
from .graph import GraphRenderError, LinePlotSpec, render_grouped_bar_chart, render_line_plot
from .models import GroupedBarChartSpec
from .render_pipeline import generate_graph, render_asset
from .validator import load_graph_spec, validate_graph_spec

__all__ = [
    "AssetRenderResult",
    "GraphRenderError",
    "GroupedBarChartSpec",
    "LinePlotSpec",
    "SpecIssue",
    "SpecValidationError",
    "generate_graph",
    "load_graph_spec",
    "render_asset",
    "render_grouped_bar_chart",
    "render_line_plot",
    "validate_graph_spec",
]
