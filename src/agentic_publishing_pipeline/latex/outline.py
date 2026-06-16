"""Extract canonical chapter IDs from the approved Phase 6 outline."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

_CHAPTER_ID_RE = re.compile(r"chapter_id:\s*([a-z0-9_-]+)")
_HEADING_RE = re.compile(r"^##\s+(?P<title>.+?)\s*$", re.MULTILINE)
_NON_WORD_RE = re.compile(r"[^a-z0-9]+")


def load_outline_chapter_ids(path: Path) -> tuple[str, ...]:
    """Support both explicit IDs and Phase 6 generated H2 chapter headings."""
    if not path.is_file():
        raise ValueError(f"outline missing: {path}")
    text = path.read_text(encoding="utf-8")
    explicit = tuple(_CHAPTER_ID_RE.findall(text))
    values = explicit or tuple(_slug(match) for match in _HEADING_RE.findall(text))
    values = tuple(value for value in values if value)
    if not values:
        raise ValueError(f"outline contains no chapter declarations: {path}")
    if len(values) != len(set(values)):
        raise ValueError("outline contains duplicate chapter IDs")
    return values


def _slug(title: str) -> str:
    normalized = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    return _NON_WORD_RE.sub("_", normalized.lower()).strip("_")
