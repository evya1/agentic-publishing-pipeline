"""Typed visualization specifications for canonical graph rendering."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MetricSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    unit: str = Field(min_length=1)
    direction: Literal["higher_is_better", "lower_is_better"]


class BarSeriesSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1)
    values: list[object] = Field(min_length=1)


class GraphDataSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    categories: list[str] = Field(min_length=1)
    series: list[BarSeriesSpec] = Field(min_length=1)


class SourceLocator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page: str | None = None
    table: str | None = None
    figure: str | None = None
    rows: list[str] = Field(default_factory=list)


class SourceSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    citation_key: str = Field(min_length=1)
    identifier: str = Field(min_length=1)
    publication_url_or_doi: str = Field(min_length=1)
    locator: SourceLocator
    notes: str = ""


class RenderSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    width_inches: float = Field(gt=0)
    height_inches: float = Field(gt=0)
    dpi: int = Field(gt=0)
    seed: int = 0


class GroupedBarChartSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1]
    asset_id: str = Field(min_length=1, max_length=64)
    kind: Literal["grouped_bar_chart"]
    slot: str = Field(min_length=1, max_length=64)
    chapter_id: str = Field(min_length=1, max_length=64)
    output_dir: str = Field(min_length=1, max_length=128)
    title: str = Field(min_length=1)
    caption: str = Field(min_length=1)
    x_label: str = Field(min_length=1)
    y_label: str = Field(min_length=1)
    metric: MetricSpec
    data: GraphDataSpec
    source: SourceSpec
    transformations: list[str] = Field(default_factory=list)
    render: RenderSpec
