"""LaTeXProjectSpec v1 — contract for edge E7 (LaTeX Agent → Renderer).

The spec is **semantic-only**: no raw LaTeX strings, no file paths
authored by the LLM. The deterministic renderer (ADR-0003) translates
this spec into ``.tex`` files. Agents never write a file path.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ._envelope import ContractEnvelope


class PreambleSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    engine: Literal["lualatex"] = "lualatex"
    main_font_english: str = "Latin Modern Roman"
    hebrew_font: str = "David CLM"
    packages: list[str] = Field(default_factory=list)


class MacroSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    body: str = Field(min_length=1)


class ChapterSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chapter_id: str = Field(min_length=1)
    file_stem: str = Field(min_length=1)


class TableRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file_stem: str = Field(min_length=1)
    chapter_id: str = Field(min_length=1)


class FigureRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file_stem: str = Field(min_length=1)
    chapter_id: str = Field(min_length=1)
    kind: Literal["tikz", "includegraphics"] = "includegraphics"


class NomenclatureSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    symbols: list[tuple[str, str]] = Field(min_length=2)


class IndexSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hebrew_terms: list[str] = Field(min_length=1)
    english_terms: list[str] = Field(min_length=1)


class LaTeXProjectSpec(ContractEnvelope):
    """Semantic instructions for the deterministic LaTeX renderer."""

    preamble: PreambleSpec = Field(default_factory=PreambleSpec)
    macros: list[MacroSpec] = Field(default_factory=list)
    chapters: list[ChapterSpec] = Field(min_length=1)
    tables: list[TableRef] = Field(default_factory=list)
    figures: list[FigureRef] = Field(default_factory=list)
    references_bib_file_stem: str = "references"
    nomenclature: NomenclatureSpec
    index_entries: IndexSpec
