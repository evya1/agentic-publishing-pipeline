# Architecture documents — agentic-publishing-pipeline

> **Status:** Phase 4 design amendment (P4-I04). Documentation-only.
> No runtime code. These documents extend the agent/task design captured
> in `docs/PRD_crewai_pipeline.md` with the runtime boundaries required
> before Phase 5 implementation may begin.

These documents are the canonical home for the C4 views, runtime sequence
diagrams, named/versioned artifact contracts, prompt/config identifiers,
allowed tools and side effects, run-relative artifact roots, validation
and bounded-repair policy, deterministic rendering/file-authority
boundary, and Architecture Decision Records (ADRs) that supplement
`docs/PRD.md`, `docs/PRD_crewai_pipeline.md`, `docs/PRD_latex_generation.md`,
`docs/PRD_pdf_validation.md`, and `docs/PRD_bibliography_and_citations.md`.

## Index

| Document | Purpose |
|---|---|
| [`c4_views.md`](c4_views.md) | C4 system-context, container, and component views. |
| [`runtime_sequences.md`](runtime_sequences.md) | Happy-path and failure/repair sequence diagrams (offline-fixture, live, invalid-output + one bounded repair, repair-exhaustion, provider/budget rejection, LaTeX compilation failure, deterministic validation failure, explicit artifact promotion). |
| [`artifact_contracts.md`](artifact_contracts.md) | Named, versioned input/output contract for every agent/task edge. Producer, consumer, required fields, validation boundary, repair behavior, run-relative storage path, side effects, and failure behavior per artifact. |
| [`run_lifecycle.md`](run_lifecycle.md) | Run ID, isolated workspace, configuration snapshot, event log, usage/cost log, artifact manifest, operational modes (dry-run, offline-fixture, live, compile-only, validate-only, topic/manifest override, resumability), and explicit promotion. |
| [`prompt_config_registry.md`](prompt_config_registry.md) | Design for the machine-readable, versioned runtime prompt/config registry and its compatibility checks. Distinguishes the registry from `docs/PROMPTS.md` (human-readable evidence ledger). |
| [`adrs/`](adrs/) | Architecture Decision Records (ADR-0001 through ADR-0007). |

## Status of the implementation

None of the runtime mechanisms designed in these documents is implemented
yet. Implementation is scheduled per `docs/PLAN.md` Phase 5 onward and is
tracked in `docs/TODO.md` under the planned internal IDs P5-I08, P5-I09,
P5-I10, P5-I11, P5-I12, P5-I13, P8-I01, P10-I03, P12-I05, P12-I06, and
P13-I05. GitHub issue numbers for those items will be allocated only when
the runtime work begins.

## Cross-references

- `docs/PRD.md` §8 (Functional Requirements), §9 (Non-Functional
  Requirements), §14 (Acceptance Criteria), §22 (Canonical Demo Article
  Topic).
- `docs/PRD_crewai_pipeline.md` §5 (Agents), §6 (Tasks), §7 (Crew
  assembly), §8 (Provider and service layer), §9 (Artifacts), §11
  (Reviewer Agent and validation handoff).
- `docs/PRD_latex_generation.md` for the deterministic LaTeX rendering
  boundary that ADR-0003 governs.
- `docs/PRD_pdf_validation.md` for the deterministic `ValidatorService`
  that runs after the Reviewer Agent (FR-40, NFR-19).
- `docs/PRD_bibliography_and_citations.md` for the no-fabricated-sources
  policy and verification workflow consumed by the Bibliography Agent.
- `docs/PROMPTS.md` for the human-readable verbatim prompt ledger
  (distinct from the runtime registry in `prompt_config_registry.md`).
- `docs/PLAN.md` for the phased roadmap (Phase 4 designs; Phase 5 onward
  implements).
- `docs/TODO.md` for the concrete backlog with traceability tags.

## Diagram conventions

Sequence diagrams use Mermaid `sequenceDiagram` syntax for inline
GitHub/Markdown rendering. C4 views use Mermaid `flowchart` syntax with
explicit subgraphs for system, container, and component boundaries.
