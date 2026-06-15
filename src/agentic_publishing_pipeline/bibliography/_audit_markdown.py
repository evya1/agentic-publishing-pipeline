"""Render the human-readable per-source section of ``docs/SOURCES.md``.

Internal helper for P7-I03; the public entrypoint lives in
:mod:`.run_audit`.
"""

from __future__ import annotations

import yaml

SECTION_HEADER = "### Per-source entries (populated by P7-I03)"
SECTION_START_MARKER = "<!-- P7I03_SECTION_START -->"
SECTION_END_MARKER = "<!-- P7I03_SECTION_END -->"


def render_entry(entry: dict[str, object]) -> str:
    """Return a fenced YAML block for one audit entry."""

    block = yaml.safe_dump(entry, sort_keys=True, allow_unicode=True, width=1000)
    return f"```yaml\n{block}```\n"


def render_section(entries: list[dict[str, object]]) -> str:
    """Return the full per-source section, including markers."""

    blocks = "\n".join(render_entry(e) for e in entries)
    summary_rows = "\n".join(
        f"| `{e['final_citation_key']}` | `{e['previous_citation_key']}` | "
        f"`{e['arxiv_id']}` | {e['verified_year']} | "
        f"{e['verification']['status']} |"
        for e in entries
    )
    summary_table = (
        "| Final key | Provisional key | arXiv ID | Year | Status |\n"
        "|-----------|------------------|----------|------|--------|\n"
        f"{summary_rows}\n"
    )
    return (
        f"{SECTION_START_MARKER}\n{SECTION_HEADER}\n\n"
        f"{summary_table}\n"
        f"{blocks}\n"
        f"{SECTION_END_MARKER}\n"
    )


def splice_section(markdown_text: str, rendered_section: str) -> str:
    """Replace any prior P7-I03 section, or append if missing."""

    if SECTION_START_MARKER in markdown_text and SECTION_END_MARKER in markdown_text:
        start = markdown_text.index(SECTION_START_MARKER)
        end = markdown_text.index(SECTION_END_MARKER) + len(SECTION_END_MARKER)
        return markdown_text[:start] + rendered_section.rstrip() + markdown_text[end:]
    # First-time splice: replace the "Reserved entries" placeholder
    # section with the new section, or append at end.
    placeholder = "### Reserved entries (placeholders pending P7-I02)"
    if placeholder in markdown_text:
        # Replace from the placeholder header to the next top-level
        # header (## …) or end of file.
        idx = markdown_text.index(placeholder)
        tail = markdown_text[idx:]
        next_section_offset = tail.find("\n## ")
        if next_section_offset < 0:
            return markdown_text[:idx] + rendered_section
        return (
            markdown_text[:idx]
            + rendered_section
            + tail[next_section_offset:]
        )
    return markdown_text.rstrip() + "\n\n" + rendered_section
