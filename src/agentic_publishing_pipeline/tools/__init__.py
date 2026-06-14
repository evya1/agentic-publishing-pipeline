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

from .gatekeeper import ApiGatekeeper, GatekeeperRejection, request_identity

__all__ = ["ApiGatekeeper", "GatekeeperRejection", "request_identity"]
