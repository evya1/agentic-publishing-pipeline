"""Translate semantic Phase 9 assets into standalone files and includes."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from .assets_figures import render_image, render_tikz
from .assets_math import render_equation, render_equation_ref, render_theorem
from .assets_table import render_table
from .config_models import AssetConfig
from .file_plan import PlannedTextFile


@dataclass(frozen=True)
class AssetFiles:
    files: tuple[PlannedTextFile, ...]
    includes_by_chapter: dict[str, tuple[str, ...]]


def build_asset_files(assets: list[AssetConfig], *, graph_path: Path) -> AssetFiles:
    files: list[PlannedTextFile] = []
    includes: dict[str, list[str]] = defaultdict(list)
    for asset in assets:
        path, content = _render(asset, graph_path=graph_path)
        files.append(PlannedTextFile(path, content))
        includes[asset.chapter_id].append(path.removesuffix(".tex"))
    return AssetFiles(
        files=tuple(files),
        includes_by_chapter={key: tuple(value) for key, value in includes.items()},
    )


def _render(asset: AssetConfig, *, graph_path: Path) -> tuple[str, str]:
    if asset.kind == "table":
        return f"tables/{asset.asset_id}.tex", render_table(asset)
    if asset.kind == "equation":
        return f"components/{asset.asset_id}.tex", render_equation(asset)
    if asset.kind == "equation_ref":
        return f"components/{asset.asset_id}.tex", render_equation_ref(asset)
    if asset.kind == "theorem":
        return f"components/{asset.asset_id}.tex", render_theorem(asset)
    if asset.kind == "tikz":
        return f"figures/{asset.asset_id}.tex", render_tikz(asset)
    if asset.kind == "image":
        content = render_image(asset, file_name=graph_path.name)
        return f"figures/{asset.asset_id}.tex", content
    raise ValueError(f"unsupported Phase 9 asset kind: {asset.kind}")
