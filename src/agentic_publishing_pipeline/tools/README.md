# tools/

> **Status:** scaffold only — no tools implemented yet.

Future home of safe tool interfaces used by CrewAI agents:

- Search tool (real source discovery).
- File access tool (read/write under approved repo paths only).
- Markdown conversion tool (Markdown ↔ LaTeX bridges).
- LaTeX compilation tool.
- Graph generation tool (wraps `../visualization/`).

Each tool must route through a gatekeeper so destructive or out-of-scope
operations are impossible by construction. Do not add real API/LLM/search
SDKs until the corresponding phase in `docs/PLAN.md` begins.
