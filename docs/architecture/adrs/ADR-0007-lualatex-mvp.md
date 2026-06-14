# ADR-0007 — LuaLaTeX as the MVP engine

- **Status:** Accepted (Phase 4 design amendment — P4-I04).
- **Date:** 2026-06-14.

## Context

The article must support Hebrew/English BiDi text, Unicode fonts,
mathematical notation, TikZ figures, theorem-like environments,
nomenclature, and an index. The PRD locks `fontspec` + `polyglossia`,
the `David CLM` Hebrew font, and `Latin Modern Roman` as the English
font (`docs/PRD.md` §16.3).

Two engines can plausibly handle these requirements: LuaLaTeX and
XeLaTeX. The PRD already states (FR-20, §16.3): "**LuaLaTeX is the
default and required MVP engine**; XeLaTeX may be supported later as
an optional fallback."

This ADR records the rationale and pins the engine for the
deterministic compiler subprocess in [ADR-0003](ADR-0003-deterministic-latex-rendering.md).

## Decision

1. The MVP uses **LuaLaTeX exclusively**. Build scripts, README
   commands, validation checks, generated templates, and the
   deterministic compiler (P5-I06) target LuaLaTeX.
2. The multi-pass build sequence is **LuaLaTeX → biber → LuaLaTeX →
   LuaLaTeX** plus `makeindex` / `makenomenclature` as required.
3. XeLaTeX is **not** added as a parallel path in the MVP. Any future
   XeLaTeX fallback must be introduced via a new ADR and must not
   conflict with the default LuaLaTeX path.
4. The renderer (ADR-0003) emits LuaLaTeX-compatible LaTeX. Font
   commands and language commands target `fontspec` + `polyglossia`.

## Consequences

- Reproducibility documentation (`README.md`) must require LuaLaTeX and
  the `David CLM` font on the operator's machine.
- The compiler service has a single subprocess argument set, making
  the deterministic boundary cleaner and the build log easier to
  validate.
- A future XeLaTeX fallback is possible but is not free work; it
  requires a new ADR and corresponding renderer/compiler/validator
  updates.

## Related

- `docs/PRD.md` FR-20, §16.3
- `docs/PRD_latex_generation.md`
- [ADR-0003 — Deterministic LaTeX rendering boundary](ADR-0003-deterministic-latex-rendering.md)
