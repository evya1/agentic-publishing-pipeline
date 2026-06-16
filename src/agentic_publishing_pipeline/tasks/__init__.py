"""CrewAI task definitions.

Factory helpers build the pre-review manuscript task graph.
"""

from __future__ import annotations

from .completeness import ManuscriptPreflightReport, run_manuscript_preflight
from .factory import (
    REQUIRED_CHAPTER_IDS,
    TASK_PROMPT_IDS,
    TaskFactoryError,
    build_manuscript_tasks,
)

__all__ = [
    "REQUIRED_CHAPTER_IDS",
    "TASK_PROMPT_IDS",
    "ManuscriptPreflightReport",
    "TaskFactoryError",
    "build_manuscript_tasks",
    "run_manuscript_preflight",
]
