"""Generate the P7-I03 per-source audit ledger and machine-readable mirror.

Run via ``uv run python -m agentic_publishing_pipeline.bibliography.run_audit``.
The script is deterministic apart from the ``generated_at`` timestamp
on the JSON mirror; the Markdown section is reproducible byte-for-byte
across runs.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from . import audit
from ._audit_markdown import render_section, splice_section
from .audit import AuditInputs


def _default_inputs() -> AuditInputs:
    return AuditInputs(
        manifest_path=Path("config/article_sources.yaml"),
        verification_report_path=Path("results/run_logs/p7i02_verification.json"),
        rekey_ledger_path=Path("results/run_logs/p7i05_rekey.json"),
        fixture_dir=Path("tests/fixtures/arxiv"),
        archive_root=Path("data/sources/arxiv/source_zips"),
        sources_md_path=Path("docs/SOURCES.md"),
        mirror_json_path=Path("results/run_logs/source_verification.json"),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    inputs = _default_inputs()
    entries = audit.build_audit_entries(inputs)
    mirror_text = audit.render_mirror(entries)
    markdown_section = render_section(entries)
    current_md = inputs.sources_md_path.read_text(encoding="utf-8")
    new_md = splice_section(current_md, markdown_section)

    if args.check:
        differs = False
        if inputs.mirror_json_path.is_file():
            existing = inputs.mirror_json_path.read_text(encoding="utf-8")
            # Strip the generated_at timestamp before comparing.
            import json

            old = json.loads(existing)
            new = json.loads(mirror_text)
            old.pop("generated_at", None)
            new.pop("generated_at", None)
            differs |= old != new
        else:
            differs = True
        differs |= new_md != current_md
        if differs:
            print("audit ledger differs from current files")
            return 1
        print("audit ledger up to date")
        return 0

    inputs.mirror_json_path.parent.mkdir(parents=True, exist_ok=True)
    inputs.mirror_json_path.write_text(mirror_text, encoding="utf-8")
    inputs.sources_md_path.write_text(new_md, encoding="utf-8")
    print(
        f"wrote {inputs.mirror_json_path} ({len(entries)} entries) "
        f"and updated {inputs.sources_md_path}"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
