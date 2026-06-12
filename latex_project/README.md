# latex_project/

> **Status:** scaffold only. `main.tex` is a placeholder template; no real
> content, citations, figures, tables, or formulas exist yet.

This is the LaTeX project that will eventually produce the HW3 PDF.

## Layout

```
main.tex          Top-level document (placeholder with TODOs).
references.bib    Bibliography source (empty — comments only).
chapters/         Per-chapter .tex files (placeholder).
figures/          Image and graph assets used by \includegraphics (placeholder).
tables/           Table .tex fragments or data (placeholder).
styles/           Custom style files / packages (placeholder).
```

## Compiler

- **Prefer LuaLaTeX** for Hebrew/English support if available.
- **XeLaTeX** is acceptable if explicitly chosen; document the reason in
  [`../docs/PRD_latex_generation.md`](../docs/PRD_latex_generation.md).
- Bibliography processing via **biber** (preferred) or **BibTeX**.

## Build (later)

Recommended steps once content exists (do **not** require these to pass
during the scaffold stage):

```sh
lualatex  -interaction=nonstopmode main.tex
biber     main
lualatex  -interaction=nonstopmode main.tex
lualatex  -interaction=nonstopmode main.tex
```

If LaTeX is not installed locally, treat that as a future environment
requirement rather than a scaffold failure.
