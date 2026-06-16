# AI Usage Log

> **Status:** Phase 9 deterministic assembly pipeline code integrated on
> 2026-06-16. No real LLM / API calls for content generation; all Phase 9
> code is deterministic. Upstream Markdown input gates are still blocked.

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

### 2026-06-16 — Phase 7 citation resolution + coverage gap (P7-I06)

- **Date:** 2026-06-16.
- **Tool / model:** Claude Code (Opus 4.7) drove the implementation.
  Citation resolution is a pure pattern-match rewrite; no LLM
  produced citation keys or factual content. The resolver lives at
  `src/agentic_publishing_pipeline/bibliography/cite.py` and the
  walking CLI at `run_citecheck.py`.
- **Purpose:** validate every `<!-- CITATION: key -->` in the
  active Markdown tree against the verified manifest, expose the
  Markdown→`\cite{...}` rewrite via `CitationResolver`, and
  surface ten-source coverage.
- **Outputs:**
  - validates that all citation placeholders resolve to verified
    final keys (no `tbd…`, no unknown, no rejected, no whitespace);
  - emits `results/run_logs/p7i06_citation_coverage.json` (schema
    `p7i06-citation-coverage/v1`) with per-file citation counts,
    cited keys, and uncited verified keys.
- **Editorial change applied:** one new citation
  `ke2025reasoningfrontiers` (A Survey of Frontiers in LLM
  Reasoning) was added to a new `## Background` section in
  `results/generated_markdown/research_notes.md` and the matching
  static template `src/agentic_publishing_pipeline/crews/
  _phase6_data/research_notes.md`. The citation truthfully
  reflects the source's intended use ("Background framing for the
  reasoning landscape (inference-time scaling, learning to reason,
  agentic systems)"), which matches the topic of the document.
  No factual claim was introduced beyond what the survey already
  covers.
- **Known coverage gap (not papered over):** `ye2024mirai` (MIRAI:
  Evaluating LLM Agents for Event Forecasting) remains uncited
  because its intended use is "Evaluation chapter; benchmark for
  LLM agents on event forecasting" and **no Evaluation chapter
  exists in Phase 7 scope**. Adding the citation to an unrelated
  section would be misleading; the gap is recorded honestly here
  and in `results/run_logs/p7i06_citation_coverage.json` under
  `uncited_verified_keys`. The canonical ten-source coverage rule
  (`docs/PRD_bibliography_and_citations.md` §10.2) will be
  satisfied when Phase 9 adds an Evaluation chapter or when the
  manifest's locked source set is reconsidered through a
  reviewed PR.
- **Phase 6 review-record integrity:** the editorial addition
  changes the `draft_sha256` again (already broken by P7-I05).
  The Phase 6 approval continues to require honest human
  reapproval; no reapproval was fabricated.
- **Cost / token estimate:** $0.00; deterministic rewrite, no
  model calls.

### 2026-06-16 — Phase 7 provisional → final key migration (P7-I05)

- **Date:** 2026-06-16.
- **Tool / model:** Claude Code (Opus 4.7) drove the implementation.
  The migration itself is deterministic ASCII string rewriting —
  no LLM produced citation keys. The orchestrator lives at
  `src/agentic_publishing_pipeline/bibliography/run_rekey.py` and
  builds the key map via
  `src/agentic_publishing_pipeline/bibliography/rekey.py`.
- **Rekey identity:** `claude-opus-4.7+rekey:evya1`.
- **Purpose:** retire the provisional `tbd…` citation keys, replace
  each with `<family><year><slug>` derived from the verified
  manifest, and re-sync every active artifact that references a
  citation key.
- **Inputs:** the verified-as-of-P7-I02 manifest
  `config/article_sources.yaml` (10 records, all `verified`).
- **Outputs:**
  - rewritten manifest, `docs/SOURCES.md` placeholder table,
    `docs/PRD_bibliography_and_citations.md` references,
    `results/generated_markdown/**`,
    `src/agentic_publishing_pipeline/crews/_phase6_data/**`, and
    `tests/fixtures/offline/task_responses.json` (101 individual
    replacements across 10 files);
  - `results/run_logs/p7i05_rekey.json` — transparent migration
    ledger with key map, files touched, previous and new
    `draft_sha256` for the generated Markdown tree.
- **Phase 6 review-record integrity:** the Phase 6 approval at
  `results/run_logs/review_record.json` is **intentionally** not
  rewritten. After the migration, the recorded `draft_sha256`
  (`a137339d…`) no longer matches the post-migration
  `draft_sha256` (`7f6c1368…`), so the Phase 6 review gate
  (`_review_gate.enforce_review_gate`) correctly refuses to
  proceed and requires honest human reapproval. No reapproval
  was fabricated.
- **Human verification:** required for the migrated Markdown
  before any LaTeX conversion can begin. Until that reapproval
  is recorded, every consumer of the Markdown tree must treat
  the migrated content as **pending human review**.
- **Cost / token estimate:** $0.00; deterministic string rewrite,
  no model calls.
- **Known limitations:**
  - The historical run-log evidence
    (`results/run_logs/phase6_review_packet.md`,
    `results/run_logs/p7i02_verification.json`) is intentionally
    not rewritten — those files document state at the time of
    each run and are kept as-is for audit.
  - The Phase 6 review record itself is also preserved; the
    migration explicitly does not forge a reapproval.

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
  `docs/SOURCES.md`. The keys named below are the **final**
  post-P7-I05 keys; the provisional keys at run time were
  respectively `tbd2025agenticreasoningtools`,
  `tbd2025planningperformance`, and `tbd2026telemem`:
  - `wu2025agenticreasoningtools` (2502.04644) — manifest title
    placeholder corrected to the authoritative arXiv title.
  - `correa2025planningperformance` (2511.09378) — manifest title
    placeholder corrected to the authoritative arXiv title.
  - `chen2025telemem` (2601.06037) — manifest year placeholder
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
- **Citation-key resolution (at time of approval):** all CITATION
  placeholders in the reviewed Markdown set used the provisional
  keys `tbd2025agenticmath`, `tbd2025agenticreasoningtools`,
  `tbd2025licomemory`, `tbd2025multimodalsurvey`,
  `tbd2025planningperformance`, `tbd2025proactiveretrievalmedical`,
  `tbd2026agenticreasoning`, `tbd2026telemem`, resolving against the
  then-current `config/article_sources.yaml`. `tbd2024mirai` and
  `tbd2025reasoningfrontiers` were present in the manifest but not
  cited by the candidate drafts.
- **Note (post-approval).** The provisional `tbd…` keys above were
  migrated to the final `authorYYYYkey` form under P7-I05 on
  2026-06-16. The historical SHA-256s above still refer to the
  pre-migration Markdown bytes; the migration map and the
  post-migration `draft_sha256` are recorded in
  `results/run_logs/p7i05_rekey.json`. The Phase 6 review record
  intentionally remains tied to the original `draft_sha256`, so
  the Phase 6 review gate now requires honest human reapproval
  against the migrated Markdown before any LaTeX conversion may
  proceed.
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

### 2026-06-16 — Phase 9 LaTeX assembly pipeline integration (P9-I01..P9-I14)

- **Date:** 2026-06-16.
- **Tool / model:** Claude Code (Sonnet 4.6) drove the integration.
  No LLM generated LaTeX content; all rendering is deterministic
  from a pre-built workpack of 22 Python modules.
- **Purpose:** integrate the Phase 9 deterministic Markdown→LaTeX
  assembly pipeline into `src/agentic_publishing_pipeline/latex/`,
  wire it into the application CLI, add tests, and document upstream
  input blockers precisely.
- **Inputs:** workpack at
  `/Users/evyatar/Desktop/agentic_publishing_phase9_adapted_current_repo/`;
  verified repository APIs in `runtime/`, `contracts/`, `tools/`,
  `crews/_review_gate.py`.
- **Outputs:**
  - 22 production modules in `src/agentic_publishing_pipeline/latex/`
    (`approval_loader`, `asset_plan`, `assets_figures`, `assets_math`,
    `assets_table`, `bibliography`, `config_loader`, `config_models`,
    `file_plan`, `hebrew`, `inline`, `markdown_renderer`, `materialize`,
    `metadata`, `outline`, `phase9_runner`, `preflight`,
    `project_renderer`, `project_spec`, `standalone`, `templates`);
  - updated `src/agentic_publishing_pipeline/latex/__init__.py`;
  - `src/agentic_publishing_pipeline/crews/_phase9_assemble.py`;
  - `assemble-phase9` mode wired into existing CLI;
  - `config/latex/phase9_project.yaml`;
  - `scripts/render_latex_project.py`;
  - 9 test files in `tests/latex/` (19 tests, all passing).
- **Human verification:** all 506 tests pass; ruff clean; line cap
  passes; `check_latex_structure.py` passes. Preflight correctly
  reports upstream blocker: review record SHA mismatch (current
  Markdown draft has drifted from the approval snapshot).
- **Cost / token estimate:** $0.00; zero external-provider tokens.
  Only Claude Code assisted the integration; no LLM generated
  content or LaTeX source.
- **Outcome:** PHASE 9 IMPLEMENTATION INTEGRATED — UPSTREAM INPUT BLOCKED.
  Exact blocker: `HumanReviewRequired: Draft set has changed since
  approval was recorded. Recorded SHA=a137339da7d1…, current
  SHA=bf12df6edf1f…`. The missing chapters (introduction, retrieval,
  tool_use, multimodal, evaluation, conclusion) must be generated and
  a new review record written before the LaTeX source tree can be
  produced.

### 2026-06-17 — Phase 10 PDF build pipeline (P10-I01, P10-I02)

- **Date:** 2026-06-17.
- **Tool / model:** Claude Code (Sonnet 4.6) implemented the build
  infrastructure. No LLM generated LaTeX content; all PDF content
  derives from the deterministic Phase 9 LaTeX source tree.
- **Purpose:** implement the multi-pass LuaLaTeX → biber → makeindex →
  LuaLaTeX → LuaLaTeX build driver (`scripts/build_pdf.py`) and produce
  `results/final.pdf` from `latex_project/`.
- **Inputs:** `latex_project/` tree from Phase 9; LuaLaTeX (TeX Live 2025
  with David CLM Hebrew font); biber 2.21; makeindex.
- **Outputs:**
  - `scripts/build_pdf.py` — multi-pass build driver with logging, fatal-error
    detection, and structured log output to `results/run_logs/`.
  - `results/final.pdf` — 21-page PDF produced by LuaLaTeX pass 3.
  - `latex_project/preamble.tex` — two fixes applied: `imakeidx` option
    `intoc` moved from package load to `\makeindex[intoc]` (TeX Live 2025
    API change); `\headheight` raised to 14 pt to silence fancyhdr warning.
  - `.gitignore` additions: `.nlo`, `.nls`, `.idx`, `.ind`, `.ilg` extensions
    for nomenclature/index auxiliary files; `latex_project/main.pdf` for the
    in-place intermediate PDF.
- **Human verification:** `pdfinfo results/final.pdf` confirms 21 pages
  (exceeds 15-page minimum). PDF opens cleanly. Nomenclature (4 symbols),
  bibliography (10 entries), and index (21 terms) all render.
- **Cost / token estimate:** $0.00; zero external-provider tokens. Only
  Claude Code assisted; no LLM generated content or LaTeX source.
- **Outcome:** PHASE 10 COMPLETE. `results/final.pdf` exists, 21 pages, all
  structural requirements satisfied (cover, TOC, chapters, headers/footers,
  Hebrew BiDi, TikZ, graph, table, equation with \\eqref, theorem environments,
  bibliography, nomenclature, index).

### 2026-06-17 — Phase 11 ValidatorService (P11-I01..P11-I06)

- **Date:** 2026-06-17.
- **Tool / model:** Claude Code (Sonnet 4.6) implemented the service.
  Zero LLM calls anywhere in the validator; all checks are deterministic.
- **Purpose:** implement the `ValidatorService` class (P11-I01..I06) that
  runs repository file checks, LaTeX structure checks, PDF content
  indicators, and citation validation — then writes a human-readable
  Markdown report.
- **Inputs:** repository file tree; `pdfinfo` (poppler-utils); `latex_project/`
  source.
- **Outputs:**
  - `src/agentic_publishing_pipeline/validation/validator_service.py`
  - `src/agentic_publishing_pipeline/validation/checks_repo.py`
  - `src/agentic_publishing_pipeline/validation/checks_latex.py`
  - `src/agentic_publishing_pipeline/validation/checks_pdf.py`
  - `src/agentic_publishing_pipeline/validation/checks_citations.py`
  - `src/agentic_publishing_pipeline/validation/report.py`
  - `src/agentic_publishing_pipeline/validation/__main__.py`
  - `.env-example` (FR-4 — was missing)
  - Validation report written to `results/run_logs/validation_report_<ts>.md`
- **Human verification:** `uv run python -m agentic_publishing_pipeline.validation`
  exits 0 with Overall: PASS (35 checks, all passing).
- **Cost / token estimate:** $0.00; zero external-provider tokens.
- **Outcome:** PHASE 11 COMPLETE. ValidatorService operational; all P11-I01..I06
  checks implemented and passing on the real repository.

### 2026-06-17 — Phase 12 tests for ValidatorService (P12-I03, P12-I04)

- **Date:** 2026-06-17.
- **Tool / model:** Claude Code (Sonnet 4.6) added the test file.
- **Purpose:** implement P12-I03 (tests for ValidatorService) and verify P12-I04
  (ruff clean, ≥85% coverage).
- **Inputs:** `tests/unit/test_validator_service.py` (new); existing test suite
  (521 tests).
- **Outputs:**
  - `tests/unit/test_validator_service.py` — 14 tests covering CheckResult,
    ValidationReport, repo checks, LaTeX FR-17a-d separation checks, citation
    resolution, and an integration smoke test against the real repository.
- **Human verification:** `uv run pytest` → 521 passed, 1 skipped; 88% coverage;
  `uv run ruff check .` → All checks passed.
- **Cost / token estimate:** $0.00; zero external-provider tokens.
- **Outcome:** P12-I03 and P12-I04 complete. Coverage gate (≥85%) maintained.
