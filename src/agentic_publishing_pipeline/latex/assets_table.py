"""Standalone table rendering from a strict semantic payload."""

from __future__ import annotations

from ..tools.markdown import escape_latex
from .config_models import AssetConfig


def render_table(asset: AssetConfig) -> str:
    columns = asset.payload.get("columns")
    rows = asset.payload.get("rows")
    if not isinstance(columns, list) or len(columns) < 2:
        raise ValueError(f"{asset.asset_id}: table requires at least two columns")
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{asset.asset_id}: table requires rows")
    parsed_columns = [escape_latex(str(value)) for value in columns]
    parsed_rows: list[list[str]] = []
    for row in rows:
        if not isinstance(row, list) or len(row) != len(parsed_columns):
            raise ValueError(f"{asset.asset_id}: table row width mismatch")
        parsed_rows.append([escape_latex(str(value)) for value in row])
    spec = "@{}" + "X" * len(parsed_columns) + "@{}"
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        f"\\begin{{tabularx}}{{\\textwidth}}{{{spec}}}",
        "\\toprule",
        " & ".join(parsed_columns) + r" \\",
        "\\midrule",
    ]
    lines.extend(" & ".join(row) + r" \\" for row in parsed_rows)
    lines.extend(
        (
            "\\bottomrule",
            "\\end{tabularx}",
            f"\\caption{{{escape_latex(asset.caption)}}}",
            f"\\label{{tab:{asset.label}}}",
            "\\end{table}",
        )
    )
    return "\n".join(lines) + "\n"
