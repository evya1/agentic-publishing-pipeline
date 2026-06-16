"""Render Hebrew prose while preserving embedded LTR technical runs."""

from __future__ import annotations

import re

from ..tools.markdown import escape_latex

_HEBREW_RE = re.compile(r"[\u0590-\u05FF]")
_LTR_RUN = re.compile(r"[A-Za-z0-9]+(?:[./+:#_-][A-Za-z0-9]+)*")


def contains_hebrew(text: str) -> bool:
    return bool(_HEBREW_RE.search(text))


def render_hebrew_text(text: str) -> str:
    """Escape prose, then wrap Latin/digit compounds in Polyglossia LTR runs."""
    escaped = escape_latex(text)
    return _LTR_RUN.sub(lambda match: f"\\textenglish{{{match.group(0)}}}", escaped)


def render_paragraph(text: str, *, allowed_citations: set[str]) -> str:
    """Render one paragraph; citations are handled before Hebrew wrapping."""
    from .inline import render_inline

    if not contains_hebrew(text):
        return render_inline(text, allowed_citations=allowed_citations)
    pieces: list[str] = []
    cursor = 0
    cite_re = re.compile(r"\\cite\{[^}]+\}")
    for match in cite_re.finditer(text):
        pieces.append(render_hebrew_text(text[cursor : match.start()]))
        pieces.append(render_inline(match.group(0), allowed_citations=allowed_citations))
        cursor = match.end()
    pieces.append(render_hebrew_text(text[cursor:]))
    return "\\begin{hebrew}\n\\raggedleft\n" + "".join(pieces) + "\n\\end{hebrew}"
