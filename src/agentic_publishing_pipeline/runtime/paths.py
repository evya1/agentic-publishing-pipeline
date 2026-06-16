"""Safe path resolution for run-scoped writes.

Every workspace write goes through :class:`WorkspacePaths`, which
guards against path-traversal and accidental writes outside the
isolated workspace root. Canonical roots are reachable only via
the explicit promotion path in :mod:`.promotion`.
"""

from __future__ import annotations

from pathlib import Path


class PathSafetyError(ValueError):
    """Raised when a requested write would escape the workspace root."""


class WorkspacePaths:
    """Workspace-relative path resolver with traversal protection."""

    SUBDIRS: tuple[str, ...] = (
        "artifacts",
        "generated_markdown",
        "generated_markdown/chapters",
        "typed_outputs",
        "raw_outputs",
        "logs",
        "raw",
        "latex_project",
        "latex_project/chapters",
        "latex_project/tables",
        "latex_project/figures",
        "build",
        "validation",
    )

    def __init__(self, root: Path) -> None:
        assert root.is_absolute(), "workspace root must be absolute"
        self._root = root.resolve()

    @property
    def root(self) -> Path:
        return self._root

    def ensure_layout(self) -> None:
        self._root.mkdir(parents=True, exist_ok=True)
        for sub in self.SUBDIRS:
            (self._root / sub).mkdir(parents=True, exist_ok=True)

    def child(self, relative: str | Path) -> Path:
        """Resolve a workspace-relative path, refusing traversal."""

        candidate = (self._root / relative).resolve()
        try:
            candidate.relative_to(self._root)
        except ValueError as exc:
            raise PathSafetyError(
                f"Refusing to resolve {relative!r}: escapes workspace root."
            ) from exc
        return candidate
