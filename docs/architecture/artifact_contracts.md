# Artifact contracts — agentic-publishing-pipeline

> **Status:** Phase 4 design amendment (P4-I04). Documentation-only.

This document specifies a **named, versioned input/output contract for
every task edge** in the CrewAI pipeline, plus the run-relative artifact
roots and per-artifact validation/repair behavior. It supplements
`docs/PRD_crewai_pipeline.md` §6 (task summary), §9 (artifacts), §11
(validation handoff). Implementation is scheduled for P5-I08 (typed
Pydantic models) and P5-I10 (run workspace).

The LLM is **never** the source of truth for any field listed here. All
parsing, validation, and downstream consumption use the deterministic
typed contract — see
[ADR-0002](adrs/ADR-0002-typed-artifact-contracts.md).

---

## 1. Edge-level contract table

Every meaningful task edge produces a named, versioned artifact. `path`
columns are **run-relative** (resolved under `results/<run_id>/`); they
become canonical only via explicit promotion (Sequence 8 in
[`runtime_sequences.md`](runtime_sequences.md)).

| Edge | Producer | Consumer(s) | Contract (name + version) | Run-relative path | Validation boundary | Repair behavior | Side effects | Failure behavior |
|---|---|---|---|---|---|---|---|---|
| E1 | Research Agent (T1) | Outline Agent (T2) | `ResearchNotes` v1 | `artifacts/research_notes.v1.json` + `raw/T1.md` | Pydantic schema; non-empty sections per reasoning dimension; candidate refs match configured manifest IDs | 1 bounded repair (ADR-0002) | atomic write to workspace `artifacts/` | halt with itemized errors after repair exhaustion |
| E2 | Outline Agent (T2) | Writer Agent (T3) | `Outline` v1 | `artifacts/outline.v1.json` + `raw/T2.md` | Pydantic schema; ≥1 chapter per required dimension; BiDi-host chapter flagged | 1 bounded repair | atomic write | halt |
| E3 | Writer Agent (T3) | Technical Asset (T4), BiDi (T5), Bibliography (T6), LaTeX (T7), Reviewer (T8) | `ChapterDrafts` v1 | `artifacts/chapter_drafts.v1.json` + `raw/T3/*.md` | Pydantic; placeholder syntax (`<!-- FIGURE/TABLE/EQUATION/CITATION -->`) parseable; chapter list covers Outline.v1 | 1 bounded repair | atomic write | halt |
| E4 | Technical Asset Agent (T4) | LaTeX Agent (T7), Validator | `AssetSpecs` v1 | `artifacts/asset_specs.v1.json` + `raw/T4/*` | Pydantic; each spec maps to exactly one placeholder in `ChapterDrafts` | 1 bounded repair | atomic write; asset rendering writes images to `latex_project/figures/` (workspace copy) | halt |
| E5 | Hebrew/BiDi Agent (T5) | Bibliography Agent (T6), LaTeX Agent (T7), Validator | `BiDiSection` v1 | `artifacts/bidi.v1.json` + `raw/T5.md` | Pydantic; minimum Hebrew/English token counts; placeholders parseable | 1 bounded repair | atomic write | halt |
| E6 | Bibliography Agent (T6) | LaTeX Agent (T7), Validator | `BibliographyBundle` v1 | `artifacts/bibliography.v1.json` + `latex_project/references.bib` (workspace copy) | Pydantic; every cited key resolves; canonical-mode citations cover all 10 manifest entries (`docs/PRD.md` §22.9) | 1 bounded repair | atomic write; bibliography agent never invents sources (`docs/PRD_bibliography_and_citations.md`) | halt |
| E7 | LaTeX Agent (T7) | Renderer, Compiler, Validator | `LaTeXProjectSpec` v1 | `artifacts/latex_project_spec.v1.json` | Pydantic; semantic-only (no raw LaTeX strings); FR-17a–d separation declared per item | 1 bounded repair | the **renderer** (deterministic) — not the LLM — writes `.tex` files under `latex_project/` | halt |
| E8 | Reviewer Agent (T8) | Validator | `ReviewerSignal` v1 | `artifacts/reviewer_signal.v1.json` + `raw/T8.md` | Pydantic; pass/flag enum; itemized review notes preserved | 1 bounded repair | atomic write | **Reviewer is advisory only — its signal does not gate canonical writes; Validator does** (FR-40, NFR-19) |
| E9 | Renderer | Compiler | rendered `latex_project/` tree | `latex_project/**` (under workspace) | path-safety + atomic write check by secure file I/O | n/a (deterministic) | atomic writes | halt and preserve workspace |
| E10 | Compiler | Validator | `BuildResult` v1 | `build/build.v1.json` + `build/main.pdf` + `build/build.log` | exit code = 0; parsed-log heuristics clean | n/a | LuaLaTeX/biber subprocesses with fixed args, timeout, bounded attempts | halt with build-log pointer (Sequence 6) |
| E11 | Validator | Promotion + Operator | `ValidationReport` v1 | `validation/report.v1.json` + human-readable `validation/report.md` | deterministic checks per `docs/PRD_pdf_validation.md` | n/a | writes report under workspace only | halt promotion on FAIL (Sequence 7) |
| E12 | Promotion | canonical roots | `PromotionRecord` v1 | `artifacts/promotion.v1.json` (record); `latex_project/` and `results/final.pdf` (canonical roots) | Validator PASS + manifest integrity + hash recompute | n/a | only writer of canonical roots; refuses if canonical already exists unless `--force` is passed and recorded (ADR-0005) | halt and emit reason |

---

## 2. Per-artifact required fields (Pydantic v1)

The full Pydantic schemas live in code under P5-I08
(`src/agentic_publishing_pipeline/contracts/` is the planned location).
This table is the design specification; field-level defaults and
validators belong with the implementation.

### `ResearchNotes` v1

- `topic: str`
- `dimensions: list[ResearchDimensionNote]` — one per reasoning dimension
  (planning, memory, retrieval, tool use, multimodal).
- `candidate_references: list[CandidateReference]` — each carries an
  `arxiv_id` or `doi` and **must** match a configured manifest entry
  (`docs/PRD.md` §22.4) in canonical mode.
- `glossary: list[GlossaryTerm]` — key terminology definitions.
- `run_id: str`, `contract_version: Literal["v1"]`, `produced_at: datetime`.

### `Outline` v1

- `chapters: list[ChapterOutline]` — title, summary, planned placement
  for figures/tables/equations/citations, optional `is_bidi_host: bool`.
- `target_total_pages: int` (informational; deterministic budget is in
  ValidatorService via P10-I03).
- standard envelope (`run_id`, `contract_version`, `produced_at`).

### `ChapterDrafts` v1

- `chapters: list[ChapterDraft]` — heading hierarchy, Markdown body,
  parsed list of placeholders.
- `placeholder_index: list[Placeholder]` — `kind ∈ {FIGURE, TABLE,
  EQUATION, CITATION}`, `slot: str`, `chapter_id: str`.
- envelope.

### `AssetSpecs` v1

- `assets: list[AssetSpec]` — `kind ∈ {tikz, image, table, equation,
  python_graph}`, semantic content (data, axes, captions, labels), the
  matching `placeholder.slot`, and explicit `theorem_like_kind?` for
  theorem/lemma/definition/example.
- envelope.

### `BiDiSection` v1

- `chapter_id: str` (must be the outline's BiDi host),
- `hebrew_body: str` (≥ configured token minimum),
- `inline_english_terms: list[str]`,
- `placeholders: list[Placeholder]`.
- envelope.

### `BibliographyBundle` v1

- `entries: list[BibEntry]` — citation key, type, authors, year, URL/DOI,
  `verified_at`, `verified_by` (`docs/PRD_bibliography_and_citations.md`).
- `placeholder_resolution: dict[str, str]` — placeholder slot → citation
  key (every placeholder in `ChapterDrafts` + `BiDiSection` resolved).
- `manifest_coverage: list[str]` — citation keys covering each of the 10
  canonical manifest sources (canonical mode only; `docs/PRD.md` §22.9).
- envelope.

### `LaTeXProjectSpec` v1

Semantic-only. **No raw LaTeX strings.** The renderer translates
semantic items into `.tex` files; the agent never writes a file path.

- `main: MainDoc` — list of `\input{}` includes only;
- `preamble: PreambleSpec` — engine `lualatex`, font config, packages,
  language config;
- `macros: list[MacroSpec]`;
- `chapters: list[ChapterSpec]` — references to `ChapterDrafts` chapters,
  resolved citation keys, asset slots;
- `tables: list[TableRef]` — each `\input{tables/<file>.tex}`;
- `figures: list[FigureRef]` — each `\input{figures/<file>.tex}` or
  `\includegraphics{...}` per FR-17d;
- `references_bib_path: str` (workspace-relative);
- `nomenclature: NomenclatureSpec` — ≥ 2 symbols;
- `index_entries: IndexSpec` — ≥ 1 Hebrew + ≥ 1 English term;
- envelope.

### `ReviewerSignal` v1

- `signal: Literal["pass", "flag"]` (advisory only),
- `notes: list[ReviewNote]` — keyed by chapter/asset id,
- envelope.

### `BuildResult` v1

- `engine: Literal["lualatex"]`,
- `passes: list[BuildPass]` — command, exit code, duration, log slice,
- `pdf_path: str` (workspace-relative),
- `parsed_warnings: list[str]`, `parsed_errors: list[str]`,
- envelope.

### `ValidationReport` v1

- `result: Literal["pass", "fail"]`,
- `checks: list[CheckOutcome]` — name, status, evidence pointer,
- `page_report: PageReport` — total + substantive pages (P10-I03),
- `citation_resolution: list[CitationCheck]`,
- envelope.

### `PromotionRecord` v1

- `source_workspace: str`,
- `canonical_paths_written: list[str]`,
- `content_hashes: dict[str, str]` — path → SHA-256,
- `validation_report_ref: str`,
- envelope.

---

## 3. Run-relative artifact roots

All workspace writes are confined to `results/<run_id>/`. Promotion is
the only path that crosses into canonical roots
(`latex_project/`, `results/final.pdf`, etc.).

```
results/<run_id>/
├── config_snapshot.json            # full effective configuration at run start
├── events.jsonl                    # structured run events (NFR-16)
├── usage.jsonl                     # provider usage/cost events (Gatekeeper)
├── artifacts/                      # versioned typed artifacts (this document)
│   ├── research_notes.v1.json
│   ├── outline.v1.json
│   ├── chapter_drafts.v1.json
│   ├── asset_specs.v1.json
│   ├── bidi.v1.json
│   ├── bibliography.v1.json
│   ├── latex_project_spec.v1.json
│   ├── reviewer_signal.v1.json
│   └── promotion.v1.json
├── raw/                            # raw LLM outputs for forensic inspection
│   └── T<n>.{md,json,…}
├── latex_project/                  # rendered LaTeX project (workspace copy)
│   ├── main.tex
│   ├── preamble.tex
│   ├── macros.tex
│   ├── references.bib
│   ├── chapters/*.tex
│   ├── tables/*.tex
│   └── figures/*
├── build/                          # compiler output
│   ├── main.pdf
│   ├── build.log
│   └── build.v1.json
├── validation/
│   ├── report.v1.json
│   └── report.md
└── manifest.v1.json                # the artifact manifest (next section)
```

Note: `results/generated_markdown/` (FR-12, PRD §12.3) is the
**canonical** Markdown path. During a run, Markdown drafts live under
`results/<run_id>/raw/` and `results/<run_id>/artifacts/`; promotion
copies the approved Markdown to `results/generated_markdown/` (canonical
location). This preserves FR-12 / §12.3 while keeping per-run artifacts
isolated.

---

## 4. Artifact manifest

The artifact manifest is a single JSON file recording every artifact a
run produced, its contract version, its content hash, and its
producer/consumer linkage.

```json
{
  "manifest_version": "v1",
  "run_id": "<ULID>",
  "started_at": "<ISO-8601>",
  "completed_at": "<ISO-8601 | null>",
  "mode": "offline-fixture | live | dry-run | compile-only | validate-only | resume",
  "config_snapshot_path": "results/<run_id>/config_snapshot.json",
  "registry_version": "<prompt_config_registry version>",
  "artifacts": [
    {
      "id": "research_notes",
      "contract": "ResearchNotes",
      "contract_version": "v1",
      "path": "results/<run_id>/artifacts/research_notes.v1.json",
      "sha256": "<hash>",
      "produced_by_task": "T1",
      "consumed_by_tasks": ["T2", "T3", "T6"]
    }
  ],
  "build_result_ref": "results/<run_id>/build/build.v1.json",
  "validation_report_ref": "results/<run_id>/validation/report.v1.json",
  "promotion_ref": "results/<run_id>/artifacts/promotion.v1.json | null"
}
```

The manifest is the single source of truth for "what did this run
produce". It is required for promotion, resumption, and the sanitized
evidence bundle (P13-I05).

---

## 5. Failure-handling rules (cross-cutting)

These rules apply to every artifact above:

1. **No silent fallback.** If a contract parse fails after the single
   allowed repair attempt, the pipeline halts. Downstream consumers
   never receive unvalidated data.
2. **Workspace preserved.** Failed runs keep their workspace for
   inspection. Explicit cleanup is a separate command, not an automatic
   side effect of failure.
3. **No canonical write on failure.** Canonical roots are only ever
   written by the explicit promotion path (E12).
4. **No LLM authority for validation.** The Reviewer Agent (E8) is
   advisory; the deterministic Validator (E11) decides promotion
   readiness (FR-40, NFR-19).
5. **Versioning.** Any change that breaks an existing parser requires a
   new contract version (e.g., `Outline v2`); both versions are
   supported during a deprecation window recorded in the registry.
6. **Hashing.** Every artifact path in the manifest carries a SHA-256
   hash computed by the deterministic writer at the moment the file
   becomes immutable.
