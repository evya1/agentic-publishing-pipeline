"""Strict project Markdown block renderer for narrative-only chapter files."""

from __future__ import annotations

import re

from .hebrew import render_paragraph
from .inline import render_inline

_HEADING_RE = re.compile(r"^(?P<marks>#{1,4})\s+(?P<title>.+)$")
_UL_RE = re.compile(r"^[-*]\s+(?P<body>.+)$")
_OL_RE = re.compile(r"^\d+[.)]\s+(?P<body>.+)$")
_COMMENT_RE = re.compile(r"^<!--.*-->$")


class UnsupportedMarkdownError(ValueError):
    """Raised with source and line for unsupported Markdown syntax."""


def render_markdown(
    markdown: str,
    *,
    source_name: str,
    allowed_citations: set[str],
) -> str:
    lines = markdown.splitlines()
    output: list[str] = []
    paragraph: list[str] = []
    list_kind: str | None = None
    saw_h1 = False

    def flush_paragraph() -> None:
        if paragraph:
            text = " ".join(paragraph)
            output.extend((render_paragraph(text, allowed_citations=allowed_citations), ""))
            paragraph.clear()

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            output.extend((f"\\end{{{list_kind}}}", ""))
            list_kind = None

    for number, raw in enumerate(lines, start=1):
        line = raw.rstrip()
        if not line.strip():
            flush_paragraph()
            close_list()
            continue
        if _COMMENT_RE.fullmatch(line.strip()):
            raise UnsupportedMarkdownError(
                f"{source_name}:{number}: unresolved semantic placeholder/comment"
            )
        heading = _HEADING_RE.match(line)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group("marks"))
            if level == 1 and saw_h1:
                raise UnsupportedMarkdownError(f"{source_name}:{number}: multiple H1 headings")
            saw_h1 |= level == 1
            command = {1: "chapter", 2: "section", 3: "subsection", 4: "subsubsection"}[level]
            title = render_inline(heading.group("title"), allowed_citations=allowed_citations)
            output.extend((f"\\{command}{{{title}}}", ""))
            continue
        match = _UL_RE.match(line) or _OL_RE.match(line)
        if match:
            flush_paragraph()
            target = "itemize" if _UL_RE.match(line) else "enumerate"
            if list_kind != target:
                close_list()
                output.append(f"\\begin{{{target}}}")
                list_kind = target
            body = render_inline(match.group("body"), allowed_citations=allowed_citations)
            output.append("\\item " + body)
            continue
        if line.startswith((">", "```", "    ", "|")) or "](" in line:
            raise UnsupportedMarkdownError(
                f"{source_name}:{number}: unsupported Markdown construct"
            )
        paragraph.append(line.strip())
    flush_paragraph()
    close_list()
    if not saw_h1:
        raise UnsupportedMarkdownError(f"{source_name}: missing H1 chapter heading")
    return "\n".join(output).rstrip() + "\n"
