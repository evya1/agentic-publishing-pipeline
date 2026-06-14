# ADR-0004 — Provider facade vs API Gatekeeper

- **Status:** Accepted (Phase 4 design amendment — P4-I04).
- **Date:** 2026-06-14.

## Context

The pipeline must route every LLM and search call through a single
controlled service layer (NFR-23, NFR-24) and must produce structured
usage/cost evidence for the final submission bundle. Two responsibilities
are often conflated in such a layer: **provider adaptation** (translate
between the codebase's internal request/response shape and an external
SDK's surface) and **policy enforcement** (budgets, timeouts, retries,
error classification, usage logging).

Conflating them produces a layer that is hard to test (every test
involves both adapter shape and policy state) and hard to extend (adding
a second provider also requires re-implementing budget logic).

## Decision

These responsibilities are split into two distinct components:

1. **Provider facade** — translates calls to the chosen LLM/search SDKs
   and returns a *typed, normalized* response. No policy decisions, no
   silent fallbacks. Adding a second provider means adding a sibling
   adapter behind the same facade interface.
2. **API Gatekeeper (P5-I09)** — the only component that knows about
   policy: budget enforcement, configurable timeouts, retry
   classification (retriable vs non-retriable), and structured usage
   events. Every request — including the bounded repair attempt from
   ADR-0002 — flows through the Gatekeeper with `run_id`, `agent_id`,
   `task_id`, and `attempt` carried as identity.

The Gatekeeper writes to `usage.jsonl` in the run workspace. The
facade does not.

When the Gatekeeper rejects a call (budget exhausted, timeout, classified
non-retriable error), it returns a typed `GatekeeperRejection` to the
facade, which propagates to the orchestrator. **There is no silent
provider fallback, no silent model swap, and no silent offline switch**
(see [`runtime_sequences.md`](../runtime_sequences.md) Sequence 5).

## Consequences

- The facade is straightforward to unit-test against a recorded fixture
  store ([ADR-0005](ADR-0005-per-run-workspace-and-promotion.md) §5 ties
  fixtures to the workspace).
- Budgets, retries, and usage logging gain a single home and a single
  source of truth (`usage.jsonl`).
- A second model class (e.g., a faster cheaper model for `T2 Outline`)
  is introduced by adding a routing rule in the Gatekeeper, not by
  modifying agents.
- Offline-fixture mode bypasses the live network (no SDK HTTP call,
  no API key required) but **still flows through the Gatekeeper** so
  that request policy, accounting, and structured usage events remain
  meaningful and identical in shape to the live path.

## Offline fixtures still flow through the Gatekeeper

The offline-fixture path is `ProviderFacade → ApiGatekeeper →
FixtureStore`. The provider facade never reads the fixture store
directly; the Gatekeeper is the **only** component allowed to route a
request to fixtures. This preserves the invariants enforced in the
`live` path:

- every call is gated against the configured budget, timeout, and
  retry-classification policy (vacuously zero-cost for fixtures);
- every call emits a `usage.jsonl` event carrying `run_id`,
  `agent_id`, `task_id`, `attempt`, `mode=offline-fixture`,
  `estimated_cost=0`, and the resolved fixture key;
- a configured per-run request cap (or any other policy constraint)
  rejects an offline run just as it would reject a live run;
- there is no silent bypass of Gatekeeper controls and no separate
  offline code path that the facade can take "around" the Gatekeeper.

Offline-fixture mode therefore exercises the same enforcement surface
as `live`, which is what makes offline tests meaningful as a
regression check on the policy layer. See
[`../runtime_sequences.md`](../runtime_sequences.md) Sequence 1 for the
diagram and the explicit invariants list.

## Related

- [ADR-0002 — Typed artifact contracts](ADR-0002-typed-artifact-contracts.md)
- [ADR-0005 — Per-run workspace and explicit promotion](ADR-0005-per-run-workspace-and-promotion.md)
