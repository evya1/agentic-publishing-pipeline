"""Load Phase 9 configuration without allowing path traversal."""

from __future__ import annotations

from pathlib import Path, PurePosixPath

import yaml

from .config_models import Phase9Config


class Phase9ConfigError(ValueError):
    """Raised when the Phase 9 configuration is absent or unsafe."""


def load_phase9_config(path: Path) -> Phase9Config:
    if not path.is_file():
        raise Phase9ConfigError(f"Phase 9 configuration missing: {path}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise Phase9ConfigError("Phase 9 configuration must be a YAML mapping")
    config = Phase9Config.model_validate(raw)
    for value in (
        config.source.markdown_root,
        config.source.review_log_root,
        config.source.bibliography_path,
        config.source.graph_path,
        config.source.outline_path,
    ):
        _validate_relative(value)
    return config


def resolve_repo_path(repo_root: Path, relative: str) -> Path:
    """Resolve one validated repository-relative path."""
    _validate_relative(relative)
    root = repo_root.resolve()
    candidate = (root / relative).resolve()
    candidate.relative_to(root)
    return candidate


def _validate_relative(value: str) -> None:
    path = PurePosixPath(value)
    if path.is_absolute() or not value.strip() or ".." in path.parts:
        raise Phase9ConfigError(f"unsafe repository-relative path: {value!r}")
