"""Human Markdown review gate (P6-I02 / issue #19).

Enforces FR-14 / NFR-19: no LaTeX conversion may begin until a human
reviewer has produced an 'approved' review record whose draft-set hash
matches the current canonical Markdown drafts.

The gate blocks on:
- missing review record;
- verdict 'changes_requested';
- reviewer identity matching an LLM/agent name;
- draft set changed since the recorded approval (hash mismatch).

Human reviewers write a review record via write_review_record() or by
manually creating results/run_logs/review_record.json.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

REVIEW_RECORD_FILENAME = "review_record.json"
ALLOWED_VERDICTS: frozenset[str] = frozenset({"approved", "changes_requested"})
# fmt: off
_LLM_IDENTITIES: frozenset[str] = frozenset({
    "llm", "ai", "claude", "codex", "gpt", "gemini", "agent",
    "reviewer_agent", "reviewer-agent", "reviewer agent", "llm reviewer",
})
# fmt: on


class HumanReviewRequired(RuntimeError):
    """Raised when the human review gate blocks LaTeX conversion."""


@dataclass(frozen=True)
class ReviewRecord:
    reviewer: str
    draft_sha256: str
    reviewed_at: str
    verdict: Literal["approved", "changes_requested"]
    notes: str = ""
    schema_version: str = "v1"


def compute_draft_revision(generated_md_root: Path) -> str:
    """SHA-256 over each draft file's POSIX relative path + exact bytes.

    Binds normalized path identity to file contents with length-framed
    segments so renames, directory moves, additions, removals, and
    content mutations all invalidate the revision while an unchanged
    tree is deterministic. README files at any depth are excluded.
    """
    root = generated_md_root.resolve()
    paths = sorted(p for p in root.rglob("*.md") if p.name != "README.md")
    digest = hashlib.sha256()
    for p in paths:
        rel = p.resolve().relative_to(root).as_posix().encode("utf-8")
        content = p.read_bytes()
        digest.update(f"P:{len(rel)}:".encode("ascii") + rel)
        digest.update(f"C:{len(content)}:".encode("ascii") + content)
    return digest.hexdigest()


def write_review_record(record: ReviewRecord, run_log_root: Path) -> Path:
    """Persist record as JSON; return the written path."""
    run_log_root.mkdir(parents=True, exist_ok=True)
    target = run_log_root / REVIEW_RECORD_FILENAME
    payload = {
        "notes": record.notes,
        "draft_sha256": record.draft_sha256,
        "reviewed_at": record.reviewed_at,
        "reviewer": record.reviewer,
        "schema_version": record.schema_version,
        "verdict": record.verdict,
    }
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target


def load_review_record(run_log_root: Path) -> ReviewRecord | None:
    """Return the stored ReviewRecord, or None when absent."""
    path = run_log_root / REVIEW_RECORD_FILENAME
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    verdict = str(data.get("verdict", ""))
    if verdict not in ALLOWED_VERDICTS:
        raise HumanReviewRequired(
            f"Review record has unknown verdict {verdict!r}. "
            f"Allowed verdicts: {sorted(ALLOWED_VERDICTS)}."
        )
    return ReviewRecord(
        reviewer=str(data.get("reviewer", "")),
        draft_sha256=str(data.get("draft_sha256", "")),
        reviewed_at=str(data.get("reviewed_at", "")),
        verdict=verdict,  # type: ignore[arg-type]
        notes=str(data.get("notes", "")),
        schema_version=str(data.get("schema_version", "v1")),
    )


def enforce_review_gate(
    generated_md_root: Path,
    run_log_root: Path,
) -> None:
    """Raise HumanReviewRequired unless a valid human-approved record exists.

    Call this before any LaTeX conversion begins (FR-14, NFR-19).
    """
    record = load_review_record(run_log_root)
    if record is None:
        raise HumanReviewRequired(
            "No review record found. A human reviewer must examine the Markdown "
            "drafts and write a review record to "
            f"{run_log_root / REVIEW_RECORD_FILENAME} "
            "before LaTeX conversion may begin (FR-14, NFR-19). "
            "Use write_review_record() or create the JSON file manually."
        )
    reviewer_lower = record.reviewer.strip().lower()
    if not reviewer_lower:
        raise HumanReviewRequired("Review record has an empty reviewer field.")
    if reviewer_lower in _LLM_IDENTITIES:
        raise HumanReviewRequired(
            f"Reviewer {record.reviewer!r} is an LLM/agent identity. "
            "Only a human reviewer may approve Markdown drafts (NFR-19)."
        )
    if record.verdict == "changes_requested":
        raise HumanReviewRequired(
            "Review verdict is 'changes_requested'. Revise the drafts and "
            f"re-submit for human review before LaTeX conversion. "
            f"Reviewer notes: {record.notes!r}"
        )
    current_sha = compute_draft_revision(generated_md_root)
    if record.draft_sha256 != current_sha:
        raise HumanReviewRequired(
            "Draft set has changed since approval was recorded. "
            f"Recorded SHA={record.draft_sha256[:12]}…, "
            f"current SHA={current_sha[:12]}…. "
            "Re-review and re-approval required before LaTeX conversion."
        )


def make_review_record(
    *,
    reviewer: str,
    generated_md_root: Path,
    verdict: Literal["approved", "changes_requested"],
    notes: str = "",
) -> ReviewRecord:
    """Convenience constructor that computes the draft revision automatically."""
    return ReviewRecord(
        reviewer=reviewer,
        draft_sha256=compute_draft_revision(generated_md_root),
        reviewed_at=datetime.now(UTC).isoformat(),
        verdict=verdict,
        notes=notes,
    )
