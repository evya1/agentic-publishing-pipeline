# PRD — Bibliography and Citations

> **Status:** scaffold-level placeholder. No bibliography entries exist yet.

## Problem

The HW3 PDF must contain a real bibliography with linked citations from the
body of the document. Fabricated sources are explicitly disallowed at every
stage of the pipeline.

## Real source collection

To be designed later. Open questions:

- How sources are discovered (manual reading list, search-tool calls).
- How sources are verified (URL still resolves, citation metadata accurate).
- How sources are stored before they enter `references.bib`.

## `.bib` management

- A single `latex_project/references.bib` is the source of truth for
  bibliography entries.
- Entries must use stable keys (e.g., `author-yearXX`) and include the
  minimum metadata required by the chosen bibliography style.
- No fabricated entries. Ever.

## Linked citation validation

- Every `\cite{...}` in the LaTeX sources must resolve to an entry in
  `references.bib`.
- Every entry in `references.bib` should ideally be cited at least once.
- The PDF validator (see `PRD_pdf_validation.md`) will enforce both.

## No fake citations

This is a non-negotiable constraint. The pipeline must:

- Refuse to insert a citation whose source has not been verified.
- Surface unresolved citations as build-time errors, not warnings.
- Keep an audit trail linking each citation to a real source artifact.

## Acceptance criteria

- [ ] Real source collection process documented.
- [ ] `references.bib` contains only verified entries.
- [ ] Every body citation links to a bibliography entry in the rendered PDF.
- [ ] Validation catches dangling citations and unused entries.
