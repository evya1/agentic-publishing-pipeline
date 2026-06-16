"""CLI entry point and run-orchestration glue.

Phase 5 provides the CLI modes (`dry-run`, `offline-fixture`,
`live`, `compile-only`, `validate-only`, `--topic` / `--manifest`
overrides, and `resume`). Real CrewAI Crew assembly lands in later
phases when the agents and tasks are wired to the provider/tools
layer; the Phase 5 CLI exercises every architectural seam (run
context, registry, provider, Gatekeeper, FileIO, search,
markdown, latex_build, graph) end-to-end against deterministic
offline fixtures. Phase 6 adds the real pre-review manuscript crew factory.
"""

from __future__ import annotations

from .cli import OFFLINE_MODES, LiveAdapterUnavailable, build_parser, main, run_cli
from .live_runner import ManuscriptPreflightFailed, run_live_manuscript
from .manuscript_crew import ManuscriptCrewError, build_manuscript_crew
from .result_parser import CrewResultError, ManuscriptOutputs, parse_manuscript_outputs

__all__ = [
    "CrewResultError",
    "LiveAdapterUnavailable",
    "OFFLINE_MODES",
    "ManuscriptOutputs",
    "ManuscriptCrewError",
    "ManuscriptPreflightFailed",
    "build_manuscript_crew",
    "build_parser",
    "main",
    "parse_manuscript_outputs",
    "run_live_manuscript",
    "run_cli",
]
