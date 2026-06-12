# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

This is **HW3** for an AI agent orchestration course. The repository is currently a **scaffold only** — package skeletons, docs, and placeholder artifact dirs exist, but **no real CrewAI agents, tools, content, citations, or compiled PDF have been implemented**. Most "phases" in `docs/PLAN.md` past Phase 1 are open. Do not mark any acceptance-criteria checkbox in `SUBMISSION_CHECKLIST.md`, `docs/HW3_REQUIREMENTS.md`, or PRDs as done until the underlying artifact actually exists and has been verified.

## Commands

All Python work goes through [`uv`](https://docs.astral.sh/uv/). Do not invoke `python`, `pip`, or `pytest` directly.

```sh
uv sync                                            # resolve & install (dev group included)
uv run pytest                                      # run the smoke test suite
uv run pytest --cov=src --cov-report=term-missing  # with coverage
uv run pytest tests/test_scaffold.py::test_root_package_imports   # single test
uv run ruff check .                                # lint
uv run ruff check --fix .                          # lint with autofix
```

Dependencies for CrewAI, LLM provider SDKs, search SDKs, and LaTeX-adjacent Python tooling are **intentionally absent** from `pyproject.toml`. Add them with `uv add <pkg>` only when the phase that needs them starts (see `docs/PLAN.md`). Do not pre-install them speculatively.

LaTeX compilation is **not** wired up yet. The target engine per the PRD is **LuaLaTeX** (XeLaTeX is an optional later fallback). Do not assume a TeX distribution is installed locally.

## Architecture (planned, not implemented)

The package layout under `src/agentic_publishing_pipeline/` reserves one subpackage per CrewAI responsibility — each currently holds only `__init__.py` and a README:

- `agents/` — Researcher, Outline, Writer, Technical-Asset, Hebrew/BiDi, LaTeX, Bibliography, Reviewer agents (per PRD §8.3).
- `tasks/` — CrewAI `Task` definitions (research → outline → write → review → LaTeX → validate).
- `crews/` — Crew assembly + kickoff entry point. Default `Process` is **sequential**; any deviation must be justified in `docs/PRD_crewai_pipeline.md`.
- `tools/` — agent tools (search, file I/O, etc.).
- `latex/` — Markdown→LaTeX conversion and `latex_project/` assembly.
- `visualization/` — Python-generated graphs that land in `latex_project/figures/`.
- `validation/` — deterministic `ValidatorService` that runs **after** the Reviewer Agent. Per NFR-19 / FR-40, the LLM is never the source of truth for validation; the validator must check files, build outputs, and PDF content via deterministic code.

The pipeline is **Markdown-first**: agents produce Markdown drafts under `content/markdown_drafts/` (also referenced in PRDs as `results/generated_markdown/`), and only after human/reviewer approval are they converted into the structured LaTeX project. Do not skip the Markdown stage by writing LaTeX directly from agent output.

## LaTeX project conventions

When implementing the `latex_project/` content, follow PRD §8.5 strictly:

- `main.tex` is a thin root that `\input{}`s everything else. The current `latex_project/main.tex` is a placeholder full of TODO comments.
- Chapter files under `chapters/` hold narrative text only. **Long table environments and TikZ pictures must not be inlined into chapter files.** Each table goes in its own file under `tables/` and each TikZ figure in its own file under `figures/`, included via `\input{...}`. Regular `\includegraphics` image figures may use a short `figure` wrapper inside the chapter.
- Required structural pieces: `preamble.tex`, `macros.tex` (reusable math notation), `references.bib`, a nomenclature section (≥2 symbols), and an index (≥1 Hebrew term + ≥1 English term).
- At least one substantial section must demonstrate Hebrew/English BiDi with correct RTL alignment. Hebrew font preference is `David CLM`, English `Latin Modern Roman`, via `fontspec` + `polyglossia` under LuaLaTeX.

## Content and source policy

- **Fabricated sources are explicitly disallowed** at every stage (see `docs/PRD_bibliography_and_citations.md`). `references.bib` entries must come from real, locatable sources.
- All AI/LLM usage must be logged in `docs/AI_USAGE.md`; the prompts used must be kept current in `docs/PROMPTS.md`.
- Secrets load from `.env` only — never hardcoded. A `.env-example` is required (FR-4) but doesn't exist yet.

## Code-quality rules from the PRD

These rules come from PRD §9 and will be checked at submission:

- Python files target ≤150 lines; split by responsibility when they grow (NFR-2).
- All functions need type hints including return types; prefer annotations on first-appearance variables when they aid clarity (NFR-7, NFR-8).
- Use f-strings for interpolation; use comprehensions only when they improve readability.
- Validate inputs explicitly with `assert` or equivalent (NFR-13).
- Keep classes and moving parts minimal; extract small named helpers instead of long inline blocks.
- Ruff config (`pyproject.toml`): line length 100, `py311` target, rules `E,F,I,B,UP,SIM`. Tests ignore `B`.

## Tests

Only `tests/test_scaffold.py` exists today. It imports the root package and each subpackage to confirm the scaffold is sound. When adding real code, add real tests alongside it — the smoke test alone is not the bar.
