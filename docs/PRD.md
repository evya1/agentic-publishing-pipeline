# PRD — agentic-publishing-pipeline

> **Status:** scaffold only.

## Problem

Producing a polished, well-cited LaTeX article/book by hand is time-consuming.
This project will explore whether an orchestrated team of CrewAI agents can
materially accelerate the research, drafting, review, and formatting steps
while keeping the final artifact accurate, auditable, and free of fabricated
sources.

## Users

- Course instructor and graders evaluating HW3.
- The group members operating the pipeline.

## Scope (HW3)

In scope (later, not during scaffold):

- A CrewAI pipeline producing a ~15-page LaTeX PDF on a chosen topic.
- A real bibliography backed by real sources.
- Hebrew/English BiDi handling demonstrated in the PDF.
- At least one image, one Python-generated graph, one table, and one math
  formula.
- README, PRDs, PLAN, TODO, AI usage log, and prompt log fully populated.

Out of scope:

- Multi-topic batch generation.
- Production deployment.
- Real-time collaborative editing.

## Non-goals

- Calling real LLMs during the scaffold stage.
- Generating any article content during the scaffold stage.
- Inventing sources, citations, figures, tables, or formulas at any stage.

## Constraints

- No real API/LLM/search calls until the dedicated PRDs say otherwise.
- All AI usage and prompts must be logged in `docs/AI_USAGE.md` and
  `docs/PROMPTS.md`.
- Dependency management uses `uv` only.

## Mechanism PRDs

The pipeline is decomposed into four mechanism PRDs:

1. [`PRD_crewai_pipeline.md`](PRD_crewai_pipeline.md)
2. [`PRD_latex_generation.md`](PRD_latex_generation.md)
3. [`PRD_bibliography_and_citations.md`](PRD_bibliography_and_citations.md)
4. [`PRD_pdf_validation.md`](PRD_pdf_validation.md)

## Acceptance criteria (high-level, scaffold-stage)

- [ ] Repository scaffold present.
- [ ] All planning documents present.
- [ ] No fabricated content or sources anywhere in the repo.
- [ ] No premature claims of CrewAI / LaTeX / PDF completeness.

Final HW3 acceptance criteria live in
[`HW3_REQUIREMENTS.md`](HW3_REQUIREMENTS.md) and the four mechanism PRDs.
