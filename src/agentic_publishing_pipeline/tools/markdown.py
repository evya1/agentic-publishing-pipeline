"""Markdown conversion tool — placeholder parsing and LaTeX escaping.

Phase 5 ships the deterministic foundation the Phase 9 LaTeX
assembly will consume: a small, side-effect-free parser that pulls
``<!-- FIGURE: ... -->`` style placeholders out of Markdown plus a
LaTeX-escape helper that the renderer uses on user-authored strings.

The agent never writes raw LaTeX; this module is the single seam
where Markdown semantic content is normalized to LaTeX-safe text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..contracts import Placeholder, PlaceholderKind

_PLACEHOLDER_RE = re.compile(
    r"<!--\s*(FIGURE|TABLE|EQUATION|CITATION)\s*:\s*(?P<desc>[^>]+?)\s*-->",
    re.IGNORECASE,
)

_LATEX_ESCAPES: dict[str, str] = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


@dataclass(frozen=True)
class ParsedPlaceholder:
    """Lightweight view of a placeholder discovered inside Markdown."""

    kind: PlaceholderKind
    description: str
    index_in_chapter: int


def parse_placeholders(
    markdown: str,
    *,
    chapter_id: str,
) -> list[Placeholder]:
    """Return :class:`Placeholder` records for every placeholder match."""

    assert chapter_id, "chapter_id must be non-empty"
    placeholders: list[Placeholder] = []
    for index, match in enumerate(_PLACEHOLDER_RE.finditer(markdown)):
        kind: PlaceholderKind = match.group(1).upper()  # type: ignore[assignment]
        description = match.group("desc").strip()
        slot = f"{chapter_id}/{kind.lower()}-{index + 1}"
        placeholders.append(
            Placeholder(kind=kind, slot=slot, chapter_id=chapter_id, description=description),
        )
    return placeholders


def escape_latex(text: str) -> str:
    """Escape LaTeX-special characters in ``text``."""

    pieces: list[str] = []
    for ch in text:
        pieces.append(_LATEX_ESCAPES.get(ch, ch))
    return "".join(pieces)


def strip_placeholders(markdown: str) -> str:
    """Return ``markdown`` with placeholder comments removed."""

    return _PLACEHOLDER_RE.sub("", markdown).strip() + "\n"


def has_placeholder(markdown: str, *, kind: PlaceholderKind) -> bool:
    """Return ``True`` if at least one placeholder of ``kind`` is present."""

    upper = kind.upper()
    return any(match.group(1).upper() == upper for match in _PLACEHOLDER_RE.finditer(markdown))
