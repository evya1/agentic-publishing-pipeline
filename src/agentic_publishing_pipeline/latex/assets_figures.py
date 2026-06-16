"""Canonical graph wrapper and standalone semantic TikZ rendering."""

from __future__ import annotations

from collections.abc import Mapping

from ..tools.markdown import escape_latex
from .config_models import AssetConfig


def render_image(asset: AssetConfig, *, file_name: str) -> str:
    width = float(asset.payload.get("width", 0.9))
    if not 0.1 <= width <= 1.0:
        raise ValueError(f"{asset.asset_id}: image width must be in [0.1, 1.0]")
    return "\n".join(
        (
            "\\begin{figure}[htbp]",
            "\\centering",
            f"\\includegraphics[width={width:.2f}\\textwidth]{{figures/{file_name}}}",
            f"\\caption{{{escape_latex(asset.caption)}}}",
            f"\\label{{fig:{asset.label}}}",
            "\\end{figure}",
            "",
        )
    )


def render_tikz(asset: AssetConfig) -> str:
    nodes = asset.payload.get("nodes")
    edges = asset.payload.get("edges")
    if not isinstance(nodes, list) or len(nodes) < 2:
        raise ValueError(f"{asset.asset_id}: TikZ requires at least two nodes")
    parsed = [_node(value) for value in nodes]
    identifiers = {identifier for identifier, _ in parsed}
    if len(identifiers) != len(parsed):
        raise ValueError(f"{asset.asset_id}: duplicate TikZ node id")
    pairs = _edges(edges, identifiers, asset.asset_id)
    lines = [
        "\\begin{figure}[htbp]",
        "\\centering",
        "\\begin{tikzpicture}[node distance=2.2cm,>=Stealth]",
    ]
    for index, (identifier, text) in enumerate(parsed):
        placement = "" if index == 0 else f", right=of {parsed[index - 1][0]}"
        lines.append(f"\\node[draw,rounded corners{placement}] ({identifier}) {{{text}}};")
    lines.extend(f"\\draw[->] ({source}) -- ({target});" for source, target in pairs)
    lines.extend(
        (
            "\\end{tikzpicture}",
            f"\\caption{{{escape_latex(asset.caption)}}}",
            f"\\label{{fig:{asset.label}}}",
            "\\end{figure}",
            "",
        )
    )
    return "\n".join(lines)


def _node(value: object) -> tuple[str, str]:
    if not isinstance(value, Mapping):
        raise ValueError("TikZ node must be a mapping")
    identifier = _identifier(value.get("id"))
    label = escape_latex(str(value.get("label", "")).strip())
    if not label:
        raise ValueError("TikZ node label is required")
    return identifier, label


def _edges(value: object, ids: set[str], asset_id: str) -> list[tuple[str, str]]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{asset_id}: TikZ edges must be a non-empty list")
    result: list[tuple[str, str]] = []
    for edge in value:
        if not isinstance(edge, list) or len(edge) != 2:
            raise ValueError(f"{asset_id}: each TikZ edge needs two node IDs")
        pair = (_identifier(edge[0]), _identifier(edge[1]))
        if pair[0] not in ids or pair[1] not in ids:
            raise ValueError(f"{asset_id}: TikZ edge references an unknown node")
        result.append(pair)
    return result


def _identifier(value: object) -> str:
    text = str(value or "").strip()
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"
    if not text or any(char not in safe_chars for char in text):
        raise ValueError(f"unsafe TikZ identifier: {text!r}")
    return text
