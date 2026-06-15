"""Apply the P7-I02 verification result to ``config/article_sources.yaml``.

The Phase 7 verification policy treats the locked manifest's
placeholder ``title``, ``year``, and empty ``authors`` fields as
pending values. P7-I02 retrieves authoritative metadata from arXiv,
P7-I02 records evidence in ``docs/SOURCES.md`` (handled by P7-I03),
and this entrypoint writes the authoritative values back into the
manifest while preserving the manifest's header comments verbatim.

The script is deterministic: re-running it after a verified run is a
no-op (it will diff cleanly).
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import yaml

from . import load_source_manifest
from ._arxiv_parse import to_surname_given

_VERIFIER_ID_DEFAULT = "claude-opus-4.7+arxiv-api"


def _split_header(text: str) -> tuple[str, str]:
    """Return the leading comment block (preserved verbatim) and the rest."""

    sentinel = "\nsources:\n"
    idx = text.find(sentinel)
    if idx < 0:
        raise RuntimeError("manifest missing 'sources:' block")
    return text[: idx + 1], text[idx + 1 :]


def _index_results(report: dict[str, object]) -> dict[str, dict[str, object]]:
    out: dict[str, dict[str, object]] = {}
    for entry in report["results"]:  # type: ignore[assignment]
        out[str(entry["citation_key"])] = entry  # type: ignore[index]
    return out


def _apply(
    manifest_text: str,
    results: dict[str, dict[str, object]],
    *,
    verified_at: str,
    verified_by: str,
) -> str:
    header, sources_block = _split_header(manifest_text)
    data = yaml.safe_load(sources_block)
    assert isinstance(data, dict) and "sources" in data, "manifest layout unexpected"
    for record in data["sources"]:
        key = record["citation_key"]
        result = results.get(key)
        assert result is not None, f"verification result missing for {key!r}"
        # The arxiv_id is the canonical identity; preserve it.
        record["title"] = result["arxiv_title"]
        record["year"] = result["arxiv_year"]
        record["authors"] = [to_surname_given(a) for a in result["arxiv_authors"]]
        if result.get("arxiv_doi"):
            record["doi"] = result["arxiv_doi"]
        record["verification"] = {
            "status": "verified",
            "method": "arxiv_api",
            "verified_at": verified_at,
            "verified_by": verified_by,
        }
    serialized = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000)
    return header + serialized


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("config/article_sources.yaml"))
    parser.add_argument(
        "--report", type=Path, default=Path("results/run_logs/p7i02_verification.json")
    )
    parser.add_argument("--verifier-id", default=_VERIFIER_ID_DEFAULT)
    parser.add_argument("--github-account", default="evya1")
    parser.add_argument("--check", action="store_true", help="Compare only; do not write.")
    args = parser.parse_args(argv)

    text = args.manifest.read_text(encoding="utf-8")
    report = json.loads(args.report.read_text(encoding="utf-8"))
    results = _index_results(report)
    rejected = [key for key, r in results.items() if r["status"] != "verified"]
    if rejected:
        raise RuntimeError(
            f"verification report has {len(rejected)} non-verified entries "
            f"({sorted(rejected)}); resolve manually before applying"
        )
    verified_at = datetime.now(UTC).isoformat()
    verified_by = f"{args.verifier_id}:{args.github_account}"
    updated = _apply(text, results, verified_at=verified_at, verified_by=verified_by)
    if args.check:
        if updated == text:
            print("manifest already aligned with verification report")
            return 0
        print("manifest differs from verification report")
        return 1
    args.manifest.write_text(updated, encoding="utf-8")
    # Smoke-test: the rewritten manifest must reload through the typed loader.
    manifest = load_source_manifest(args.manifest)
    for record in manifest.records:
        assert record.verification.status == "verified", record.citation_key
    print(f"manifest updated: {len(manifest)} verified entries")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
