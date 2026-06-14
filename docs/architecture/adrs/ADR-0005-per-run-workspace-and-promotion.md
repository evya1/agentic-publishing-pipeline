# ADR-0005 — Per-run workspace and explicit promotion

- **Status:** Accepted (Phase 4 design amendment — P4-I04).
- **Date:** 2026-06-14.

## Context

The canonical artifacts required by `docs/PRD.md` §13 (the LaTeX project
under `latex_project/`, the final PDF at `results/final.pdf`, the
canonical Markdown drafts under `results/generated_markdown/`) are
high-value and slow to regenerate. Allowing every intermediate stage to
write directly to canonical paths causes several problems:

- a failed mid-pipeline run can corrupt previously good canonical
  artifacts;
- two concurrent runs (e.g., topic exploration vs canonical demo) race
  on the same paths;
- "what produced this PDF?" loses a stable answer because canonical
  paths are mutable;
- evidence-bundle assembly (P13-I05) cannot reconstruct a specific run.

## Decision

1. Every run owns an **isolated workspace** under `results/<run_id>/`
   (see [`artifact_contracts.md`](../artifact_contracts.md) §3 for the
   layout and [`run_lifecycle.md`](../run_lifecycle.md) §1 for the
   lifecycle).
2. **No intermediate stage writes to canonical roots.** Renderers,
   compilers, validators, and graph/asset code write only under the
   workspace.
3. **Canonical roots are written exclusively by the promotion
   operation**, which runs only against a workspace whose
   `ValidationReport v1` reports `pass`. Promotion verifies manifest
   integrity, recomputes hashes, refuses to overwrite an existing
   canonical artifact unless `--force` is passed with a recorded
   reason, and writes atomically.
4. Failed and aborted runs are **preserved** for inspection. Cleanup is
   a separate operator-driven command.
5. The artifact manifest (`manifest.v1.json`) is the single record of
   what a run produced and is required as input for promotion,
   resumption, and the sanitized evidence bundle.

## Consequences

- Canonical artifacts always correspond to a known, validated run.
- Concurrent runs (e.g., the canonical demonstration vs a second-topic
  genericity proof under P12-I06) do not collide.
- The cost of preserving workspaces is paid in disk space; the
  benefit is full traceability for evidence and debugging.
- Promotion becomes a clear governance checkpoint — both the human
  operator and the deterministic Validator must agree before canonical
  state changes.

## Related

- [`run_lifecycle.md`](../run_lifecycle.md) §4 (promotion procedure)
- [`runtime_sequences.md`](../runtime_sequences.md) Sequence 8
- [ADR-0002 — Typed artifact contracts](ADR-0002-typed-artifact-contracts.md)
