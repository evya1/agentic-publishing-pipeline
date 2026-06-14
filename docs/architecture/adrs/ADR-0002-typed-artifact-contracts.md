# ADR-0002 — Typed artifact contracts and one bounded repair

- **Status:** Accepted (Phase 4 design amendment — P4-I04).
- **Date:** 2026-06-14.

## Context

The CrewAI pipeline passes structured data between agents and tasks.
Raw LLM output is unreliable: schema drift, missing fields, JSON
formatting errors, and silently degraded content are common. NFR-19 and
FR-40 forbid the LLM from being the source of truth for validation.

The pipeline therefore needs an explicit type system at every task edge
and a clear, finite policy for handling invalid output. Retries that
keep going indefinitely waste budget and disguise persistent failure;
fallbacks that silently degrade content violate the no-silent-fallback
policy in `docs/PRD.md`.

## Decision

1. **Every task edge has a named, versioned Pydantic contract.** The
   list of contracts lives in
   [`artifact_contracts.md`](../artifact_contracts.md) §1–§2.
2. **No downstream task consumes raw LLM output.** A typed-contract
   parse and validation step sits between the producing task and any
   consuming task.
3. **Repairs are bounded.** When a parse fails, the orchestrator may
   make **exactly one** repair attempt. The repair prompt receives the
   preserved validation error.
4. **If the repair attempt also fails, the run halts.** No silent
   fallback, no downstream consumption of invalid data, no canonical
   write.
5. **Contracts are versioned.** Breaking changes require a new version
   (`v2`); both versions may live in the registry during a deprecation
   window declared in the prompt/config registry compatibility list.

## Consequences

- A persistent agent failure is surfaced immediately and visibly.
  Operators see the validation error, not a misleading "completed" run.
- The repair attempt consumes budget; the API Gatekeeper (ADR-0004)
  accounts for it under the normal usage/cost log.
- The "exactly one" rule is a hard upper bound, not a target. A task
  that consistently needs a repair indicates prompt or contract drift
  that should be addressed in the registry.
- Schema versioning is necessary so a re-run against an older workspace
  can still parse stored artifacts.

## Related

- [`artifact_contracts.md`](../artifact_contracts.md) (the contract
  catalogue)
- [`runtime_sequences.md`](../runtime_sequences.md) Sequences 3
  (success) and 4 (exhaustion).
- [ADR-0006 — Canonical vs configurable source manifests](ADR-0006-source-manifests.md)
