# agentic-publishing-pipeline

> **Status:** scaffold only. No article topic selected. No final PDF generated. No CrewAI pipeline implemented.

This repository will host a CrewAI-based pipeline that produces a polished LaTeX
PDF article/book on a user-selected topic. The current state is a *scaffold
only* — directory structure, documentation placeholders, and package skeletons
are in place, but no real agents, tools, content, citations, or compiled PDF
exist yet.

## HW3 — Article / Book Generation with CrewAI and LaTeX

### Current status

- Scaffold only.
- No article/book topic has been selected.
- No final PDF has been generated.
- CrewAI is **not** implemented yet.
- LaTeX compilation has **not** been verified yet.
- PDF validation has **not** been implemented yet.

### Goal

Implement a future CrewAI-based team of agents that helps produce an
article/book on a chosen topic, with the final deliverable being a polished
LaTeX-generated PDF (~15 pages) meeting all HW3 requirements documented in
[`docs/HW3_REQUIREMENTS.md`](docs/HW3_REQUIREMENTS.md).

### Planned architecture (placeholder)

```
Topic / scope
  -> Researcher agent
  -> Outline agent
  -> Writer agent
  -> Technical-Asset agent
  -> Hebrew/BiDi agent
  -> LaTeX agent
  -> Bibliography agent
  -> Reviewer agent
```

Full architecture is documented in [`docs/PRD.md`](docs/PRD.md) §8.3 and
[`docs/PRD_crewai_pipeline.md`](docs/PRD_crewai_pipeline.md); Phase 13
finalizes this section against the running system.

The planned CrewAI flow:

```
Research task -> Writing task -> Review task -> Markdown assembly task
  -> LaTeX generation task -> PDF validation task
```

The default planned `Process` is sequential. Any deviation must be justified in
[`docs/PRD_crewai_pipeline.md`](docs/PRD_crewai_pipeline.md).

### Planned artifact directories

- [`content/`](content/) — approved Markdown drafts (Markdown-first workflow).
- [`latex_project/`](latex_project/) — LaTeX project (`main.tex`,
  `references.bib`, `chapters/`, `figures/`, `tables/`, `styles/`).
- [`assets/`](assets/) — source images and other static inputs.
- [`results/`](results/) — generated graphs and compiled PDFs.
- [`submission/`](submission/) — final submission bundle prepared from the
  official Moodle template later.

### Future local development commands

All commands will use [`uv`](https://docs.astral.sh/uv/) only. Examples for
later use:

```sh
uv sync                                          # resolve and install
uv run pytest                                    # run tests
uv run pytest --cov=src --cov-report=term-missing
uv run ruff check .                              # lint
```

No CrewAI or model-provider command lines are documented yet, because no real
agents have been implemented. They will be added once the pipeline exists.

### Future LaTeX build workflow (placeholder)

The LaTeX build process will be documented in
[`docs/PRD_latex_generation.md`](docs/PRD_latex_generation.md). The current
guidance:

- **LuaLaTeX** is the required MVP engine; XeLaTeX is an optional later
  fallback (PRD §16.3 / FR-20). The README's full LaTeX build commands land
  in Phase 13.
- Use a real `.bib` file together with **biber** (or BibTeX) for bibliography.
- Do **not** assume the local machine has a TeX distribution installed.
- A successful LaTeX compile is **not** required during the scaffold stage.

### Markdown-first content workflow

Article drafts will be authored and reviewed as Markdown first (under
[`results/generated_markdown/`](results/generated_markdown/), canonical per
FR-12 / PRD §12.3). The scaffold also has
[`content/markdown_drafts/`](content/markdown_drafts/) as a transitional
placeholder; the retire-or-alias decision is tracked in P6-I00. Only after
manual inspection will Markdown be converted to LaTeX. No draft chapters
exist yet.

### Citations and bibliography reminder

Real citations and bibliography entries must be created later from real
selected sources. Fabricated sources are explicitly disallowed at every stage.
See [`docs/PRD_bibliography_and_citations.md`](docs/PRD_bibliography_and_citations.md).

### AI usage and prompt log

All AI/LLM usage and the prompts used to drive the pipeline must be documented:

- [`docs/AI_USAGE.md`](docs/AI_USAGE.md)
- [`docs/PROMPTS.md`](docs/PROMPTS.md)

These files exist as scaffolds today and must be filled in as real work happens.

## Repository layout (current)

```
content/             Markdown drafts (placeholder)
latex_project/       LaTeX project (placeholder)
assets/              Source images / static inputs (placeholder)
results/             Generated graphs and compiled PDFs (placeholder)
submission/          Final Moodle bundle (placeholder)
docs/                PRDs, PLAN, TODO, HW3 requirements, AI usage, prompts
src/agentic_publishing_pipeline/
                     Python package skeleton (no real agents yet)
tests/               Smoke test only
```

## Planning documents

- [`docs/PRD.md`](docs/PRD.md) — top-level product requirements.
- [`docs/PLAN.md`](docs/PLAN.md) — phased delivery plan.
- [`docs/TODO.md`](docs/TODO.md) — open TODOs for later work.
- [`docs/HW3_REQUIREMENTS.md`](docs/HW3_REQUIREMENTS.md) — HW3 checklist.
- [`docs/PRD_crewai_pipeline.md`](docs/PRD_crewai_pipeline.md)
- [`docs/PRD_latex_generation.md`](docs/PRD_latex_generation.md)
- [`docs/PRD_bibliography_and_citations.md`](docs/PRD_bibliography_and_citations.md)
- [`docs/PRD_pdf_validation.md`](docs/PRD_pdf_validation.md)
- [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md) — final submission gate.

## Contributing and onboarding

This project synchronises a Markdown-first planning workflow
(`docs/PRD.md`, `docs/PLAN.md`, `docs/TODO.md`) with GitHub tracking
objects (issues, milestones, labels, branches, pull requests). Both
sides are operated by the same workflow, and neither is allowed to
drift into being the only place where project status is recorded.

Before you change any artifact in this repository or any GitHub
tracking object, read the following in order:

1. [`CONTRIBUTING.md`](CONTRIBUTING.md) — the canonical detailed
   workflow for **every** human contributor, project partner, future
   maintainer, and AI agent. Covers onboarding, issue selection,
   self-assignment, the linked-branch workflow, the Project Tracking
   Synchronization Contract, the PR template, drift recovery, and the
   handoff protocol.
2. [`CLAUDE.md`](CLAUDE.md) — mandatory AI-agent operating rules
   layered on top of `CONTRIBUTING.md`. Read this whenever an AI agent
   (Claude Code session or otherwise) is part of the workflow.
3. [`docs/PRD.md`](docs/PRD.md) — what the system must do.
4. [`docs/PLAN.md`](docs/PLAN.md) — the phase you are working in and
   its exit criterion. PLAN phases mirror GitHub Milestones.
5. [`docs/TODO.md`](docs/TODO.md) — the concrete backlog item you are
   working on. TODO items mirror GitHub Issues by internal ID
   (`P<phase>-I<nn>`).
6. The **GitHub issue** for the work item — read the full body and all
   existing comments, check its milestone, labels, dependencies,
   linked branches, and linked pull requests.

The same six-step sequence applies to project owners, partners, new
developers, and AI-assisted sessions. Skipping any step is a violation
of the Synchronization Contract in `CONTRIBUTING.md` §8.

Issues and pull requests are governed by the templates in
`.github/ISSUE_TEMPLATE/` and `.github/pull_request_template.md`. Use
them.
