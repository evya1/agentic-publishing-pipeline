"""Shared manuscript task identifiers."""

from __future__ import annotations

REQUIRED_CHAPTER_IDS: tuple[str, ...] = (
    "introduction",
    "planning",
    "memory",
    "retrieval",
    "tool_use",
    "multimodal",
    "evaluation",
    "conclusion",
)

TASK_PROMPT_IDS: dict[str, str] = {
    "research": "PROMPT-TASK-RESEARCH-001",
    "outline": "PROMPT-TASK-OUTLINE-001",
    "write": "PROMPT-TASK-WRITE-001",
    "asset": "PROMPT-TASK-ASSET-001",
    "bidi": "PROMPT-TASK-BIDI-001",
    "bibliography": "PROMPT-TASK-BIBLIOGRAPHY-001",
    "review": "PROMPT-TASK-REVIEW-001",
}
