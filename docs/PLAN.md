# PLAN — agentic-publishing-pipeline

> **Status:** scaffold-stage only. Documentation alignment, all CrewAI
> implementation, all LaTeX content, all bibliography work, all validation
> work, the final PDF, and all submission packaging are still open.

## How PRD, PLAN, TODO, and GitHub fit together

These artifacts have distinct, non-overlapping roles. Keep them in sync, do
not duplicate content:

| Artifact | Role |
|---|---|
| [`docs/PRD.md`](PRD.md) | Source of truth for **requirements** (FRs, NFRs, acceptance criteria). |
| [`docs/PLAN.md`](PLAN.md) (this file) | **Phased roadmap / milestones** from scaffold to submission. |
| [`docs/TODO.md`](TODO.md) | **Concrete task backlog** with checkable items, each traceable to a PRD requirement. |
| GitHub **Milestones** | GUI mirror of PLAN phases. Created later (see Phase 2). |
| GitHub **Issues** | GUI mirror of TODO items. Created later (see Phase 2). |
| [`CLAUDE.md`](../CLAUDE.md) | Repository conventions for AI assistants. Aligned with `docs/PRD.md`. |
| HW3 mechanism PRDs (`docs/PRD_*.md`) | Per-mechanism refinements of `docs/PRD.md`. Currently scaffold-level placeholders — see Phase 1. |

GitHub Milestones/Issues are a GUI representation of this plan and TODO; they
are **not** a replacement for these documents. The Markdown files remain
authoritative.

## Canonical paths

`docs/PRD.md` §12.3, §13, and FR-12 designate
**`results/generated_markdown/`** as the canonical location for Markdown
drafts. The scaffold currently also has `content/markdown_drafts/` for
historical reasons; treat that as a transitional placeholder that will either
be removed or aliased once the Markdown pipeline is implemented. New planning
text in this repo should use `results/generated_markdown/`.

## Phases

The phases below are ordered. Each phase has an explicit exit criterion. Do
**not** mark a phase complete until its exit criterion is *verifiably* met by
artifacts on disk and (where relevant) by a passing build, test, or
validator run. Detailed task checklists live in [`docs/TODO.md`](TODO.md),
not here.

### Phase 0 — Scaffold setup *(complete)*

Only items below were verified on disk and are marked complete. Everything
beyond Phase 0 is open.

- Repository tree, `.gitignore`, `pyproject.toml` (uv-managed, dev group
  only — no `crewai` / LLM / search SDKs yet by design).
- Placeholder package tree under `src/agentic_publishing_pipeline/`
  (`agents/`, `tasks/`, `crews/`, `tools/`, `latex/`, `validation/`,
  `visualization/`), each with `__init__.py` and a README.
- Placeholder artifact directories: `content/`, `latex_project/`
  (`chapters/`, `figures/`, `tables/`, `styles/`), `assets/`, `results/`,
  `submission/`.
- Smoke test at `tests/test_scaffold.py` (imports only; no behavioural
  coverage).
- Top-level docs that **exist** as scaffolds: `README.md`,
  `SUBMISSION_CHECKLIST.md`, `CLAUDE.md`, `docs/PRD.md` (expanded),
  `docs/HW3_REQUIREMENTS.md`, `docs/AI_USAGE.md`, `docs/PROMPTS.md`,
  the four mechanism PRDs (`PRD_crewai_pipeline.md`,
  `PRD_latex_generation.md`, `PRD_bibliography_and_citations.md`,
  `PRD_pdf_validation.md`).

**Exit criterion (met):** `uv sync` succeeds, `uv run pytest` passes the
smoke suite, `uv run ruff check .` is clean. Note that scaffold "complete"
means *the scaffold itself* is complete, not that any HW3 requirement is
satisfied.

### Phase 1 — Documentation alignment *(open)*

Reconcile the four mechanism PRDs and supporting docs with the current
`docs/PRD.md`. They predate the expanded PRD and still describe a 5-agent
flow (`PRD_crewai_pipeline.md`), do not lock LuaLaTeX as the default
(`PRD_latex_generation.md`), and do not codify FR-40 / NFR-19's deterministic
`ValidatorService` (`PRD_pdf_validation.md`). They **exist** but **require
update/review** before they can be treated as complete.

**Exit criterion:** every mechanism PRD references the same agent list,
engine choice, separation-of-responsibilities rules, validation policy, and
acceptance criteria as `docs/PRD.md`; `README.md` and `SUBMISSION_CHECKLIST.md`
agree with that same picture.

### Phase 2 — Project management setup *(open)*

Set up GitHub as the GUI tracking layer for this plan and TODO. The
"no GitHub changes yet" guidance in this document refers to the current
**documentation-rewrite pass** that produced this PLAN/TODO; Phase 2 is
explicitly the phase where the issues and milestones **do** get created.

Planned work:

- Create **GitHub Milestones** for every open phase — Phases 1 through 14
  (one milestone per phase; milestone title matches the phase title).
  Phase 0 does not get a milestone because it is already complete.
- Create **GitHub Issues** from the concrete tasks in `docs/TODO.md`;
  preserve TODO wording so issue titles remain traceable to TODO items.
- Apply a small **label** vocabulary on each issue:
  `docs`, `architecture`, `crewai`, `latex`, `validation`, `bidi`,
  `bibliography`, `testing`, `submission`.
- An issue may be closed only when the underlying artifact is verified on
  disk (or by a passing build/test). Closing an issue does **not** by itself
  let a corresponding TODO item or PRD acceptance criterion be ticked.

**Exit criterion:** milestones exist for every open phase (Phases 1–14),
every open TODO item has a tracking issue with the right labels, and the
mapping TODO ↔ issue ↔ milestone ↔ PRD requirement is documented in
`docs/TODO.md`'s introduction.

### Phase 3 — Topic and scope *(open)*

Group agrees on the article topic, the research question, the audience, the
depth target, and the BiDi balance (mostly-English with a Hebrew BiDi
section vs. balanced bilingual — see PRD §21 Open Questions).

**Exit criterion:** topic, scope, audience, and BiDi balance recorded in
`docs/PRD.md` (or a successor section), and the same decisions reflected in
the mechanism PRDs.

### Phase 4 — CrewAI architecture design *(open)*

Design the **eight** agents from `docs/PRD.md` §8.3 — Researcher, Outline,
Writer, Technical-Asset, Hebrew/BiDi, LaTeX, Bibliography, Reviewer — with
explicit `role`, `goal`, `backstory`, and tool list each. Design the task
graph (research → outline → write → review → LaTeX → validate; ≥5 tasks per
KPI; ≥3 tasks consume earlier task `context` per AC §14.5). Default
`Process` is **sequential** (FR-8); any deviation must be justified in
`docs/PRD_crewai_pipeline.md`. Draft initial prompts in `docs/PROMPTS.md`.

**Exit criterion:** agent and task design captured in
`docs/PRD_crewai_pipeline.md` and reflected in updates to `docs/PROMPTS.md`;
no implementation code yet.

### Phase 5 — Provider/service layer and tools *(open)*

Implement the controlled provider/service layer (NFR-23) so model and search
calls route through one place. Add `.env-example` (FR-4) and load secrets
exclusively via environment (FR-3). Implement agent tools: search, file
I/O, Markdown conversion, LaTeX compilation, graph generation. Real
dependencies (`crewai`, model SDK, search SDK, `matplotlib`, etc.) enter
`pyproject.toml` only as each tool is implemented — `uv add` per package,
no speculative installs.

**Exit criterion:** `.env-example` committed, provider layer importable
from `src/agentic_publishing_pipeline/tools/`, every tool exercised by at
least one unit test.

### Phase 6 — Markdown-first content pipeline *(open)*

Writer/Outline/Reviewer agents produce Markdown drafts at
`results/generated_markdown/` (canonical, per FR-12 and §12.3). The
`content/markdown_drafts/` scaffold is transitional and should be retired or
aliased during this phase. Markdown must include heading structure, figure
placeholders, table placeholders, equation placeholders, and citation
placeholders (FR-13). A human review gate runs before any LaTeX conversion.

**Exit criterion:** at least one full draft set lives under
`results/generated_markdown/`, has been reviewed, and is approved for LaTeX
conversion; `docs/AI_USAGE.md` records the run.

### Phase 7 — Real-source and bibliography pipeline *(open)*

Implement the Bibliography Agent's source discovery, verification, and
`references.bib` curation per `docs/PRD_bibliography_and_citations.md`.
**No fabricated sources, ever** — citation insertion must refuse unverified
sources and surface unresolved `\cite{...}` as build-time errors.

**Exit criterion:** `latex_project/references.bib` contains only verified
real entries; every `\cite{...}` in the LaTeX sources resolves.

### Phase 8 — Python graph generation pipeline *(open)*

Implement `src/agentic_publishing_pipeline/visualization/`. It must produce
at least one graph image saved under `latex_project/figures/` (FR-29,
FR-30) and consumed by a chapter via `\includegraphics`.

**Exit criterion:** a real Python-generated graph file exists under
`latex_project/figures/` and is included by a chapter.

### Phase 9 — LaTeX project assembly *(open)*

Convert approved Markdown into the structured LaTeX project per PRD §8.5 /
§14.3:

- `main.tex` is a thin root that `\input{}`s everything else; current
  `latex_project/main.tex` is still the TODO-only placeholder.
- `preamble.tex`, `macros.tex` (reusable math notation per FR-18),
  `references.bib`, chapter files under `chapters/`.
- Tables live in dedicated files under `tables/`, TikZ figures in
  dedicated files under `figures/`; chapter files `\input{...}` them
  (FR-17a–d). Regular `\includegraphics` images may use a short `figure`
  wrapper inside the chapter.
- LuaLaTeX is the **required MVP engine** (FR-20). Hebrew font preference
  `David CLM`, English `Latin Modern Roman`, via `fontspec` + `polyglossia`.
- Required content: at least one image (FR-28), Python-generated graph
  (FR-29), table (FR-31), equation with `\ref`/`\eqref` cross-reference
  (FR-25, FR-32), theorem-like environment (FR-24), TikZ figure (AC §14.2),
  nomenclature with ≥2 symbols (FR-26), index with ≥1 Hebrew and ≥1 English
  term (FR-27), headers/footers (FR-21), title page and TOC (FR-22), and at
  least one substantial Hebrew/English BiDi section (FR-15-onward + AC
  §14.4).

**Exit criterion:** the LaTeX project compiles cleanly with LuaLaTeX using
the documented build command, and every PRD §14.3 / §14.4 acceptance
checkbox is verifiable in the resulting PDF.

### Phase 10 — PDF build pipeline *(open)*

Document and script the multi-pass build (LuaLaTeX → biber → LuaLaTeX →
LuaLaTeX, plus `makeindex` / `makenomenclature` as needed). Output is
`results/final.pdf` (FR-38, §12.3). Build commands are documented in
`README.md` so a new developer can reproduce.

**Exit criterion:** `results/final.pdf` exists, opens cleanly, is ≥15 pages
(KPI), and is regenerable from a clean checkout via documented commands.

### Phase 11 — Deterministic ValidatorService *(open)*

Implement the deterministic `ValidatorService` in
`src/agentic_publishing_pipeline/validation/` per FR-40 / NFR-19. It runs
**after** the Reviewer Agent and is **not** an LLM. It checks: required
repository files, required LaTeX files (PRD §14.1, §14.3), generated
artifacts (Markdown drafts, graph files, run logs), LaTeX build outputs,
PDF page count, embedded image / graph / table / equation indicators where
feasible, presence of a BiDi section, presence of bibliography /
nomenclature / index, and resolution of every `\cite{...}` (PRD
`PRD_pdf_validation.md`, `PRD_bibliography_and_citations.md`). Output is a
human-readable validation report (FR-37).

**Exit criterion:** the validator runs from a documented entry point,
produces a report, and fails loudly on missing artifacts; it does not
delegate any decision to an LLM.

### Phase 12 — Tests, lint, and reproducibility *(open)*

Replace smoke-only coverage with real tests for the provider layer, tools,
Markdown→LaTeX conversion, visualization, and `ValidatorService`. Keep
`uv run ruff check .` and `uv run pytest` green. Document reproducibility
in `README.md`: install steps, LaTeX distribution requirements (LuaLaTeX +
`David CLM` font), regeneration commands, and cost/usage notes.

**Exit criterion:** `uv run pytest` and `uv run ruff check .` both pass on
a clean checkout; `README.md` reproducibility instructions are accurate.

### Phase 13 — README, AI usage, and prompt log finalization *(open)*

Bring `README.md` to current architecture (8-agent flow, real commands,
real run output), and fill `docs/AI_USAGE.md` and `docs/PROMPTS.md` with
the actual prompts, models, costs, and human verification notes used to
generate the final PDF.

**Exit criterion:** README accurately describes the running system; AI
usage and prompt log are complete and current at submission time.

### Phase 14 — Final submission packaging *(open)*

Prepare the Moodle wrapper PDF from the official template, confirm the
`<GROUP_CODE>-ex03.pdf` filename convention, and confirm each group member
submits separately in Moodle (per `SUBMISSION_CHECKLIST.md`).

**Exit criterion:** the wrapper PDF exists under `submission/`, the
`SUBMISSION_CHECKLIST.md` checkboxes are individually verified, and each
group member has submitted in Moodle.

## Notes

- Phases 1 through 14 are all open. None of them is allowed to be marked
  complete preemptively. PRD acceptance-criteria checkboxes
  (`docs/PRD.md` §14, `docs/HW3_REQUIREMENTS.md`,
  `SUBMISSION_CHECKLIST.md`) are ticked only after the underlying artifact
  is verified on disk and, where applicable, by a passing build, test, or
  validator run.
- Real Python dependencies (`crewai`, model SDKs, search SDKs,
  `matplotlib`, etc.) are added via `uv add` only when the phase that
  needs them begins.
- LaTeX compilation is not wired up yet. Do not assume a TeX distribution
  is installed locally; the README must call out the LuaLaTeX + David CLM
  requirement before Phase 10 can be validated on another machine.
