# PRD — CrewAI Pipeline

> **Status:** design/specification only. No CrewAI agents, tasks, crew
> assembly, kickoff entry point, tools, or run logs have been implemented
> yet. This document defines what will be built; checking any of its
> acceptance-criteria boxes requires the corresponding artifact to exist
> on disk and be verified.

## 1. Scope and relationship to other documents

This PRD refines the CrewAI workflow described in `docs/PRD.md` §8.2–§8.3,
§8.4 (Markdown stage), §8.7 (validation handoff), §12.3 (artifact paths),
and §14.5 (CrewAI acceptance criteria). It is the canonical mechanism PRD
for the pipeline; the four mechanism PRDs are listed under `docs/PRD.md`
§20.

This document is the workflow PRD referenced by `docs/PRD.md` §13 and §20
as `docs/PRD_crewai_pipeline.md`. It does not replace the main PRD; it
specifies how the requirements there are realized as a multi-agent CrewAI
flow.

Sister mechanism PRDs:

- `docs/PRD_latex_generation.md` — LaTeX project assembly and PDF build.
- `docs/PRD_bibliography_and_citations.md` — `references.bib` curation
  and citation policy.
- `docs/PRD_pdf_validation.md` — the deterministic `ValidatorService` that
  runs **after** the Reviewer Agent.

Planning and tracking:

- `docs/PLAN.md` — phased roadmap (Phase 4 designs the agents and tasks;
  Phase 5 implements the provider/service layer and tools; Phase 6
  produces the first Markdown drafts).
- `docs/TODO.md` — concrete backlog with PRD requirement tags.
- `CLAUDE.md` — repository conventions; mirrors the rules below.

## 2. Problem

A high-quality technical article requires several distinct cognitive
tasks: research, outline design, drafting, technical-asset production
(figures, graphs, tables, formulas), Hebrew/English BiDi authoring,
bibliography curation, LaTeX assembly, qualitative review, and
deterministic validation. Bundling all of this into one prompt makes the
output hard to reproduce, debug, extend, or validate.

CrewAI lets us split the work across specialized agents that pass
structured context between each other while keeping each agent's
responsibility small and inspectable. This PRD specifies how that split
is organized.

## 3. Goals

- Realize `docs/PRD.md` §8.3 with **eight** specialized agents.
- Define **at least five** CrewAI tasks (KPI in `docs/PRD.md` §6).
- Pass structured `context` between tasks; **at least three** tasks
  consume earlier task outputs via explicit `context`
  (`docs/PRD.md` §14.5).
- Generate intermediate **Markdown drafts before any LaTeX** is produced
  (FR-11, FR-12, FR-13, FR-14).
- Hand the reviewed Markdown to the LaTeX Agent, then run the
  deterministic `ValidatorService` after the Reviewer Agent stage
  (FR-40, NFR-19).
- Route every model and search call through a single controlled
  provider/service layer (NFR-23, NFR-24).
- Preserve all intermediate artifacts so the pipeline is debuggable
  (NFR-16, NFR-17).

## 4. Non-goals

- Implementing the agents, tasks, or crew assembly in this pass — Phase 4
  designs them; Phases 5–10 implement them.
- Choosing the LLM provider or search SDK — that decision belongs to
  Phase 5 and is recorded in `.env-example` and `README.md`.
- Defining LaTeX templates, fonts, or build commands — see
  `docs/PRD_latex_generation.md`.
- Defining the validator's check list — see `docs/PRD_pdf_validation.md`.

## 5. Agents (per `docs/PRD.md` §8.3)

The pipeline uses **eight** agents. Each agent has explicit `role`,
`goal`, `backstory`, and `tools` fields (FR-5). Agent prompts are kept
verbatim in `docs/PROMPTS.md`.

| # | Agent | Responsibility | Primary outputs |
|---|---|---|---|
| 1 | **Research Agent** | Collects background, key points, terminology, and candidate references for the topic. Calls the search tool through the provider layer. | Research notes (Markdown) |
| 2 | **Outline Agent** | Designs a coherent article structure from the research notes. | Outline (Markdown) |
| 3 | **Writer Agent** | Produces readable Markdown chapters from the research notes and outline, including heading structure, figure / table / equation / citation placeholders (FR-13). | Chapter drafts under `results/generated_markdown/` |
| 4 | **Technical Asset Agent** | Produces or specifies figures, the Python-generated graph, tables, formulas, and theorem-like content. Does not write LaTeX directly; it emits structured asset specifications and Markdown placeholders consumed by the LaTeX Agent. | Asset specs + placeholder Markdown |
| 5 | **Hebrew/BiDi Agent** | Produces and validates at least one substantial Hebrew/English mixed section, ensuring readable Hebrew, embedded English technical terms, and correct visual order (NFR-28–31). | BiDi section draft (Markdown) |
| 6 | **Bibliography Agent** | Discovers and verifies real sources; curates `references.bib` entries with stable keys; resolves citation placeholders from the Writer Agent and the BiDi Agent. **Fabricated sources are forbidden** (see `docs/PRD_bibliography_and_citations.md`). | Verified `.bib` entries + citation key map |
| 7 | **LaTeX Agent** | Converts the approved Markdown drafts and asset specs into the structured LaTeX project under `latex_project/`, following the separation rules in `docs/PRD_latex_generation.md` (FR-17a–d). | `latex_project/` source tree |
| 8 | **Reviewer Agent** | Reviews coherence, structure, formatting requirements, and missing deliverables before deterministic validation. May identify likely issues, but **is not the source of truth for validation** (NFR-19). | Review notes; pass/flag signal for downstream validation |

After the Reviewer Agent finishes, the deterministic `ValidatorService`
(see `docs/PRD_pdf_validation.md`) runs as a non-agent stage. The
`ValidatorService` is plain Python that checks files, build outputs, and
PDF content. **It is not an LLM agent**; LLM judgment is never the final
gate (FR-40, NFR-19).

## 6. Tasks

The pipeline defines at least the following CrewAI tasks. Each task is
declared with `description`, `expected_output`, `agent`, and `context`
fields (FR-6). At least three tasks consume earlier task outputs via
`context` (AC §14.5).

| # | Task | Agent | Consumes context from | Output |
|---|---|---|---|---|
| T1 | Research the topic | Research Agent | — | Research notes |
| T2 | Design the article outline | Outline Agent | T1 | Outline |
| T3 | Draft Markdown chapters with placeholders | Writer Agent | T1, T2 | Markdown drafts in `results/generated_markdown/` |
| T4 | Produce technical assets and figure/table/equation specs | Technical Asset Agent | T2, T3 | Asset specs + placeholder Markdown |
| T5 | Draft Hebrew/English BiDi section | Hebrew/BiDi Agent | T2, T3 | BiDi Markdown |
| T6 | Curate `references.bib` and resolve citation placeholders | Bibliography Agent | T1, T3, T5 | `references.bib` + citation key map |
| T7 | Assemble the LaTeX project | LaTeX Agent | T3, T4, T5, T6 | `latex_project/` source tree |
| T8 | Review coherence, structure, and required deliverables | Reviewer Agent | T3, T4, T5, T6, T7 | Review notes + pass/flag signal |

Task count: **8 ≥ 5** (`docs/PRD.md` KPI). Tasks consuming earlier
`context`: **T2, T3, T4, T5, T6, T7, T8 — at least 7 ≥ 3** (AC §14.5).

After T8 completes, the deterministic `ValidatorService` runs as a
non-CrewAI stage and produces the validation report (FR-37, see
`docs/PRD_pdf_validation.md`).

## 7. Crew assembly and process

- **Process:** sequential by default (FR-8). The sequence above
  (T1 → T2 → T3 → T4 → T5 → T6 → T7 → T8 → ValidatorService) is the MVP.
  Any deviation (hierarchical process, parallel sub-crews) must be
  justified in a future revision of this document and approved before
  implementation.
- **Kickoff:** the crew is launched from a single documented entry point
  under `src/agentic_publishing_pipeline/crews/` (FR-9). The entry point
  reads configuration from `config/` and `.env`, constructs the agents
  and tasks, builds the crew, calls `crew.kickoff(...)`, and then invokes
  the `ValidatorService`.
- **Outputs:** raw and processed outputs are saved at well-known paths
  (FR-10) — see §9.

## 8. Provider and service layer (NFR-23, NFR-24)

All model and search calls go through a single controlled provider /
service layer under `src/agentic_publishing_pipeline/tools/` (or a
sibling `services/` module created in Phase 5). The layer:

- centralizes model selection, base URL, retries, and timeouts;
- centralizes search-API usage;
- reads secrets only from environment variables loaded from `.env`
  (FR-3); never from hardcoded source;
- is replaceable: swapping LLM providers must not require rewriting the
  agents, tasks, or crew (NFR-24).

A `.env-example` documents every required environment variable (FR-4,
NFR-21). It is added in Phase 5; it does not exist yet.

## 9. Artifacts and canonical paths

The pipeline writes the following artifacts. Paths come from
`docs/PRD.md` §12.3 and FR-12.

| Stage | Artifact | Canonical path |
|---|---|---|
| Research notes | Markdown | `results/generated_markdown/research_notes.md` (or equivalent) |
| Outline | Markdown | `results/generated_markdown/outline.md` |
| Markdown chapter drafts | Markdown | `results/generated_markdown/chapters/*.md` |
| Asset specs | JSON/Markdown | `results/generated_markdown/assets/*` |
| BiDi section draft | Markdown | `results/generated_markdown/bidi.md` |
| Verified bibliography | `.bib` | `latex_project/references.bib` |
| LaTeX project | `.tex` tree | `latex_project/` (see `docs/PRD_latex_generation.md`) |
| Reviewer notes | Markdown | `results/run_logs/reviewer_notes.md` |
| Per-agent / per-task logs | Text or JSON | `results/run_logs/` |
| Validation report | Markdown / text | `results/run_logs/validation_report.md` (see `docs/PRD_pdf_validation.md`) |

`results/generated_markdown/` is the **canonical** Markdown drafts
location per FR-12 and `docs/PRD.md` §12.3 / §13. The scaffold also
contains `content/markdown_drafts/` for historical reasons; the decision
on whether to retire that path or keep it as an alias is recorded in
§13 below.

## 10. Markdown-first policy (FR-11–FR-14)

The pipeline is **Markdown-first**. The LaTeX Agent is not allowed to
consume agent output that has not first been emitted as Markdown into
`results/generated_markdown/`.

Markdown drafts:

- include heading structure (FR-13);
- include figure placeholders (FR-13);
- include table placeholders (FR-13);
- include equation placeholders (FR-13);
- include citation placeholders such as `\cite{authorYYYYkey}` or a
  semantically equivalent marker the Bibliography Agent can resolve
  (FR-13);
- progress through the topic logically and avoid filler (FR-14).

A human review gate is expected between Markdown approval and LaTeX
assembly (Phase 6 in `docs/PLAN.md`). The Reviewer Agent's pass/flag
signal does not bypass the human review gate; it complements it.

## 11. Reviewer Agent and deterministic validation handoff (FR-40, NFR-19)

The Reviewer Agent is the last LLM stage. It performs qualitative review
of coherence, structure, formatting requirements, and missing
deliverables. It **does not** decide whether the pipeline succeeded.

After the Reviewer Agent finishes, the deterministic `ValidatorService`
defined in `docs/PRD_pdf_validation.md` runs as a non-LLM Python module
under `src/agentic_publishing_pipeline/validation/`. It checks required
files, required LaTeX files, generated artifacts, LaTeX build outputs,
PDF content indicators, citation resolution, and the FR-17a–d
table/TikZ separation rules. It emits a human-readable validation report
(FR-37).

**The LLM is never the source of truth for validation** (NFR-19). The
Reviewer Agent's verdict is advisory; the `ValidatorService`'s verdict
is binding.

## 12. Observability and logging (NFR-16, NFR-17)

- Every agent invocation, tool call, model call, and produced artifact
  is logged.
- Logs and run summaries live under `results/run_logs/`.
- Intermediate Markdown drafts are kept under
  `results/generated_markdown/` for debugging.
- The exact log schema (JSON lines vs. plain Markdown vs. structured
  events) is fixed in Phase 5 and recorded here.

## 13. Open decisions to capture during implementation

- **`content/markdown_drafts/` disposition.** Phase 6 in `docs/PLAN.md`
  must decide whether to (a) retire the directory, (b) keep it as an
  alias / symlink of `results/generated_markdown/`, or (c) repurpose it
  for raw / unreviewed input. The chosen disposition is recorded back
  into this section.
- **Reviewer Agent escalation policy.** Whether the Reviewer Agent can
  send work back to earlier agents (e.g., by raising a flag the crew
  re-routes), or whether reviewer feedback always becomes human-review
  input. The MVP assumes the latter.
- **Per-task vs. per-agent prompt files.** Whether `docs/PROMPTS.md`
  holds one section per agent, one per task, or both.

## 14. Acceptance criteria

These mirror the CrewAI acceptance criteria in `docs/PRD.md` §14.5.
**None of these may be ticked until the underlying artifact exists on
disk and has been verified** (and, where relevant, until a kickoff run
has succeeded).

- [ ] All eight specialized agents from §8.3 are defined with explicit
      `role`, `goal`, `backstory`, and `tools` (FR-5, AC §14.5).
- [ ] At least five CrewAI tasks are defined with `description`,
      `expected_output`, `agent`, and `context` (FR-6, KPI, AC §14.5).
- [ ] At least three tasks consume earlier task outputs via explicit
      `context` (AC §14.5).
- [ ] The crew uses a sequential `Process` by default, or any deviation
      is justified in this document (FR-8).
- [ ] The crew is launched from a single documented kickoff entry point
      (FR-9).
- [ ] Raw and processed outputs are saved at the canonical paths in §9
      (FR-10).
- [ ] Markdown drafts are produced before any LaTeX assembly and live
      under `results/generated_markdown/` (FR-11, FR-12, AC §14.5).
- [ ] Markdown drafts include heading, figure, table, equation, and
      citation placeholders, and follow a logical topic progression
      (FR-13, FR-14).
- [ ] Agent prompts and task descriptions are documented verbatim in
      `docs/PROMPTS.md` (AC §14.5).
- [ ] All model and search calls go through the controlled
      provider/service layer (NFR-23, NFR-24).
- [ ] `.env-example` exists and documents the required environment
      variables (FR-4, NFR-21).
- [ ] Every agent invocation, tool call, and produced artifact is
      logged under `results/run_logs/` (NFR-16).
- [ ] The Reviewer Agent runs as the last LLM stage and produces review
      notes (FR-37).
- [ ] After the Reviewer Agent finishes, the deterministic
      `ValidatorService` defined in `docs/PRD_pdf_validation.md` runs
      and emits a validation report; **the LLM is not the source of
      truth for validation** (FR-40, NFR-19, AC §14.5).
- [ ] No fabricated sources enter `references.bib` at any stage
      (see `docs/PRD_bibliography_and_citations.md`).
