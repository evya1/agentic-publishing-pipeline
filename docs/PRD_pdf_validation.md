# PRD — PDF Validation

> **Status:** scaffold-level placeholder. No validator exists yet.

## Problem

The HW3 deliverable must satisfy a precise list of structural requirements.
A validator will keep us honest as the document grows so we cannot ship a PDF
that quietly drops one of them.

## Checks to implement

### Page count

- [ ] Final PDF page count is approximately 15 pages (target range defined
      later — likely 14–16).

### Cover / TOC / headers / footers

- [ ] Cover sheet present with topic, author/team, course, and date.
- [ ] Table of contents present.
- [ ] Page headers present on body pages.
- [ ] Page footers present on body pages.

### Graphs / tables / formulas / images

- [ ] At least one image embedded.
- [ ] At least one Python-generated graph embedded.
- [ ] At least one table rendered.
- [ ] At least one mathematical formula rendered.

### BiDi

- [ ] At least one Hebrew-English BiDi section/chapter, with correct RTL/LTR
      handling.

### Citations / bibliography

- [ ] Every `\cite{...}` resolves to a `references.bib` entry.
- [ ] Bibliography is rendered at the end of the document.
- [ ] Citations are clickable links in the PDF.

### PDF readability

- [ ] PDF opens cleanly in a standard reader.
- [ ] Text is selectable (not rendered as image only).
- [ ] No obviously broken layout (overflowing boxes, missing figures).

## Acceptance criteria

- [ ] All checks above implemented as automated validators (or
      manual-with-checklist where automation is infeasible).
- [ ] Validator output is human-readable and surfaces specific failures.
- [ ] CI / local script wired up so the validator is easy to re-run after
      each rebuild.
