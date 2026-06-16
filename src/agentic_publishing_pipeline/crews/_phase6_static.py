"""Phase 6 canonical static-Markdown emitters (P6-I01 follow-up).

``run_phase6_generate()`` writes per-chapter Markdown drafts from the
``WRITE`` offline fixture.  The Phase 6 candidate set also includes
``outline.md`` and ``research_notes.md`` whose bodies are richer than
the structural OUTLINE/RESEARCH fixtures encode (per-dimension citation
keys, intended-use table, glossary entries).  The canonical bytes for
those two files ship as package data under ``_phase6_data/`` and are
written verbatim by this module so a clean-tmp regeneration reproduces
the committed candidate set byte-for-byte.
"""

from __future__ import annotations

import re
from pathlib import Path

_PHASE6_DATA_DIR = Path(__file__).resolve().parent / "_phase6_data"
_STATIC_TEMPLATES: tuple[tuple[str, str], ...] = (
    ("outline.md", "outline.md"),
    ("research_notes.md", "research_notes.md"),
)
_CITATION_RE = re.compile(r"<!--\s*CITATION:\s*(?P<key>[A-Za-z0-9_\-]+)\s*-->")


def _load_and_validate(
    manifest_keys: list[str],
) -> tuple[list[tuple[str, bytes]], list[str]]:
    """Load every static template and validate CITATIONs against the manifest.

    Returns ``(loaded, citation_keys)`` where ``loaded`` preserves the
    deterministic ``_STATIC_TEMPLATES`` order. Raises ``ValueError`` on
    the first template whose CITATION keys are not all in ``manifest_keys``;
    no filesystem write is attempted by this phase.
    """
    manifest_set = set(manifest_keys)
    loaded: list[tuple[str, bytes]] = []
    cites: list[str] = []
    for rel_name, src_name in _STATIC_TEMPLATES:
        body = (_PHASE6_DATA_DIR / src_name).read_bytes()
        keys_here = [m.group("key") for m in _CITATION_RE.finditer(body.decode("utf-8"))]
        unknown = [k for k in keys_here if k not in manifest_set]
        if unknown:
            raise ValueError(
                f"{rel_name}: CITATION key(s) not in manifest: {unknown}. "
                f"Valid keys: {sorted(manifest_set)}"
            )
        loaded.append((rel_name, body))
        cites.extend(keys_here)
    return loaded, cites


def write_static_templates(md_root: Path, manifest_keys: list[str]) -> tuple[list[str], list[str]]:
    """Atomically copy canonical templates into ``md_root``.

    Phase 1 loads every template and validates every CITATION key
    against ``manifest_keys`` in memory; if any template is invalid
    the function raises ``ValueError`` before touching the filesystem.
    Phase 2 only runs when every template is valid; it then writes
    each file through an atomic ``tmp-p6`` + ``replace`` step so a
    pre-existing target is replaced only after its new bytes are on
    disk. No temporary file remains when phase 1 fails.
    """
    loaded, cites = _load_and_validate(manifest_keys)
    md_root.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for rel_name, body in loaded:
        target = md_root / rel_name
        tmp = target.with_suffix(target.suffix + ".tmp-p6")
        tmp.write_bytes(body)
        tmp.replace(target)
        written.append(rel_name)
    return written, cites
