# results/generated_markdown/

**Canonical Markdown draft root** per FR-12, §12.3, and `docs/PRD.md`.

The `content/markdown_drafts/` transitional path was retired in P6-I00
(2026-06-15). This directory is the sole canonical location for
Markdown drafts produced by the Writer/Outline/Reviewer agent pipeline.

## Layout

```
results/generated_markdown/
├── research_notes.md     # Research Agent (T1) output
├── outline.md            # Outline Agent (T2) output
├── chapters/
│   └── <chapter_id>.md   # Writer Agent (T3) chapter drafts
├── assets/               # Technical Asset Agent (T4) specs
└── bidi.md               # BiDi Agent (T5) output
```

## Artifact policy

- Files here are committed Phase 6 deliverables (not per-run workspace
  artifacts). Per-run workspace files live under `results/RUN-*/`
  (gitignored).
- Every citation placeholder (HTML comment with `CITATION:` prefix) must
  reference a key present in `config/article_sources.yaml`.
- No LaTeX conversion may begin until a human review record is present
  in `results/run_logs/review_record.json` with `verdict: "approved"`.
