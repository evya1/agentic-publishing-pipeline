"""Citation, bibliography, and locked-source rules for manuscript preflight."""

from __future__ import annotations

from ..contracts import BibliographyBundle
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
    bad_resolutions = sorted(set(bibliography.placeholder_resolution.values()) - allowed)
    if bad_resolutions:
        errors.append(f"citation resolutions outside locked manifest: {bad_resolutions}")


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
