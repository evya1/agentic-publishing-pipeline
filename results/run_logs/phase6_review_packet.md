# Phase 6 Human-Review Packet

This file is **informational only**. It describes the Phase 6 candidate
Markdown set, the per-file and aggregate hashes that the
`enforce_review_gate()` mechanism checks against, the approved/changes_requested
response templates a human reviewer uses, and the exact destination
and API for recording the verdict. It is **not** the approval record.
The human review record is `results/run_logs/review_record.json`,
which now records the approved Phase 6 revision.

## Canonical files included by the aggregate hash

The review hash covers every `*.md` file under
`results/generated_markdown/` except files literally named `README.md`
(which document the directory layout):

- `chapters/memory.md`
- `chapters/planning.md`
- `outline.md`
- `research_notes.md`

## Aggregate path-sensitive revision (P6-I02 algorithm)

`a137339da7d176ecf44a84a29f0bb1c73bdf3045891cc40ef1ce0fcd4519cbe8`

The algorithm hashes, for each file in sorted-by-relative-path order, a
length-framed POSIX relative path segment (`P:<len>:<rel_posix>`)
followed by a length-framed content segment (`C:<len>:<bytes>`), under
SHA-256. Renames, directory moves, additions, removals, and content
mutations all invalidate this revision; an unchanged tree is
deterministic.

## Per-file SHA-256 (file bytes only, sha256sum-style)

- `chapters/memory.md` →
  `c824cf41457a5843af8f37bf43f75654c7110612de99e287c846277af64038a1`
- `chapters/planning.md` →
  `36e36aa24433b6894598928b33399aa21bbc077e78bf1b296785a56f3d794ae5`
- `outline.md` →
  `e0b06a67b9b0a34f05df49ec70f0eba01b30c839c2430766f1c264c07bf160c3`
- `research_notes.md` →
  `8b2ef7820cf16f7dc8faeffcc0a2ceaa5ba454aba2f46a130740a9fec0b89aa3`

## Manifest / citation-key summary

- Manifest: `config/article_sources.yaml` (10 keys total).
- Cited by the committed Markdown set (8 keys): `tbd2025agenticmath`,
  `tbd2025agenticreasoningtools`, `tbd2025licomemory`,
  `tbd2025multimodalsurvey`, `tbd2025planningperformance`,
  `tbd2025proactiveretrievalmedical`, `tbd2026agenticreasoning`,
  `tbd2026telemem`.
- Present in the manifest but not yet cited by candidate drafts (2):
  `tbd2024mirai`, `tbd2025reasoningfrontiers`.
- Every CITATION placeholder resolves to a manifest key (proven by
  `tests/crews/test_phase6_generate.py::test_committed_citation_keys_resolve_to_manifest`).

## Placeholder inventory

- `chapters/memory.md`: 1 × FIGURE, 1 × TABLE, 1 × EQUATION, 2 × CITATION.
- `chapters/planning.md`: 1 × FIGURE, 1 × TABLE, 1 × EQUATION, 2 × CITATION.
- `outline.md`: structural outline (no placeholder markers).
- `research_notes.md`: 10 × CITATION (one per manifest key not deferred).
- All four placeholder kinds (FIGURE, TABLE, EQUATION, CITATION) are
  represented at least once in the chapter set, satisfying FR-13.

## Known content and fixture limitations

- The committed Markdown is produced by the deterministic offline
  fixture `crews/fixtures/task_responses.json` (`WRITE` entry), not by a
  live provider call.
- Placeholders are intentional `<!-- FIGURE: ... -->`, `<!-- TABLE: ... -->`,
  `<!-- EQUATION: ... -->`, and `<!-- CITATION: ... -->` markers; the
  Phase 6 mechanism does not yet substitute final figures, tables,
  equations, or rendered citations.
- The reviewer-identity check in `_review_gate.py` is a heuristic
  denylist (`llm`, `claude`, `codex`, `gpt`, `gemini`, `agent`, …),
  not a cryptographic identity proof; a determined LLM caller could
  bypass it. Final authority on whether a record is human remains
  with the human reviewer.
- LaTeX, BibTeX, and PDF generation are explicitly out of Phase 6
  scope; no `.tex`, `.bib`, or `.pdf` is produced by this run.

## Response templates

A human reviewer copies one of the two templates below, fills the
reviewer name (and notes), and saves the file as
`results/run_logs/review_record.json`. The `draft_sha256` value must
exactly match the path-sensitive aggregate revision above; if drafts
change after the record is written, the gate will reject the stale
revision and require a fresh review.

### Approve template

```json
{
  "draft_sha256": "a137339da7d176ecf44a84a29f0bb1c73bdf3045891cc40ef1ce0fcd4519cbe8",
  "notes": "",
  "reviewed_at": "YYYY-MM-DDTHH:MM:SS+00:00",
  "reviewer": "<your full human name>",
  "schema_version": "v1",
  "verdict": "approved"
}
```

### Request-changes template

```json
{
  "draft_sha256": "a137339da7d176ecf44a84a29f0bb1c73bdf3045891cc40ef1ce0fcd4519cbe8",
  "notes": "<what must change before approval>",
  "reviewed_at": "YYYY-MM-DDTHH:MM:SS+00:00",
  "reviewer": "<your full human name>",
  "schema_version": "v1",
  "verdict": "changes_requested"
}
```

## Canonical record destination

`results/run_logs/review_record.json`

## Recording the verdict via Python API

```python
from pathlib import Path
from agentic_publishing_pipeline.crews._review_gate import (
    make_review_record, write_review_record,
)

repo = Path("/path/to/agentic-publishing-pipeline")
md_root = repo / "results" / "generated_markdown"
log_root = repo / "results" / "run_logs"

record = make_review_record(
    reviewer="<your full human name>",
    generated_md_root=md_root,
    verdict="approved",          # or "changes_requested"
    notes="",                    # required when verdict == "changes_requested"
)
write_review_record(record, log_root)
```

After saving the record, run
`uv run python -m agentic_publishing_pipeline.crews.cli --mode
compile-only --results-root <root> --run-id <run-id>` to confirm the
gate passes for the approved revision. The gate exits with
`HumanReviewRequired` if the record is missing, stale, marked
`changes_requested`, or attributed to an LLM/agent identity.

## Human approval status

**APPROVED.** Human reviewer `evya1` approved the exact revision above
at `2026-06-15T22:59:51+02:00`. The approval is recorded in
`results/run_logs/review_record.json` with verdict `approved`. Any later
content mutation, rename, directory move, addition, or removal
invalidates this approval and requires a fresh human review.
