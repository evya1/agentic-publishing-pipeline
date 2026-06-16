"""Citation, bibliography, and locked-source rules for manuscript preflight."""

from __future__ import annotations

from ..contracts import BibliographyBundle
from ..contracts._common import Placeholder
from ..services.source_context import SourceContext


def check_citation_set(
    cited: set[str],
    manifest_keys: tuple[str, ...],
    errors: list[str],
) -> tuple[str, ...]:
    allowed = set(manifest_keys)
    unknown = sorted(cited - allowed)
    if unknown:
        errors.append(f"unknown citation keys: {unknown}")
    missing = tuple(sorted(allowed - cited))
    if missing:
        errors.append(f"locked sources not cited: {list(missing)}")
    return missing


def check_bibliography(
    cited: set[str],
    manifest_keys: tuple[str, ...],
    bibliography: BibliographyBundle,
    placeholders: list[Placeholder],
    errors: list[str],
) -> None:
    allowed = set(manifest_keys)
    entry_keys = [entry.citation_key for entry in bibliography.entries]
    duplicate_entries = sorted({key for key in entry_keys if entry_keys.count(key) > 1})
    if duplicate_entries:
        errors.append(f"duplicate bibliography entries: {duplicate_entries}")
    unknown_entries = sorted(set(entry_keys) - allowed)
    if unknown_entries:
        errors.append(f"bibliography entries outside locked manifest: {unknown_entries}")
    unverified = [
        entry.citation_key
        for entry in bibliography.entries
        if entry.verification_status != "verified"
    ]
    if unverified:
        errors.append(f"bibliography entries not verified: {sorted(unverified)}")
    missing_entries = sorted(cited - set(entry_keys))
    if missing_entries:
        errors.append(f"cited keys missing bibliography entries: {missing_entries}")
    coverage = set(bibliography.manifest_coverage)
    if coverage != allowed:
        errors.append(
            "bibliography manifest coverage mismatch: "
            f"missing={sorted(allowed - coverage)} extra={sorted(coverage - allowed)}"
        )
    _check_placeholder_resolution(
        bibliography=bibliography,
        placeholders=placeholders,
        allowed=allowed,
        errors=errors,
    )


def _check_placeholder_resolution(
    *,
    bibliography: BibliographyBundle,
    placeholders: list[Placeholder],
    allowed: set[str],
    errors: list[str],
) -> None:
    slot_to_keys: dict[str, set[str]] = {}
    for ph in placeholders:
        if ph.kind != "CITATION":
            continue
        keys = {key.strip() for key in ph.description.split(",") if key.strip()}
        if not keys:
            errors.append(f"malformed citation placeholder {ph.slot}: no citation keys")
            continue
        slot_to_keys[ph.slot] = keys
    expected_slots = set(slot_to_keys)
    resolution = dict(bibliography.placeholder_resolution)
    resolution_slots = set(resolution)
    missing_slots = sorted(expected_slots - resolution_slots)
    extra_slots = sorted(resolution_slots - expected_slots)
    if missing_slots:
        errors.append(f"placeholder_resolution missing citation slots: {missing_slots}")
    if extra_slots:
        errors.append(f"placeholder_resolution has unknown slots: {extra_slots}")
    for slot, mapped in resolution.items():
        if slot not in slot_to_keys:
            continue
        if mapped not in allowed:
            errors.append(
                f"placeholder_resolution[{slot!r}] maps to unknown key {mapped!r}"
            )
            continue
        if mapped not in slot_to_keys[slot]:
            declared = sorted(slot_to_keys[slot])
            errors.append(
                f"placeholder_resolution[{slot!r}]={mapped!r} not in declared keys {declared}"
            )


def check_source_provenance(
    manifest_keys: tuple[str, ...],
    bibliography: BibliographyBundle | None,
    source_context: SourceContext,
    errors: list[str],
) -> None:
    locked = {record.citation_key: record for record in source_context.records}
    if set(manifest_keys) != set(locked):
        errors.append("manifest keys differ from locked source context")
    if bibliography is None:
        return
    for entry in bibliography.entries:
        source = locked.get(entry.citation_key)
        if source is None:
            continue
        if entry.title != source.title:
            errors.append(f"bibliography title drift for {entry.citation_key}")
        if str(entry.year) != source.year:
            errors.append(f"bibliography year drift for {entry.citation_key}")
        if source.arxiv_id and entry.arxiv_id != source.arxiv_id:
            errors.append(f"bibliography arXiv drift for {entry.citation_key}")
        if source.doi and entry.doi != source.doi:
            errors.append(f"bibliography DOI drift for {entry.citation_key}")
