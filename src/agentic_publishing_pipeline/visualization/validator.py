"""Deterministic loading and validation for canonical graph specs."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError as PydanticValidationError

from .errors import SpecIssue, SpecValidationError
from .models import GroupedBarChartSpec
from .naming import validate_output_dir, validate_slug


def load_graph_spec(path: str | Path) -> GroupedBarChartSpec:
    raw_path = Path(path)
    payload = yaml.safe_load(raw_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SpecValidationError([SpecIssue("root", "YAML document must be a mapping")])
    try:
        spec = GroupedBarChartSpec.model_validate(payload)
    except PydanticValidationError as exc:
        raise SpecValidationError(_issues_from_pydantic(exc)) from exc
    issues = validate_graph_spec(spec)
    if issues:
        raise SpecValidationError(issues)
    return spec


def validate_graph_spec(spec: GroupedBarChartSpec) -> list[SpecIssue]:
    issues = [
        *validate_slug(spec.asset_id, field="asset_id"),
        *validate_slug(spec.slot, field="slot"),
        *validate_slug(spec.chapter_id, field="chapter_id"),
        *validate_output_dir(spec.output_dir),
    ]
    for index, category in enumerate(spec.data.categories):
        if not category.strip():
            issues.append(SpecIssue(f"data.categories[{index}]", "must be non-empty"))
    category_count = len(spec.data.categories)
    for series_index, series in enumerate(spec.data.series):
        if len(series.values) != category_count:
            issues.append(
                SpecIssue(
                    f"data.series[{series_index}].values",
                    f"must contain {category_count} values to match data.categories",
                )
            )
        for value_index, value in enumerate(series.values):
            issues.extend(
                _validate_numeric_value(
                    value,
                    path=f"data.series[{series_index}].values[{value_index}]",
                )
            )
    if not spec.source.locator.table:
        issues.append(SpecIssue("source.locator.table", "must identify the source table"))
    if not spec.source.locator.rows:
        issues.append(SpecIssue("source.locator.rows", "must identify at least one source row"))
    return issues


def _validate_numeric_value(value: object, *, path: str) -> list[SpecIssue]:
    if value is None:
        return [SpecIssue(path, "must not be null")]
    if isinstance(value, bool):
        return [SpecIssue(path, "must be numeric; booleans are not allowed")]
    if not isinstance(value, int | float):
        return [SpecIssue(path, "must be numeric")]
    if not math.isfinite(float(value)):
        return [SpecIssue(path, "must be finite (not NaN or infinity)")]
    return []


def _issues_from_pydantic(exc: PydanticValidationError) -> list[SpecIssue]:
    return [
        SpecIssue(_format_loc(error["loc"]), str(error["msg"]))
        for error in exc.errors(include_url=False)
    ]


def _format_loc(loc: tuple[Any, ...]) -> str:
    parts: list[str] = []
    for item in loc:
        if isinstance(item, int):
            if not parts:
                parts.append(f"[{item}]")
            else:
                parts[-1] = f"{parts[-1]}[{item}]"
            continue
        parts.append(str(item))
    return ".".join(parts) if parts else "root"
