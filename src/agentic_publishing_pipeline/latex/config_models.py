"""Validated configuration models for deterministic Phase 9 assembly."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

AssetKind = Literal["image", "table", "equation", "equation_ref", "theorem", "tikz"]


class MetadataConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    subtitle: str = ""
    authors: list[str] = Field(default_factory=list)
    group_code: str = ""
    course: str = Field(min_length=1)
    date_text: str = Field(min_length=1)


class SourceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    markdown_root: str = "results/generated_markdown"
    review_log_root: str = "results/run_logs"
    bibliography_path: str = "latex_project/references.bib"
    graph_path: str = "latex_project/figures/planning_benchmark_comparison_02e65860.png"
    outline_path: str = "results/generated_markdown/outline.md"


class AssetConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: AssetKind
    asset_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    chapter_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")
    caption: str = ""
    label: str = Field(pattern=r"^[a-z0-9][a-z0-9:_-]*$")
    payload: dict[str, object] = Field(default_factory=dict)


class TermConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    term: str = Field(min_length=1)
    chapter_id: str = Field(pattern=r"^[a-z0-9][a-z0-9_-]*$")


class Phase9Config(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["v1"] = "v1"
    metadata: MetadataConfig
    source: SourceConfig = Field(default_factory=SourceConfig)
    chapter_order: list[str] = Field(min_length=1)
    minimum_hebrew_words: int = Field(default=40, ge=1)
    minimum_words_per_chapter: int = Field(default=400, ge=1)
    minimum_total_words: int = Field(default=5000, ge=1)
    require_all_bibliography_entries: bool = True
    chapter_citation_requirements: dict[str, list[str]] = Field(default_factory=dict)
    macros: list[str] = Field(default_factory=lambda: ["AgentState", "ToolCall"])
    nomenclature: list[tuple[str, str]] = Field(min_length=2)
    english_index: list[TermConfig] = Field(min_length=1)
    hebrew_index: list[TermConfig] = Field(min_length=1)
    assets: list[AssetConfig] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_cross_references(self) -> Phase9Config:
        chapters = set(self.chapter_order)
        referenced = {asset.chapter_id for asset in self.assets}
        referenced |= {item.chapter_id for item in self.english_index + self.hebrew_index}
        referenced |= set(self.chapter_citation_requirements)
        if unknown := sorted(referenced - chapters):
            raise ValueError(f"configuration references unknown chapters: {unknown}")
        asset_ids = [asset.asset_id for asset in self.assets]
        if len(asset_ids) != len(set(asset_ids)):
            raise ValueError("duplicate Phase 9 asset_id")
        kinds = {asset.kind for asset in self.assets}
        required = {"image", "table", "equation", "equation_ref", "theorem", "tikz"}
        if missing := sorted(required - kinds):
            raise ValueError(f"required Phase 9 asset kinds missing: {missing}")
        equation_labels = {asset.label for asset in self.assets if asset.kind == "equation"}
        reference_targets = {
            str(asset.payload.get("target", "")).strip()
            for asset in self.assets
            if asset.kind == "equation_ref"
        }
        if missing_targets := sorted(reference_targets - equation_labels):
            raise ValueError(f"equation_ref targets missing equation labels: {missing_targets}")
        return self
