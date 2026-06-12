# PRD — LaTeX Generation

> **Status:** design/specification only. No LaTeX content, no
> `preamble.tex` / `macros.tex` / chapter files, no PDF, and no build
> scripts have been implemented yet. The current
> `latex_project/main.tex` is a TODO-only placeholder; `references.bib`
> is empty. This document defines what will be built; checking any of
> its acceptance-criteria boxes requires the corresponding artifact to
> exist on disk and the LuaLaTeX build to succeed.

## 1. Scope and relationship to other documents

This PRD refines `docs/PRD.md` §5.2 (LaTeX engineering goals), §5.3
(BiDi goals), §8.5 (LaTeX generation requirements), §8.6 (assets,
figures, tables, references), §12.3 (final outputs), §14.3 (LaTeX
acceptance criteria), §14.4 (BiDi acceptance criteria), §16.2–§16.3
(system and LaTeX dependencies), and §17 (constraints).

Sister mechanism PRDs:

- `docs/PRD_crewai_pipeline.md` — the workflow that produces the
  reviewed Markdown drafts this PRD consumes.
- `docs/PRD_bibliography_and_citations.md` — the source of
  `references.bib` entries this PRD's build pulls from.
- `docs/PRD_pdf_validation.md` — the deterministic `ValidatorService`
  that runs after the build and checks the project structure and PDF
  content.

Planning and tracking:

- `docs/PLAN.md` — Phase 9 assembles the LaTeX project; Phase 10 runs
  the multi-pass PDF build.
- `docs/TODO.md` — concrete backlog with PRD requirement tags.
- `CLAUDE.md` — repository conventions; the LaTeX conventions there
  mirror this PRD.

## 2. Problem

The final deliverable is a polished, ≥15-page PDF article composed of
multiple internal `.tex` files, with mathematics, theorem-like
environments, a Python-generated graph, a TikZ figure, a table, an
image, a nomenclature section, an index, a bibliography, and at least
one substantial Hebrew/English BiDi section. The LaTeX project must be
structured the way a small research group would maintain it: a thin
root, chapter files focused on narrative, tables and TikZ figures kept
out of the chapter source, and a single deterministic build path. This
PRD specifies how the reviewed Markdown drafts become that LaTeX project
and how the project compiles into the final PDF.

## 3. Goals

- Lock **LuaLaTeX** as the **required MVP engine** (FR-20, §17).
- Lock fonts: **`David CLM`** for Hebrew, **`Latin Modern Roman`** for
  English, via **`fontspec` + `polyglossia`** (`docs/PRD.md` §16.3).
- Enforce **`main.tex` as a thin root** that `\input{}`s every other
  file (`docs/PRD.md` §8.5, CLAUDE.md).
- Enforce **FR-17a–d**: chapter files contain narrative text only;
  tables live in `tables/*.tex`; TikZ figures live in `figures/*.tex`;
  chapters include them via `\input{...}`.
- Cover every required content element: image, Python-generated graph,
  TikZ figure, table, labeled equation cross-referenced with `\ref` /
  `\eqref`, theorem-like environment, nomenclature (≥2 symbols), index
  (≥1 Hebrew term + ≥1 English term), headers/footers, title page, TOC,
  substantial Hebrew/English BiDi section.
- Build the final PDF deterministically into **`results/final.pdf`**
  (FR-38, §12.3) using a documented multi-pass command sequence.

## 4. Non-goals

- Producing the actual chapter content — that comes from the Markdown
  drafts in `results/generated_markdown/` (see
  `docs/PRD_crewai_pipeline.md`).
- Maintaining bibliography entries — see
  `docs/PRD_bibliography_and_citations.md`.
- Running the validator — see `docs/PRD_pdf_validation.md`.
- Supporting every TeX distribution. The README will document a known
  working setup (LuaLaTeX from TeX Live or MacTeX, plus `biber` and the
  required fonts).

## 5. Engine and fonts

### 5.1 Engine

- **LuaLaTeX is the required MVP engine** (FR-20). All templates, build
  scripts, README commands, and validator checks target LuaLaTeX.
- **XeLaTeX** is at most an optional later fallback. It is not the
  default for anything and must not silently replace LuaLaTeX in the
  build.
- **Bibliography processing**: `biber` (preferred, per `biblatex`
  configuration). `bibtex` is acceptable only if a future revision of
  `docs/PRD_bibliography_and_citations.md` justifies the switch.

### 5.2 Fonts (`docs/PRD.md` §16.3)

- Main / English font: **`Latin Modern Roman`**
- Hebrew font: **`David CLM`**
- Math font: default LaTeX math font is acceptable for the MVP unless a
  dedicated Unicode math font is added later.
- Code font: default monospace font is acceptable for the MVP.

The `preamble.tex` template uses `fontspec` + `polyglossia`:

```latex
\usepackage{fontspec}
\usepackage{polyglossia}

\setdefaultlanguage{hebrew}
\setotherlanguage{english}

\setmainfont{Latin Modern Roman}
\newfontfamily\hebrewfont[Script=Hebrew]{David CLM}
\newfontfamily\englishfont[Script=Latin]{Latin Modern Roman}
```

If `David CLM` is not available on the local machine, the build must
fail with a clear LuaLaTeX error, or use a documented fallback Hebrew
font that is recorded in `README.md`. Silent font substitution is not
acceptable.

## 6. Project layout

The structured LaTeX project lives under `latex_project/`. The MVP
layout:

```
latex_project/
  main.tex                # thin root, \input{}s everything
  preamble.tex            # packages, fonts, language, theorem setup
  macros.tex              # reusable math/notation commands
  references.bib          # bibliography (owned by Bibliography Agent)
  chapters/
    01_intro.tex
    02_*.tex              # narrative text only; \input{} tables / TikZ
    ...
  tables/
    <table_name>.tex      # one substantial table per file
  figures/
    <tikz_name>.tex       # one TikZ figure per file
    <graph_name>.{pdf,png,jpg}   # Python-generated graph images
    <image_name>.{pdf,png,jpg}   # static images
```

The current `latex_project/main.tex` is a TODO-only placeholder; it is
replaced in Phase 9 by the thin root described in §7.

## 7. `main.tex` — thin-root rule (FR-16, §8.5)

`main.tex` only:

- declares the document class and the engine-specific configuration
  (loaded via `\input{preamble.tex}`);
- pulls in macros (`\input{macros.tex}`);
- includes chapters one by one via `\input{chapters/NN_*.tex}`;
- includes back-matter (bibliography, nomenclature, index).

`main.tex` contains **no narrative text, no table environments, no TikZ
pictures, no inline `\begin{equation}` blocks**. Anything substantial
lives in a dedicated file and is included by `\input{...}`.

## 8. Chapter files

Chapter files under `chapters/` hold narrative text and high-level
`\input{...}` calls only. Concretely:

- Hebrew/English BiDi section text is allowed inline.
- Inline math (e.g., `$E = mc^2$`) is allowed inline.
- Short display equations (1–3 lines) are allowed inline.
- **Table environments must not be inlined.** Each substantial table
  lives in its own file under `tables/` and is included with
  `\input{tables/<name>.tex}` (FR-17a, FR-17c, FR-17d, NFR-6a).
- **TikZ pictures must not be inlined.** Each TikZ figure lives in its
  own file under `figures/` and is included with
  `\input{figures/<name>.tex}` (FR-17b, FR-17c, FR-17d, NFR-6a).
- Regular `\includegraphics` images may use a short `figure` wrapper
  inside the chapter file when that is more readable (FR-17d).

## 9. Tables (FR-31)

- Each substantial table lives in its own `.tex` file under
  `latex_project/tables/`.
- The table source is wrapped in a `table` environment with a caption
  and a label.
- The chapter `\input{tables/<name>.tex}` at the position where the
  table belongs.
- At least one table appears in the final PDF (FR-31, AC §14.2).

## 10. Figures and graphs (FR-28, FR-29, FR-30)

- **Image (FR-28).** At least one regular image is included via
  `\includegraphics` from a short `figure` wrapper in its chapter.
- **Python-generated graph (FR-29, FR-30).** The
  `src/agentic_publishing_pipeline/visualization/` package generates at
  least one graph image saved under `latex_project/figures/`. A `figure`
  wrapper in the corresponding chapter `\includegraphics` it.
- **TikZ figure (AC §14.2, FR-17b).** At least one TikZ figure (e.g., a
  simple automaton) lives in its own `.tex` file under
  `latex_project/figures/` and is included from a chapter via
  `\input{figures/<name>.tex}`.

## 11. Equations, theorems, and macros

- **`macros.tex` (FR-18).** Holds reusable mathematical and notational
  commands used across chapters.
- **At least one labeled equation (FR-25, FR-32, AC §14.2).** The
  equation has a `\label{...}` and is later referenced from the text
  with `\ref{...}` or `\eqref{...}`.
- **At least one theorem-like environment (FR-24, AC §14.2).** One of
  `definition`, `theorem`, `lemma`, or `example`. Configured via
  `amsthm` or `thmtools` in `preamble.tex`.

## 12. Hebrew/English BiDi section (`docs/PRD.md` §5.3, §8.6, §14.4)

- At least one substantial section mixes Hebrew and English text.
- Hebrew paragraphs are right-aligned; English technical terms inside
  Hebrew sentences preserve correct character order (NFR-28, NFR-29,
  NFR-30).
- Fonts: `David CLM` for Hebrew and `Latin Modern Roman` for English,
  configured via `fontspec` + `polyglossia` (§5.2, NFR-31).
- The example target sentence from `docs/PRD.md` §14.4 should render
  cleanly in the final PDF:
  > בפרק זה אנו מתארים את המושג Agent Runtime ואת הקשר שלו ל־Observability,
  > כאשר המערכת משתמשת ב־CrewAI כדי לנהל תהליך כתיבה מודולרי.

## 13. Headers, footers, title page, TOC

- **Headers and footers (FR-21).** Configured via `fancyhdr` (or
  equivalent) in `preamble.tex` and applied to body pages.
- **Title page (FR-22).** Includes topic, author / group, date, and
  course context.
- **Table of contents (FR-22).** Generated by `\tableofcontents` from
  `main.tex`.

## 14. Nomenclature and index

- **Nomenclature (FR-26).** A nomenclature section near the end of the
  document lists **at least two symbols** used in the article.
  Configured via `nomencl` (or equivalent) in `preamble.tex`; built with
  `makenomenclature` (or `makeindex` against the nomenclature file).
- **Index (FR-27).** An index near the end of the document includes
  **at least one Hebrew term and at least one English term**.
  Configured via `makeidx` (or equivalent); built with `makeindex`.

## 15. Markdown → LaTeX flow

- The LaTeX Agent consumes the reviewed Markdown drafts from
  **`results/generated_markdown/`** (canonical, per FR-12 and §12.3).
- A human review gate runs before the LaTeX Agent starts assembling the
  project (see `docs/PRD_crewai_pipeline.md` §10).
- The exact converter (custom Python, `pandoc`, CrewAI tool-driven) is
  fixed in Phase 9 and recorded back into this section. Whatever the
  choice, it must preserve:
  - heading structure → chapter sectioning;
  - figure placeholders → `\includegraphics` or `\input{figures/...}`;
  - table placeholders → `\input{tables/...}`;
  - equation placeholders → labeled equations consumed by `\ref` /
    `\eqref`;
  - citation placeholders → `\cite{...}` keys that resolve into
    `references.bib`.

## 16. Build pipeline (FR-20, FR-38, §16.3)

- Output: **`results/final.pdf`** (FR-38, §12.3).
- Multi-pass build sequence (MVP):

  ```sh
  lualatex --interaction=nonstopmode main.tex
  biber main
  makeindex main.idx               # for the index
  makeindex main.nlo -s nomencl.ist -o main.nls   # for nomenclature
  lualatex --interaction=nonstopmode main.tex
  lualatex --interaction=nonstopmode main.tex
  ```

- The exact commands and any wrapping script (`Makefile`, `justfile`,
  Python tool) are documented in `README.md` once Phase 10 lands.
- Intermediate artifacts (`*.aux`, `*.bbl`, `*.idx`, `*.ind`, `*.nlo`,
  `*.nls`, `*.toc`, etc.) are gitignored.
- The build does **not** assume a TeX distribution is installed; the
  README must call out LuaLaTeX, `biber`, `makeindex`, and the `David
  CLM` font as prerequisites.

## 17. Required LaTeX packages (per `docs/PRD.md` §16.3)

The MVP loads only the packages required for stable LuaLaTeX builds:

- Engine and language: `fontspec`, `polyglossia`.
- Math and theorems: `amsmath`, `amssymb`, `amsthm` (or `thmtools`),
  `mathtools` (optional).
- Figures and diagrams: `graphicx`, `float`, `tikz`, `pgfplots` (when
  used).
- Tables: `booktabs`.
- Cross-references and links: `hyperref`, `cleveref`.
- Layout: `geometry`, `fancyhdr`.
- Code blocks (if used): `listings`.
- Back-matter: `biblatex` (with `biber` backend), `nomencl`, `makeidx`.
- Utilities: `etoolbox`, `xparse` (as needed).

Advanced styling (custom theorem colors, TikZ-heavy diagrams, custom
math symbols, page-aware Hebrew references) is treated as optional
template extension and not a hard requirement.

## 18. Page-count requirement

The final PDF is **at least 15 pages, target 15–20 pages**
(`docs/PRD.md` KPI, AC §14.2). The validator enforces this; see
`docs/PRD_pdf_validation.md`.

## 19. Acceptance criteria

These mirror the LaTeX acceptance criteria in `docs/PRD.md` §14.3 and
the BiDi acceptance criteria in §14.4. **None of these may be ticked
until the underlying artifact exists on disk and the build succeeds.**

### 19.1 Project structure (§14.3)

- [ ] `main.tex` exists and is a thin root that `\input{}`s every other
      file (no narrative text, no inline tables, no inline TikZ).
- [ ] `preamble.tex` exists and configures `fontspec` + `polyglossia`,
      the fonts (`Latin Modern Roman`, `David CLM`), theorem
      environments, headers/footers, nomenclature, and index.
- [ ] `macros.tex` exists and holds reusable math/notation commands
      (FR-18).
- [ ] Chapters live under `chapters/` as separate `.tex` files.
- [ ] Tables live under `tables/` as one `.tex` file per substantial
      table, included from chapters via `\input{...}` (FR-17a, FR-17c,
      FR-17d).
- [ ] TikZ figures live under `figures/` as one `.tex` file per TikZ
      picture, included from chapters via `\input{...}` (FR-17b,
      FR-17c, FR-17d).
- [ ] Chapter files contain no long table environments and no inline
      TikZ pictures (FR-17d, NFR-6a).
- [ ] `references.bib` exists (FR-19, sourced from
      `docs/PRD_bibliography_and_citations.md`).

### 19.2 Required content (§14.2 / §14.3)

- [ ] Title page with topic, author/group, date, and course context
      (FR-22).
- [ ] Table of contents (FR-22).
- [ ] Headers and footers on body pages (FR-21).
- [ ] At least one image included via `\includegraphics` (FR-28).
- [ ] At least one Python-generated graph saved under
      `latex_project/figures/` and included by a chapter (FR-29,
      FR-30).
- [ ] At least one TikZ figure stored in its own `.tex` file under
      `latex_project/figures/` and included via `\input{...}`
      (AC §14.2).
- [ ] At least one table stored in its own `.tex` file under
      `latex_project/tables/`, wrapped in a `table` environment with a
      caption, and included via `\input{...}` (FR-31).
- [ ] At least one labeled equation, referenced later with `\ref` or
      `\eqref` (FR-25, FR-32).
- [ ] At least one theorem-like environment (`definition`, `theorem`,
      `lemma`, or `example`) (FR-24).
- [ ] Nomenclature section with at least two symbols (FR-26).
- [ ] Index section with at least one Hebrew term and at least one
      English term (FR-27).
- [ ] Bibliography citations appear in the body text and a rendered
      bibliography section appears at the end (FR-33).

### 19.3 BiDi (§14.4)

- [ ] At least one section includes Hebrew text.
- [ ] At least one Hebrew paragraph includes embedded English technical
      terms.
- [ ] Mixed Hebrew and English text renders in the correct visual order
      (NFR-29).
- [ ] Hebrew text alignment is correct (right-aligned) (NFR-30).
- [ ] English citations, labels, references, and inline technical
      identifiers remain readable inside Hebrew text (NFR-29).
- [ ] Fonts support both Hebrew and English (`David CLM`,
      `Latin Modern Roman`) (NFR-31).
- [ ] No visible RTL/LTR corruption in the final PDF.

### 19.4 Engine, build, and output

- [ ] The project compiles cleanly with **LuaLaTeX** using the
      documented multi-pass command sequence (FR-20, AC §14.3).
- [ ] `results/final.pdf` is produced and opens in a standard PDF
      reader (FR-38, KPI).
- [ ] `results/final.pdf` is **at least 15 pages, target 15–20 pages**
      (KPI, AC §14.2).
- [ ] PDF compilation instructions are documented in `README.md`,
      including the LuaLaTeX + `biber` + `David CLM` prerequisites.
