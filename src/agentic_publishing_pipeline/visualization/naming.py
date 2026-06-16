"""Deterministic naming and path validation for visualization artifacts."""

from __future__ import annotations

import re
from pathlib import PurePosixPath

from .errors import SpecIssue
from .models import GroupedBarChartSpec

_SLUG_RE = re.compile(r"^[a-z0-9_-]+$")
_MAX_COMPONENT_LENGTH = 64


def validate_slug(value: str, *, field: str) -> list[SpecIssue]:
    issues: list[SpecIssue] = []
    if not value:
        return [SpecIssue(field, "must be non-empty")]
    if not _SLUG_RE.fullmatch(value):
        issues.append(
            SpecIssue(field, "must use lowercase ASCII letters, digits, '_' or '-' only")
        )
    if value.startswith("."):
        issues.append(SpecIssue(field, "must not start with '.'"))
    if len(value) > _MAX_COMPONENT_LENGTH:
        issues.append(SpecIssue(field, f"must be <= {_MAX_COMPONENT_LENGTH} characters"))
    return issues


def validate_output_dir(value: str) -> list[SpecIssue]:
    issues: list[SpecIssue] = []
    if "\\" in value:
        issues.append(SpecIssue("output_dir", "must use forward slashes only"))
    path = PurePosixPath(value)
    if path.is_absolute():
        issues.append(SpecIssue("output_dir", "must be relative, not absolute"))
    if ".." in path.parts:
        issues.append(SpecIssue("output_dir", "must not contain '..'"))
    if any(part.startswith(".") for part in path.parts):
        issues.append(SpecIssue("output_dir", "must not contain hidden path segments"))
    for index, part in enumerate(path.parts):
        if part in {"", "."}:
            issues.append(SpecIssue(f"output_dir[{index}]", "must not contain empty path segments"))
            continue
        if len(part) > _MAX_COMPONENT_LENGTH:
            issues.append(
                SpecIssue(f"output_dir[{index}]", f"must be <= {_MAX_COMPONENT_LENGTH} characters")
            )
        if not _SLUG_RE.fullmatch(part):
            issues.append(
                SpecIssue(
                    f"output_dir[{index}]",
                    "must use lowercase ASCII letters, digits, '_' or '-' only",
                )
            )
    return issues


def build_output_paths(spec: GroupedBarChartSpec, *, input_sha256: str) -> tuple[str, str]:
    stem = f"{spec.asset_id}_{input_sha256[:8]}"
    png_relative = PurePosixPath(spec.output_dir, f"{stem}.png").as_posix()
    return png_relative, f"{png_relative}.prov.json"
