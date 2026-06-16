# ADR-0003 — Deterministic LaTeX rendering boundary

- **Status:** Accepted (Phase 4 design amendment — P4-I04).

## Context

The pipeline must produce a structured LaTeX project that compiles
reliably with LuaLaTeX (`docs/PRD.md` FR-15..FR-27, `docs/PRD_latex_generation.md`).
LaTeX is fragile: escaping rules, package interactions, BiDi handling,
and table/TikZ separation (FR-17a–d) must be enforced consistently.

If the LaTeX Agent (LLM) emits raw LaTeX strings, the system inherits
every LLM failure mode (unescaped `&`, broken `\input{}` paths, raw
strings smuggling around path safety, silent BiDi corruption). The
no-silent-fallback policy and FR-17a–d separation rules become
impossible to enforce.

## Decision

The LaTeX Agent emits only a **semantic** `LaTeXProjectSpec v1` (see
[`artifact_contracts.md`](../artifact_contracts.md) §2). It does not
emit raw `.tex` content or file paths.

A **deterministic renderer** (Python code, no LLM) translates
`LaTeXProjectSpec v1` into the `.tex` files under the run workspace's
`latex_project/`. The renderer:

- chooses filenames and paths;
- performs all LaTeX escaping;
- enforces FR-17a–d separation (tables and TikZ in dedicated files);
- writes files atomically through the secure file I/O layer
  (path-guarded; workspace-rooted);
- computes content hashes that the artifact manifest records.

The deterministic renderer is the sole writer of `.tex` content in the
run workspace. Even agent-supplied snippets (e.g., equation body,
caption text) are escaped and embedded by the renderer.

## Consequences

- LaTeX correctness becomes a property of code, not of an LLM.
- The same `LaTeXProjectSpec v1` always produces the same `.tex` tree
  (given the same renderer version), aiding reproducibility (NFR-24)
  and validation (P11 / `docs/PRD_pdf_validation.md`).
- The LaTeX Agent's prompt becomes simpler and more stable; it focuses
  on document structure rather than escape sequences.
- New LaTeX features (e.g., a new theorem-like environment) require
  renderer support, not just an LLM prompt change.

## Related

- `docs/PRD_latex_generation.md` (LaTeX project conventions)
- [ADR-0007 — LuaLaTeX as the MVP engine](ADR-0007-lualatex-mvp.md)
- [`artifact_contracts.md`](../artifact_contracts.md) edge E7/E9.
