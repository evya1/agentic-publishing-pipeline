# ADR-0001 — Sequential CrewAI orchestration

- **Status:** Accepted (Phase 4 design amendment — P4-I04).

## Context

The CrewAI pipeline composes eight specialized agents and eight tasks
(`docs/PRD.md` §8.3, `docs/PRD_crewai_pipeline.md` §5–§6). CrewAI
supports several `Process` modes (sequential and hierarchical). FR-8 in
`docs/PRD.md` states the default `Process` is sequential, and AC §14.5
requires inspectable intermediate artifacts and explicit `context`
between tasks.

## Decision

The MVP uses CrewAI's **sequential** process exclusively. Tasks execute
in the fixed order T1 → T2 → T3 → T4 → T5 → T6 → T7 → T8, followed by
the deterministic `ValidatorService`.

Any deviation (hierarchical, parallel sub-crews, dynamic delegation)
must be justified in a future revision of
`docs/PRD_crewai_pipeline.md` and approved before implementation.

## Consequences

- The task graph is linear and easy to reason about. Reviewers and
  validators can walk the graph by reading
  [`artifact_contracts.md`](../artifact_contracts.md) §1.
- Sequential execution serializes provider cost; this is acceptable for
  HW3-scale runs and simplifies the API Gatekeeper (P5-I09).
- Failure modes are localized: a halted task means no downstream task
  runs (see [`runtime_sequences.md`](../runtime_sequences.md) sequence
  4).
- Adding parallelism later requires re-deriving the artifact contracts'
  consumer/producer linkage and the bounded-repair semantics.

## Related

- [ADR-0002 — Typed artifact contracts](ADR-0002-typed-artifact-contracts.md)
- [ADR-0004 — Provider facade vs API Gatekeeper](ADR-0004-provider-vs-gatekeeper.md)
