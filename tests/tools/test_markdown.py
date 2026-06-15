"""Markdown placeholder / LaTeX escape tests."""

from __future__ import annotations

import pytest

from agentic_publishing_pipeline.tools import (
    escape_latex,
    has_placeholder,
    parse_placeholders,
    strip_placeholders,
)


def test_parse_placeholders_finds_all_kinds() -> None:
    md = (
        "# Heading\n"
        "Some text.\n"
        "<!-- FIGURE: planning diagram -->\n"
        "<!-- TABLE: comparison -->\n"
        "<!-- EQUATION: definition -->\n"
        "<!-- CITATION: smith2024memory -->\n"
    )
    placeholders = parse_placeholders(md, chapter_id="intro")
    assert len(placeholders) == 4
    kinds = {p.kind for p in placeholders}
    assert kinds == {"FIGURE", "TABLE", "EQUATION", "CITATION"}
    assert placeholders[0].slot == "intro/figure-1"
    assert placeholders[3].description == "smith2024memory"


def test_parse_placeholders_case_insensitive() -> None:
    md = "<!-- figure: diagram -->"
    placeholders = parse_placeholders(md, chapter_id="x")
    assert placeholders[0].kind == "FIGURE"


def test_parse_placeholders_rejects_empty_chapter_id() -> None:
    with pytest.raises(AssertionError):
        parse_placeholders("x", chapter_id="")


def test_parse_placeholders_returns_empty_when_no_markers() -> None:
    assert parse_placeholders("Just text.\n", chapter_id="x") == []


def test_escape_latex_basic_specials() -> None:
    assert escape_latex("a & b") == r"a \& b"
    assert escape_latex("$x$") == r"\$x\$"
    assert escape_latex("a_b") == r"a\_b"
    assert escape_latex("{x}") == r"\{x\}"


def test_escape_latex_idempotent_on_safe_text() -> None:
    assert escape_latex("hello world") == "hello world"


def test_strip_placeholders_removes_comments() -> None:
    md = "Some text.\n<!-- FIGURE: x -->\nMore text.\n"
    stripped = strip_placeholders(md)
    assert "FIGURE" not in stripped
    assert "Some text." in stripped
    assert stripped.endswith("\n")


def test_has_placeholder_returns_true_when_present() -> None:
    md = "<!-- TABLE: x -->"
    assert has_placeholder(md, kind="TABLE") is True
    assert has_placeholder(md, kind="FIGURE") is False
