"""Deterministic metadata and title-page rendering."""

from __future__ import annotations

from ..tools.markdown import escape_latex
from .config_models import MetadataConfig


def render_metadata(config: MetadataConfig) -> str:
    title = _one_line(config.title)
    subtitle = _one_line(config.subtitle)
    authors = " \\and ".join(_one_line(value) for value in config.authors)
    return "\n".join(
        (
            f"\\title{{{title}}}",
            f"\\author{{{authors}}}",
            f"\\date{{{_one_line(config.date_text)}}}",
            f"\\newcommand{{\\BookTitle}}{{{title}}}",
            f"\\newcommand{{\\BookSubtitle}}{{{subtitle}}}",
            f"\\newcommand{{\\CourseName}}{{{_one_line(config.course)}}}",
            f"\\newcommand{{\\GroupCode}}{{{_one_line(config.group_code)}}}",
            f"\\newcommand{{\\DocumentAuthors}}{{{authors}}}",
            f"\\newcommand{{\\DocumentDate}}{{{_one_line(config.date_text)}}}",
            "",
        )
    )


def render_titlepage() -> str:
    return r"""\begin{titlepage}
\centering
\vspace*{2cm}
{\Huge\bfseries \BookTitle\par}
\vspace{0.8cm}
{\Large \BookSubtitle\par}
\vfill
{\large \CourseName\par}
\vspace{0.5cm}
{\large Group: \GroupCode\par}
\vspace{1cm}
{\large \DocumentAuthors\par}
\vfill
{\large \DocumentDate\par}
\end{titlepage}
"""


def _one_line(value: str) -> str:
    return escape_latex(" ".join(value.split()))
