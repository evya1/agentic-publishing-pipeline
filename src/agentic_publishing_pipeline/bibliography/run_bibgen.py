"""Generate ``latex_project/references.bib`` from the verified manifest.

Run via ``uv run python -m agentic_publishing_pipeline.bibliography.run_bibgen``.

The script pulls per-source ``primary_category`` values from the
P7-I02 verification report so each ``@online`` entry can carry the
authoritative ``primaryclass`` field. Use ``--check`` to assert the
committed ``.bib`` is in sync (CI mode).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import load_source_manifest
from .bibgen import render_bib


def _primary_categories(verification_report_path: Path) -> dict[str, str]:
    report = json.loads(verification_report_path.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for entry in report["results"]:
        arxiv_id = str(entry["arxiv_id"])
        cat = entry.get("primary_category")
        if cat:
            out[arxiv_id] = str(cat)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("config/article_sources.yaml"))
    parser.add_argument(
        "--report", type=Path, default=Path("results/run_logs/p7i02_verification.json")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("latex_project/references.bib")
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    manifest = load_source_manifest(args.manifest)
    bib = render_bib(manifest, primary_categories=_primary_categories(args.report))

    if args.check:
        existing = args.output.read_text(encoding="utf-8") if args.output.is_file() else ""
        if existing == bib:
            print(f"{args.output} is up to date")
            return 0
        print(f"{args.output} differs from generated bibliography")
        return 1

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(bib, encoding="utf-8")
    entry_count = sum(1 for r in manifest.records if r.verification.status == "verified")
    print(f"wrote {args.output} ({entry_count} verified entries)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
