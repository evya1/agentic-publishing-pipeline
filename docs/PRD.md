# PRD: CrewAI Research-to-LaTeX-to-PDF Generator

**Document type:** Product Requirements Document  
**Project:** Homework 03 — Orchestration of AI Agents / אורקסטרציה של סוכני AI  
**Primary product:** A professional agentic document-generation system that transforms a research topic into a structured LaTeX project and a final PDF article.  
**Status:** Production PRD.
**Language policy:** The system and documentation are primarily English, while the generated article must include Hebrew and English mixed content to demonstrate Bi-Directional (BiDi) support.

---

## 1. Overview

The **CrewAI Research-to-LaTeX-to-PDF Generator** is an agentic software system that receives a document topic and produces a professional, reproducible, at least 15-page PDF article using a CrewAI-based workflow and a structured LaTeX project.

The system is a modular AI-assisted publishing pipeline composed of multiple agents, tasks, intermediate artifacts, validation steps, and a final LaTeX-to-PDF compilation stage.

The project must demonstrate:

- professional software-engineering workflow;
- modular CrewAI orchestration;
- responsible use of AI-generated content;
- structured Markdown-to-LaTeX production;
- professional LaTeX document engineering;
- correct handling of Hebrew and English BiDi formatting;
- use of diagrams, tables, and figures in the text;
- reproducible repository structure and documentation;
- visible evidence of quality control, validation, logs, and cost awareness.
 

---

## 2. Problem Statement

Producing a high-quality technical article requires several coordinated activities: research, outline design, technical writing, editing, bibliography management, diagram/figure preparation, mathematical notation and coherent conventions, combination of hebrew and english text togther, tables, glossary/index-like structures, LaTeX organization, PDF compilation, and final validation.

When this process is done manually or with one large prompt, it becomes difficult to reproduce, debug, extend, validate, or maintain. A real-world organization or open-source community needs a system where each responsibility is separated, observable, and replaceable.

This project solves that problem by building a **multi-agent document factory**: a modular CrewAI workflow that turns an input topic into a complete LaTeX project and a polished PDF output.

---

## 3. Product Vision

The product should feel like a small internal tool that a large technology company, an AI research group, or an open-source documentation team could use to generate technical white papers, internal engineering reports, or research-style documentation.

The product is expected to be:

- structured enough for professional engineering review;
- simple enough to run locally as a course project;
- modular enough to replace agents, prompts, LLM providers, or LaTeX templates;
- transparent enough to inspect intermediate artifacts and debug failures.

---

## 4. Target Users and Stakeholders

| Stakeholder                                     | Need                                                                                                                                          |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| **AI workflow / agent orchestration engineers** | Design and evaluate a multi-agent pipeline with specialized agents for research, writing, validation, and artifact generation.                |
| **Research automation teams**                   | Transform research topics or rough ideas into structured technical documents with references, figures, tables, and a reproducible PDF output. |
| **Technical writers working with AI tools**     | Produce consistent, reviewable technical reports from research notes, engineering inputs, and intermediate outputs.                           |
| **R&D teams in AI / software companies**        | Prototype agent-based systems that automate parts of the research-to-report workflow while keeping the process modular and inspectable.       |
| **Future developer / maintainer**               | Extend, debug, and improve the pipeline without rewriting the whole project or breaking its workflow structure.                               |

---

## 5. Product Goals

### 5.1 Core Goals

1. Generate a final PDF article of at least 15 pages.
2. Use CrewAI to orchestrate a team of specialized agents.
3. Use clear task boundaries: research, outline, writing, review, asset generation, LaTeX conversion, bibliography, and validation.
4. Pass structured context between tasks instead of relying on one large prompt.
5. Generate intermediate Markdown before generating LaTeX.
6. Produce a full LaTeX project directory, not only a final PDF.
7. Compile the LaTeX project into a polished final PDF.
8. Preserve intermediate artifacts so the pipeline is observable and debuggable.
9. Document installation, configuration, execution, and regeneration instructions.
10. Demonstrate professional code quality and project structure and design. 

### 5.2 LaTeX Document Engineering Goals

1. The final LaTeX document must be composed from multiple internal `.tex` files, similar to professional academic article  projects.
2. Each internal LaTeX file must have a clear responsibility, such as:
   - `main.tex` — root document and includes;
   - `preamble.tex` — packages, fonts, document settings;
   - `macros.tex` — project-specific mathematical notation and reusable commands;
   - `chapters/*.tex` — individual chapters/sections;
   - `figures/` — generated and static figures;
   - `tables/` — standalone table `.tex` files;
   - `references.bib` — bibliography records.

   Tables and TikZ figures must not be written inline inside chapter files. Their LaTeX source code must be placed in dedicated files under tables/ or figures/, and chapter files must include them at the relevant location using \input{...}. This keeps chapter files focused on the article text and follows the same clean-code principle used in software: large technical blocks should be separated by responsibility instead of bloating the main content files.

3. The system must include a `macros.tex` file for mathematical conventions used throughout the article.
4. The article must include a nomenclature section for at least two symbols used in the document.
5. The article must include an index at the end of the file, with at least one Hebrew indexed term and at least one English indexed term.
6. The document should be written in a way that resembles a coherent article, not unrelated filler sections.

### 5.3 BiDi and Hebrew and English Goals

1. The final PDF must include at least one substantial section that mixes Hebrew and English.
2. The system must demonstrate correct right-to-left and left-to-right formatting.
3. English technical terms inside Hebrew sentences must be readable and correctly ordered.
4. Hebrew paragraphs must be right-aligned.
5. English formulas, code terms, references, and citations must remain visually stable inside Hebrew text.
6. Font choices must support both Hebrew and English in LuaLaTeX, which is the default LaTeX engine for the MVP. XeLaTeX may be supported later as an optional fallback.

### 5.4 Repository and Submission Goals

1. The repository must include `README.md` at the root.
2. The repository must include `docs/PRD.md`, `docs/PLAN.md`, and `docs/TODO.md`.
3. The repository must include the complete LaTeX project used to generate the PDF.
4. The repository must include the final generated PDF under a clear output path, such as `results/final.pdf`.
5. The repository must include source code, prompts, diagrams/assets, documentation, and reproducibility instructions.

---

## 6. Success Metrics / KPIs

| KPI | Target |
|---|---|
| Final PDF generation | `results/final.pdf` exists and opens successfully. |
| Page count | Final PDF is  always nore than  15 pages, preferably 15–20 pages according to layout.|
| LaTeX project completeness | Full LaTeX source directory exists and can regenerate the PDF. |
| Multi-file LaTeX structure | `main.tex` includes separate files for preamble, macros, and chapters. Each chapter may call related table files and TikZ figure files using `\input{...}`. Table code and TikZ figure code must live in dedicated `.tex` files, not directly inside chapter files. |
| Required content coverage | PDF contains title page, table of contents, chapters, headers/footers, image, Python-generated graph, tikz figure, table, equation, theorem-like environment, bibliography, nomenclature, and index. |
| CrewAI orchestration | Specialized agents (as defined in §8.3) and at least 5 tasks are defined. |
| Context propagation | Tasks should consume outputs from previous tasks via explicit context. |
| Markdown-first workflow | Intermediate Markdown artifacts are generated before LaTeX conversion. |
| BiDi handling | At least one section demonstrates mixed Hebrew and English text with correct RTL behavior, alignment, and fonts. |
| Cross-references | At least one figure/table/equation is referenced later using LaTeX references such as `\ref` or `\eqref`. |
| Bibliography citations | The document includes bibliography citations in the text and a rendered bibliography section. |
| Nomenclature | At least two symbols appear in a nomenclature section near the end of the document. |
| Index | At least one Hebrew word and one English word appear in the final index. |
| Reproducibility | README instructions allow a new developer to install dependencies and regenerate the main outputs. |
| Observability | Logs or run summaries document major pipeline stages, failures, and outputs. |
| Cost awareness | The project documents provider/model usage and estimated or measured cost. |
| Code quality | `ruff check` and `pytest` pass, or any deviations are explicitly documented. |
| Security | No API keys or secrets are committed; `.env-example` exists. |

---

## 7. Scope

### 7.1 In Scope

The project includes:

- CrewAI-based orchestration;
- agent definitions and task definitions;
- prompt templates or prompt documentation;
- Markdown intermediate generation;
- LaTeX project generation;
- Python-generated graph creation;
- at least one static or generated image;
- table generation or inclusion;
- mathematical equation generation;
- theorem/definition/lemma-like LaTeX environment;
- bibliography generation using BibTeX/Biber-compatible records;
- nomenclature generation;
- index generation;
- Hebrew and English BiDi section;
- final PDF compilation, with `results/final.pdf` committed or included as a required output, and a clearly documented local command for regenerating it;
- validation checks for required artifacts;
- logs/run summaries;
- README and required docs.

### 7.2 Out of Scope

The project does not include:

- a full SaaS product;
- a production deployment;
- a web UI;
- real-time collaborative editing;
- peer-reviewed factual verification of every generated claim;
- unrestricted autonomous code execution;
- support for every possible LaTeX distribution;

---

## 8. Functional Requirements

### 8.1 Input and Configuration

| ID | Requirement |
|---|---|
| FR-1 | The system shall accept a document topic through configuration and/or CLI. |
| FR-2 | The system shall allow configuration of model provider, model name, output paths, language mode, and LaTeX engine. The default LaTeX engine for the MVP shall be LuaLaTeX. |
| FR-3 | The system shall load secrets from environment variables or `.env`, never from hardcoded source code. |
| FR-4 | The system shall provide `.env-example` documenting required environment variables. |

### 8.2 CrewAI Workflow

| ID | Requirement |
|---|---|
| FR-5 | The system shall define CrewAI agents with explicit `role`, `goal`, `backstory`, and optional tools. |
| FR-6 | The system shall define tasks with clear `description`, `expected_output`, assigned `agent`, and `context` where relevant. |
| FR-7 | The system shall assemble agents and tasks into a CrewAI crew. |
| FR-8 | The process should be sequential. |
| FR-9 | The system shall run the crew using a kickoff-style entry point. |
| FR-10 | The system shall save raw and processed outputs from the crew. |

### 8.3 Agent Responsibilities

| Agent | Responsibility |
|---|---|
| Research Agent | Collects background, key points, terminology, and candidate references. |
| Outline Agent | Designs a coherent article structure. |
| Writer Agent | Produces readable Markdown chapters from the research and outline. |
| Technical Asset Agent | Produces or specifies figures, a Python-generated graph, tables, formulas, and theorem-like content. |
| Hebrew/BiDi Agent | Produces and validates at least one Hebrew and English mixed section. |
| LaTeX Agent | Converts approved Markdown and assets into a structured LaTeX project. |
| Bibliography Agent | Creates and maintains `references.bib` and citation keys. |
| Reviewer Agent | Reviews coherence, structure, formatting requirements, and missing deliverables before deterministic validation. The Reviewer Agent may identify likely issues, but it is not the source of truth for validation. |

### 8.4 Markdown Generation

| ID | Requirement |
|---|---|
| FR-11 | The system shall generate Markdown drafts before LaTeX conversion. |
| FR-12 | Markdown drafts shall be stored in `results/generated_markdown/` or equivalent. |
| FR-13 | Markdown shall include headings, figure placeholders, table placeholders, equation placeholders, and citation placeholders. |
| FR-14 | Markdown content shall be coherent and follow a logical topic progression. |

### 8.5 LaTeX Generation

| ID | Requirement |
|---|---|
| FR-15 | The system shall generate a full LaTeX project directory. |
| FR-16 | The LaTeX project shall contain `main.tex`. |
| FR-17 | The LaTeX project shall contain separated internal `.tex` files. Chapter files shall contain the main narrative content only. Each substantial table and each TikZ figure shall be stored in its own dedicated `.tex` file and included from the corresponding chapter using `\input{...}`. |
| FR-17a | The LaTeX project shall include a `tables/` directory for standalone table `.tex` files. |
| FR-17b | The LaTeX project shall include a `figures/` directory for figure assets, figure wrapper `.tex` files, and TikZ figure `.tex` files. |
| FR-17c | Chapter files shall call related tables and TikZ figures using `\input{tables/<table_file>.tex}` or `\input{figures/<figure_file>.tex}`. |
| FR-17d | Long table environments and TikZ pictures shall not be embedded directly inside chapter files, because this bloats the chapter source and violates the project’s clean-code and separation-of-responsibilities principles. Regular image figures may use a short `figure` wrapper inside the corresponding chapter file when appropriate. |
| FR-18 | The LaTeX project shall contain `macros.tex` for reusable mathematical notation. |
| FR-19 | The LaTeX project shall contain a bibliography file such as `references.bib`. |
| FR-20 | The LaTeX project shall compile with LuaLaTeX as the default and required MVP engine. XeLaTeX may be supported later as an optional fallback, but generated templates, build scripts, README commands, and validation checks must target LuaLaTeX by default. |
| FR-21 | The document shall include headers and footers. |
| FR-22 | The document shall include a title page and table of contents. |
| FR-23 | The document shall include chapters. |
| FR-24 | The document shall include at least one theorem-like environment, such as `definition`, `theorem`, `lemma`, or `example`. |
| FR-25 | The document shall include at least one equation with a label and a later reference using `\ref` or `\eqref`. |
| FR-26 | The document shall include a nomenclature section with at least two symbols. |
| FR-27 | The document shall include an index with at least one Hebrew term and one English term. |

### 8.6 Assets, Figures, Tables, and References

| ID | Requirement |
|---|---|
| FR-28 | The system shall include at least one image in the final PDF. |
| FR-29 | The system shall generate at least one graph using Python code. |
| FR-30 | Python-generated graph image files shall be saved under `latex_project/figures/`. A fixed figure shall be included through a `figure` wrapper in its corresponding chapter `.tex` file. |
| FR-31 | The document shall include at least one table. Each table shall be stored in its own dedicated `.tex` file under `latex_project/tables/` and included from the relevant chapter using `\input{...}`. The table input shall be wrapped in a `table` environment with a caption. |
| FR-32 | At least one figure, table, or equation shall be referenced from the text using LaTeX cross-reference commands. |
| FR-33 | Bibliography citations shall be used in the document text and rendered in the bibliography section. |

### 8.7 Validation and Output

| ID | Requirement |
|---|---|
| FR-34 | The system shall validate required repository files. |
| FR-35 | The system shall validate required LaTeX files. |
| FR-36 | The system shall validate required PDF content indicators where feasible. |
| FR-37 | The system shall generate a run summary and validation report after the reviewer stage and deterministic validation stage complete. |
| FR-38 | The final PDF shall be saved in a predictable output path. |
| FR-39 | The system shall fail with a clear error message if required dependencies or configuration values are missing. |
| FR-40 | After the Reviewer Agent completes its review, the system shall run a deterministic `ValidatorService` that checks required files, required directories, generated artifacts, LaTeX build outputs, and basic PDF/content indicators where feasible. This service must not rely on an LLM as the source of truth for validation. |

---

## 9. Non-Functional Requirements

### 9.1 Maintainability

| ID | Requirement |
|---|---|
| NFR-1 | Code shall be modular and organized by responsibility. |
| NFR-2 | Files should stay reasonably short (`.py` at most 150 lines); large files must be split by responsibility. |
| NFR-3 | Functions should be short, readable, and focused. |
| NFR-4 | If a function becomes long or messy, helper functions should be extracted. |
| NFR-5 | The project should avoid unnecessary classes and moving parts. |
| NFR-6 | The codebase should follow the DRY principle and avoid duplication. |
| NFR-6a | LaTeX source files shall follow separation of responsibilities. Chapter files should contain readable article text and high-level `\input{...}` calls only. Verbose table code, TikZ code, and figure wrapper code shall be moved into dedicated files under `tables/` or `figures/`. |

### 9.2 Python Code Quality

| ID | Requirement |
|---|---|
| NFR-7 | All functions shall use type hints, including return types. |
| NFR-8 | When introducing a new Python variable or a new code block/scope, use type annotations on the variable’s first appearance where they improve safety, clarity, or readability, for example `a: int = 10`. This is a guideline rather than a strict rule: annotations should be used thoughtfully and should not clutter or overburden the code. |
| NFR-9 | String interpolation should use f-strings always. |
| NFR-10 | Use listcomp and dictcomp when they make the code easier to read. Avoid them when they make the logic harder to understand. |
| NFR-11 | Function names and variable names shall be self-descriptive. |
| NFR-12 | Complex logic should not be written as long inline code blocks. It should be decomposed into small, semantic, well-named functions to improve readability, reuse, testing, and maintainability. |
| NFR-13 | Input validation shall use `assert` or an equivalent explicit validation mechanism always. |
| NFR-14 | If a function can throw an exception, exception handling or explicit propagation must be designed intentionally. |
| NFR-15 | Code shall be clean, readable, and free of avoidable duplication. |

### 9.3 Reliability and Observability

| ID | Requirement |
|---|---|
| NFR-16 | The pipeline shall log major workflow stages. |
| NFR-17 | The system shall preserve intermediate artifacts for debugging. |
| NFR-18 | Errors shall be actionable and explain what should be fixed. |
| NFR-19 | Do not rely on the LLM to validate its own output. The Reviewer Agent may perform qualitative review, but LLM-generated content must also be checked afterward by deterministic validation steps such as schemas, tests, compilers, file-system checks, and PDF/content checks where feasible. |

### 9.4 Security and Configuration

| ID | Requirement |
|---|---|
| NFR-20 | Secrets shall never be committed. |
| NFR-21 | `.env-example` shall document required variables. |
| NFR-22 | Configuration shall be separated from source code. |
| NFR-23 | External API/model calls should be routed through a controlled provider/service layer. |

### 9.5 Extensibility

| ID | Requirement |
|---|---|
| NFR-24 | It should be possible to replace the model provider without rewriting the whole pipeline. |
| NFR-25 | It should be possible to add or replace agents with minimal changes. |
| NFR-26 | It should be possible to replace the LaTeX template without rewriting the CrewAI workflow. |
| NFR-27 | It should be possible to change the article topic through configuration. |

### 9.6 BiDi and Typography Quality

| ID | Requirement |
|---|---|
| NFR-28 | Hebrew text shall be readable and correctly directed. |
| NFR-29 | English terms inside Hebrew sentences shall preserve correct character order. |
| NFR-30 | Hebrew paragraphs shall be right-aligned when appropriate. |
| NFR-31 | Font choices shall support Hebrew, English, math, and code-like technical terms. |
| NFR-32 | Tables and figures shall not overflow page boundaries. |

---

## 10. User Stories

| ID | User Story |
|---|---|
| US-1 | As a technical documentation team, we want to generate a structured technical article from a topic so that we can accelerate internal documentation work. |
| US-2 | As an open-source maintainer, we want the generated article to include reproducible LaTeX sources so that the community can inspect and improve it. |
| US-3 | As an AI engineer, we want each agent to have a clear responsibility so that we can debug and improve the workflow. |
| US-4 | As a future developer, we want intermediate Markdown and logs so that failures are easy to locate. |
| US-5 | As a product/research team, we want figures, tables, formulas, and citations so that the document looks like a real technical publication. |
| US-6 | As a Hebrew and English technical writer, we want BiDi support so that Hebrew explanations can include English technical terms, formulas, and citations. |
| US-7 | As a reviewer, we want a validation checklist so that missing deliverables are detected before submission. |

---

## 11. Main Use Cases

### UC-1: Generate a Full Article from a Topic

1. User defines a topic in configuration or CLI.
2. Research Agent gathers structured research notes.
3. Outline Agent creates a coherent article outline.
4. Writer Agent drafts Markdown chapters.
5. Reviewer Agent reviews the draft for coherence, structure, formatting requirements, and missing deliverables. 
6. LaTeX Agent converts the reviewed content into a LaTeX project. 
7. Deterministic `ValidatorService` checks required files, LaTeX files, build outputs, and PDF/content indicators where feasible.
8. The system produces the final PDF and validation report.

### UC-2: Regenerate LaTeX After Content Changes

1. User edits Markdown or generated content.
2. LaTeX generation is rerun.
3. PDF is recompiled.
4. Validation confirms that references, bibliography, index, and nomenclature still render.

### UC-3: Validate Before Submission

1. User runs a validation command.
2. The system checks repository files, docs, LaTeX files, assets, and output PDF.
3. The system reports missing or failed requirements.
4. User fixes issues and reruns validation.

---

## 12. Inputs and Outputs

### 12.1 Inputs

- Article topic.
- Model provider configuration.
- LaTeX engine configuration.
- Style/template configuration.
- Optional source references or seed notes.

### 12.2 Intermediate Outputs

- Research notes.
- Outline.
- Markdown draft.
- Reviewed Markdown draft.
- Generated graph image.
- Table data or table LaTeX.
- Formula/theorem snippets.
- Bibliography entries.
- BiDi section draft.
- Logs and run summaries.

### 12.3 Final Outputs

- `results/final.pdf`
- `latex_project/main.tex`
- `latex_project/preamble.tex`
- `latex_project/macros.tex`
- `latex_project/references.bib`
- `latex_project/chapters/*.tex`
- `latex_project/figures/*.tex`
- `latex_project/figures/*`
- `latex_project/tables/*.tex`
- `results/generated_markdown/*`
- `results/run_logs/*`
- `docs/PRD.md`
- `docs/PLAN.md`
- `docs/TODO.md`

---

## 13. Required Deliverables

| Deliverable | Required Path / Example |
|---|---|
| Root README | `README.md` |
| PRD | `docs/PRD.md` |
| Plan | `docs/PLAN.md` |
| TODO | `docs/TODO.md` |
| CrewAI pipeline PRD | `docs/PRD_crewai_pipeline.md` |
| LaTeX generation PRD | `docs/PRD_latex_generation.md` |
| PDF validation PRD | `docs/PRD_pdf_validation.md` |
| Bibliography and citations PRD | `docs/PRD_bibliography_and_citations.md` |
| Python package | `src/<package_name>/` |
| Tests | `tests/` |
| Configuration | `config/` |
| Environment example | `.env-example` |
| LaTeX project | `latex_project/` |
| Final PDF | `results/final.pdf` |
| Generated Markdown | `results/generated_markdown/` |
| Logs | `results/run_logs/` |
| Assets | `assets/` or `latex_project/figures/` |

---

## 14. Acceptance Criteria

### 14.1 Course and Repository Acceptance Criteria

- [ ] Repository contains `README.md` at the root.
- [ ] Repository contains `docs/PRD.md`.
- [ ] Repository contains `docs/PLAN.md`.
- [ ] Repository contains `docs/TODO.md`.
- [ ] Repository contains the complete LaTeX project.
- [ ] Repository contains the final generated PDF.
- [ ] Repository contains source code for the CrewAI workflow.
- [ ] README explains installation, configuration, usage, architecture, and how to regenerate the PDF.
- [ ] README explains the CrewAI architecture and agent/task workflow.
- [ ] README documents the LaTeX project structure.
- [ ] README documents current limitations and  areas for future improvement.


### 14.2 PDF Content and Structure Acceptance Criteria

- [ ] Final PDF is at least 15 pages.
- [ ] Final PDF contains a cover/title page.
- [ ] Cover page includes topic, author/group, date, and course context.
- [ ] Final PDF contains a table of contents.
- [ ] Final PDF is divided into coherent chapters or sections.
- [ ] Final PDF contains headers and footers.
- [ ] Final PDF contains at least one image.
- [ ] Final PDF contains at least one graph generated by Python code.
- [ ] Final PDF contains at least one tikz (simple automata) figure.
- [ ] Final PDF contains at least one table.
- [ ] Final PDF contains at least one mathematical equation.
- [ ] At least one equation has a LaTeX label and is referenced later with `\ref` or `\eqref`.
- [ ] Final PDF contains at least one theorem-like environment: definition, theorem, lemma, example, or similar.
- [ ] Final PDF contains bibliography citations in the text.
- [ ] Final PDF contains a rendered bibliography section.
- [ ] Final PDF contains a nomenclature section near the end.
- [ ] Nomenclature contains at least two symbols.
- [ ] Final PDF contains an index near the end.
- [ ] Index contains at least one Hebrew word and at least one English word.
- [ ] The content has a logical progression and does not use unrelated filler sections.

### 14.3 LaTeX Acceptance Criteria

- [ ] `main.tex` exists.
- [ ] `main.tex` includes or inputs internal `.tex` files.
- [ ] `preamble.tex` or equivalent exists.
- [ ] `macros.tex` exists and contains reusable mathematical/technical commands.
- [ ] Chapters are separated into multiple files under `chapters/` or equivalent.
- [ ] `references.bib` exists.
- [ ] The project compiles successfully with LuaLaTeX using the documented build command.
- [ ] The project supports Hebrew and English text.
- [ ] The project includes packages or configuration for theorem-like environments.
- [ ] The project includes packages or configuration for nomenclature.
- [ ] The project includes packages or configuration for index generation.
- [ ] Figures and tables are referenced correctly.
- [ ] Tables do not overflow the page.
- [ ] PDF compilation instructions are documented.
- [ ] Table code is stored in dedicated `.tex` files under `tables/` or equivalent.
- [ ] TikZ figure code is stored in dedicated `.tex` files under `figures/` or equivalent.
- [ ] Chapter files include related tables and TikZ figures using `\input{...}`.
- [ ] Chapter files are not bloated with long table environments or TikZ code.

### 14.4 BiDi Acceptance Criteria

- [ ] At least one section includes Hebrew text.
- [ ] At least one Hebrew paragraph includes embedded English technical terms.
- [ ] Mixed Hebrew and English text renders in the correct visual order.
- [ ] Hebrew text alignment is correct.
- [ ] English citations, labels, references, and inline technical identifiers remain readable inside Hebrew text.
- [ ] Fonts support both Hebrew and English.
- [ ] No visible RTL/LTR corruption appears in the final PDF.

Example (plain text) target sentence for validation:

> בפרק זה אנו מתארים את המושג Agent Runtime ואת הקשר שלו ל־Observability, כאשר המערכת משתמשת ב־CrewAI כדי לנהל תהליך כתיבה מודולרי.

### 14.5 CrewAI Acceptance Criteria

- [ ] Specialized agents are defined (at §8.3).
- [ ] At least 5 tasks are defined.
- [ ] Each task has a clear expected output.
- [ ] At least 3 tasks use context from previous tasks.
- [ ] The workflow produces inspectable intermediate artifacts.
- [ ] The workflow separates research, writing, review, LaTeX generation, and validation.
- [ ] The crew can be launched from a clear entry point.
- [ ] Agent prompts or prompt templates are documented.
- [ ] The workflow runs deterministic validation after the Reviewer Agent stage.

### 14.6 Code Quality Acceptance Criteria

- [ ] Code uses type hints for function parameters and return values.
- [ ] Newly introduced variables use type annotations on first appearance where they improve safety, clarity, or readability, without cluttering the code.
- [ ] Code uses f-strings where string interpolation is needed.
- [ ] Code uses listcomp/dictcomp where they improve clarity.
- [ ] Code is modular and organized by responsibility.
- [ ] Long technical strings are not embedded directly inside business logic.
- [ ] Inputs are validated using `assert` or an equivalent explicit validation mechanism.
- [ ] Expected exceptions are handled or intentionally propagated with clear messages.
- [ ] Function and Variable names are self-descriptive.
- [ ] Functions are not long and messy.
- [ ] Extractable components are moved into smaller helper functions when this improves readability.
- [ ] DRY principle is followed.
- [ ] Clean code does not contain avoidable duplication.
- [ ] Clean code contains a minimal number of classes and moving parts.
- [ ] `ruff check` passes or documented exceptions exist.
- [ ] `pytest` passes or documented exceptions exist.

### 14.7 Security, Configuration, and Cost Acceptance Criteria

- [ ] No API keys are committed.
- [ ] `.env-example` exists.
- [ ] Configuration is separated from source code.
- [ ] Model provider and model name are configurable.
- [ ] Output paths are configurable.
- [ ] Cost/pricing considerations are documented.
- [ ] Logs or run summaries include enough information to understand what happened during execution.

---

## 15. Assumptions

- The user has access to a supported LLM provider or local model.
- The user can install Python dependencies using `uv` or another documented method.
- The user can install or access a LaTeX distribution that supports LuaLaTeX.
- The generated document is evaluated mainly as a technical production artifact, not as peer-reviewed research.
- The project is allowed to use AI tools, but AI usage must be transparent and documented.
- The system is designed as a local/course-level project, not a production SaaS deployment.

---

## 16. Dependencies

### 16.1 Python Dependencies

Potential dependencies:

- `crewai`
- `pydantic`
- `python-dotenv`
- `matplotlib`
- `rich` or logging utilities
- `pytest`
- `ruff`
- optional: `bibtexparser`

### 16.2 System Dependencies

Potential dependencies:

- Python 3.11+ or project-defined version.
- LaTeX distribution such as MiKTeX, TeX Live, or MacTeX.
- LuaLaTeX as the required MVP engine; XeLaTeX is optional only if explicitly added later.
- Biber/BibTeX.
- Make or shell scripts for repeatable build commands, if used.

### 16.3 LaTeX Dependencies

The generated LaTeX project should compile with LuaLaTeX as the default and required MVP engine, because the document must support Unicode, Hebrew, English, custom fonts, math, and BiDi text. XeLaTeX may be supported later as an optional fallback, but it should not be the default target for templates, build scripts, README commands, or validation checks.

#### Engine and language support

Potential LaTeX packages:

* `fontspec` — required for Unicode font selection with LuaLaTeX.
* `polyglossia` — Hebrew/English language configuration for LuaLaTeX.
* `bidi` or LuaLaTeX-compatible BiDi support — bidirectional text support for Hebrew-heavy documents when needed.
* `lmodern` — Latin Modern font support for English/Latin text.
* `xcolor` — extended color support for links, theorem names, diagrams, and highlights.

#### Font requirements

The LaTeX template should define explicit fonts for Hebrew and English text.

Preferred fonts:

* Hebrew font: `David CLM`
* English font: `Latin Modern Roman`
* Math font: default LaTeX math font is acceptable for the MVP, unless a dedicated Unicode math font is added later.
* Code font: default monospace font is acceptable for the MVP.

The generated `preamble.tex` should be written and tested for LuaLaTeX:

```latex
\usepackage{fontspec}
\usepackage{polyglossia}

\setdefaultlanguage{hebrew}
\setotherlanguage{english}

\setmainfont{Latin Modern Roman}
\newfontfamily\hebrewfont[Script=Hebrew]{David CLM}
\newfontfamily\englishfont[Script=Latin]{Latin Modern Roman}
```

If `David CLM` is not available on the local machine, the system should fail with a clear LaTeX/build error or use a documented fallback Hebrew font. The README should mention that the required fonts must be installed or available through the chosen LaTeX distribution.

- Mathematics and theorem environments:

* `amsmath`, `amssymb`, `amsthm` — standard mathematical notation and theorem support.
* `mathtools` — useful extensions to `amsmath`.
* `thmtools` — cleaner theorem environment configuration.
* `thm-restate` — optional support for restating theorems later in the document.
* `autobreak` — optional support for long automatically broken equations.

- Figures, diagrams, and plots:

* `graphicx` — inserting generated figures and external images.
* `float` — improved control over figure/table placement.
* `tikz` — LaTeX-native diagrams.
* `pgfplots` — plots generated directly in LaTeX.
* Optional TikZ libraries: `arrows.meta`,  `positioning`,`graphs`, `automata`.

- Tables

* `booktabs` — professional table formatting.

- Cross-references, links, and navigation:

* `hyperref` — clickable links, PDF metadata, and internal navigation.
* `cleveref` — semantic references such as “Figure”, “Table”, “Equation”, “Theorem”.
* `varioref` — page-aware references such as “on the next page”.
* `zref-abspage` — advanced page-number/reference logic if needed.

- Layout and document styling:

* `geometry` — page size and margin configuration.
* `fancyhdr` — custom headers and footers.
* `afterpage` — delayed page-style commands when needed.

- Code and technical content

* `listings` — source-code blocks in the generated article.

- Bibliography, nomenclature, and index support:

* `biblatex` — bibliography management.
* `nomencl` — nomenclature or symbol list generation.
* `makeidx` or equivalent — index generation.

- Utility packages:

* `etoolbox` — robust LaTeX patching and conditional logic.
* `xparse` — modern command definitions.
* `ifthen` — simple conditional logic.
* `relsize` — relative font-size adjustments.

The MVP should use only the packages required for stable PDF generation. Advanced styling, custom theorem colors, page-aware Hebrew references, TikZ-heavy diagrams, and custom math symbols should be treated as optional template extensions rather than hard requirements.


## 17. Constraints

- The final article must be at least 15 pages.
- The final document must be generated through LaTeX, not Word.
- The repository must contain the LaTeX project used to generate the PDF.
- The repository must contain required documentation files.
- Hebrew and English BiDi handling must be demonstrated.
- Secrets must not be committed.
- Long prompt or technical instruction strings should not be buried inside Python business logic.
- The system must remain understandable and maintainable as a course project.
- The MVP build pipeline must target LuaLaTeX. Any XeLaTeX support is optional and must not conflict with the default LuaLaTeX path.
- LaTeX chapter files must remain focused on narrative content. Tables and TikZ figures must be separated into dedicated `.tex` files and included with `\input{...}` from the chapter where they belong.

---

## 18. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| LaTeX compilation fails | No final PDF | Add validation, clear build commands, and incremental compilation. |
| Hebrew and English text renders incorrectly | Major formatting issue | Use LuaLaTeX, proper Hebrew andEnglish fonts, and a dedicated BiDi validation section.|
| Bibliography does not render | Missing citations/references | Use `biblatex` + `biber` and document multi-pass compilation. |
| Index or nomenclature does not render | Missing required advanced LaTeX features | Add explicit build steps for index/nomenclature. |
| CrewAI output is inconsistent | Pipeline quality varies | Save intermediate outputs, use task-specific prompts, and add reviewer/validator stages. |
| Generated content becomes filler | PDF looks unprofessional | Enforce outline coherence and reviewer checks. |
| Code becomes over-engineered | Hard to understand | Keep minimal classes, clear services, short files, and simple architecture. |
| API keys leak | Security issue | Use `.env`, `.env-example`, and `.gitignore`. |
| Token/API costs become unclear | Poor cost awareness | Log provider/model usage and estimate cost. |
| Large strings make code unreadable | Maintenance issue | Move prompts/templates into dedicated files. |
| Chapter `.tex` files become bloated with table or TikZ code | LaTeX project becomes hard to read, review, and maintain | Store each table and TikZ figure in a dedicated `.tex` file under `tables/` or `figures/`, and include it from the corresponding chapter using `\input{...}`. |

---

## 19. Proposed Milestones

| Milestone | Description | Exit Criteria |
|---|---|---|
| M1 — Requirements | Define topic, goals, PRD, and acceptance criteria. | `docs/PRD.md` approved. |
| M2 — Architecture | Define agents, tasks, project structure, and LaTeX structure. | `docs/PLAN.md` completed. |
| M3 — Task Planning | Break implementation into small tasks. | `docs/TODO.md` completed. |
| M4 — CrewAI MVP | Implement researcher → writer → reviewer pipeline. | Markdown draft generated. |
| M5 — Full Agent Workflow | Add technical assets, bibliography, BiDi, LaTeX, validation. | All required intermediate artifacts exist. |
| M6 — LaTeX Project | Generate structured LaTeX project. | `main.tex`, chapters, macros, bib, figures exist. |
| M7 — PDF Build | Compile final PDF. | `results/final.pdf` opens and is at least 15 pages. |
| M8 — Validation and Polish | Run tests, lint, validation, README updates. | All acceptance criteria reviewed. |
| M9 — Submission Readiness | Prepare final GitHub repository and model submission PDF. | Final checklist completed. |

---

## 20. Required Additional PRDs

Because the project contains complex mechanisms, the following dedicated PRDs are Required:

1. `docs/PRD_crewai_pipeline.md`  
   Describes the CrewAI agent/task/context workflow, expected intermediate artifacts, the Markdown-first generation stage, and the handoff to deterministic validation after the Reviewer Agent.

2. `docs/PRD_latex_generation.md`  
   Describes the LaTeX project structure, the LuaLaTeX MVP engine, BiDi handling with `fontspec` + `polyglossia` and the `David CLM` / `Latin Modern Roman` font pair, macros, theorem environments, nomenclature, index, table/TikZ separation rules, and the multi-pass PDF build process.

3. `docs/PRD_pdf_validation.md`  
   Describes the deterministic `ValidatorService` that runs after the Reviewer Agent stage, the file and PDF content checks it performs, and the validation report it emits. The LLM is not the source of truth for validation.

4. `docs/PRD_bibliography_and_citations.md`  
   Describes the Bibliography Agent's source-discovery and verification workflow, the `references.bib` toolchain (`biblatex` + `biber`), the citation-key convention, the no-fabricated-sources policy, and how unresolved `\cite{...}` references are surfaced as build-time errors by the deterministic validator.

These should not replace this main PRD. They should refine the most complex mechanisms.

---

## 21. Open Questions

- What exact topic will the final article cover?
- Should the article be mostly Hebrew with English terms, mostly English with one Hebrew/BiDi chapter, or balanced bilingual?
- Should XeLaTeX fallback support be implemented now, or deferred as a future improvement?
- Which LLM provider/model will be used for the final run?
- Will web search be used, or will the project rely only on provided/local sources?
- How strict should the PDF page-count validation be?
- Should graph generation be deterministic with fixed data, or generated from actual research data?
- Should the theorem-like environment be a `definition`, `theorem`, `lemma`, or `example`?

---

## 22. Canonical Demo Article Topic

This section concretizes the first item in §21 Open Questions ("What
exact topic will the final article cover?") for the **default demo
run** of the pipeline. It is a **runtime default**, not a hardcoded
implementation detail: the topic, source set, and intended angle are
loaded from configuration (`config/article_sources.yaml`,
`.env` / CLI overrides per FR-1 and FR-2) and can be replaced without
modifying source code (NFR-27).

### 22.1 Status and overridability

- The demo topic below is the **default** the pipeline targets on a
  fresh run; it is not the only topic the pipeline must be able to
  produce (NFR-27).
- The article, the bibliography, the LaTeX project, the final PDF, the
  CrewAI workflow, and the deterministic `ValidatorService` are **not
  yet implemented**. This section only locks the topic and source
  manifest; real research synthesis, bibliography curation, and
  article generation happen in later phases of `docs/PLAN.md`.

### 22.2 Topic and target angle

- **Working title:** *Reasoning-Centric Agentic LLM Systems: Planning,
  Memory, Retrieval, Tool Use, and Multimodal Reasoning in 2025–2026.*
- **Angle.** A practitioner-facing technical survey-style article that
  organizes recent (2024–2026) work around five reasoning dimensions
  for agentic LLM systems: **planning**, **memory**, **retrieval**,
  **tool use**, and **multimodal reasoning**. The article emphasizes
  how these dimensions are evaluated and combined, rather than
  benchmarking a single model.
- **Tone.** Closer to a curated technical white paper than a peer-reviewed
  survey; aligned with the product vision in §3.

### 22.3 Article scope

- Background framing of "reasoning-centric agentic LLM systems" in the
  2025–2026 landscape, anchored on recent reasoning surveys.
- One coherent chapter per reasoning dimension (planning, memory,
  retrieval, tool use, multimodal reasoning), each grounded in the
  source set in §22.4.
- A short evaluation chapter discussing how agentic-LLM reasoning is
  measured (planning benchmarks, agentic-reasoning evaluation, event
  forecasting).
- A Hebrew/English BiDi section satisfying §5.3 / §14.4; the BiDi
  section discusses one of the reasoning dimensions in mixed
  Hebrew/English text using `David CLM` + `Latin Modern Roman` per
  §16.3.
- Required LaTeX content as listed in §14.2 (image, Python-generated
  graph, TikZ figure, table, labeled equation with cross-reference,
  theorem-like environment, nomenclature ≥2 symbols, index ≥1 Hebrew
  + ≥1 English term, bibliography section).

### 22.4 Source set summary

The default run uses the following 10 arXiv papers. The canonical,
machine-readable manifest with citation keys and verification status
lives in **`config/article_sources.yaml`** (owned by the Bibliography
Agent per `docs/PRD_bibliography_and_citations.md` §5).

| arXiv ID | Title | Intended dimension |
|---|---|---|
| 2504.09037 | A Survey of Frontiers in LLM Reasoning: Inference Scaling, Learning to Reason, and Agentic Systems | Background / reasoning survey |
| 2502.04644 | Agentic Reasoning: Reasoning LLMs with Tools for the Deep Research | Tool use / deep research |
| 2511.09378 | The 2025 Planning Performance of Frontier Large Language Models | Planning evaluation |
| 2511.01448 | LiCoMemory: Lightweight and Cognitive Agentic Memory for Efficient Long-Term Reasoning | Memory |
| 2601.06037 | TeleMem: Building Long-Term and Multimodal Memory for Agentic AI | Memory + multimodal |
| 2510.10991 | A Survey on Agentic Multimodal Large Language Models | Multimodal reasoning (survey) |
| 2510.18303 | Proactive Reasoning-with-Retrieval Framework for Medical Multimodal Large Language Models | Retrieval + multimodal |
| 2510.19361 | AgenticMath: Enhancing LLM Reasoning via Agentic-based Math Data Generation | Reasoning data / math |
| 2407.01231 | MIRAI: Evaluating LLM Agents for Event Forecasting | Evaluation |
| 2601.12538 | Agentic Reasoning for Large Language Models | Agentic reasoning core |

### 22.5 Source archives and manifest

- **Archive bytes are local-only.** The arXiv LaTeX source archives
  (`*.zip`) live under **`data/sources/arxiv/source_zips/`**. That
  directory is gitignored; the bytes are **not** committed to the
  repository.
- **The manifest is tracked.** `config/article_sources.yaml` is the
  single tracked record of which sources the default demo run uses,
  with citation keys, intended use, and verification status.
- **Verification is not done yet.** Each entry's verification status
  starts as `unverified`. The Bibliography Agent performs URL/DOI
  verification and finalizes citation keys during Phase 7 of
  `docs/PLAN.md`, per `docs/PRD_bibliography_and_citations.md` §7–§9.
- **Author metadata may be incomplete.** Where authoritative author
  metadata is not yet available, manifest entries use `authors: []`
  and a TODO is tracked in `docs/TODO.md`. No fabricated authors,
  ever (CLAUDE.md, `docs/PRD_bibliography_and_citations.md`).

## 23. Definition of Done

The project is considered done when:

- the CrewAI workflow runs from a documented entry point;
- the system generates inspectable intermediate Markdown artifacts;
- the system generates a structured multi-file LaTeX project;
- the LaTeX project includes macros, bibliography, nomenclature, index, theorem-like environment, labeled equation, figure, table, image, and Python-generated graph;
- the final PDF is at least 15 pages and visually coherent;
- Hebrew and English BiDi formatting is visibly demonstrated and correct;
- required repository documentation exists;
- README explains how to install, run, validate, and regenerate the PDF;
- tests/lint/validation are run and documented;
- secrets are not committed;
- cost and AI usage are documented;
- the repository is ready for professional review.