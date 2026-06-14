# C4 views — agentic-publishing-pipeline

> **Status:** Phase 4 design amendment (P4-I04). Documentation-only.

This document records the system-context (C4 Level 1), container
(C4 Level 2), and component (C4 Level 3) views of the planned runtime.
The runtime is **not implemented**; this is design scope only.

The diagrams below are intentionally aligned with the eight agents and
eight tasks specified in `docs/PRD_crewai_pipeline.md` §5–§6 and with the
deterministic `ValidatorService` boundary in
`docs/PRD_pdf_validation.md`.

---

## 1. System context (C4 Level 1)

The system context view shows the publishing pipeline as a single
software system that consumes external inputs (topic, source manifest,
provider/search APIs, LaTeX toolchain) and produces external outputs
(LaTeX project, final PDF, validation report, evidence bundle).

```mermaid
flowchart TB
    Operator["Course operator<br/>(human)"]
    Reviewer["Human reviewer<br/>(approves Markdown stage)"]
    LLMProvider["LLM provider<br/>(model API)"]
    SearchProvider["Search provider<br/>(metadata-verification API)"]
    SourceManifest["Verified source manifest<br/>(config/article_sources.yaml)"]
    LaTeXToolchain["LaTeX toolchain<br/>(LuaLaTeX, biber, makeindex)"]

    subgraph System["Agentic Publishing Pipeline"]
        Pipeline["CrewAI workflow +<br/>deterministic services"]
    end

    PDF["Final PDF<br/>(results/&lt;run_id&gt;/final.pdf)"]
    Report["Validation report +<br/>artifact manifest +<br/>usage/cost log"]
    Evidence["Sanitized evidence bundle<br/>(submission/)"]

    Operator -->|topic, mode, overrides| System
    SourceManifest -->|verified entries| System
    Reviewer -->|approval / rejection| System
    System <-->|prompt + response| LLMProvider
    System <-->|metadata lookup| SearchProvider
    System -->|build commands| LaTeXToolchain
    LaTeXToolchain -->|build artifacts| System
    System --> PDF
    System --> Report
    System --> Evidence
```

### Boundaries

- **In scope of the system:** the CrewAI orchestration, agents and tasks,
  provider facade, API Gatekeeper, deterministic renderer, LaTeX
  compilation service, Python graph/asset rendering, deterministic
  `ValidatorService`, run workspace, prompt/config registry, and the
  artifact promotion machinery.
- **Out of scope:** the LLM provider, the search provider, the LaTeX
  distribution, and Moodle submission.

---

## 2. Container view (C4 Level 2)

The container view decomposes the system into the long-lived runtime
containers. Every container has an owner, an authoritative configuration
source, an allowed root for side effects, and an explicit boundary
between LLM-authored content and deterministic processing.

```mermaid
flowchart LR
    subgraph CLI["CLI entry point (P5-I11)"]
        Modes["Operational modes:<br/>dry-run, offline-fixture, live,<br/>compile-only, validate-only,<br/>topic/manifest override, resume"]
    end

    subgraph RunCtx["PipelineRunContext (P5-I10)"]
        RunID["Run ID<br/>(ULID/UUID)"]
        Workspace["Isolated workspace<br/>(results/&lt;run_id&gt;/...)"]
        ConfigSnap["Configuration snapshot"]
        EventLog["Structured event log"]
        UsageLog["Usage/cost log"]
        Manifest["Artifact manifest"]
    end

    subgraph Registry["Prompt/config registry (P5-I12)"]
        PromptStore["Versioned prompts +<br/>agent/task config"]
    end

    subgraph Crew["CrewAI orchestration"]
        Agents["8 agents (PRD §8.3)"]
        Tasks["T1–T8 (PRD_crewai_pipeline §6)"]
    end

    subgraph Contracts["Typed artifact contracts (P5-I08)"]
        Models["Pydantic models<br/>(named, versioned)"]
        Repair["One bounded repair<br/>attempt per stage"]
    end

    subgraph Provider["Provider facade"]
        ModelAdapter["Model adapter<br/>(typed normalized response)"]
        SearchAdapter["Search adapter"]
    end

    subgraph Gatekeeper["API Gatekeeper (P5-I09)"]
        Policy["Budgets, retries,<br/>timeouts, classification"]
        UsageEmit["Usage/cost events"]
    end

    subgraph Render["Deterministic rendering & file I/O (P5-I04, P5-I05)"]
        SemanticToLatex["Semantic spec → LaTeX"]
        SafePaths["Path guards +<br/>atomic writes"]
    end

    subgraph Build["LaTeX build service (P5-I06)"]
        Compile["LuaLaTeX + biber<br/>multi-pass"]
        BuildLog["Build log capture"]
    end

    subgraph Assets["Python graph & asset rendering (P5-I07, P8-I02)"]
        GraphRender["Typed graph specs →<br/>figures/*.png|pdf"]
    end

    subgraph Validator["Deterministic ValidatorService (P11)"]
        FileCheck["Files / LaTeX checks"]
        PDFCheck["PDF content checks +<br/>page budget (P10-I03)"]
    end

    subgraph Fixtures["Offline fixtures (P5-I11)"]
        FixtureStore["Recorded provider<br/>responses"]
    end

    CLI --> RunCtx
    CLI --> Registry
    Registry --> Crew
    Crew --> Contracts
    Contracts --> Crew
    Crew --> Provider
    Provider --> Gatekeeper
    Gatekeeper -->|live| LLMProvider["LLM/Search providers"]
    Gatekeeper -->|offline| FixtureStore
    Crew --> Render
    Render --> SafePaths
    SafePaths --> Workspace
    Crew --> Assets
    Assets --> SafePaths
    RunCtx --> Build
    Build --> SafePaths
    Build --> Validator
    Render --> Build
    Validator --> Manifest
    Validator --> EventLog
    Manifest --> Promotion["Explicit promotion<br/>(workspace → canonical)"]
    Promotion --> Canonical["latex_project/ +<br/>results/final.pdf"]
```

### Container responsibilities

| Container | Owner / authority | Allowed root for writes | Side effects |
|---|---|---|---|
| CLI entry point | Operator | none directly | starts the run, selects mode, passes overrides |
| `PipelineRunContext` | Deterministic code | `results/<run_id>/` | creates run ID, workspace, config snapshot, event log, usage log, artifact manifest |
| Prompt/config registry | Deterministic code | read-only at runtime | loads versioned prompts/config; validates schema/version compatibility |
| CrewAI orchestration | CrewAI runtime | none directly (delegates) | drives sequential T1 → T8 |
| Typed artifact contracts | Deterministic code | none directly | parses & validates LLM/agent output; emits validation errors; allows ≤1 repair attempt (ADR-0002) |
| Provider facade | Deterministic code | none directly | normalizes model/search calls into typed responses |
| API Gatekeeper | Deterministic code | usage/cost log entries via run context | enforces budgets, timeouts, retry classification; emits structured events |
| Deterministic rendering & file I/O | Deterministic code | run workspace; canonical roots only via promotion | escapes/renders LaTeX; atomic writes; write-audit events |
| LaTeX build service | Deterministic code | run workspace build dir | runs LuaLaTeX/biber subprocesses with fixed args, timeout, bounded attempts; captures build log |
| Python graph & asset rendering | Deterministic code | `<run_workspace>/latex_project/figures/` | renders Python-generated graphs and other typed assets |
| Deterministic `ValidatorService` | Deterministic code | report file under run workspace | reads workspace, evaluates checks, writes validation report; never an LLM |
| Offline fixtures | Deterministic code | read-only | supplies recorded responses for offline/dry-run/test modes |

### LLM authority vs deterministic authority

- **LLM-authored:** semantic content only — Markdown drafts, semantic
  document specs, citation placeholders, asset specs, BiDi narrative,
  review notes.
- **Deterministic authority (LLM never the source of truth):** file
  paths, file names, file writes, LaTeX escaping/rendering, subprocess
  invocations, page counting, citation resolution, deterministic
  validation, artifact promotion, run workspace lifecycle, prompt/config
  versioning, budget enforcement. This boundary is the subject of
  [ADR-0003](adrs/ADR-0003-deterministic-latex-rendering.md) and
  [ADR-0004](adrs/ADR-0004-provider-vs-gatekeeper.md).

---

## 3. Component view (C4 Level 3) — CrewAI orchestration and deterministic adjuncts

The component view zooms into the CrewAI container, the typed-contract
boundary, and the deterministic adjuncts.

```mermaid
flowchart TB
    subgraph Agents["Eight agents (PRD §8.3 / PRD_crewai_pipeline §5)"]
        A1["Research Agent<br/>prompt: PROMPT-AGENT-RESEARCH-001"]
        A2["Outline Agent<br/>prompt: PROMPT-AGENT-OUTLINE-001"]
        A3["Writer Agent<br/>prompt: PROMPT-AGENT-WRITER-001"]
        A4["Technical Asset Agent<br/>prompt: PROMPT-AGENT-ASSET-001"]
        A5["Hebrew/BiDi Agent<br/>prompt: PROMPT-AGENT-BIDI-001"]
        A6["LaTeX Agent<br/>prompt: PROMPT-AGENT-LATEX-001"]
        A7["Bibliography Agent<br/>prompt: PROMPT-AGENT-BIBLIOGRAPHY-001"]
        A8["Reviewer Agent<br/>prompt: PROMPT-AGENT-REVIEWER-001"]
    end

    subgraph Tasks["Tasks (PRD_crewai_pipeline §6)"]
        T1["T1 Research<br/>PROMPT-TASK-RESEARCH-001"]
        T2["T2 Outline<br/>PROMPT-TASK-OUTLINE-001"]
        T3["T3 Draft Markdown<br/>PROMPT-TASK-WRITE-001"]
        T4["T4 Technical assets<br/>PROMPT-TASK-ASSET-001"]
        T5["T5 BiDi section<br/>PROMPT-TASK-BIDI-001"]
        T6["T6 Bibliography<br/>PROMPT-TASK-BIBLIOGRAPHY-001"]
        T7["T7 LaTeX assembly<br/>PROMPT-TASK-LATEX-001"]
        T8["T8 Review<br/>PROMPT-TASK-REVIEW-001"]
    end

    subgraph TypedBoundary["Typed contract boundary (P5-I08)"]
        ParseT1["ResearchNotes v1"]
        ParseT2["Outline v1"]
        ParseT3["ChapterDrafts v1"]
        ParseT4["AssetSpecs v1"]
        ParseT5["BiDiSection v1"]
        ParseT6["BibliographyBundle v1"]
        ParseT7["LaTeXProjectSpec v1"]
        ParseT8["ReviewerSignal v1"]
    end

    subgraph Adjuncts["Deterministic adjuncts"]
        FileIO["Secure file I/O"]
        Renderer["Deterministic renderer"]
        Compiler["LaTeX compilation service"]
        AssetR["Graph/asset rendering"]
        Validator["ValidatorService"]
        Promotion["Explicit promotion"]
    end

    A1 --> T1 --> ParseT1 --> T2
    A2 --> T2 --> ParseT2 --> T3
    A3 --> T3 --> ParseT3 --> T4
    A4 --> T4 --> ParseT4 --> T5
    A5 --> T5 --> ParseT5 --> T6
    A7 --> T6 --> ParseT6 --> T7
    A6 --> T7 --> ParseT7 --> T8
    A8 --> T8 --> ParseT8 --> Validator

    ParseT4 --> AssetR
    AssetR --> FileIO
    ParseT7 --> Renderer
    Renderer --> FileIO
    FileIO --> Compiler
    Compiler --> Validator
    Validator --> Promotion
```

### Component responsibilities

| Component | Owns | Reads | Writes |
|---|---|---|---|
| Agent A1–A8 | LLM-authored semantic output | provider facade, prompt registry | none (output captured by tasks) |
| Task T1–T8 | execution of LLM step + repair invocation | prompt registry, run context, prior task outputs | raw LLM output (captured to run workspace under `raw/`) |
| Typed contract boundary | parse + validate every agent output | raw LLM output | parsed artifact (under `artifacts/`) and validation report entry |
| Secure file I/O | path guards, atomic writes, write audit | requested target path | files under run workspace only |
| Deterministic renderer | semantic doc spec → LaTeX | parsed `LaTeXProjectSpec` | LaTeX files under `<run_workspace>/latex_project/` |
| Asset rendering | typed graph/asset specs → image files | parsed `AssetSpecs` | files under `<run_workspace>/latex_project/figures/` |
| LaTeX compilation service | subprocess management | `<run_workspace>/latex_project/` | build outputs + build log under `<run_workspace>/build/` |
| `ValidatorService` | deterministic checks | run workspace contents | validation report under `<run_workspace>/validation/` |
| Explicit promotion | move from run workspace to canonical roots | manifest + validation report | `latex_project/` + `results/final.pdf` (only after explicit approval) |

---

## 4. Identifiers and versioning

- Every prompt ID (e.g., `PROMPT-AGENT-RESEARCH-001`) is governed by the
  registry in [`prompt_config_registry.md`](prompt_config_registry.md)
  and is the canonical link between the registry and `docs/PROMPTS.md`.
- Every artifact contract carries an explicit version tag (e.g.,
  `ResearchNotes v1`); changes that break a downstream parser require a
  new version, recorded in [`artifact_contracts.md`](artifact_contracts.md).
- ADR identifiers (`ADR-0001` …) are immutable; superseding decisions
  link to the prior ADR rather than mutating it.
