"""AssetSpecs v1 — contract for edge E4 (Technical Asset → many)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ._envelope import ContractEnvelope

AssetKind = Literal["tikz", "image", "table", "equation", "python_graph"]
TheoremLikeKind = Literal["theorem", "lemma", "definition", "example", "proposition"]


class AssetSpec(BaseModel):
    """A single semantic asset specification linked to a placeholder slot."""

    model_config = ConfigDict(extra="forbid")

    kind: AssetKind
    slot: str = Field(min_length=1)
    chapter_id: str = Field(min_length=1)
    caption: str = ""
    payload: dict[str, object] = Field(default_factory=dict)
    theorem_like_kind: TheoremLikeKind | None = None


class AssetSpecs(ContractEnvelope):
    """Set of asset specs covering every placeholder of kinds the agent owns."""

    assets: list[AssetSpec] = Field(default_factory=list)
