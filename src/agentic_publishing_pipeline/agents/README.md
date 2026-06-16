# agents/

> **Status:** scaffold only — no CrewAI agents defined yet.

Future home of CrewAI agent definitions. Each agent will have an explicit
`role`, `goal`, `backstory`, and `tools`.

Planned agents:

- **Researcher** — gathers and summarizes real sources.
- **Outline** — turns research into the chapter plan.
- **Writer** — writes structured Markdown from approved research.
- **Technical Asset** — specifies figures, tables, equations, and graphs.
- **Hebrew/BiDi** — drafts and checks the Hebrew/English subsection.
- **Bibliography** — maps citations to verified source keys.
- **Reviewer** — checks clarity, consistency, and source coverage.
- **LaTeX Formatter** — converts approved Markdown into LaTeX project files.

Do not import `crewai` here until the implementation phase begins (see
`docs/PLAN.md`).
