# agents/

> **Status:** scaffold only — no CrewAI agents defined yet.

Future home of CrewAI agent definitions. Each agent will have an explicit
`role`, `goal`, `backstory`, and `tools`.

Planned agents:

- **Researcher** — gathers and summarizes real sources.
- **Writer** — writes structured Markdown from approved research.
- **Reviewer** — checks clarity, consistency, and source coverage.
- **LaTeX Formatter** — converts approved Markdown into LaTeX project files.
- **PDF Validator** — checks generated PDF requirements.

Do not import `crewai` here until the implementation phase begins (see
`docs/PLAN.md`).
