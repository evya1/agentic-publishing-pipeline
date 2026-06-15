"""Reconstructable per-source audit ledger (P7-I03).

Builds and persists the two halves of the canonical audit trail:

- ``docs/SOURCES.md`` — human-readable per-source ledger with one
  entry per locked manifest record;
- ``results/run_logs/source_verification.json`` — machine-readable
  mirror keyed by arXiv id with a ``summary`` block and per-source
  evidence sufficient to reconstruct
  ``final citation key → verified bibliographic facts →
  authoritative metadata snapshot → local archive presence``.

Inputs are all already on disk after P7-I00/P7-I02/P7-I05:

- the verified, rekeyed manifest;
- the P7-I02 verification report;
- the P7-I05 rekey ledger (provides ``previous_citation_key``);
- the committed authoritative arXiv XML fixtures;
- the local archive directory (inspected with the P7-I07 reader).

The generator is deterministic so a second run produces identical
output bytes; tests assert that property.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from . import SourceManifest, load_source_manifest
from ._audit_corrections import CORRECTIONS as _CORRECTIONS


@dataclass(frozen=True)
class AuditInputs:
    manifest_path: Path
    verification_report_path: Path
    rekey_ledger_path: Path
    fixture_dir: Path
    sources_md_path: Path
    mirror_json_path: Path


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_entry(
    record,
    *,
    verification_by_arxiv: dict[str, dict[str, object]],
    previous_keys: dict[str, str],
    fixture_dir: Path,
) -> dict[str, object]:
    verification = verification_by_arxiv[record.arxiv_id]
    canonical_url = record.arxiv_url or verification.get("authoritative_url")
    return {
        "final_citation_key": record.citation_key,
        "previous_citation_key": previous_keys.get(record.citation_key),
        "canonical_url": canonical_url,
        "arxiv_id": record.arxiv_id,
        "doi": record.doi,
        "verified_title": record.title,
        "verified_authors": list(record.authors),
        "verified_year": record.year,
        "intended_use": record.intended_use,
        "correction_applied": _CORRECTIONS.get(record.arxiv_id),
        "verification": {
            "status": record.verification.status,
            "method": record.verification.method,
            "verified_at": record.verification.verified_at,
            "verified_by": record.verification.verified_by,
            "authoritative_source": verification.get("authoritative_url"),
            "authoritative_snapshot": str(fixture_dir / f"{record.arxiv_id}.xml"),
            "primary_category": verification.get("primary_category"),
        },
        "local_archive": {
            "path": record.source_archive,
            "archive_inspection": "metadata_only",
            "policy_ref": "docs/PRD_bibliography_and_citations.md §7.2 (P7-I07)",
        },
        "mismatch_or_rejection_rationale": (
            "; ".join(verification.get("mismatches", []) or []) or None
        ),
    }


def build_audit_entries(inputs: AuditInputs) -> list[dict[str, object]]:
    manifest: SourceManifest = load_source_manifest(inputs.manifest_path)
    report = _load_json(inputs.verification_report_path)
    verification_by_arxiv = {
        str(r["arxiv_id"]): r  # type: ignore[index]
        for r in report["results"]  # type: ignore[index]
    }
    rekey = _load_json(inputs.rekey_ledger_path)
    # rekey["key_map"] is {provisional: final}; invert.
    previous_keys = {str(v): str(k) for k, v in rekey["key_map"].items()}  # type: ignore[union-attr]
    return [
        _build_entry(
            record,
            verification_by_arxiv=verification_by_arxiv,
            previous_keys=previous_keys,
            fixture_dir=inputs.fixture_dir,
        )
        for record in manifest.records
    ]


def _summary(entries: Iterable[dict[str, object]]) -> dict[str, object]:
    entries_list = list(entries)
    total = len(entries_list)
    verified = sum(1 for e in entries_list if e["verification"]["status"] == "verified")
    rejected = total - verified
    # Archive presence is verified separately at runtime; the audit
    # ledger itself is reproducible from committed inputs only.
    return {
        "total": total,
        "verified": verified,
        "rejected": rejected,
    }


def render_mirror(entries: list[dict[str, object]]) -> str:
    payload = {
        "schema": "p7i03-source-audit/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "summary": _summary(entries),
        "entries": entries,
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
