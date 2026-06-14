# PRD — PDF Validation

> **Status:** design/specification only. No `ValidatorService`, no
> validator entry point, and no validation report exist yet. The current
> `src/agentic_publishing_pipeline/validation/` package holds only an
> `__init__.py` and a README. This document defines what will be built;
> checking any of its acceptance-criteria boxes requires the validator
> to exist on disk and to have produced a real report.

## 1. Scope and relationship to other documents

This PRD refines `docs/PRD.md` §8.7 (validation and output), FR-34 /
FR-35 / FR-36 / FR-37 / FR-39 / FR-40, NFR-16 / NFR-17 / NFR-18 /
NFR-19, §14.1 (course / repository acceptance criteria), §14.2 (PDF
content and structure), §14.3 (LaTeX acceptance criteria), §14.4 (BiDi
acceptance criteria), and §14.5 (CrewAI acceptance criteria — specifically
"the workflow runs deterministic validation after the Reviewer Agent
stage").

Sister mechanism PRDs:

- `docs/PRD_crewai_pipeline.md` — defines the Reviewer Agent as the
  last LLM stage and the deterministic `ValidatorService` as the
  non-agent stage that runs after it.
- `docs/PRD_latex_generation.md` — defines the LaTeX project structure
  and the multi-pass build whose outputs this validator inspects.
- `docs/PRD_bibliography_and_citations.md` — defines the citation /
  bibliography rules this validator enforces deterministically.

Planning and tracking:

- `docs/PLAN.md` — Phase 11 implements the `ValidatorService`.
- `docs/TODO.md` — concrete backlog with PRD requirement tags.
- `CLAUDE.md` — repository conventions; the "LLM is never the source of
  truth for validation" rule mirrors this PRD.

## 2. Problem

The HW3 deliverable must satisfy a precise list of structural,
content, LaTeX, BiDi, and workflow requirements. A qualitative
LLM review (the Reviewer Agent) cannot be the gate, because LLM
verdicts are not reproducible and not auditable. We need a
**deterministic** check that runs after the Reviewer Agent, inspects
files, build outputs, and PDF content, and emits a human-readable
report that names every missing or failing requirement.

## 3. Goals

- Implement a **deterministic** `ValidatorService` (FR-40, NFR-19) in
  `src/agentic_publishing_pipeline/validation/` as plain Python — **not**
  an LLM, not a CrewAI agent.
- Run the validator **after the Reviewer Agent** has finished (FR-40,
  AC §14.5).
- Check every requirement that can be mechanically verified: required
  repository files (FR-34, AC §14.1), required LaTeX files (FR-35,
  AC §14.3), generated artifacts, LaTeX build outputs, and PDF content
  indicators (FR-36, AC §14.2, AC §14.4).
- Enforce the FR-17a–d table / TikZ separation rules at the LaTeX
  source level.
- Enforce citation correctness (every `\cite{...}` resolves; bibliography
  rendered) per `docs/PRD_bibliography_and_citations.md`.
- Emit a **human-readable validation report** (FR-37) that names every
  failure and points at the file or PDF location to investigate.
- **Fail loud** on missing dependencies or required artifacts (FR-39).

## 4. Non-goals

- Subjective quality judgments (clarity, prose quality, argument
  strength) — those are the Reviewer Agent's job and remain advisory.
- Re-running the CrewAI workflow or the LaTeX build — the validator
  inspects existing artifacts; it does not trigger generation.
- Replacing manual human review for cases the validator cannot check
  mechanically (e.g., "does the prose make sense"). For those, the
  validator can at most warn and defer.

## 5. Architecture

- **Location:** `src/agentic_publishing_pipeline/validation/`.
- **Form:** plain Python. The validator is **not** a CrewAI agent, does
  **not** call an LLM, and does **not** depend on `crewai`.
- **Entry point:** a single documented entry point (e.g.,
  `python -m agentic_publishing_pipeline.validation` or a `uv run`
  alias documented in `README.md`).
- **Inputs:** the on-disk repository state plus the final PDF.
- **Outputs:** the validation report at
  `results/run_logs/validation_report.md` (or equivalent path fixed in
  Phase 11) and a non-zero exit code on any failure.

## 6. When the validator runs

- The validator runs **after the Reviewer Agent** stage of the CrewAI
  workflow completes (FR-40, AC §14.5).
- The validator is also runnable standalone from a documented
  command, so a developer can re-verify after a manual edit without
  re-running the whole CrewAI workflow.
- The validator is idempotent: running it twice on the same artifacts
  yields the same report.

## 7. Checks

Every check below is traced to the requirement it enforces. The check
list is the spec; the implementation order is decided in Phase 11.

### 7.1 Repository files (FR-34, AC §14.1)

- [ ] `README.md` exists at the repository root.
- [ ] `docs/PRD.md` exists.
- [ ] `docs/PLAN.md` exists.
- [ ] `docs/TODO.md` exists.
- [ ] `docs/PRD_crewai_pipeline.md` exists.
- [ ] `docs/PRD_latex_generation.md` exists.
- [ ] `docs/PRD_pdf_validation.md` exists.
- [ ] `docs/PRD_bibliography_and_citations.md` exists.
- [ ] `docs/AI_USAGE.md` exists.
- [ ] `docs/PROMPTS.md` exists.
- [ ] `.env-example` exists at the repository root (FR-4, NFR-21).
- [ ] `pyproject.toml` exists.
- [ ] `tests/` exists and contains at least one test file.
- [ ] `src/agentic_publishing_pipeline/` exists with the expected
      subpackages.

### 7.2 LaTeX project files (FR-35, AC §14.3)

- [ ] `latex_project/main.tex` exists.
- [ ] `latex_project/preamble.tex` exists.
- [ ] `latex_project/macros.tex` exists.
- [ ] `latex_project/references.bib` exists and is non-empty.
- [ ] `latex_project/chapters/` exists and contains at least two
      chapter `.tex` files.
- [ ] `latex_project/tables/` exists and contains at least one table
      `.tex` file (FR-31, FR-17a).
- [ ] `latex_project/figures/` exists and contains at least one TikZ
      `.tex` file and at least one image file (FR-29, FR-30, FR-17b,
      AC §14.2).

### 7.3 FR-17a–d table and TikZ separation enforcement

- [ ] No chapter file under `latex_project/chapters/` contains a
      `\begin{table}` ... `\end{table}` or `\begin{tabular}` ...
      `\end{tabular}` environment (table source belongs in
      `tables/*.tex`; FR-17a, FR-17d).
- [ ] No chapter file under `latex_project/chapters/` contains a
      `\begin{tikzpicture}` ... `\end{tikzpicture}` environment (TikZ
      source belongs in `figures/*.tex`; FR-17b, FR-17d).
- [ ] Chapter files use `\input{tables/...}` / `\input{figures/...}`
      to include their tables and TikZ figures (FR-17c).
- [ ] `main.tex` contains no narrative paragraphs (thin-root rule,
      `docs/PRD_latex_generation.md` §7).

### 7.4 Generated intermediate artifacts (NFR-16, NFR-17)

- [ ] `results/generated_markdown/` exists and contains at least one
      Markdown draft (FR-11, FR-12, AC §14.5).
- [ ] `results/run_logs/` exists and contains at least one log or run
      summary (NFR-16).
- [ ] At least one Python-generated graph file exists under
      `latex_project/figures/` (FR-29, FR-30).

### 7.5 LaTeX build (FR-20, AC §14.3)

- [ ] A `results/final.pdf` exists (FR-38).
- [ ] The build was performed with LuaLaTeX (recorded in
      `results/run_logs/` or in PDF metadata; AC §14.3).
- [ ] No catastrophic build errors are present in the LuaLaTeX log
      under `latex_project/` (FR-39 / NFR-18). Unresolved citations,
      missing references, or font-substitution warnings are
      surfaced as failures, not warnings.

### 7.6 PDF content indicators (FR-36, AC §14.2)

The validator extracts text and structural indicators from
`results/final.pdf` (e.g., via `pdftotext` or a Python PDF library
chosen in Phase 11) and checks:

- [ ] Page count is **at least 15 pages, target 15–20 pages**
      (KPI, AC §14.2).
- [ ] A cover/title page is present with topic, author/group, date,
      and course context (AC §14.2).
- [ ] A table of contents is present (FR-22, AC §14.2).
- [ ] Headers and footers appear on body pages (FR-21, AC §14.2).
- [ ] At least one image is embedded (FR-28, AC §14.2).
- [ ] At least one Python-generated graph is embedded (FR-29, FR-30,
      AC §14.2).
- [ ] At least one TikZ figure renders (AC §14.2).
- [ ] At least one table is rendered (FR-31, AC §14.2).
- [ ] At least one mathematical equation is rendered (AC §14.2).
- [ ] At least one equation has a label and is cross-referenced with
      `\ref` or `\eqref` (FR-25, FR-32, AC §14.2). The validator can
      verify this at the LaTeX-source level by matching a labeled
      `equation`/`align` environment against a corresponding `\ref` /
      `\eqref` later in the sources.
- [ ] At least one theorem-like environment (`definition`, `theorem`,
      `lemma`, `example`) appears (FR-24, AC §14.2).
- [ ] A nomenclature section with at least two symbols appears near the
      end (FR-26, AC §14.2).
- [ ] An index with at least one Hebrew term and at least one English
      term appears near the end (FR-27, AC §14.2).
- [ ] Text is selectable in the PDF (not rendered as image-only).

### 7.7 BiDi indicators (AC §14.4)

- [ ] At least one section in the PDF contains Hebrew text.
- [ ] For the canonical HW3 run, the substantial Hebrew/English BiDi
      section is present in the configured **Memory** chapter, per
      `docs/PRD.md` §22.8. Generic runs validate the selected BiDi host
      from configuration and do not assume Memory unless that is the
      configured host.
- [ ] At least one Hebrew paragraph contains embedded English technical
      terms (best-effort check: Hebrew Unicode characters and ASCII
      characters in the same paragraph).
- [ ] Hebrew text is present in `David CLM` per `preamble.tex`
      configuration (validated at the LaTeX-source level; the
      validator does not inspect rendered glyph metrics).
- [ ] Fonts configured in `preamble.tex` match the PRD requirement
      (`David CLM` for Hebrew, `Latin Modern Roman` for English) per
      `docs/PRD_latex_generation.md` §5.2.

### 7.8 Bibliography and citations (FR-33, AC §14.2)

Delegated to `docs/PRD_bibliography_and_citations.md`; the validator
enforces these deterministically.

- [ ] Every `\cite{...}` in the LaTeX sources resolves to an entry in
      `latex_project/references.bib`.
- [ ] The selected source manifest is loaded and checked before
      citation-coverage validation. Generic runs validate against their
      selected verified manifest and must not assume every run has ten
      sources.
- [ ] For the canonical HW3 run, every one of the ten configured
      canonical manifest sources is cited at least once across the
      complete final article. This can be checked deterministically by
      comparing the selected manifest entries with the resolved
      citation keys in the LaTeX sources.
- [ ] The canonical HW3 run targets approximately 2–3 relevant verified
      sources per chapter as a balance check; justified variation is
      allowed and the validator must not enforce it as an exact per-
      chapter count.
- [ ] A rendered bibliography section is present in the PDF.
- [ ] Citations are present in the body text (the body contains
      `\cite{...}` commands and the rendered PDF shows their resolved
      forms).
- [ ] Unresolved citations are reported as **errors**, not warnings.

### 7.9 Configuration and security

- [ ] No file under version control contains a hardcoded API key or
      `.env`-style secret pattern (best-effort regex check) (NFR-20).
- [ ] `.env-example` lists at least the model-provider and search-API
      variables expected by the provider/service layer (FR-4, NFR-21).

## 8. Validation report (FR-37)

- **Format:** human-readable Markdown.
- **Path:** `results/run_logs/validation_report.md` (or a path fixed in
  Phase 11 and recorded back here).
- **Structure:** one section per check group from §7. Each failure
  names:
  - the failing requirement (e.g., `FR-26 — nomenclature ≥2 symbols`);
  - the file / PDF location to investigate;
  - what was expected vs. what was found.
- **Summary line:** an overall pass/fail and the number of checks
  passed / failed / skipped.
- **Exit code:** zero only when every required check passes; non-zero
  otherwise (FR-39).

## 9. Failure semantics

- The validator does not attempt to fix anything.
- The validator does not delegate any decision to an LLM (NFR-19).
- Missing required dependencies (LuaLaTeX, `biber`, `David CLM`,
  Python packages) are surfaced as actionable errors that name the
  missing dependency and the install hint (FR-39, NFR-18).
- Warnings (e.g., "every `.bib` entry should ideally be cited") are
  printed but do not fail the run, unless they correspond to a hard
  requirement.

## 10. Open decisions to capture during implementation

- **PDF library.** `pdftotext` (poppler) vs. `pypdf` vs. `pdfplumber`
  for text and structure extraction. Fixed in Phase 11.
- **Validation report path.** `results/run_logs/validation_report.md`
  is the default; confirm during Phase 11.
- **CI integration.** Whether the validator runs in CI as well as
  locally. Likely a Phase 12 / Phase 13 concern.

## 11. Acceptance criteria

These trace back to `docs/PRD.md` §14.1, §14.2, §14.3, §14.4, §14.5,
FR-34 / FR-35 / FR-36 / FR-37 / FR-39 / FR-40, and NFR-19.
**None of these may be ticked until the validator exists on disk and
has produced a real report against real artifacts.**

- [ ] A deterministic `ValidatorService` is implemented in
      `src/agentic_publishing_pipeline/validation/`; it is plain
      Python, calls no LLM, and depends on no LLM SDK (FR-40, NFR-19).
- [ ] The validator runs from a single documented entry point.
- [ ] The validator runs **after the Reviewer Agent stage** of the
      CrewAI workflow (FR-40, AC §14.5).
- [ ] The validator is runnable standalone from a documented command
      so a developer can re-verify after a manual edit.
- [ ] The validator implements every check group in §7.1–§7.9 and ties
      each check to its source requirement.
- [ ] The validator produces a human-readable Markdown report at the
      documented path (FR-37).
- [ ] The validator exits non-zero on any failure (FR-39).
- [ ] Missing dependencies are surfaced as actionable errors (FR-39,
      NFR-18).
- [ ] The LLM is **never** the source of truth for any check (NFR-19).
- [ ] Page-count check uses **≥15 pages, target 15–20 pages** (KPI,
      AC §14.2).
- [ ] FR-17a–d separation is enforced: chapter files contain no inline
      `table` / `tabular` / `tikzpicture` environments.
- [ ] Every `\cite{...}` resolves to a `references.bib` entry, per
      `docs/PRD_bibliography_and_citations.md`.
