# TODO — agentic-publishing-pipeline

> Open work items for later implementation. **Nothing below is done.** Do not
> tick boxes during the scaffold stage.

## Topic and scope

- [ ] Choose article/book topic.
- [ ] Define research question and scope.
- [ ] Define real source policy (what counts, what is rejected).

## CrewAI design

- [ ] Design CrewAI Researcher / Writer / Reviewer / LaTeX Formatter /
      PDF Validator agents (role, goal, backstory, tools).
- [ ] Design tasks (description, expected_output, agent, context).
- [ ] Decide sequential vs hierarchical Process and document the rationale.

## Tools

- [ ] Implement safe tool interfaces through the gatekeeper:
  - [ ] Search tool.
  - [ ] File access tool.
  - [ ] Markdown conversion tool.
  - [ ] LaTeX compilation tool.
  - [ ] Graph generation tool.

## Content

- [ ] Implement Markdown draft generation.
- [ ] Implement Markdown-to-LaTeX conversion.
- [ ] Implement Python graph generation.
- [ ] Add real image / table / formula content.
- [ ] Add real citations and `.bib` entries.

## Build and validation

- [ ] Compile LaTeX to PDF.
- [ ] Validate links / citations / bibliography.
- [ ] Validate Hebrew/English BiDi handling.
- [ ] Validate required PDF elements (cover, TOC, headers/footers, image,
      graph, table, formula, BiDi section, bibliography, linked citations,
      ~15 pages).

## Documentation

- [ ] Update README with architecture, CrewAI flow, and run instructions.
- [ ] Fill `docs/AI_USAGE.md`.
- [ ] Fill `docs/PROMPTS.md` prompt log.

## Submission

- [ ] Prepare the Moodle wrapper PDF using the official template.
- [ ] Verify the group-code filename convention `<GROUP_CODE>-ex03.pdf`.
- [ ] Verify each group member submits individually.
