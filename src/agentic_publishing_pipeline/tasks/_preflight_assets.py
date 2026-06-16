"""Asset placeholder rules for manuscript preflight."""

from __future__ import annotations

from ..contracts import AssetSpecs
from ..contracts._common import Placeholder, PlaceholderKind

_FIGURE_ASSET_KINDS = {"tikz", "image", "python_graph"}


def check_asset_specs(
    placeholders: list[Placeholder],
    assets: AssetSpecs,
    errors: list[str],
) -> None:
    owned = [ph for ph in placeholders if ph.kind in {"FIGURE", "TABLE", "EQUATION"}]
    owned_by_slot = {ph.slot: ph for ph in owned}
    asset_slots: dict[str, str] = {}
    for asset in assets.assets:
        if asset.slot in asset_slots:
            errors.append(f"duplicate asset slot: {asset.slot}")
        asset_slots[asset.slot] = asset.kind
        placeholder = owned_by_slot.get(asset.slot)
        if placeholder is None:
            errors.append(f"orphan asset slot: {asset.slot}")
            continue
        if placeholder.chapter_id != asset.chapter_id:
            errors.append(f"asset {asset.slot} chapter mismatch")
        if not _asset_matches_placeholder(asset.kind, placeholder.kind):
            errors.append(
                f"asset {asset.slot} kind {asset.kind!r} does not match {placeholder.kind}"
            )
    missing = sorted(set(owned_by_slot) - set(asset_slots))
    if missing:
        errors.append(f"asset specs missing placeholder slots: {missing}")


def _asset_matches_placeholder(asset_kind: str, placeholder_kind: PlaceholderKind) -> bool:
    if placeholder_kind == "FIGURE":
        return asset_kind in _FIGURE_ASSET_KINDS
    return asset_kind == placeholder_kind.lower()
