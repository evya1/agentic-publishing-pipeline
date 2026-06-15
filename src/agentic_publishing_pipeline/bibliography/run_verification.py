"""Orchestrate Phase 7 verification across the locked source manifest.

Run via ``uv run python -m agentic_publishing_pipeline.bibliography.run_verification``.

Behaviour:

1. Load ``config/article_sources.yaml`` as a typed manifest.
2. For every arXiv-bearing record, fetch its authoritative Atom feed
   (live, polite delay), persist the raw XML as a committed test
   fixture, and parse it.
3. Run :func:`verify_record` against the parsed metadata.
4. Persist a machine-readable per-source result table to the run
   logs directory; print a concise summary.

The script does **not** rewrite ``config/article_sources.yaml`` in
place; the manifest update and audit-ledger fill-in are committed
separately so the diff is reviewable.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from . import (
    SourceManifest,
    load_source_manifest,
)
from ._arxiv_fetch import fetch_arxiv_metadata
from ._arxiv_parse import parse_arxiv_feed
from .verify import VerificationResult, verify_record


def _save_fixture(fixture_dir: Path, arxiv_id: str, body: bytes) -> Path:
    fixture_dir.mkdir(parents=True, exist_ok=True)
    target = fixture_dir / f"{arxiv_id}.xml"
    target.write_bytes(body)
    return target


def _verify_manifest(
    manifest: SourceManifest, fixture_dir: Path, *, polite_delay_s: float
) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for record in manifest.records:
        if record.arxiv_id is None:
            continue
        response = fetch_arxiv_metadata(record.arxiv_id, polite_delay_s=polite_delay_s)
        _save_fixture(fixture_dir, record.arxiv_id, response.body)
        metadata = parse_arxiv_feed(response.body, expected_id=record.arxiv_id)
        outcome: VerificationResult = verify_record(record, metadata)
        results.append(
            {
                "citation_key": outcome.citation_key,
                "arxiv_id": outcome.arxiv_id,
                "status": outcome.status,
                "title_match": outcome.title_match,
                "year_match": outcome.year_match,
                "arxiv_id_match": outcome.arxiv_id_match,
                "populated_authors": list(outcome.populated_authors),
                "mismatches": list(outcome.mismatches),
                "authoritative_url": response.url,
                "arxiv_title": metadata.title,
                "arxiv_year": metadata.published_year,
                "arxiv_authors": list(metadata.authors),
                "arxiv_doi": metadata.doi,
                "primary_category": metadata.primary_category,
            }
        )
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("config/article_sources.yaml"))
    parser.add_argument(
        "--fixture-dir",
        type=Path,
        default=Path("tests/fixtures/arxiv"),
        help="Where to persist the authoritative XML responses.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("results/run_logs/p7i02_verification.json"),
    )
    parser.add_argument("--polite-delay-s", type=float, default=3.0)
    args = parser.parse_args(argv)

    manifest = load_source_manifest(args.manifest)
    started_at = datetime.now(UTC).isoformat()
    results = _verify_manifest(
        manifest, args.fixture_dir, polite_delay_s=args.polite_delay_s
    )
    finished_at = datetime.now(UTC).isoformat()
    report = {
        "schema": "p7i02-verification-run/v1",
        "started_at": started_at,
        "finished_at": finished_at,
        "manifest_path": str(args.manifest),
        "fixture_dir": str(args.fixture_dir),
        "results": results,
        "summary": {
            "total": len(results),
            "verified": sum(1 for r in results if r["status"] == "verified"),
            "rejected": sum(1 for r in results if r["status"] == "rejected"),
        },
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
