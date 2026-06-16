"""Build the repository's existing semantic LaTeXProjectSpec contract."""

from __future__ import annotations

from ..contracts import (
    ChapterSpec,
    FigureRef,
    IndexSpec,
    LaTeXProjectSpec,
    MacroSpec,
    NomenclatureSpec,
    PreambleSpec,
    TableRef,
)
from .approval_loader import ApprovedManuscript
from .config_models import Phase9Config
from .templates import semantic_macro_body


def build_project_spec(
    *, run_id: str, manuscript: ApprovedManuscript, config: Phase9Config
) -> LaTeXProjectSpec:
    tables = [
        TableRef(file_stem=asset.asset_id, chapter_id=asset.chapter_id)
        for asset in config.assets
        if asset.kind == "table"
    ]
    figures = [
        FigureRef(
            file_stem=asset.asset_id,
            chapter_id=asset.chapter_id,
            kind="tikz" if asset.kind == "tikz" else "includegraphics",
        )
        for asset in config.assets
        if asset.kind in {"image", "tikz"}
    ]
    return LaTeXProjectSpec(
        run_id=run_id,
        preamble=PreambleSpec(
            engine="lualatex",
            main_font_english="Latin Modern Roman",
            hebrew_font="David CLM",
            packages=[
                "fontspec",
                "polyglossia",
                "graphicx",
                "booktabs",
                "amsmath",
                "tikz",
                "fancyhdr",
                "nomencl",
                "imakeidx",
                "biblatex",
                "hyperref",
                "cleveref",
            ],
        ),
        macros=[MacroSpec(name=name, body=semantic_macro_body(name)) for name in config.macros],
        chapters=[
            ChapterSpec(chapter_id=chapter.chapter_id, file_stem=chapter.chapter_id)
            for chapter in manuscript.chapters
        ],
        tables=tables,
        figures=figures,
        references_bib_file_stem="references",
        nomenclature=NomenclatureSpec(symbols=config.nomenclature),
        index_entries=IndexSpec(
            english_terms=[item.term for item in config.english_index],
            hebrew_terms=[item.term for item in config.hebrew_index],
        ),
    )
