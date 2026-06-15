"""Python-generated visualizations for the article.

The Phase 5 layer ships the deterministic renderer; the article
content (real data) lives in Phase 8 (P8-I01). The renderer accepts
a typed :class:`AssetSpec` of kind ``python_graph`` and produces a
deterministic PNG file under ``latex_project/figures/`` with
provenance metadata so the asset can be traced back to its spec.
"""

from __future__ import annotations

from .graph import (
    GraphRenderError,
    LinePlotSpec,
    render_line_plot,
    render_python_graph_asset,
)

__all__ = [
    "GraphRenderError",
    "LinePlotSpec",
    "render_line_plot",
    "render_python_graph_asset",
]
