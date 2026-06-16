# Submission checklist

> **Status (2026-06-17):** Phases 10–12 complete. Final PDF produced (21 pages).
> ValidatorService passes all 35 checks. Moodle submission pending (Phase 14).

## Repository

- [x] GitHub repository is public or shared with the instructor.
- [x] Root `README.md` exists and describes the project status accurately.
      *(verified 2026-06-17 — status, installation, build, and run sections present)*
- [x] `docs/PRD.md`, `docs/PLAN.md`, and `docs/TODO.md` exist.
      *(verified 2026-06-17 — ValidatorService file check PASS)*
- [x] HW3-specific PRDs exist:
  - [x] `docs/PRD_crewai_pipeline.md`
  - [x] `docs/PRD_latex_generation.md`
  - [x] `docs/PRD_bibliography_and_citations.md`
  - [x] `docs/PRD_pdf_validation.md`
- [x] LaTeX project folder (`latex_project/`) exists.
      *(verified 2026-06-17 — all chapter, table, figure, and root files present)*

## Final PDF (HW3 deliverable)

- [x] Final PDF exists.
      *(`results/final.pdf` — 218,186 bytes, verified 2026-06-17 by pdfinfo)*
- [x] PDF was generated from the included LaTeX project.
      *(`scripts/build_pdf.py` runs multi-pass LuaLaTeX from `latex_project/`)*
- [x] PDF includes a cover sheet (topic, author/team, course, date).
      *(title page: "Agentic Reasoning for Large Language Models: A Survey", \\today)*
- [x] PDF includes a table of contents.
      *(LaTeX \\tableofcontents present in `main.tex`)*
- [x] PDF includes headers / footers.
      *(fancyhdr configured in `preamble.tex`: page numbers, chapter marks, footer title)*
- [x] PDF includes chapters / sections.
      *(8 chapters: introduction, planning, memory, retrieval, tool_use, multimodal,
       evaluation, conclusion)*
- [x] PDF includes at least one image.
      *(`planning_benchmark_comparison_02e65860.png` — Phase 8 Python-generated PNG)*
- [x] PDF includes at least one Python-generated graph.
      *(same PNG; generated deterministically by visualization pipeline, Phase 8)*
- [x] PDF includes at least one table.
      *(`tables/planning_methods.tex` — standalone booktabs planning-methods table)*
- [x] PDF includes at least one mathematical formula.
      *(`eq:planning-objective` — policy optimisation objective in Chapter 2)*
- [x] PDF includes at least one Hebrew-English BiDi section.
      *(sections in Chapters 1 and 3; David CLM font via polyglossia + LuaLaTeX)*
- [x] PDF includes linked citations.
      *(\\eqref and \\ref cross-references; hyperref with colorlinks in preamble)*
- [x] PDF includes a bibliography backed by real sources.
      *(10 verified ArXiv entries in `references.bib`, Phase 7; rendered by biber)*

## Documentation

- [x] README explains the architecture and the CrewAI flow.
      *(8-agent flow, installation, build commands, run commands — updated 2026-06-17)*
- [x] AI usage is documented in `docs/AI_USAGE.md`.
      *(Phases 1–12 entries; model IDs, purpose, outputs, verification, cost)*
- [x] Prompt log is documented in `docs/PROMPTS.md`.
      *(verbatim prompts for all 8 agents and 8 tasks; version 1.0 / 2026-06-13)*
- [x] Costs / resources are documented if real model / API calls are used.
      *(all phases: $0.00; no external-provider tokens; deterministic pipelines only)*

## Moodle submission

- [ ] Moodle filename follows `<GROUP_CODE>-ex03.pdf` and file is ready.
- [ ] Each group member submits separately in Moodle.
