# agents/

> **Status:** CrewAI agent factory implemented for Phase 6 recovery.

This package builds the eight PRD agents from the prompt registry. Each
agent has explicit `role`, `goal`, and `backstory` fields.

Phase 6 live manuscript generation uses the locked-context/tool-free
execution profile: no live agent receives CrewAI tools, no agent performs
source discovery, and all model calls still route through the provider
facade and `ApiGatekeeper`. The locked source manifest is injected into
task prompts, while deterministic Python services own persistence,
preflight, review packets, and promotion boundaries. This profile does
not satisfy the broader PRD tools contract for later phases; it is the
approved recovery profile for P6-I04/P6-I05.

Implemented agents:

- **Researcher** — gathers and summarizes real sources.
- **Outline** — turns research into the chapter plan.
- **Writer** — writes structured Markdown from approved research.
- **Technical Asset** — specifies figures, tables, equations, and graphs.
- **Hebrew/BiDi** — drafts and checks the Hebrew/English subsection.
- **Bibliography** — maps citations to verified source keys.
- **Reviewer** — checks clarity, consistency, and source coverage.
- **LaTeX Formatter** — converts approved Markdown into LaTeX project files.
