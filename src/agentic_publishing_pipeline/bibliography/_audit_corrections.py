"""Documented P7-I02 placeholder-field corrections (P7-I03).

The live verification run on 2026-06-16 found that three manifest
entries carried placeholder ``title`` or ``year`` values that the
authoritative arXiv response disagreed with. Each correction is
recorded here verbatim so the audit ledger reflects what changed
and why. Keys are arXiv ids (stable across rekeys).
"""

from __future__ import annotations

CORRECTIONS: dict[str, dict[str, object]] = {
    "2502.04644": {
        "field": "title",
        "original_manifest_value": (
            "Agentic Reasoning: Reasoning LLMs with Tools for the Deep Research"
        ),
        "authoritative_value": (
            "Agentic Reasoning: A Streamlined Framework for Enhancing LLM "
            "Reasoning with Agentic Tools"
        ),
        "applied_at": "2026-06-16",
        "applied_by": "claude-opus-4.7+arxiv-api:evya1",
        "rationale": (
            "manifest title was an explicit placeholder pending Phase 7 "
            "verification; replaced with authoritative arXiv title."
        ),
    },
    "2511.09378": {
        "field": "title",
        "original_manifest_value": (
            "The 2025 Planning Performance of Frontier Large Language Models"
        ),
        "authoritative_value": ("Frontier Large Language Models Rival State-of-the-Art Planners"),
        "applied_at": "2026-06-16",
        "applied_by": "claude-opus-4.7+arxiv-api:evya1",
        "rationale": (
            "manifest title was an explicit placeholder pending Phase 7 "
            "verification; replaced with authoritative arXiv title."
        ),
    },
    "2601.06037": {
        "field": "year",
        "original_manifest_value": 2026,
        "authoritative_value": 2025,
        "applied_at": "2026-06-16",
        "applied_by": "claude-opus-4.7+arxiv-api:evya1",
        "rationale": (
            "manifest year was an estimate from the arXiv submission month "
            "(2601 = 2026/01); arXiv <published> reports 2025."
        ),
    },
}
