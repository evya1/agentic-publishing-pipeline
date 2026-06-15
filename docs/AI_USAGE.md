# AI Usage Log

> **Status:** scaffold only. No real LLM / API calls have been made for this
> project yet.

This file must be kept up to date as real AI usage begins. Every distinct
phase of AI-assisted work should be recorded here.

## Scope and boundary (fixed by P7-I00, 2026-06-16)

This log records **AI-assisted activity**: model identity, prompts,
limitations, human verification, cost. Per-source bibliographic
verification evidence lives in `docs/SOURCES.md` (the canonical
source-verification ledger) — not here. AI-assisted verification runs
add a single AI Usage entry that links back to the affected
`docs/SOURCES.md` entries by citation key and `run_id`; they do not
duplicate the per-source evidence fields. The split is binding under
`docs/PRD_bibliography_and_citations.md` §13.1.

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

### 2026-06-16 — Phase 7 source verification run (P7-I02, live arXiv API)

- **Date:** 2026-06-16.
- **Tool / model:** Claude Code (Opus 4.7) drove the implementation
  and the orchestration; the authoritative metadata for each source
  came from the **arXiv Atom API**
  (`http://export.arxiv.org/api/query?id_list=<id>`). No model
  produced bibliographic facts. The script lives at
  `src/agentic_publishing_pipeline/bibliography/run_verification.py`
  and uses stdlib `urllib.request` with a 3-second polite delay
  per request and a `User-Agent` identifying the project.
- **Verifier identity:** `claude-opus-4.7+arxiv-api:evya1`
  (honest-identity convention per
  `docs/PRD_bibliography_and_citations.md` §7.3).
- **Purpose:** populate `authors:` and flip `verification.status`
  for every entry in `config/article_sources.yaml` against
  authoritative arXiv metadata; commit the raw responses as
  reproducible test fixtures.
- **Inputs:** the 10-source locked manifest; the arXiv Atom feed for
  each `arxiv_id`.
- **Outputs:**
  - `tests/fixtures/arxiv/<arxiv_id>.xml` — 10 raw Atom responses
    (committed as deterministic offline test fixtures).
  - `results/run_logs/p7i02_verification.json` — machine-readable
    per-source report (mismatches, populated authors, primary
    category, arxiv DOI when present).
  - `config/article_sources.yaml` — manifest rewritten with
    authoritative `title`, `year`, and `authors` for each source
    and `verification.status = verified`.
- **Live verification result:** 10/10 verified against the committed
  fixtures. The first live run flagged three placeholder
  mismatches in the original manifest, which are recorded in
  `docs/SOURCES.md`:
  - `tbd2025agenticreasoningtools` (2502.04644) — manifest title
    placeholder corrected to the authoritative arXiv title.
  - `tbd2025planningperformance` (2511.09378) — manifest title
    placeholder corrected to the authoritative arXiv title.
  - `tbd2026telemem` (2601.06037) — manifest year placeholder
    `2026` corrected to authoritative `2025` (arXiv `<published>`).
  No fabricated authors or titles were introduced; every
  authoritative value came from the committed XML fixture.
- **Human verification:** Phase 7 verification ran under the
  authenticated GitHub account `evya1`; the rejected-then-corrected
  cases are surfaced in `docs/SOURCES.md` and the matching
  `verification.json` so a reviewer can reproduce the
  authoritative comparison against the committed fixtures.
- **Cost / token estimate:** $0.00 for arXiv fetches (arXiv API is
  free); ten HTTP requests; no LLM calls were made to derive
  bibliographic facts.
- **Known limitations:**
  - Provisional `tbd…` citation keys remain until P7-I05 rekeys
    them to the `authorYYYYkey` convention.
  - `references.bib` emission is the scope of P7-I04; this entry
    does not produce `.bib` output.
  - The verification script always runs live; offline regression
    tests use the committed XML fixtures.



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
- **Human verification:** approved by human reviewer `evya1` at
  `2026-06-15T22:59:51+02:00`. The approval is recorded in
  `results/run_logs/review_record.json` with verdict `approved`
  and draft revision
  `a137339da7d176ecf44a84a29f0bb1c73bdf3045891cc40ef1ce0fcd4519cbe8`.
  The committed `_review_gate.enforce_review_gate()` blocks any
  LaTeX conversion unless that recorded `draft_sha256` matches the
  current path-sensitive aggregate revision.
- **Cost / token estimate:** $0.00; zero external-provider tokens
  for this run. Development assistance from Claude Code (Opus 4.7)
  and Codex (independent reviewer in a separate clone) is tracked
  separately in `docs/PROMPTS.md` per the existing AI usage schema;
  that assistance contributed no committed Markdown text directly.
- **Known limitations:**
  - Drafts come from deterministic offline-fixture and
    static-template generation, not from a live provider run;
    live-provider generation is deferred to a later phase.
  - The reviewer-identity check in the review gate is a heuristic
    denylist, not cryptographic identity proof.
  - Bibliography verification, LaTeX conversion, final PDF
    generation, and PDF validation are explicitly out of scope for
    this entry; no `.tex`, `.bib`, or `.pdf` was produced.
  - The current Markdown files are intermediate Phase 6 candidates
    rather than final publication-ready chapters.
- **Status on `main`:** merged through PR #81 at merge commit
  `f18a54af4a0cf6a6fff0ebd70eeacd60006530e7`; Phase 6 issues
  #17-#20 are closed and the Phase 6 milestone is closed.
