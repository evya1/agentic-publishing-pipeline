# PRD — CrewAI Pipeline

> **Status:** scaffold-level placeholder. No CrewAI code exists yet.

## Problem

Producing a high-quality, well-cited article/book requires distinct cognitive
tasks (research, drafting, review, formatting, validation) that can plausibly
be split across specialized agents coordinated by CrewAI. This PRD will
specify *how* once we commit to it.

## Future agents

To be designed later. Placeholders only:

1. **Researcher** — gathers and summarizes real sources.
2. **Writer** — produces structured Markdown from approved research.
3. **Reviewer** — checks clarity, consistency, and source coverage.
4. **LaTeX Formatter** — converts approved Markdown into the LaTeX project.
5. **PDF Validator** — checks generated PDF requirements.

Each agent will have explicit:

- `role`
- `goal`
- `backstory`
- `tools`

## Future tasks

To be designed later. Each task will declare:

- `description`
- `expected_output`
- `agent`
- `context` dependencies on earlier tasks

The planned task sequence:

```
Research -> Writing -> Review -> Markdown assembly
  -> LaTeX generation -> PDF validation
```

## Future Crew and Process

- Default `Process`: **sequential**.
- Any deviation (e.g., hierarchical) must be justified in a future revision
  of this PRD.

## Context passing

- Each task's `context` should list the earlier tasks it depends on so CrewAI
  can route outputs forward without bespoke glue code.

## Observability and logging

- Every agent invocation, tool call, and produced artifact must be logged.
- The log destination and schema will be designed when implementation begins.

## No-real-API scaffold policy

- During scaffold: no `crewai` import, no LLM SDK, no search SDK.
- Real dependencies will be added with `uv add` only when the corresponding
  phase in `docs/PLAN.md` begins.
- Secrets must never be hardcoded.

## Acceptance criteria

- [ ] Agent roles / goals / backstories / tools captured here and in
      `src/agentic_publishing_pipeline/agents/`.
- [ ] Tasks captured with description / expected_output / agent / context.
- [ ] Crew assembly captured with a documented Process choice.
- [ ] Observability / logging design captured.
- [ ] No real API/LLM/search call made until this PRD says so.
