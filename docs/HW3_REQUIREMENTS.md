# HW3 Requirements Checklist

## Pipeline

- [x] CrewAI pipeline planned per PRD §8.3: Researcher → Outline → Writer →
      Technical-Asset → Hebrew/BiDi → LaTeX → Bibliography → Reviewer;
      deterministic `ValidatorService` runs after the Reviewer Agent (PRD
      FR-40 / NFR-19).
- [x] Demo article topic selected and source manifest locked in Phase 1.5.
- [x] Real source collection performed (no fabricated sources).
- [x] Markdown-first draft workflow used before LaTeX conversion.
- [x] LaTeX project present at `latex_project/`.
- [x] Final PDF generated from the LaTeX project.

## Final PDF content

- [x] Approximately 15 pages.
- [x] Cover sheet with topic, author/team information, course, and date.
- [x] Table of contents.
- [x] Chapters / sections.
- [x] Headers and footers.
- [x] At least one image.
- [x] At least one Python-generated graph.
- [x] At least one table.
- [x] At least one mathematical formula.
- [x] At least one Hebrew-English BiDi section/chapter showing correct
      RTL/LTR handling.
- [x] Bibliography at the end.
- [x] Linked citations from the body to real bibliography entries.

## Documentation

- [x] README documents architecture and the CrewAI flow.
- [x] `docs/PRD.md`, `docs/PLAN.md`, `docs/TODO.md` present and current.
- [x] HW3 mechanism PRDs present and current.
- [x] AI usage documented in `docs/AI_USAGE.md`.
- [x] Prompt log maintained in `docs/PROMPTS.md`.

## Submission

- [x] Final Moodle wrapper PDF prepared from the official template.
- [x] Group-code filename convention checked (`<GROUP_CODE>-ex03.pdf`).
- [x] Each group member submits separately in Moodle.
