"""Apply the P7-I05 provisional → final key migration across active artifacts.

Run via ``uv run python -m agentic_publishing_pipeline.bibliography.run_rekey``.

The active artifact list is fixed below so a reviewer can see exactly
which files migrate. Historical run-log evidence (the Phase 6 review
packet, the review record, the verification JSON snapshot) is **not**
rewritten — that preserves the audit trail and lets the Phase 6
review gate request honest human reapproval against the new content
hash.

A transparent migration ledger is written to
``results/run_logs/p7i05_rekey.json`` recording the key map, the
files touched, and (for the generated Markdown tree) the previous
and new ``draft_sha256`` values from the Phase 6 gate.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from ..crews._review_gate import compute_draft_revision
from . import load_source_manifest
from .rekey import apply_key_map, build_key_map

# Active artifacts whose citation keys must migrate. Order is the
# order touched; the audit ledger records the same list.
DEFAULT_TARGETS: tuple[Path, ...] = (
    Path("config/article_sources.yaml"),
    Path("docs/SOURCES.md"),
    Path("docs/AI_USAGE.md"),
    Path("docs/PRD_bibliography_and_citations.md"),
    Path("results/generated_markdown/outline.md"),
    Path("results/generated_markdown/research_notes.md"),
    Path("results/generated_markdown/chapters/planning.md"),
    Path("results/generated_markdown/chapters/memory.md"),
    Path("src/agentic_publishing_pipeline/crews/_phase6_data/outline.md"),
    Path("src/agentic_publishing_pipeline/crews/_phase6_data/research_notes.md"),
    Path("tests/fixtures/offline/task_responses.json"),
)


def _rekey_file(path: Path, key_map: dict[str, str]) -> int:
    if not path.is_file():
        return 0
    original = path.read_text(encoding="utf-8")
    updated, count = apply_key_map(original, key_map)
    if count and updated != original:
        path.write_text(updated, encoding="utf-8")
    return count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("config/article_sources.yaml"))
    parser.add_argument(
        "--ledger",
        type=Path,
        default=Path("results/run_logs/p7i05_rekey.json"),
    )
    parser.add_argument(
        "--generated-md-root",
        type=Path,
        default=Path("results/generated_markdown"),
    )
    parser.add_argument("--rekey-by", default="claude-opus-4.7+rekey:evya1")
    args = parser.parse_args(argv)

    manifest = load_source_manifest(args.manifest)
    rejected = [r.citation_key for r in manifest.records if r.verification.status != "verified"]
    if rejected:
        raise RuntimeError(
            f"manifest has {len(rejected)} non-verified records ({sorted(rejected)}); rekey refused"
        )
    key_map = build_key_map(manifest)
    previous_md_sha = compute_draft_revision(args.generated_md_root)
    touched: list[dict[str, object]] = []
    for target in DEFAULT_TARGETS:
        count = _rekey_file(target, key_map)
        touched.append({"path": str(target), "replacements": count})
    new_md_sha = compute_draft_revision(args.generated_md_root)

    ledger = {
        "schema": "p7i05-rekey/v1",
        "applied_at": datetime.now(UTC).isoformat(),
        "applied_by": args.rekey_by,
        "manifest_path": str(args.manifest),
        "key_map": key_map,
        "touched": touched,
        "generated_markdown_root": str(args.generated_md_root),
        "previous_draft_sha256": previous_md_sha,
        "new_draft_sha256": new_md_sha,
        "note": (
            "Provisional 'tbd...' citation keys migrated to authorYYYYkey. "
            "The Phase 6 review record (results/run_logs/review_record.json) "
            "is intentionally NOT rewritten; the Phase 6 gate will request "
            "honest human reapproval against the new draft_sha256."
        ),
    }
    args.ledger.parent.mkdir(parents=True, exist_ok=True)
    args.ledger.write_text(json.dumps(ledger, indent=2, sort_keys=True), encoding="utf-8")
    summary = {
        "replacements_total": sum(int(t["replacements"]) for t in touched),
        "files_touched": sum(1 for t in touched if int(t["replacements"])),
        "key_map_size": len(key_map),
        "previous_draft_sha256": previous_md_sha[:12],
        "new_draft_sha256": new_md_sha[:12],
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
