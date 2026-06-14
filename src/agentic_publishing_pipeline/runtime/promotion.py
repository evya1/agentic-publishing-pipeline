"""Explicit promotion from run workspace to canonical roots.

Promotion is the only writer of canonical roots (``latex_project/``,
``results/final.pdf``, ``results/generated_markdown/``). It refuses
to run unless the validation report is PASS and the manifest's
recorded SHA-256 hashes match the on-disk content. Existing canonical
artifacts are never silently overwritten; the caller must pass
``force=True`` and a written ``force_reason`` to overwrite.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from .manifest import sha256_of


class PromotionRefused(RuntimeError):
    """Raised when the promotion preconditions are not met."""


def _verify_pass(validation_report_path: Path) -> None:
    if not validation_report_path.exists():
        raise PromotionRefused(f"validation report not found: {validation_report_path}")
    payload = json.loads(validation_report_path.read_text(encoding="utf-8"))
    result = payload.get("result")
    if result != "pass":
        raise PromotionRefused(f"validation report result is {result!r}; promotion refused")


def _atomic_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp-promote")
    shutil.copy2(source, tmp)
    tmp.replace(target)


def promote(
    *,
    workspace_root: Path,
    canonical_root: Path,
    manifest_path: Path,
    validation_report_path: Path,
    pairs: list[tuple[str, str]],
    force: bool = False,
    force_reason: str | None = None,
) -> dict[str, str]:
    """Promote workspace files to canonical paths.

    ``pairs`` is a list of ``(workspace_relative, canonical_relative)``.
    Returns a mapping ``canonical_relative -> sha256``.
    """

    assert workspace_root.is_absolute(), "workspace_root must be absolute"
    assert canonical_root.is_absolute(), "canonical_root must be absolute"
    if force and not force_reason:
        raise PromotionRefused("force=True requires a non-empty force_reason")
    _verify_pass(validation_report_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    recorded_hashes: dict[str, str] = {a["path"]: a["sha256"] for a in manifest["artifacts"]}
    promoted: dict[str, str] = {}
    for workspace_rel, canonical_rel in pairs:
        source = (workspace_root / workspace_rel).resolve()
        source.relative_to(workspace_root.resolve())
        if not source.exists():
            raise PromotionRefused(f"missing workspace source: {workspace_rel}")
        if workspace_rel in recorded_hashes:
            actual = sha256_of(source)
            if actual != recorded_hashes[workspace_rel]:
                raise PromotionRefused(
                    f"manifest hash mismatch for {workspace_rel}: "
                    f"{actual} != {recorded_hashes[workspace_rel]}"
                )
        target = (canonical_root / canonical_rel).resolve()
        target.relative_to(canonical_root.resolve())
        if target.exists() and not force:
            raise PromotionRefused(
                f"canonical artifact already exists: {canonical_rel}; "
                "pass force=True with a force_reason to overwrite"
            )
        _atomic_copy(source, target)
        promoted[canonical_rel] = sha256_of(target)
    return promoted
