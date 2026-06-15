"""Bibliography Agent — typed source manifest, verification, and \\.bib emission.

The subpackage owns the Phase 7 boundary between the locked source
manifest (`config/article_sources.yaml`) and downstream LaTeX
artifacts. Submodules:

- :mod:`.manifest` — typed immutable source records and a
  deterministic loader (P7-I01).

Future Phase 7 submodules (added by their respective issues):

- ``verify`` — authoritative metadata verification (P7-I02).
- ``audit`` — `docs/SOURCES.md` mirror generation (P7-I03).
- ``bibgen`` — verified `references.bib` emission (P7-I04).
- ``cite`` — Markdown placeholder → LaTeX `\\cite{...}` resolution (P7-I06).
"""

from .manifest import (
    SourceManifest,
    SourceManifestError,
    SourceRecord,
    VerificationRecord,
    load_source_manifest,
)

__all__ = [
    "SourceManifest",
    "SourceManifestError",
    "SourceRecord",
    "VerificationRecord",
    "load_source_manifest",
]
