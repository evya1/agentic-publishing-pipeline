# PLAN — agentic-publishing-pipeline

> **Status:** scaffold-stage only the early phases are done. All HW3
> implementation phases remain open.

## Phases

### Phase 1 — Scaffold setup *(in progress)*

- [x] Initialize repository structure.
- [x] Add `pyproject.toml` (uv-managed, no CrewAI / LLM / search SDKs yet).
- [x] Add `.gitignore` covering Python + LaTeX build artifacts.
- [x] Add base documentation (PRD, PLAN, TODO, AI_USAGE, PROMPTS,
      SUBMISSION_CHECKLIST).
- [x] Add HW3 documentation (HW3_REQUIREMENTS + four mechanism PRDs).
- [x] Add placeholder package tree under
      `src/agentic_publishing_pipeline/`.
- [x] Add placeholder artifact directories (`content/`, `latex_project/`,
      `assets/`, `results/`, `submission/`).
- [x] Add smoke test.

### Phase 2 — HW3 requirement ingestion

- [ ] Re-read course brief and confirm `docs/HW3_REQUIREMENTS.md` matches the
      official assignment text.
- [ ] Capture any deltas in the PRDs.

### Phase 3 — Topic selection

- [ ] Group agrees on a topic and scope.
- [ ] Document the topic, audience, and depth target.

### Phase 4 — CrewAI architecture design

- [ ] Finalize the Researcher / Writer / Reviewer / LaTeX Formatter /
      PDF Validator agent roles, goals, and backstories on paper.
- [ ] Decide sequential vs hierarchical `Process`. Default sequential.
- [ ] Capture the design in `PRD_crewai_pipeline.md`.

### Phase 5 — Agent / task prompt design

- [ ] Draft initial prompts for each agent and task.
- [ ] Store prompts in `docs/PROMPTS.md` as they evolve.

### Phase 6 — Markdown-first content pipeline

- [ ] Implement Markdown draft generation under `content/markdown_drafts/`.
- [ ] Human review gate before any LaTeX conversion.

### Phase 7 — Real source and bibliography pipeline

- [ ] Source-collection policy, capture, and verification.
- [ ] `.bib` management and linkage from the Markdown / LaTeX bodies.

### Phase 8 — Python graph generation pipeline

- [ ] `visualization/` produces at least one figure consumed by LaTeX.

### Phase 9 — LaTeX generation pipeline

- [ ] Markdown -> LaTeX conversion.
- [ ] `latex_project/main.tex` assembled with real chapters, figures, tables,
      formulas, and at least one Hebrew/English BiDi section.

### Phase 10 — PDF validation pipeline

- [ ] Automated checks per `PRD_pdf_validation.md`.

### Phase 11 — README and documentation update

- [ ] Fill in run instructions, costs, and architecture diagrams reflecting the
      real implementation.
- [ ] Update `docs/AI_USAGE.md` and `docs/PROMPTS.md`.

### Phase 12 — Final submission packaging

- [ ] Prepare the Moodle wrapper PDF from the official template.
- [ ] Verify filename convention `<GROUP_CODE>-ex03.pdf`.
- [ ] Confirm each group member submits separately in Moodle.

## Notes

- Phases 2 through 12 are all gated on phase 1 being complete and the topic
  being chosen. Do **not** mark any of them done preemptively.
- Real dependencies (e.g., `crewai`, model SDKs, search SDKs) will be added
  with `uv add` only when the phase that needs them begins.
