# agentic-publishing-pipeline

> **Status:** Phases 0 through 5, 7, and 8 are merged into `main`. Phase 6
> is under corrective recovery for real CrewAI orchestration and a fresh
> human-reviewed complete manuscript. Phase 8 delivered a deterministic
> Python graph pipeline: typed grouped-bar-chart spec,
> strict validation, Matplotlib Agg renderer, SHA-256 provenance, and a
> canonical artifact committed to `latex_project/figures/` (PR #92). Phase 12
> hardened CI with coverage gates, lint, and regression-guard scripts
> (PR #86). Phase 9 (LaTeX project assembly) waits on fresh Phase 6
> manuscript approval. No final PDF has been generated.

This repository will host a CrewAI-based pipeline that produces a polished LaTeX
PDF article/book on a user-selected topic. The current state includes the
Phase 5 provider/service layer, deterministic runtime modes, typed artifact
contracts, core tools, CLI, offline fixture path, a stale Phase 6
Markdown-first draft set under `results/generated_markdown/`, Phase 7
verified bibliography with locked ArXiv metadata, migrated citation keys, and
a resolved `\cite{}` map in `results/run_logs/`, and Phase 8 deterministic
Python graph pipeline with a canonical PNG artifact and provenance in
`latex_project/figures/`. Final LaTeX assembly, deterministic final
validation, and `results/final.pdf` remain unfinished.

## HW3 — Article / Book Generation with CrewAI and LaTeX

### Current status

- Phase 6 Markdown-first content generation is under corrective recovery:
  real CrewAI construction is now implemented on the recovery branch, and the
  next gate is a fresh human review of complete candidate Markdown bytes.
- Phase 7 real-source bibliography pipeline is merged into `main` (PR #83):
  ArXiv metadata verified, citation keys migrated, `\cite{}` placeholders
  resolved, untrusted-archive policy enforced.
- Phase 8 Python graph generation pipeline is merged into `main` (PR #92):
  deterministic grouped-bar-chart renderer, typed YAML spec with strict
  validation, SHA-256 provenance, and a canonical PNG committed to
  `latex_project/figures/` with regeneration evidence (409 tests, 88% coverage).
- Phase 12 CI hardening merged (PR #86): `ci-core.yml` with 85% coverage
  gate, 150-line cap, and `scripts/check_*.py` regression-guard scripts.
  Workflows are currently set to `workflow_dispatch`-only pending runner
  verification.
- Phase 9 (LaTeX project assembly) waits on the fresh Phase 6 manuscript
  approval.
- The canonical HW3 topic is selected in `docs/PRD.md` §22.
- No final PDF has been generated.
- Live model/search adapters are **not** implemented yet.
- Final LaTeX assembly has **not** been completed yet.
- Deterministic final PDF validation has **not** been implemented yet.

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

### Local development commands

All commands will use [`uv`](https://docs.astral.sh/uv/) only. Examples for
later use:

```sh
uv sync --frozen --group dev                     # exact, reproducible install
uv run pytest                                    # run tests
uv run pytest --cov=src --cov-report=term-missing
uv run ruff check .                              # lint
uv run python scripts/check_line_cap.py --limit 150 src
```

Phase 5 adds the package CLI and deterministic CI-safe runtime modes:

```sh
uv run python -m agentic_publishing_pipeline --help

uv run python -m agentic_publishing_pipeline \
  --mode dry-run \
  --results-root /tmp/app-dry-run

uv run python -m agentic_publishing_pipeline \
  --mode offline-fixture \
  --topic "Reasoning-Centric Agentic LLM Systems" \
  --manifest config/article_sources.yaml \
  --registry config/prompt_registry \
  --results-root /tmp/app-offline-fixture
```

`dry-run` validates configuration/registry compatibility and creates an
isolated run workspace without task artifacts, API keys, network, or paid
calls. `offline-fixture` routes deterministic model/search fixtures through
`ProviderFacade -> ApiGatekeeper -> fixture adapters`, records zero-cost
usage events, parses the eight canonical task responses into typed contracts,
and preserves the run workspace under the chosen results root.

`live` currently validates credentials and then refuses because Phase 5 has no
supported live adapter yet; it never silently falls back to fixtures.
`compile-only`, `validate-only`, and `resume` operate on an existing
`--run-id` workspace and remain bounded to deterministic Phase 5 seams.

CI was overhauled in P12-I05 (PR #86). `phase5-validation.yml` was replaced
by four workflow files under `.github/workflows/`:

- **`ci-core.yml`** — lint (`ruff check`), format check, pytest with ≥85%
  coverage gate, 150-line production-source cap, `uv build`, and dry/offline
  smoke runs.
- **`baseline-contracts.yml`** — Phase 1–7 regression guards: required-doc
  presence, unique planning IDs, no tracked secrets/archives, provider and
  gatekeeper tests, offline smoke, Phase 6 review-gate tests, Phase 7
  bibliography tests, and phase-order protection.
- **`artifact-pipeline.yml`** — graceful stubs for Phases 8–14.
- **`security.yml`** — CodeQL, dependency review, and actionlint.

All workflows are currently set to `workflow_dispatch`-only pending runner
verification. Re-enable `pull_request`/`push` triggers per workflow as each
is confirmed passing on a clean checkout.

Validator scripts live in `scripts/check_*.py` and have unit tests in
`tests/test_ci_scripts.py`.

Dependencies follow a strict per-tool, no-speculative-install policy: a new
runtime dependency is added (via `uv add <pkg>`) only inside the issue commit
that actually consumes it. See [`CONTRIBUTING.md`](CONTRIBUTING.md) §11.5
"Dependency policy" for the binding rule.

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
                     Python package plus Phase 5 provider/runtime/tool seams
tests/               Unit tests plus Phase 5 CLI/offline-fixture coverage
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
