import pytest

from agentic_publishing_pipeline.latex.inline import render_inline
from agentic_publishing_pipeline.latex.markdown_renderer import (
    UnsupportedMarkdownError,
    render_markdown,
)
from agentic_publishing_pipeline.latex.metadata import render_metadata
from agentic_publishing_pipeline.latex.templates import render_main, render_preamble


def test_inline_preserves_verified_citation() -> None:
    rendered = render_inline("See \\cite{known}.", allowed_citations={"known"})
    assert "\\cite{known}" in rendered
    with pytest.raises(ValueError, match="unknown citation"):
        render_inline("See \\cite{missing}.", allowed_citations={"known"})


def test_markdown_renders_hebrew_citation_and_rejects_comments() -> None:
    rendered = render_markdown(
        "# Memory\n\nזיכרון with LLM state \\cite{known}.",
        source_name="memory.md",
        allowed_citations={"known"},
    )
    assert "\\begin{hebrew}" in rendered
    assert "\\raggedleft" in rendered
    assert "\\textenglish{LLM}" in rendered
    assert "\\cite{known}" in rendered
    with pytest.raises(UnsupportedMarkdownError, match="placeholder/comment"):
        render_markdown(
            "# Bad\n\n<!-- FIGURE: unresolved -->",
            source_name="bad.md",
            allowed_citations=set(),
        )


def test_templates_are_phase9_only() -> None:
    preamble = render_preamble()
    main = render_main(["chapters/01_planning"])
    assert "David CLM" in preamble
    assert "\\newfontfamily\\englishfont" in preamble
    assert "cleveref" in preamble
    assert "backend=biber,style=numeric,sorting=none" in preamble
    assert "\\input{chapters/01_planning}" in main
    assert "lualatex" not in main.lower()


def test_metadata_defines_title_page_macros(config) -> None:
    rendered = render_metadata(config.metadata)
    assert "\\newcommand{\\DocumentAuthors}{Ada Example}" in rendered
    assert "\\newcommand{\\DocumentDate}{2026}" in rendered
