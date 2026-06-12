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
  -> Writer agent
  -> Reviewer agent
  -> LaTeX Formatter agent
  -> PDF Validator agent
```

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

- Prefer **LuaLaTeX** for Hebrew/English support if available.
- **XeLaTeX** is acceptable if explicitly chosen and the reason is documented.
- Use a real `.bib` file together with **biber** (or BibTeX) for bibliography.
- Do **not** assume the local machine has a TeX distribution installed.
- A successful LaTeX compile is **not** required during the scaffold stage.

### Markdown-first content workflow

Article drafts will be authored and reviewed as Markdown first (under
[`content/markdown_drafts/`](content/markdown_drafts/)). Only after manual
inspection will Markdown be converted to LaTeX. No draft chapters exist yet.

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
