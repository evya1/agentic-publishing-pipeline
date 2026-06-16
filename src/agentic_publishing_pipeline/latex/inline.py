"""Restricted inline Markdown renderer with verified citations."""

from __future__ import annotations

import re

from ..tools.markdown import escape_latex

_TOKEN_RE = re.compile(r"(`[^`]+`|\\cite\{[^}]+\}|\*\*[^*]+\*\*|\*[^*]+\*)")
_CITE_RE = re.compile(r"^\\cite\{(?P<keys>[^}]+)\}$")


def render_inline(text: str, *, allowed_citations: set[str]) -> str:
    parts: list[str] = []
    cursor = 0
    for match in _TOKEN_RE.finditer(text):
        parts.append(escape_latex(text[cursor : match.start()]))
        parts.append(_render_token(match.group(0), allowed_citations))
        cursor = match.end()
    parts.append(escape_latex(text[cursor:]))
    return "".join(parts)


def _render_token(token: str, allowed: set[str]) -> str:
    cite = _CITE_RE.match(token)
    if cite:
        keys = [value.strip() for value in cite.group("keys").split(",")]
        if unknown := [value for value in keys if value not in allowed]:
            raise ValueError(f"unknown citation keys: {unknown}")
        return "\\cite{" + ",".join(keys) + "}"
    if token.startswith("`"):
        return "\\texttt{" + escape_latex(token[1:-1]) + "}"
    if token.startswith("**"):
        return "\\textbf{" + escape_latex(token[2:-2]) + "}"
    if token.startswith("*"):
        return "\\emph{" + escape_latex(token[1:-1]) + "}"
    raise ValueError(f"unsupported inline token: {token}")
