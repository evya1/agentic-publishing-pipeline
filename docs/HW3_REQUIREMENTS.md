# HW3 Requirements Checklist

> Source: course assignment "HW3 — Article / Book Generation with CrewAI and
> LaTeX". This file paraphrases the requirements as a tracking checklist. If
> the official brief differs from this restatement, the brief wins — update
> this file rather than the brief.

> **Status:** scaffold only. None of the implementation items are done yet.

## Pipeline

- [ ] CrewAI pipeline planned per PRD §8.3: Researcher → Outline → Writer →
      Technical-Asset → Hebrew/BiDi → LaTeX → Bibliography → Reviewer;
      deterministic `ValidatorService` runs after the Reviewer Agent (PRD
      FR-40 / NFR-19).
- [x] Demo article topic selected and source manifest locked in Phase 1.5.
- [ ] Real source collection performed (no fabricated sources).
- [ ] Markdown-first draft workflow used before LaTeX conversion.
- [ ] LaTeX project present at `latex_project/`.
- [ ] Final PDF generated from the LaTeX project.

## Final PDF content

- [ ] Approximately 15 pages.
- [ ] Cover sheet with topic, author/team information, course, and date.
- [ ] Table of contents.
- [ ] Chapters / sections.
- [ ] Headers and footers.
- [ ] At least one image.
- [ ] At least one Python-generated graph.
- [ ] At least one table.
- [ ] At least one mathematical formula.
- [ ] At least one Hebrew-English BiDi section/chapter showing correct
      RTL/LTR handling.
- [ ] Bibliography at the end.
- [ ] Linked citations from the body to real bibliography entries.

## Documentation

- [ ] README documents architecture and the CrewAI flow.
- [ ] `docs/PRD.md`, `docs/PLAN.md`, `docs/TODO.md` present and current.
- [ ] HW3 mechanism PRDs present and current.
- [ ] AI usage documented in `docs/AI_USAGE.md`.
- [ ] Prompt log maintained in `docs/PROMPTS.md`.

## Submission

- [ ] Final Moodle wrapper PDF prepared from the official template.
- [ ] Group-code filename convention checked (`<GROUP_CODE>-ex03.pdf`).
- [ ] Each group member submits separately in Moodle.
