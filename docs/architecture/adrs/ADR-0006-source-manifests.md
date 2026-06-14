# ADR-0006 — Canonical vs configurable source manifests

- **Status:** Accepted (Phase 4 design amendment — P4-I04).
- **Date:** 2026-06-14.

## Context

`docs/PRD.md` §22 records the **canonical HW3 demonstration** topic and
its fixed ten-source manifest in `config/article_sources.yaml`. The same
PRD requires the reusable product to be **generic** (NFR-27): a
different topic and a different verified manifest must work without
source-code changes.

Phase 3 (P3-I02) reconciled the mechanism PRDs to distinguish the
"canonical run rules" (all-ten coverage, ~2–3 verified sources per
chapter for the demonstration article) from the "generic product
behavior" (consume any verified manifest, validate citations against
that manifest).

`docs/PRD_bibliography_and_citations.md` already forbids fabricated
sources at every stage. `docs/PRD_crewai_pipeline.md` §4.1 already
specifies that reusable code may not hardcode arXiv IDs, citation keys,
or source counts.

## Decision

1. **The reusable runtime treats the source manifest as a typed input.**
   Agents, prompts, and code never reference canonical arXiv IDs,
   citation keys, or counts.
2. **The canonical HW3 demonstration is one configuration**, recorded
   in `config/article_sources.yaml` and locked by PRD §22.
3. **Canonical-mode rules** (all-ten coverage; the four Phase 3
   decisions in PRD §§22.6–22.9) apply **only** when the active manifest
   is the canonical one. A different manifest activates manifest-relative
   validation (every citation resolves; no fabricated sources; no
   silent replacement).
4. **Automatic source discovery is deferred beyond the MVP.** The MVP
   does not invent or auto-add sources. Future discovery may suggest
   candidates for a later verified manifest, but unverified candidates
   never enter a run.
5. **Verification is recorded.** Every manifest entry carries a
   `verification` block (status, `verified_at`, `verified_by`).
   Unverified entries cannot be cited.

## Consequences

- The same code can produce the canonical HW3 article and, under a
  different manifest, produce a different article — demonstrated by
  P12-I06 (planned).
- Canonical-mode rules remain enforceable because the runtime can
  detect canonical mode via the manifest's identity, not via hardcoded
  IDs.
- The Bibliography Agent's prompt does not change between modes; only
  the input manifest does. This preserves prompt stability across
  configurations.

## Related

- `docs/PRD.md` §22 (canonical demo article topic)
- `docs/PRD_crewai_pipeline.md` §4.1 (topic/source scope contract)
- `docs/PRD_bibliography_and_citations.md` (no-fabricated-sources policy)
- [ADR-0002 — Typed artifact contracts](ADR-0002-typed-artifact-contracts.md)
