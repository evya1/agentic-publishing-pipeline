# validation/

> **Status:** scaffold only — no validators implemented yet.

Future home of checks against the compiled PDF and other generated
artifacts. Coverage will include:

- PDF structure (cover sheet, TOC, headers/footers, page count).
- Citations and bibliography linkage.
- Hebrew/English BiDi rendering.
- Presence of the required graph, table, formula, and image.
- General PDF readability (text selectable, no broken layout).

See `docs/PRD_pdf_validation.md` for the full list of checks.
