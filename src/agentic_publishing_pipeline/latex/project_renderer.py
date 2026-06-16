"""Assemble approved narrative and deterministic assets into a file plan."""

from __future__ import annotations

from pathlib import Path

from ..tools.markdown import escape_latex
from .approval_loader import ApprovedManuscript
from .asset_plan import build_asset_files
from .bibliography import copy_bibliography_bytes, load_bibliography_keys
from .config_models import Phase9Config
from .file_plan import LaTeXFilePlan, PlannedBinaryFile, PlannedTextFile
from .markdown_renderer import render_markdown
from .metadata import render_metadata, render_titlepage
from .templates import render_macros, render_main, render_nomenclature, render_preamble


def build_project_plan(
    *,
    manuscript: ApprovedManuscript,
    config: Phase9Config,
    bibliography_path: Path,
    graph_path: Path,
) -> LaTeXFilePlan:
    """Create the complete deterministic tree before writing any file."""
    allowed = set(load_bibliography_keys(bibliography_path))
    assets = build_asset_files(config.assets, graph_path=graph_path)
    text_files: list[PlannedTextFile] = _root_files(config)
    chapter_files: list[str] = []
    for index, chapter in enumerate(manuscript.chapters, start=1):
        stem = f"{index:02d}_{chapter.chapter_id}"
        narrative = render_markdown(
            chapter.markdown,
            source_name=chapter.path.as_posix(),
            allowed_citations=allowed,
        )
        includes = list(assets.includes_by_chapter.get(chapter.chapter_id, ()))
        index_text = _index_entries(chapter.chapter_id, config)
        if index_text:
            index_path = f"components/index_{chapter.chapter_id}.tex"
            text_files.append(PlannedTextFile(index_path, index_text))
            includes.append(index_path.removesuffix(".tex"))
        chapter_path = f"chapters/{stem}.tex"
        text_files.append(
            PlannedTextFile(chapter_path, _chapter_content(narrative, tuple(includes)))
        )
        chapter_files.append(chapter_path.removesuffix(".tex"))
    text_files.extend(assets.files)
    text_files.append(PlannedTextFile("main.tex", render_main(chapter_files)))
    return LaTeXFilePlan.build(
        text_files=text_files,
        binary_files=[
            PlannedBinaryFile("references.bib", copy_bibliography_bytes(bibliography_path)),
            PlannedBinaryFile(f"figures/{graph_path.name}", graph_path.read_bytes()),
        ],
    )


def _root_files(config: Phase9Config) -> list[PlannedTextFile]:
    return [
        PlannedTextFile("preamble.tex", render_preamble()),
        PlannedTextFile("macros.tex", render_macros(config.macros)),
        PlannedTextFile("metadata.tex", render_metadata(config.metadata)),
        PlannedTextFile("titlepage.tex", render_titlepage()),
        PlannedTextFile("nomenclature_entries.tex", render_nomenclature(config.nomenclature)),
    ]


def _chapter_content(narrative: str, includes: tuple[str, ...]) -> str:
    lines = [narrative.rstrip(), ""]
    lines.extend(f"\\input{{{value}}}" for value in includes)
    return "\n".join(lines).rstrip() + "\n"


def _index_entries(chapter_id: str, config: Phase9Config) -> str:
    entries: list[str] = []
    for item in config.english_index:
        if item.chapter_id == chapter_id:
            entries.append(f"\\index{{{escape_latex(item.term)}}}")
    for item in config.hebrew_index:
        if item.chapter_id == chapter_id:
            entries.append(f"\\index{{{escape_latex(item.term)}}}")
    return "\n".join(entries) + "\n" if entries else ""
