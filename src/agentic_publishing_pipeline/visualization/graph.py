"""Deterministic Python-graph renderer for AssetSpec(kind='python_graph').

The renderer uses Matplotlib with the ``Agg`` backend so no GUI is
required. Outputs are written via the FileIO tool so paths stay
inside the workspace and the write is audited (P5-I04). A small
JSON provenance file is written next to each PNG so the asset can
be traced back to its spec.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402  (after backend select)

from ..contracts import AssetSpec
from ..tools import FileIO


class GraphRenderError(ValueError):
    """Raised when a graph spec cannot be rendered."""


@dataclass
class LinePlotSpec:
    """Minimal deterministic line-plot spec consumed by the renderer."""

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


def _figure(spec: LinePlotSpec) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(6.0, 3.5))
    ax.plot(spec.x_values, spec.y_values, marker="o", label=spec.series_label)
    ax.set_xlabel(spec.x_label)
    ax.set_ylabel(spec.y_label)
    if spec.title:
        ax.set_title(spec.title)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    return fig


def render_line_plot(
    spec: LinePlotSpec,
    *,
    fileio: FileIO,
    relative_target: str | Path,
) -> Path:
    """Render ``spec`` to a PNG under the workspace and return the path."""

    target = fileio.resolve(relative_target)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig = _figure(spec)
    try:
        fig.savefig(target, dpi=200, format="png")
    finally:
        plt.close(fig)
    fileio._ctx.events.append(  # noqa: SLF001  (audit hook)
        "graph.rendered",
        {"path": str(target.relative_to(fileio._ctx.paths.root))},
    )
    provenance = target.with_suffix(target.suffix + ".prov.json")
    fileio.write_json(
        Path(provenance).relative_to(fileio._ctx.paths.root),
        {
            "kind": "line_plot",
            "series_label": spec.series_label,
            "x_label": spec.x_label,
            "y_label": spec.y_label,
            "title": spec.title,
            "n_points": len(spec.x_values),
        },
    )
    return target


def _spec_from_asset(asset: AssetSpec) -> LinePlotSpec:
    if asset.kind != "python_graph":
        raise GraphRenderError(f"asset kind {asset.kind!r} is not 'python_graph'")
    payload = dict(asset.payload)
    return LinePlotSpec(
        series_label=str(payload.get("series_label", asset.slot)),
        x_values=[float(v) for v in payload.get("x_values", [])],
        y_values=[float(v) for v in payload.get("y_values", [])],
        x_label=str(payload.get("x_label", "x")),
        y_label=str(payload.get("y_label", "y")),
        title=str(payload.get("title", asset.caption)),
    )


def render_python_graph_asset(
    asset: AssetSpec,
    *,
    fileio: FileIO,
    figures_subdir: str = "latex_project/figures",
) -> Path:
    """Render a typed ``python_graph`` :class:`AssetSpec` to a PNG."""

    plot_spec = _spec_from_asset(asset)
    file_stem = asset.slot.replace("/", "_") + ".png"
    relative = f"{figures_subdir}/{file_stem}"
    return render_line_plot(plot_spec, fileio=fileio, relative_target=relative)
