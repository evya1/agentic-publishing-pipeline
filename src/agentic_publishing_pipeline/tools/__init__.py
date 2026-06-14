"""Safe tool interfaces for CrewAI agents.

The Phase 5 tooling layer exposes:

- :mod:`.gatekeeper` — API Gatekeeper policy seam wrapping the
  provider facade (ADR-0004).
- :mod:`.fileio` — sandboxed file I/O bound to a run workspace.
- :mod:`.search` — manifest-backed source verification.
- :mod:`.markdown` — Markdown-to-LaTeX semantic conversion.
- :mod:`.latex_build` — deterministic LuaLaTeX + biber multi-pass.
- :mod:`.graph` — Python-graph rendering with provenance.

Each tool is small, deterministic, and fully tested without network
or paid-provider access.
"""

from .fileio import FileIO
from .gatekeeper import ApiGatekeeper, GatekeeperRejection, request_identity
from .latex_build import LaTeXBuildError, SubprocessRunner, build_pdf
from .markdown import (
    ParsedPlaceholder,
    escape_latex,
    has_placeholder,
    parse_placeholders,
    strip_placeholders,
)
from .search import (
    ManifestLoadError,
    load_source_manifest_hits,
    manifest_coverage,
    verify_arxiv_id,
)

__all__ = [
    "ApiGatekeeper",
    "FileIO",
    "GatekeeperRejection",
    "LaTeXBuildError",
    "ManifestLoadError",
    "ParsedPlaceholder",
    "SubprocessRunner",
    "build_pdf",
    "escape_latex",
    "has_placeholder",
    "load_source_manifest_hits",
    "manifest_coverage",
    "parse_placeholders",
    "request_identity",
    "strip_placeholders",
    "verify_arxiv_id",
]
