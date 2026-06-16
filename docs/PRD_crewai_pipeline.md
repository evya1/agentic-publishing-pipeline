# PRD — CrewAI Pipeline

> **Status:** Phase 4 design complete. Agent and task specifications are
> captured with explicit `role`, `goal`, `backstory`, and `tools` fields.
> Verbatim prompts are documented in `docs/PROMPTS.md`. No implementation
> code exists yet — Phases 5–10 will build the agents, tasks, crew
> assembly, kickoff entry point, tools, and run logs. Checking any
> implementation-level acceptance-criteria box requires the corresponding
> artifact to exist on disk and be verified.

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
- Implementing automatic source discovery for the MVP. The pipeline
  consumes the configured topic and verified source manifest; future
  discovery support may propose candidates for a later manifest, but
  unverified discoveries cannot enter the canonical HW3 run.

## 4.1 Topic and source scope contract

The reusable CrewAI workflow is generic. It accepts a configured topic
and a configured, verified source manifest as runtime inputs
(`docs/PRD.md` §22.1). Reusable agents, tasks, and prompts must not
hardcode canonical arXiv IDs, citation keys, source counts, or article
identifiers.

For the canonical HW3 demonstration run, the topic and fixed ten-source
manifest are supplied through configuration (`docs/PRD.md` §22.4). That
run preserves the Phase 3 decisions in `docs/PRD.md` §§22.6–22.9:
practitioner-facing audience, survey-style depth, Memory as the
substantial Hebrew/English BiDi host, approximately 2–3 relevant
verified sources per chapter, and citation of all ten canonical
manifest sources at least once across the complete final article.

## 5. Agents (per `docs/PRD.md` §8.3)

The pipeline uses **eight** agents. Each agent has explicit `role`,
`goal`, `backstory`, and `tools` fields (FR-5). Agent prompts are kept
verbatim in `docs/PROMPTS.md`.

### 5.1 Agent Summary Table

| # | Agent | Responsibility | Primary outputs |
|---|---|---|---|
| 1 | **Research Agent** | Collects background, key points, terminology, and candidate references for the topic. Calls the search tool through the provider layer. | Research notes (Markdown) |
| 2 | **Outline Agent** | Designs a coherent article structure from the research notes. | Outline (Markdown) |
| 3 | **Writer Agent** | Produces readable Markdown chapters from the research notes and outline, including heading structure, figure / table / equation / citation placeholders (FR-13). | Chapter drafts under `results/generated_markdown/` |
| 4 | **Technical Asset Agent** | Produces or specifies figures, the Python-generated graph, tables, formulas, and theorem-like content. Does not write LaTeX directly; it emits structured asset specifications and Markdown placeholders consumed by the LaTeX Agent. | Asset specs + placeholder Markdown |
| 5 | **Hebrew/BiDi Agent** | Produces and validates at least one substantial Hebrew/English mixed section, ensuring readable Hebrew, embedded English technical terms, and correct visual order (NFR-28–31). | BiDi section draft (Markdown) |
| 6 | **Bibliography Agent** | Consumes the configured source manifest, validates source metadata before use, curates `references.bib` entries with stable keys, and resolves citation placeholders from the Writer Agent and the BiDi Agent. **Fabricated or silently substituted sources are forbidden** (see `docs/PRD_bibliography_and_citations.md`). | Verified `.bib` entries + citation key map |
| 7 | **LaTeX Agent** | Converts the approved Markdown drafts and asset specs into the structured LaTeX project under `latex_project/`, following the separation rules in `docs/PRD_latex_generation.md` (FR-17a–d). | `latex_project/` source tree |
| 8 | **Reviewer Agent** | Reviews coherence, structure, formatting requirements, and missing deliverables before deterministic validation. May identify likely issues, but **is not the source of truth for validation** (NFR-19). | Review notes; pass/flag signal for downstream validation |

### 5.2 Detailed Agent Specifications

Each agent below is defined with the four CrewAI fields: `role`, `goal`,
`backstory`, and `tools`. The verbatim prompt text is stored in
`docs/PROMPTS.md`.

#### Agent 1 — Research Agent

- **role**: `Research Specialist`
- **goal**: Collect comprehensive, accurate background information about
  the configured article topic and verified source manifest. Synthesize
  key concepts and terminology into structured research notes that
  downstream agents can use to draft coherent content. Do not fabricate,
  silently replace, or silently discover sources for the run.
- **backstory**: You are an experienced technical researcher specializing
  in artificial intelligence and large language model systems. You have
  a track record of producing clear, well-organized research summaries
  that distill complex topics into actionable insights. Your work is
  known for being thorough yet concise, always citing verifiable sources
  and avoiding speculation.
- **tools**: `search_tool` (web/arXiv search through provider layer),
  `file_write` (write research notes to
  `results/generated_markdown/research_notes.md`)

#### Agent 2 — Outline Agent

- **role**: `Technical Writing Strategist`
- **goal**: Design a coherent, logically structured article outline from
  the research notes. The outline must define chapter headings, section
  flow, and content allocation so that the Writer Agent can produce
  focused, non-repetitive chapters.
- **backstory**: You are a senior technical editor with deep experience
  in structuring survey-style articles and white papers. You excel at
  organizing complex material into a narrative arc that guides the
  reader from background through core concepts to evaluation and
  conclusion. Your outlines are known for eliminating redundancy and
  ensuring each section has a clear purpose.
- **tools**: `file_read` (read research notes), `file_write` (write
  outline to `results/generated_markdown/outline.md`)

#### Agent 3 — Writer Agent

- **role**: `Technical Content Author`
- **goal**: Produce readable, well-structured Markdown chapter drafts
  from the research notes and outline. Each chapter must include
  headings, body text, and placeholders for figures, tables, equations,
  and citations. The content must follow a logical progression and avoid
  filler.
- **backstory**: You are a professional technical writer who specializes
  in AI and machine learning topics. You write clear, engaging prose
  that is accessible to practitioners while maintaining technical
  rigor. You are skilled at translating research findings into
  narrative explanations and at embedding structured placeholders for
  assets that will be filled in by specialized agents.
- **tools**: `file_read` (read research notes and outline),
  `file_write` (write chapter drafts to
  `results/generated_markdown/chapters/*.md`)

#### Agent 4 — Technical Asset Agent

- **role**: `Technical Asset Specialist`
- **goal**: Produce or specify all technical assets required by the
  article: figures (including TikZ diagrams and a Python-generated
  graph), tables, mathematical equations, and theorem-like environments.
  Emit structured asset specifications and Markdown placeholders that
  the LaTeX Agent can consume.
- **backstory**: You are a technical documentation engineer with expertise
  in LaTeX, TikZ, and data visualization. You understand how to design
  figures and tables that clarify complex concepts, and you know how to
  write clean, modular LaTeX code. You produce assets that are self-
  contained and follow separation-of-responsibility principles.
- **tools**: `file_read` (read chapter drafts and outline),
  `file_write` (write asset specs to
  `results/generated_markdown/assets/*`), `code_execution` (for Python
  graph generation — see `docs/PRD_latex_generation.md`)

#### Agent 5 — Hebrew/BiDi Agent

- **role**: `Hebrew/English BiDi Author`
- **goal**: Produce at least one substantial Hebrew/English mixed section
  that demonstrates correct bidirectional text handling. The section must
  include readable Hebrew prose with embedded English technical terms,
  proper RTL alignment, and stable English formulas/citations.
- **backstory**: You are a bilingual technical writer fluent in both
  Hebrew and English, with deep knowledge of BiDi typography and
  LuaLaTeX typesetting. You specialize in writing technical content in
  Hebrew while naturally incorporating English terminology, formulas,
  and citations without breaking the visual flow. Your work respects
  the conventions of both languages.
- **tools**: `file_read` (read outline and chapter drafts for context),
  `file_write` (write BiDi section to
  `results/generated_markdown/bidi.md`)

#### Agent 6 — Bibliography Agent

- **role**: `Bibliography Curator`
- **goal**: Verify and curate real sources for the article. Consume the
  configured manifest, validate source metadata, produce a
  valid `references.bib` file with stable citation keys, and resolve all
  citation placeholders from the Writer Agent and BiDi Agent.
  **Fabricated or silently substituted sources are strictly forbidden.**
- **backstory**: You are a meticulous academic librarian and bibliography
  specialist with expertise in BibTeX/Biber toolchains. You have a
  zero-tolerance policy for fabricated, unverifiable, or silently
  substituted sources. You validate every configured entry against
  authoritative metadata (arXiv, DOI registries) and ensure citation
  keys follow a consistent naming convention.
- **tools**: `search_tool` (verify configured sources through provider layer),
  `file_read` (read citation placeholders from drafts), `file_write`
  (write `latex_project/references.bib` and citation key map)

#### Agent 7 — LaTeX Agent

- **role**: `LaTeX Project Engineer`
- **goal**: Convert the approved Markdown drafts and asset specifications
  into a structured, compilable LaTeX project under `latex_project/`.
  Follow the separation rules: chapter files contain narrative text
  only; tables and TikZ figures live in dedicated files under
  `tables/` and `figures/`; `main.tex` is a thin root that inputs
  everything else.
- **backstory**: You are a LaTeX expert with extensive experience in
  academic document engineering. You build modular, maintainable LaTeX
  projects that follow professional conventions. You understand the
  LuaLaTeX toolchain, BiDi font configuration, theorem environments,
  nomenclature, and index generation. Your projects compile cleanly
  and are easy to maintain.
- **tools**: `file_read` (read all Markdown drafts, asset specs, and
  bibliography), `file_write` (write LaTeX project files under
  `latex_project/`)

#### Agent 8 — Reviewer Agent

- **role**: `Quality Review Editor`
- **goal**: Perform qualitative review of the complete pipeline output:
  coherence, structure, formatting requirements, and presence of all
  required deliverables. Identify issues and produce a pass/flag signal
  for the downstream deterministic `ValidatorService`. You are advisory;
  you do not make binding validation decisions.
- **backstory**: You are a senior technical reviewer with a keen eye for
  consistency, completeness, and structural quality. You check whether
  the article flows logically, whether all required elements are present
  (figures, tables, equations, citations, BiDi section, nomenclature,
  index), and whether the LaTeX project follows the separation rules.
  You flag issues clearly but defer final validation to deterministic
  checks.
- **tools**: `file_read` (read all Markdown drafts, LaTeX project files,
  and bibliography), `file_write` (write review notes to
  `results/run_logs/reviewer_notes.md`)

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

### 6.1 Task Summary Table

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

### 6.2 Detailed Task Specifications

Each task below is defined with the four CrewAI fields: `description`,
`expected_output`, `agent`, and `context`. The verbatim prompt text is
stored in `docs/PROMPTS.md`.

#### Task T1 — Research the topic

- **description**: Research the article topic and verified source
  manifest defined in configuration. Collect comprehensive background
  information, key concepts, and technical terminology. Use provider
  tools only to validate configured source metadata or enrich notes from
  approved sources; do not add unverified discovered sources to the run.
  Synthesize findings into structured research notes that cover all
  reasoning dimensions: planning, memory, retrieval, tool use, and
  multimodal reasoning.
- **expected_output**: A Markdown file at
  `results/generated_markdown/research_notes.md` containing:
  organized research notes with section headers for each reasoning
  dimension, key terminology definitions, and a list of candidate
  references with arXiv IDs or DOIs.
- **agent**: Research Agent
- **context**: *(none — this is the first task in the pipeline)*

#### Task T2 — Design the article outline

- **description**: Read the research notes from T1 and design a coherent
  article outline. The outline must define chapter headings, section
  structure, and content allocation for each chapter. Ensure the outline
  covers all required elements: background/introduction, five reasoning
  dimension chapters, evaluation chapter, Hebrew/English BiDi section
  (placed in the Memory chapter for the canonical HW3 run), conclusion,
  nomenclature, and index. The outline must ensure logical flow and
  eliminate redundancy. For the canonical run, it targets approximately
  2–3 relevant verified sources per chapter without treating that target
  as an exact hardcoded count.
- **expected_output**: A Markdown file at
  `results/generated_markdown/outline.md` containing:
  a hierarchical outline with chapter titles, section headings, brief
  descriptions of each section's content, and notes about where figures,
  tables, equations, and citations should be placed.
- **agent**: Outline Agent
- **context**: Output of T1 (research notes)

#### Task T3 — Draft Markdown chapters with placeholders

- **description**: Using the research notes (T1) and the outline (T2),
  draft complete Markdown chapters for the article. Each chapter must
  include headings, body text, and structured placeholders for figures,
  tables, equations, and citations. The content must follow a logical
  progression and avoid filler. Do not write LaTeX directly; produce
  clean Markdown that the LaTeX Agent can later convert.
- **expected_output**: Markdown chapter files under
  `results/generated_markdown/chapters/*.md` containing:
  complete chapter drafts with heading structure, narrative text, and
  placeholders in the form `<!-- FIGURE: description -->`,
  `<!-- TABLE: description -->`, `<!-- EQUATION: description -->`, and
  `<!-- CITATION: author_topic -->`.
- **agent**: Writer Agent
- **context**: Output of T1 (research notes), T2 (outline)

#### Task T4 — Produce technical assets and figure/table/equation specs

- **description**: Based on the chapter drafts (T3) and outline (T2),
  produce or specify all technical assets required by the article:
  TikZ figures (e.g., automata diagrams), a Python-generated graph,
  tables, mathematical equations with labels, and theorem-like
  environments. Emit structured asset specifications and Markdown
  placeholders that the LaTeX Agent can consume. Do not write LaTeX
  directly into chapter files.
- **expected_output**: Asset specification files under
  `results/generated_markdown/assets/*` containing:
  structured descriptions of each required asset (type, content, LaTeX
  code or generation instructions), plus placeholder markers that map
  to the chapter draft placeholders.
- **agent**: Technical Asset Agent
- **context**: Output of T2 (outline), T3 (chapter drafts)

#### Task T5 — Draft Hebrew/English BiDi section

- **description**: Produce a substantial Hebrew/English mixed section
  for the Memory dimension chapter. The section must demonstrate correct
  bidirectional text handling: readable Hebrew prose with embedded
  English technical terms, proper RTL alignment, and stable English
  formulas/citations. Use the outline (T2) and chapter drafts (T3) for
  context about the Memory dimension content.
- **expected_output**: A Markdown file at
  `results/generated_markdown/bidi.md` containing:
  a complete BiDi section with Hebrew text, embedded English technical
  terms, and proper directional markers. The content must be substantive
  (not a token demonstration) and must cover a meaningful portion of the
  Memory dimension discussion.
- **agent**: Hebrew/BiDi Agent
- **context**: Output of T2 (outline), T3 (chapter drafts)

#### Task T6 — Curate `references.bib` and resolve citation placeholders

- **description**: Consume the configured source manifest, validate
  source metadata, and curate real sources for the article. Read the
  citation placeholders from the Writer Agent (T3) and BiDi Agent (T5),
  and resolve each placeholder to a verified source. Produce a valid
  `references.bib` file with stable citation keys. Cross-reference every
  entry against authoritative databases (arXiv, DOI registries).
  **Fabricated or silently substituted sources are strictly forbidden.**
  For the canonical HW3 run, ensure every source in the fixed ten-source
  manifest is cited at least once across the complete final article.
- **expected_output**: A BibTeX file at `latex_project/references.bib`
  containing verified bibliography entries with stable citation keys,
  plus a citation key map that resolves all placeholders from T3 and T5.
- **agent**: Bibliography Agent
- **context**: Output of T1 (research notes), T3 (chapter drafts with
  citation placeholders), T5 (BiDi section with citation placeholders)

#### Task T7 — Assemble the LaTeX project

- **description**: Convert all approved Markdown drafts and asset
  specifications into a structured, compilable LaTeX project under
  `latex_project/`. Follow the separation rules strictly: chapter files
  contain narrative text only; each table lives in its own file under
  `tables/`; each TikZ figure lives in its own file under `figures/`;
  `main.tex` is a thin root that inputs everything else. Include
  `preamble.tex`, `macros.tex`, `references.bib`, nomenclature,
  nomenclature setup, and index configuration. Target LuaLaTeX with
  `fontspec` + `polyglossia` for BiDi support.
- **expected_output**: A complete LaTeX project tree under
  `latex_project/` containing: `main.tex`, `preamble.tex`, `macros.tex`,
  `references.bib`, `chapters/*.tex`, `tables/*.tex`, `figures/*.tex`,
  and any supporting configuration files.
- **agent**: LaTeX Agent
- **context**: Output of T3 (chapter drafts), T4 (asset specs), T5
  (BiDi section), T6 (bibliography)

#### Task T8 — Review coherence, structure, and required deliverables

- **description**: Perform qualitative review of the complete pipeline
  output. Check coherence, structure, formatting requirements, and the
  presence of all required deliverables: figures, tables, equations,
  citations, BiDi section, nomenclature, index, theorem-like environment,
  and bibliography. Identify issues clearly and produce a pass/flag
  signal for the downstream deterministic `ValidatorService`. You are
  advisory; you do not make binding validation decisions.
- **expected_output**: A Markdown file at
  `results/run_logs/reviewer_notes.md` containing:
  structured review notes listing checked items, identified issues,
  and an overall pass/flag recommendation. The notes must be specific
  enough to guide human review or automated validation.
- **agent**: Reviewer Agent
- **context**: Output of T3 (chapter drafts), T4 (asset specs), T5
  (BiDi section), T6 (bibliography), T7 (LaTeX project)

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

- **Phase 6 stage split — DECISION RECORDED (P6-I04/P6-I05,
  2026-06-16).** Corrective Phase 6 recovery launches the real CrewAI
  manuscript crew only through the pre-review manuscript stage: research,
  outline, writing, technical assets, BiDi, bibliography, and reviewer
  signal. That kickoff writes typed outputs and candidate Markdown into an
  isolated run workspace, then stops at deterministic preflight and the
  maintainer-owned human review gate. LaTeX planning/rendering remains
  downstream of the fresh approval boundary and must not consume stale or
  unapproved Markdown bytes.
- **`content/markdown_drafts/` disposition — DECISION RECORDED (P6-I00,
  2026-06-15).** The directory is **retired**. Rationale: a survey of
  every tracked file confirmed that `content/markdown_drafts/` had zero
  Python or YAML code consumers; all twelve references were documentation
  only. The canonical path `results/generated_markdown/` is already wired
  in the prompt registry, runtime promotion module, architecture docs,
  milestone description, and every relevant PRD section (FR-12, §9, §12.3).
  Maintaining a parallel transitional path introduces naming ambiguity with
  no backward-compatibility benefit. The directory has been removed from the
  repository; `results/generated_markdown/` is the sole canonical Markdown
  draft root. Follow-up doc edits to `CLAUDE.md` and the LaTeX READMEs
  that still reference the old path are queued under P13-I01.
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

### Design-level criteria *(satisfied by Phase 4)*

- [x] All eight specialized agents from §8.3 are defined with explicit
      `role`, `goal`, `backstory`, and `tools` (FR-5, AC §14.5).
- [x] At least five CrewAI tasks are defined with `description`,
      `expected_output`, `agent`, and `context` (FR-6, KPI, AC §14.5).
- [x] At least three tasks consume earlier task outputs via explicit
      `context` (AC §14.5). T2, T3, T4, T5, T6, T7, T8 all consume
      context from earlier tasks (7 ≥ 3).
- [x] The crew uses a sequential `Process` by default, or any deviation
      is justified in this document (FR-8). Sequential process is
      confirmed in §7.
- [x] Agent prompts and task descriptions are documented verbatim in
      `docs/PROMPTS.md` (AC §14.5).

### Implementation-level criteria *(require Phases 5–10)*

- [ ] The crew is launched from a single documented kickoff entry point
      (FR-9). *Requires Phase 5 implementation.*
- [ ] Raw and processed outputs are saved at the canonical paths in §9
      (FR-10). *Requires Phase 6+ implementation.*
- [ ] Markdown drafts are produced before any LaTeX assembly and live
      under `results/generated_markdown/` (FR-11, FR-12, AC §14.5).
      *Requires Phase 6 implementation.*
- [ ] Markdown drafts include heading, figure, table, equation, and
      citation placeholders, and follow a logical topic progression
      (FR-13, FR-14). *Requires Phase 6 implementation.*
- [ ] All model and search calls go through the controlled
      provider/service layer (NFR-23, NFR-24). *Requires Phase 5
      implementation.*
- [ ] `.env-example` exists and documents the required environment
      variables (FR-4, NFR-21). *Requires Phase 5 implementation.*
- [ ] Every agent invocation, tool call, and produced artifact is
      logged under `results/run_logs/` (NFR-16). *Requires Phase 5
      implementation.*
- [ ] The Reviewer Agent runs as the last LLM stage and produces review
      notes (FR-37). *Requires Phase 6+ implementation.*
- [ ] After the Reviewer Agent finishes, the deterministic
      `ValidatorService` defined in `docs/PRD_pdf_validation.md` runs
      and emits a validation report; **the LLM is not the source of
      truth for validation** (FR-40, NFR-19, AC §14.5). *Requires
      Phase 11 implementation.*
- [ ] No fabricated sources enter `references.bib` at any stage
      (see `docs/PRD_bibliography_and_citations.md`). *Requires Phase 7
      implementation.*
