"""Validate citation resolution across the active Markdown tree (P7-I06).

Walks ``results/generated_markdown/**/*.md``, validates every
``<!-- CITATION: key -->`` against the verified manifest, and emits a
coverage report at ``results/run_logs/p7i06_citation_coverage.json``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import load_source_manifest
from .cite import CitationResolutionError, CitationResolver


def _markdown_files(root: Path) -> list[Path]:
    return sorted(
        p
        for p in root.rglob("*.md")
        if p.name != "README.md" and "__pycache__" not in p.parts
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("config/article_sources.yaml"))
    parser.add_argument(
        "--markdown-root",
        type=Path,
        default=Path("results/generated_markdown"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("results/run_logs/p7i06_citation_coverage.json"),
    )
    parser.add_argument("--require-full-coverage", action="store_true")
    args = parser.parse_args(argv)

    manifest = load_source_manifest(args.manifest)
    resolver = CitationResolver(manifest)
    files = _markdown_files(args.markdown_root)
    try:
        coverage = resolver.coverage(files)
    except CitationResolutionError as exc:
        print(f"citation resolution failed: {exc}")
        return 2
    payload = {
        "schema": "p7i06-citation-coverage/v1",
        "markdown_root": str(args.markdown_root),
        "manifest_path": str(args.manifest),
        "files": [str(p) for p in coverage.files],
        "citations_per_file": {
            str(p): n for p, n in coverage.citations_per_file.items()
        },
        "cited_keys": list(coverage.cited_keys),
        "uncited_verified_keys": list(coverage.uncited_verified_keys),
        "summary": {
            "verified_total": len(resolver.verified_keys),
            "cited_unique": len(coverage.cited_keys),
            "uncited_unique": len(coverage.uncited_verified_keys),
        },
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload["summary"], sort_keys=True))
    if args.require_full_coverage and coverage.uncited_verified_keys:
        print(
            "uncited verified keys: " + ", ".join(coverage.uncited_verified_keys)
        )
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
