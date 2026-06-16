"""Sandboxed file I/O tool bound to a per-run workspace.

The tool is the only way agents and deterministic services should
write inside a run workspace. It enforces three invariants:

1. **Path safety.** Every write target resolves under the configured
   workspace root via :class:`WorkspacePaths`; traversal raises.
2. **Atomic writes.** Files are written to ``<target>.tmp-fio`` and
   then renamed; partial files never appear on disk.
3. **Write audit.** Every write emits a ``fileio.wrote`` event into
   the run context's event log so the manifest stays explainable.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Literal

from ..runtime import PipelineRunContext

Encoding = Literal["utf-8", "ascii"]


class FileIO:
    """Workspace-scoped file I/O with audit, atomic writes, and path guards."""

    def __init__(self, run_context: PipelineRunContext) -> None:
        self._ctx = run_context

    def resolve(self, relative: str | Path) -> Path:
        return self._ctx.paths.child(relative)

    def relative_path(self, relative: str | Path) -> str:
        target = self.resolve(relative)
        return target.relative_to(self._ctx.paths.root).as_posix()

    def record_event(
        self,
        kind: str,
        payload: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        return self._ctx.events.append(kind, payload)

    def write_text(
        self,
        relative: str | Path,
        content: str,
        *,
        encoding: Encoding = "utf-8",
    ) -> Path:
        target = self.resolve(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".tmp-fio")
        tmp.write_text(content, encoding=encoding)
        tmp.replace(target)
        self._ctx.events.append(
            "fileio.wrote",
            {"path": str(target.relative_to(self._ctx.paths.root)), "encoding": encoding},
        )
        return target

    def write_bytes(self, relative: str | Path, content: bytes) -> Path:
        target = self.resolve(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".tmp-fio")
        tmp.write_bytes(content)
        tmp.replace(target)
        self._ctx.events.append(
            "fileio.wrote",
            {"path": str(target.relative_to(self._ctx.paths.root)), "encoding": "bytes"},
        )
        return target

    def write_json(self, relative: str | Path, payload: object) -> Path:
        return self.write_text(
            relative,
            json.dumps(payload, indent=2, sort_keys=True, default=str),
        )

    def read_text(self, relative: str | Path, *, encoding: Encoding = "utf-8") -> str:
        return self.resolve(relative).read_text(encoding=encoding)

    def read_json(self, relative: str | Path) -> object:
        return json.loads(self.read_text(relative))

    def exists(self, relative: str | Path) -> bool:
        try:
            return self.resolve(relative).exists()
        except Exception:
            return False
