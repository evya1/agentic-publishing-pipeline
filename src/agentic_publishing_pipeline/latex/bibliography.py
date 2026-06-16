"""Read verified BibLaTeX keys from the existing canonical bibliography."""

from __future__ import annotations

import re
from pathlib import Path

_ENTRY_RE = re.compile(r"@[A-Za-z]+\s*\{\s*([^,\s]+)\s*,")


class BibliographyError(ValueError):
    """Raised when the existing bibliography cannot be consumed safely."""


def load_bibliography_keys(path: Path) -> tuple[str, ...]:
    if not path.is_file():
        raise BibliographyError(f"verified bibliography missing: {path}")
    keys = [match.group(1).strip() for match in _ENTRY_RE.finditer(path.read_text("utf-8"))]
    if not keys:
        raise BibliographyError(f"bibliography contains no entries: {path}")
    if len(keys) != len(set(keys)):
        raise BibliographyError("bibliography contains duplicate citation keys")
    return tuple(keys)


def copy_bibliography_bytes(path: Path) -> bytes:
    """Return exact Phase 7 bibliography bytes; Phase 9 never rewrites metadata."""
    load_bibliography_keys(path)
    return path.read_bytes()
