# AI Usage Log

> **Status:** scaffold only. No real LLM / API calls have been made for this
> project yet.

This file must be kept up to date as real AI usage begins. Every distinct
phase of AI-assisted work should be recorded here.

## Required entries (later)

For each AI-assisted activity, record:

- **Date** of the session.
- **Tool / model** used (e.g., Claude Opus 4.7, GPT-X, search SDK Y).
- **Purpose** (research, drafting, review, formatting, validation).
- **Inputs** (prompt summary — full prompts go in `PROMPTS.md`).
- **Outputs** (what was produced and where it landed in the repo).
- **Human verification** (who reviewed it and what was changed).
- **Cost / token estimate** if known.

## Entries

### 2026-06-15 — Phase 6 Markdown-first run (P6-I01, offline fixture)

- **Date:** 2026-06-15.
- **Tool / model:** none. The committed Phase 6 candidate Markdown
  artifacts were produced by `run_phase6_generate()` in
  `src/agentic_publishing_pipeline/crews/_phase6_generate.py`.
  Chapter drafts (`chapters/planning.md`, `chapters/memory.md`) come
  from the deterministic offline fixture
  `tests/fixtures/offline/task_responses.json` (`WRITE` entry).
  `outline.md` and `research_notes.md` are emitted verbatim from
  bundled canonical templates under
  `src/agentic_publishing_pipeline/crews/_phase6_data/` via
  `write_static_templates()` in `_phase6_static.py`. A clean-tmp
  regeneration reproduces all four candidate files byte-for-byte
  (`tests/crews/test_phase6_static_templates.py`). No live provider
  call (Anthropic, OpenAI, or other) was issued for this run; no
  model identifier applies.
- **Provider mode:** offline-fixture (CLI mode `--mode
  offline-fixture`). No `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` was
  required or consulted; the network-blocked regression test
  (`test_run_phase6_generate_no_network`) proves no socket is opened.
- **Phase 6 task / prompt identifiers:** issues #18 (P6-I01,
  Markdown generation) and #19 (P6-I02, human review gate). The
  related prompt-registry entries used for fixture authoring are
  documented in `docs/PROMPTS.md`; the offline fixture is the
  canonical input for this run.
- **Purpose:** produce the canonical Phase 6 candidate Markdown set
  for human review per FR-11/FR-12/FR-13 (chapters with figure,
  table, equation, and citation placeholders) and exercise the
  enforceable human review gate (FR-14 / NFR-19) before any LaTeX
  conversion.
- **Inputs:** manifest `config/article_sources.yaml` (10 citation
  keys); deterministic offline fixture `WRITE` response containing
  the chapter drafts; no agent prompts were dispatched to any
  external provider.
- **Outputs (committed under `results/`):**
  - `results/generated_markdown/chapters/planning.md` (fixture)
  - `results/generated_markdown/chapters/memory.md` (fixture)
  - `results/generated_markdown/outline.md` (canonical template)
  - `results/generated_markdown/research_notes.md` (canonical template)
  - `results/run_logs/phase6-p6i01-offline-fixture.jsonl`
- **Path-sensitive aggregate draft revision (Phase 6 path-bound
  SHA-256, P6-I02 algorithm):**
  `a137339da7d176ecf44a84a29f0bb1c73bdf3045891cc40ef1ce0fcd4519cbe8`.
- **Per-file SHA-256 (file bytes only):**
  - `chapters/memory.md`
    → `c824cf41457a5843af8f37bf43f75654c7110612de99e287c846277af64038a1`
  - `chapters/planning.md`
    → `36e36aa24433b6894598928b33399aa21bbc077e78bf1b296785a56f3d794ae5`
  - `outline.md`
    → `e0b06a67b9b0a34f05df49ec70f0eba01b30c839c2430766f1c264c07bf160c3`
  - `research_notes.md`
    → `8b2ef7820cf16f7dc8faeffcc0a2ceaa5ba454aba2f46a130740a9fec0b89aa3`
- **Citation-key resolution:** all CITATION placeholders in the
  committed Markdown set (`tbd2025agenticmath`,
  `tbd2025agenticreasoningtools`, `tbd2025licomemory`,
  `tbd2025multimodalsurvey`, `tbd2025planningperformance`,
  `tbd2025proactiveretrievalmedical`, `tbd2026agenticreasoning`,
  `tbd2026telemem`) resolve to keys present in
  `config/article_sources.yaml`. `tbd2024mirai` and
  `tbd2025reasoningfrontiers` are present in the manifest but not
  yet cited by the candidate drafts.
- **Human verification:** PENDING. The committed
  `_review_gate.enforce_review_gate()` blocks any LaTeX conversion
  until a human reviewer records an `approved` verdict whose
  recorded `draft_sha256` matches the current path-sensitive
  aggregate revision above. No real `review_record.json` has been
  written under `results/run_logs/` and none will be written during
  the Phase 6 implementation pass.
- **Cost / token estimate:** $0.00; zero external-provider tokens
  for this run. Development assistance from Claude Code (Opus 4.7)
  and Codex (independent reviewer in a separate clone) is tracked
  separately in `docs/PROMPTS.md` per the existing AI usage schema;
  that assistance contributed no committed Markdown text directly.
- **Known limitations:**
  - Drafts come from the deterministic offline fixture, not from a
    live provider run; live-provider generation is deferred to a
    later phase.
  - The reviewer-identity check in the review gate is a heuristic
    denylist, not cryptographic identity proof.
  - LaTeX, BibTeX, and PDF generation are explicitly out of scope
    for this entry; no `.tex`, `.bib`, or `.pdf` was produced.
- **Status on `main`:** not yet merged. Implementation is ready on
  PR #81 (branch `phase/06-markdown-first-content-pipeline`),
  human approval is pending, and independent checkpoint 2 and merge
  are pending.
