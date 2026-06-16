"""Deterministic Matplotlib rendering helpers for visualization assets."""

from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

from ..tools import FileIO
from .models import GroupedBarChartSpec

_SERIES_COLORS = ("#1b9e77", "#d95f02", "#7570b3", "#66a61e")


class GraphRenderError(ValueError):
    """Raised when a graph specification cannot be rendered."""


@dataclass(frozen=True)
class LinePlotSpec:
    series_label: str
    x_values: list[float]
    y_values: list[float]
    x_label: str = "x"
    y_label: str = "y"
    title: str = ""

    def __post_init__(self) -> None:
        if len(self.x_values) != len(self.y_values):
            raise GraphRenderError("x_values and y_values must have equal length")
        if not self.x_values:
            raise GraphRenderError("x_values must be non-empty")


def render_grouped_bar_chart(spec: GroupedBarChartSpec) -> bytes:
    fig, ax = plt.subplots(figsize=(spec.render.width_inches, spec.render.height_inches))
    series_count = len(spec.data.series)
    bar_width = 0.8 / series_count
    x_positions = list(range(len(spec.data.categories)))
    offsets = [index - (series_count - 1) / 2 for index in range(series_count)]
    for series_index, series in enumerate(spec.data.series):
        positions = [x + offsets[series_index] * bar_width for x in x_positions]
        values = [float(value) for value in series.values]
        ax.bar(
            positions,
            values,
            width=bar_width,
            label=series.label,
            color=_SERIES_COLORS[series_index % len(_SERIES_COLORS)],
        )
    ax.set_title(spec.title)
    ax.set_xlabel(spec.x_label)
    ax.set_ylabel(spec.y_label)
    ax.set_xticks(x_positions, spec.data.categories, rotation=12)
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    return _png_bytes(fig, dpi=spec.render.dpi)


def render_line_plot(
    spec: LinePlotSpec,
    *,
    fileio: FileIO,
    relative_target: str | Path,
) -> Path:
    fig, ax = plt.subplots(figsize=(6.0, 3.5))
    ax.plot(spec.x_values, spec.y_values, marker="o", label=spec.series_label)
    ax.set_xlabel(spec.x_label)
    ax.set_ylabel(spec.y_label)
    if spec.title:
        ax.set_title(spec.title)
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=False)
    fig.tight_layout()
    png_bytes = _png_bytes(fig, dpi=200)
    target = fileio.write_bytes(relative_target, png_bytes)
    provenance_relative = f"{fileio.relative_path(relative_target)}.prov.json"
    fileio.write_json(
        provenance_relative,
        {
            "kind": "line_plot",
            "series_label": spec.series_label,
            "x_values": spec.x_values,
            "y_values": spec.y_values,
            "x_label": spec.x_label,
            "y_label": spec.y_label,
            "title": spec.title,
        },
    )
    fileio.record_event("graph.rendered", {"path": fileio.relative_path(relative_target)})
    return target


def _png_bytes(fig: plt.Figure, *, dpi: int) -> bytes:
    buffer = io.BytesIO()
    try:
        fig.savefig(buffer, format="png", dpi=dpi, metadata={})
        return buffer.getvalue()
    finally:
        buffer.close()
        plt.close(fig)
