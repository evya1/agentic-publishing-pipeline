# Submission checklist

> **Status :** Phases 10–12 complete. Final PDF produced (21 pages).
> ValidatorService passes all 35 checks. Moodle submission pending (Phase 14).

## Repository

- [x] GitHub repository is public or shared with the instructor.
- [x] Root `README.md` exists and describes the project status accurately.
      _(verified status, installation, build, and run sections present)_
- [x] `docs/PRD.md`, `docs/PLAN.md`, and `docs/TODO.md` exist.
      _(verified ValidatorService file check PASS)_
- [x] HW3-specific PRDs exist:
    - [x] `docs/PRD_crewai_pipeline.md`
    - [x] `docs/PRD_latex_generation.md`
    - [x] `docs/PRD_bibliography_and_citations.md`
    - [x] `docs/PRD_pdf_validation.md`
- [x] LaTeX project folder (`latex_project/`) exists.
      _(verified all chapter, table, figure, and root files present)_

## Final PDF (HW3 deliverable)

- [x] Final PDF exists.
      _(`results/final.pdf` — 218,186 bytes, verified by pdfinfo)_
- [x] PDF was generated from the included LaTeX project.
      _(`scripts/build_pdf.py` runs multi-pass LuaLaTeX from `latex_project/`)_
- [x] PDF includes a cover sheet (topic, author/team, course, date).
      _(title page: "Agentic Reasoning for Large Language Models: A Survey", \\today)_
- [x] PDF includes a table of contents.
      _(LaTeX \\tableofcontents present in `main.tex`)_
- [x] PDF includes headers / footers.
      _(fancyhdr configured in `preamble.tex`: page numbers, chapter marks, footer title)_
- [x] PDF includes chapters / sections.
      _(8 chapters: introduction, planning, memory, retrieval, tool_use, multimodal,
      evaluation, conclusion)_
- [x] PDF includes at least one image.
      _(`planning_benchmark_comparison_02e65860.png` — Phase 8 Python-generated PNG)_
- [x] PDF includes at least one Python-generated graph.
      _(same PNG; generated deterministically by visualization pipeline, Phase 8)_
- [x] PDF includes at least one table.
      _(`tables/planning_methods.tex` — standalone booktabs planning-methods table)_
- [x] PDF includes at least one mathematical formula.
      _(`eq:planning-objective` — policy optimisation objective in Chapter 2)_
- [x] PDF includes at least one Hebrew-English BiDi section.
      _(sections in Chapters 1 and 3; David CLM font via polyglossia + LuaLaTeX)_
- [x] PDF includes linked citations.
      _(\\eqref and \\ref cross-references; hyperref with colorlinks in preamble)_
- [x] PDF includes a bibliography backed by real sources.
      _(10 verified ArXiv entries in `references.bib`, Phase 7; rendered by biber)_

## Documentation

- [x] README explains the architecture and the CrewAI flow.
      _(8-agent flow, installation, build commands, run commands — updated )_
- [x] AI usage is documented in `docs/AI_USAGE.md`.
      _(Phases 1–14 entries; model IDs, purpose, outputs, verification, cost)_
- [x] Prompt log is documented in `docs/PROMPTS.md`.
      _(verbatim prompts for all 8 agents and 8 tasks; version 1.0)_
- [x] Costs / resources are documented if real model / API calls are used.
      _(all phases: $0.00; no external-provider tokens; deterministic pipelines only)_
