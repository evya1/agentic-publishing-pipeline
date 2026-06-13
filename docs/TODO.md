# TODO — agentic-publishing-pipeline

> **Status:** scaffold-stage only. Almost every box below is unchecked **by
> design**. Do not tick an item until its underlying artifact exists and
> has been verified on disk (and, where applicable, by a passing build,
> test, or validator run). The only ticked items live in §A and reflect
> scaffold pieces that physically exist.

## How to read this file

- This file is the **concrete task backlog** for the project. Each item is
  traceable to a requirement in [`docs/PRD.md`](PRD.md) via an `[FR-…]`,
  `[NFR-…]`, `[KPI]`, or `[AC §…]` tag, or to a phase in
  [`docs/PLAN.md`](PLAN.md) via a `[Phase N]` tag.
- The phased roadmap lives in [`docs/PLAN.md`](PLAN.md). This file does not
  duplicate the roadmap — it lists the discrete work needed to discharge
  it.
- GitHub Issues will later mirror these items (see §F). Keep TODO wording
  intact when filing issues so titles remain traceable.

## A. Already completed scaffold work *(verified on disk)*

- [x] Repository tree, `.gitignore`, `pyproject.toml` (uv-managed, dev
      group only). [Phase 0]
- [x] Placeholder Python package tree at
      `src/agentic_publishing_pipeline/` with the seven subpackages
      `agents/`, `tasks/`, `crews/`, `tools/`, `latex/`, `validation/`,
      `visualization/` (each with `__init__.py` and a README). [Phase 0]
- [x] Placeholder artifact directories: `content/`,
      `content/markdown_drafts/` (transitional), `latex_project/`
      (`chapters/`, `figures/`, `tables/`, `styles/`), `assets/`,
      `results/`, `submission/`. [Phase 0]
- [x] Smoke test `tests/test_scaffold.py` (import-only). [Phase 0]
- [x] Scaffold docs **exist** (not necessarily aligned — see §B):
      `README.md`, `SUBMISSION_CHECKLIST.md`, `CLAUDE.md`, `docs/PRD.md`,
      `docs/HW3_REQUIREMENTS.md`, `docs/AI_USAGE.md`, `docs/PROMPTS.md`,
      and the four mechanism PRDs. [Phase 0]
- [x] Placeholder `latex_project/main.tex` (TODO-only template) and
      empty `latex_project/references.bib`. [Phase 0]

## B. Documentation and planning work *(open)*

These docs **exist** but **require update/review** to match the current
`docs/PRD.md`.

- [x] Reconcile `docs/PRD_crewai_pipeline.md` with `docs/PRD.md` §8.3:
      replace the 5-agent list with the eight agents (Researcher, Outline,
      Writer, Technical-Asset, Hebrew/BiDi, LaTeX, Bibliography,
      Reviewer); reflect FR-8 sequential default; reflect FR-40 / NFR-19
      deterministic validation after the Reviewer Agent. [Phase 1]
      [FR-5, FR-6, FR-8, FR-40, NFR-19, AC §14.5]
      *Done — commit `4e5517c`.*
- [x] Reconcile `docs/PRD_latex_generation.md` with `docs/PRD.md` §8.5:
      lock LuaLaTeX as the required MVP engine; record `David CLM` +
      `Latin Modern Roman` font preferences via `fontspec` + `polyglossia`;
      codify FR-17a–d separation of tables/TikZ into dedicated `.tex`
      files. [Phase 1] [FR-15..FR-20, FR-17a, FR-17b, FR-17c, FR-17d,
      AC §14.3] *Done — commit `4e5517c`.*
- [x] Reconcile `docs/PRD_pdf_validation.md` with `docs/PRD.md` FR-40 /
      NFR-19: validator is **deterministic**, runs after the Reviewer
      Agent, and is **not** an LLM source-of-truth. [Phase 1] [FR-34..FR-40,
      NFR-19, AC §14.5] *Done — commit `4e5517c`.*
- [x] Reconcile `docs/PRD_bibliography_and_citations.md` with
      `docs/PRD.md` §8.6: no fabricated sources; unresolved `\cite{...}`
      must surface as build-time errors. [Phase 1] [FR-33, AC §14.2]
      *Done — commit `4e5517c`.*
- [ ] Refresh `README.md` to point at the canonical Markdown path
      `results/generated_markdown/` (per FR-12 and §12.3), describe the
      8-agent flow, and call out LuaLaTeX + `David CLM` as a
      reproducibility prerequisite. [Phase 1, Phase 13]
- [ ] Refresh `SUBMISSION_CHECKLIST.md` so its bullets match the PRD
      §14 acceptance criteria one-for-one. [Phase 1] [AC §14.*]
- [ ] Decide whether to retire `content/markdown_drafts/` once Phase 6
      begins, or keep it as an alias of `results/generated_markdown/`.
      Record the decision in `docs/PRD_crewai_pipeline.md`. [Phase 1,
      Phase 6] [FR-12]
- [ ] Confirm `docs/HW3_REQUIREMENTS.md` still matches the official
      assignment text and capture any deltas in the PRDs. [Phase 1]

## B.5 Phase 1.5 — Demo topic and source manifest lock *(complete — commit `303a425`; downstream follow-ups tracked below and in §C.5)*

The default demo runtime topic and the arXiv source set were locked in
commit `303a425`. Items marked `[x]` are verified on disk; items
marked `[ ]` are downstream follow-ups owned by Phase 3 / Phase 7 and
do not block the Phase 1.5 lock.

- [x] Add `docs/PRD.md` §22 "Canonical Demo Article Topic" with the
      working title, target angle, scope, source-set summary, and
      manifest pointer; mark the topic as a runtime default
      (NFR-27), not a hardcoded implementation detail. [Phase 1.5]
- [x] Populate `config/article_sources.yaml` with one entry per source
      in the manifest: `citation_key` (provisional, `tbd…` prefix),
      `title`, `year`, `arxiv_id`, `arxiv_url`, `source_archive`,
      `intended_use`, and `verification: {status: unverified, ...}`.
      [Phase 1.5] [FR-19, FR-33]
- [x] Confirm the 10 arXiv archive files live under
      `data/sources/arxiv/source_zips/` locally and are gitignored
      (not staged, not committed). [Phase 1.5]
- [x] Update `data/sources/arxiv/README.md` so it reflects that
      archives are present locally while remaining gitignored.
      [Phase 1.5]
- [x] Confirm `.gitignore` covers `data/sources/arxiv/source_zips/`,
      `data/sources/arxiv/unpacked/`, `data/sources/arxiv/raw_eprint/`,
      `__pycache__/`, `*.pyc`, `.DS_Store`. [Phase 1.5]
- [ ] Populate `authors:` for each entry in
      `config/article_sources.yaml` once authoritative metadata
      (arXiv API or paper PDF metadata) is verified. No fabricated
      authors. [Phase 1.5 → Phase 7] [`docs/PRD_bibliography_and_citations.md`]
- [ ] Rekey provisional `tbd…` citation keys to the
      `authorYYYYkey` convention once authors are verified. Owned by
      the Bibliography Agent in Phase 7.
      [Phase 7] [`docs/PRD_bibliography_and_citations.md` §9]
- [ ] Resolve the remaining Phase 3 open questions (audience, depth
      target, BiDi balance, citation density target) and record them
      in `docs/PRD.md` §22 or §3. [Phase 3] [PRD §21 open questions]

## C. Future implementation work *(open)*

### C.1 Topic and scope

- [x] Lock the default demo article topic, the working title, and the
      arXiv source set in `docs/PRD.md` §22 and
      `config/article_sources.yaml`. [Phase 1.5]
- [ ] Decide audience, depth target, BiDi balance (mostly-English with
      one Hebrew BiDi section vs. balanced bilingual), and citation
      density target per chapter. [Phase 3] [PRD §21 open questions,
      PRD §22]

### C.2 CrewAI architecture and prompts

- [ ] Specify all eight agents from PRD §8.3 with explicit `role`, `goal`,
      `backstory`, and tools. [Phase 4] [FR-5, AC §14.5]
- [ ] Define ≥5 tasks with `description`, `expected_output`, `agent`, and
      `context`. At least three tasks must consume earlier task outputs
      via `context`. [Phase 4] [FR-6, KPI, AC §14.5]
- [ ] Confirm `Process` is sequential or justify any deviation in
      `docs/PRD_crewai_pipeline.md`. [Phase 4] [FR-8]
- [ ] Capture initial prompts (agent `backstory` + `goal`, task
      `description` + `expected_output`, tool prompts) verbatim in
      `docs/PROMPTS.md`. [Phase 4, Phase 13]

### C.3 Provider/service layer, configuration, and tools

- [ ] Implement a controlled provider/service layer for model and search
      calls. [Phase 5] [NFR-23, NFR-24]
- [ ] Add `.env-example` documenting required environment variables.
      [Phase 5] [FR-4, NFR-21]
- [ ] Load all secrets from `.env` only; never hardcode. [Phase 5]
      [FR-3, NFR-20]
- [ ] Add `crewai`, the chosen model SDK, the chosen search SDK, and
      `matplotlib` to `pyproject.toml` via `uv add` — one per tool as it
      is implemented, no speculative installs. [Phase 5]
- [ ] Implement agent tools under
      `src/agentic_publishing_pipeline/tools/`:
  - [ ] Search tool (real-source discovery). [Phase 5, Phase 7] [FR-5]
  - [ ] File I/O tool. [Phase 5]
  - [ ] Markdown conversion tool (used by the Markdown→LaTeX path).
        [Phase 5, Phase 9]
  - [ ] LaTeX compilation tool (LuaLaTeX + biber multi-pass). [Phase 5,
        Phase 10] [FR-20]
  - [ ] Graph generation tool. [Phase 5, Phase 8] [FR-29, FR-30]

### C.4 Markdown-first content pipeline

- [ ] Generate Markdown drafts at `results/generated_markdown/`. [Phase 6]
      [FR-11, FR-12, §12.3]
- [ ] Markdown drafts include headings, figure placeholders, table
      placeholders, equation placeholders, and citation placeholders.
      [Phase 6] [FR-13]
- [ ] Run the human review gate before any LaTeX conversion. [Phase 6]
      [FR-14, NFR-19]
- [ ] Record the run in `docs/AI_USAGE.md`. [Phase 6, Phase 13]

### C.5 Real-source and bibliography pipeline

- [ ] Define the source-collection policy and the verification procedure.
      [Phase 7] [`docs/PRD_bibliography_and_citations.md` §7]
- [ ] Consume `config/article_sources.yaml` from the Research Agent (T1)
      and the Bibliography Agent (T6) per
      `docs/PRD_crewai_pipeline.md` §6. [Phase 6, Phase 7]
- [ ] Verify each manifest entry: URL/DOI resolution, title/author/year
      cross-check, archive-file presence under
      `data/sources/arxiv/source_zips/`. Update
      `config/article_sources.yaml` `verification.status` to
      `verified` (or `rejected`) and record `verified_at` /
      `verified_by`. [Phase 7] [`docs/PRD_bibliography_and_citations.md` §7]
- [ ] Record the per-source audit trail (citation key → archive →
      verification method → timestamp / run id) in `docs/AI_USAGE.md`
      (or `docs/SOURCES.md` if that location is chosen).
      [Phase 7] [`docs/PRD_bibliography_and_citations.md` §8]
- [ ] Extract `.bib` entries from the verified arXiv sources into
      `latex_project/references.bib` (stable keys, no fabricated
      entries). [Phase 7] [FR-19, FR-33]
- [ ] Rekey provisional `tbd…` citation keys in
      `config/article_sources.yaml` and in any Markdown placeholders to
      the final `authorYYYYkey` convention. [Phase 7]
      [`docs/PRD_bibliography_and_citations.md` §9]
- [ ] Wire `\cite{...}` placeholders in Markdown drafts and resolve them
      into the LaTeX project so every citation links to a real `.bib`
      entry. [Phase 7, Phase 9] [FR-33, AC §14.2]
- [ ] Treat all archive contents under
      `data/sources/arxiv/source_zips/` and
      `data/sources/arxiv/unpacked/` as **untrusted external source
      material**: no LaTeX builds run from third-party archives, no
      code from archives is executed, and unpacked content is only
      read for metadata / citation extraction. [Phase 7] [security]

### C.6 Python graph generation pipeline

- [ ] Implement `src/agentic_publishing_pipeline/visualization/` and
      produce at least one graph image saved under
      `latex_project/figures/`, consumed by a chapter via
      `\includegraphics`. [Phase 8] [FR-29, FR-30, AC §14.2]

### C.7 LaTeX project assembly (LuaLaTeX MVP)

- [ ] Replace the placeholder `latex_project/main.tex` with a thin root
      that only `\input{}`s other files. [Phase 9] [FR-16]
- [ ] Create `preamble.tex` configured for LuaLaTeX with `fontspec` +
      `polyglossia`, `\setmainfont{Latin Modern Roman}`,
      `\newfontfamily\hebrewfont[Script=Hebrew]{David CLM}`. [Phase 9]
      [FR-20, §16.3]
- [ ] Create `macros.tex` with reusable math/notation commands.
      [Phase 9] [FR-18]
- [ ] Generate chapter files under `chapters/` — narrative text only.
      [Phase 9] [FR-23, NFR-6a]
- [ ] Put each substantial table in its own file under `tables/` and each
      TikZ figure in its own file under `figures/`; include them from
      chapters with `\input{...}`. [Phase 9] [FR-17a..FR-17d, AC §14.3]
- [ ] Include at least one image in the PDF. [Phase 9] [FR-28]
- [ ] Include at least one table (own `.tex` file, wrapped in a `table`
      environment with a caption). [Phase 9] [FR-31]
- [ ] Include at least one mathematical equation with a label, and
      reference it later with `\ref` / `\eqref`. [Phase 9] [FR-25, FR-32,
      AC §14.2]
- [ ] Include at least one theorem-like environment (`definition`,
      `theorem`, `lemma`, or `example`). [Phase 9] [FR-24, AC §14.2]
- [ ] Include at least one TikZ figure (e.g., simple automaton).
      [Phase 9] [AC §14.2]
- [ ] Configure headers and footers (e.g., `fancyhdr`). [Phase 9]
      [FR-21]
- [ ] Build a real cover/title page with topic, author/team, course, and
      date. [Phase 9] [FR-22, AC §14.2]
- [ ] Generate the table of contents. [Phase 9] [FR-22]
- [ ] Add a nomenclature section with at least two symbols. [Phase 9]
      [FR-26, AC §14.2]
- [ ] Add an index with at least one Hebrew term and one English term.
      [Phase 9] [FR-27, AC §14.2]
- [ ] Include at least one substantial Hebrew/English BiDi section with
      correct RTL alignment, embedded English technical terms, and
      readable Hebrew. [Phase 9] [§8.6, AC §14.4, NFR-28..NFR-31]

### C.8 PDF build

- [ ] Document and script the multi-pass build (LuaLaTeX → biber →
      LuaLaTeX → LuaLaTeX, plus `makeindex` /
      `makenomenclature` as needed). [Phase 10] [FR-20, §16.3]
- [ ] Produce `results/final.pdf` (≥15 pages). [Phase 10] [FR-38, KPI,
      AC §14.2]

## D. Future validation and submission work *(open)*

### D.1 Deterministic ValidatorService

- [ ] Implement `src/agentic_publishing_pipeline/validation/` as a
      deterministic `ValidatorService` that runs **after** the Reviewer
      Agent. The LLM must not be the source of truth. [Phase 11]
      [FR-40, NFR-19]
- [ ] Validate required repository files. [Phase 11] [FR-34, AC §14.1]
- [ ] Validate required LaTeX files (`main.tex`, `preamble.tex`,
      `macros.tex`, `references.bib`, chapters, `tables/`, `figures/`).
      [Phase 11] [FR-35, AC §14.3]
- [ ] Validate PDF content indicators where feasible: page count,
      bibliography presence, BiDi section presence, nomenclature, index,
      equation cross-reference, image/graph/table presence. [Phase 11]
      [FR-36, AC §14.2, AC §14.4]
- [ ] Validate every `\cite{...}` resolves to a `references.bib` entry,
      and that bibliography renders. [Phase 11] [FR-33, AC §14.2]
- [ ] Produce a human-readable validation report after the run.
      [Phase 11] [FR-37]

### D.2 Tests, lint, reproducibility

- [ ] Real unit tests for the provider layer and each tool. [Phase 12]
- [ ] Tests for `ValidatorService`. [Phase 12]
- [ ] Tests for the Markdown→LaTeX conversion. [Phase 12]
- [ ] `uv run pytest` passes on a clean checkout. [Phase 12]
- [ ] `uv run ruff check .` passes on a clean checkout. [Phase 12]
- [ ] README documents the LaTeX-distribution requirement (LuaLaTeX) and
      the `David CLM` Hebrew font requirement so reproduction is
      possible. [Phase 12, Phase 13]

### D.3 Documentation finalization

- [ ] Update `README.md` to describe the running system: installation,
      configuration, the 8-agent flow, run commands, LaTeX build
      commands, and limitations. [Phase 13] [AC §14.1]
- [ ] Fill `docs/AI_USAGE.md` with the real run history (model, prompts
      summary, outputs, human verification, cost). [Phase 13]
- [ ] Fill `docs/PROMPTS.md` with the actual prompts used in the run.
      [Phase 13]

### D.4 Final submission packaging

- [ ] Prepare the Moodle wrapper PDF from the official template.
      [Phase 14]
- [ ] Verify the `<GROUP_CODE>-ex03.pdf` filename convention.
      [Phase 14]
- [ ] Confirm each group member submits separately in Moodle.
      [Phase 14]
- [ ] Verify every checkbox in `SUBMISSION_CHECKLIST.md` is satisfied
      individually. [Phase 14] [AC §14.*]

## E. Cross-cutting policies *(always apply, not phase-gated)*

- [ ] Every AI/LLM call is recorded in `docs/AI_USAGE.md` as it happens.
      [Phase 6, Phase 13]
- [ ] Every prompt is recorded verbatim in `docs/PROMPTS.md`.
      [Phase 4, Phase 13]
- [ ] No secrets committed; `.env` only. [Phase 5] [NFR-20, NFR-21]
- [ ] Python files stay ≤150 lines; long files are split by
      responsibility. [NFR-2]
- [ ] All functions have type hints including return types. [NFR-7]
- [ ] Inputs validated explicitly (e.g., `assert`). [NFR-13]
- [ ] DRY and minimal classes/moving parts; extract small named helpers
      instead of long inline blocks. [NFR-5, NFR-6, NFR-12]
- [ ] f-strings for interpolation; comprehensions only where they
      improve readability. [NFR-9, NFR-10]

## F. GitHub project management *(future, no GitHub changes in this documentation-rewrite pass)*

Mirror this plan into GitHub as the GUI tracking layer. **No issues or
milestones are created in this documentation-rewrite pass** — the actual
creation work belongs to Phase 2 below; this is not a permanent ban.

- [ ] Create one **GitHub Milestone** per open phase in `docs/PLAN.md`
      (Phases 2 through 14). Milestone titles match phase titles. Phases 0,
      1, and 1.5 do not get milestones because they are already complete.
      [Phase 2]
- [ ] Create **GitHub Issues** from every open item in §B, §C, §D, and
      §E above. Preserve the TODO wording in the issue title so the
      mapping back to this file is obvious. [Phase 2]
- [ ] Assign each issue to the milestone for its phase tag (e.g.,
      `[Phase 9]` items go to the "Phase 9 — LaTeX project assembly"
      milestone). [Phase 2]
- [ ] Apply labels from this fixed vocabulary as appropriate:
      `docs`, `architecture`, `crewai`, `latex`, `validation`, `bidi`,
      `bibliography`, `testing`, `submission`. [Phase 2]
- [ ] Document the mapping TODO ↔ issue ↔ milestone ↔ PRD requirement
      in this file's introduction once the issues are filed. [Phase 2]
- [ ] An issue may be closed **only** when the underlying artifact is
      verified on disk (or by a passing build, test, or validator run).
      Closing an issue does **not** by itself allow ticking a TODO box,
      a PRD acceptance-criterion checkbox in `docs/PRD.md` §14, a
      `docs/HW3_REQUIREMENTS.md` checkbox, or a `SUBMISSION_CHECKLIST.md`
      checkbox. [Phase 2, all later phases]
