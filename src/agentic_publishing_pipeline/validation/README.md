# validation/

> **Status:** scaffold only — no validators implemented yet.

Future home of deterministic Python checks against the compiled PDF and other
generated artifacts. This package is not a CrewAI agent; it runs after agent
work and build steps as a source-of-truth validator. Coverage will include:

- PDF structure (cover sheet, TOC, headers/footers, page count).
- Citations and bibliography linkage.
- Hebrew/English BiDi rendering.
- Presence of the required graph, table, formula, and image.
- General PDF readability (text selectable, no broken layout).

See `docs/PRD_pdf_validation.md` for the full list of checks.
