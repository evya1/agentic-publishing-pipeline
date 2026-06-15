"""CLI entry point and run-orchestration glue.

Phase 5 provides the CLI modes (`dry-run`, `offline-fixture`,
`live`, `compile-only`, `validate-only`, `--topic` / `--manifest`
overrides, and `resume`). Real CrewAI Crew assembly lands in later
phases when the agents and tasks are wired to the provider/tools
layer; the Phase 5 CLI exercises every architectural seam (run
context, registry, provider, Gatekeeper, FileIO, search,
markdown, latex_build, graph) end-to-end against deterministic
offline fixtures.
"""

from __future__ import annotations

from .cli import OFFLINE_MODES, build_parser, main, run_cli

__all__ = ["OFFLINE_MODES", "build_parser", "main", "run_cli"]
