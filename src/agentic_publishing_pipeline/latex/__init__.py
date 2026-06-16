"""Deterministic Phase 9 LaTeX project assembly.

The package converts only human-approved canonical Markdown into a structured
LaTeX source tree. It deliberately does not compile a PDF; compilation remains
owned by the existing Phase 10 build seam.

No Markdown-to-LaTeX conversion or build orchestration was implemented before
Phase 9. See ``README.md`` in this directory and ``docs/PRD_latex_generation.md``.
"""

from .approval_loader import (
    ApprovedChapter,
    ApprovedManuscript,
    load_approved_manuscript,
)
from .config_loader import load_phase9_config
from .config_models import Phase9Config
from .phase9_runner import Phase9InputNotReady, Phase9Result, assemble_phase9_project
from .preflight import Phase9PreflightReport, run_phase9_preflight

__all__ = [
    "ApprovedChapter",
    "ApprovedManuscript",
    "Phase9Config",
    "Phase9InputNotReady",
    "Phase9PreflightReport",
    "Phase9Result",
    "assemble_phase9_project",
    "load_approved_manuscript",
    "load_phase9_config",
    "run_phase9_preflight",
]
