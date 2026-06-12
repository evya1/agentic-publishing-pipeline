# PRD — LaTeX Generation

> **Status:** scaffold-level placeholder. No real LaTeX content exists.

## Problem

The final HW3 deliverable is a polished LaTeX PDF. This PRD will describe how
approved Markdown content becomes that PDF.

## Markdown-to-LaTeX conversion

To be designed later. Open questions:

- Which converter to use (`pandoc`, custom code, CrewAI-generated)?
- How to preserve citation keys across the conversion.
- How to insert Python-generated figures.
- How to handle Hebrew/English BiDi blocks safely.

## LaTeX project layout

Already scaffolded:

```
latex_project/
  main.tex
  references.bib
  chapters/
  figures/
  tables/
  styles/
```

Final structure may evolve as the document grows.

## Compiler choice

- **Prefer LuaLaTeX** for Hebrew/English support if available.
- **XeLaTeX** is acceptable if explicitly chosen — the choice must be
  documented here, including the reason.
- Bibliography processing via **biber** (preferred) or **BibTeX**.
- Do not assume a TeX distribution is installed locally; document the
  required setup in the README when implementation begins.

## Hebrew/English BiDi support

To be designed later. Likely involves `babel` with `hebrew` and `english`
languages, or `polyglossia` under LuaLaTeX/XeLaTeX. At least one section or
chapter of the final PDF must demonstrate correct RTL/LTR rendering.

## Image / table / formula handling

- Images: stored under `latex_project/figures/` (with sources under
  `assets/` when raw inputs differ from the included artifact).
- Tables: real data only — fabrications are disallowed.
- Formulas: standard `amsmath` environments; at least one mathematical
  formula must appear in the final PDF.

## Build artifacts

- Generated PDF lands under `results/` (path to be confirmed during
  implementation).
- Intermediate LaTeX artifacts (`*.aux`, `*.bbl`, etc.) are gitignored.

## Acceptance criteria

- [ ] Conversion path Markdown → LaTeX documented and implemented.
- [ ] Project compiles cleanly with the chosen compiler.
- [ ] Hebrew/English BiDi section renders correctly.
- [ ] All required PDF elements (image, graph, table, formula) are present
      and reference real assets.
