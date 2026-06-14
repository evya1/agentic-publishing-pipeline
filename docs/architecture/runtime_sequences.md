# Runtime sequence diagrams — agentic-publishing-pipeline

> **Status:** Phase 4 design amendment (P4-I04). Documentation-only.
> No runtime implementation exists yet; see `docs/PLAN.md` Phase 5
> onward for implementation phasing.

This document records the runtime sequences that the planned
implementation must follow. Each sequence is labelled with the
operational mode that triggers it (per
[`run_lifecycle.md`](run_lifecycle.md) §3).

The eight sequences below collectively satisfy the P4-I04 deliverable
"successful offline-fixture sequence; successful live sequence; invalid
output plus one bounded repair sequence; repair-exhaustion failure;
provider/budget rejection; LaTeX compilation failure; deterministic
validation failure; explicit artifact promotion."

Common participants:

- **Operator** — human launching the CLI.
- **CLI** — entry point in `src/agentic_publishing_pipeline/crews/`.
- **RunCtx** — `PipelineRunContext` (P5-I10).
- **Registry** — prompt/config registry (P5-I12).
- **Crew** — CrewAI sequential orchestration.
- **Contracts** — typed artifact-contract boundary (P5-I08).
- **Provider** — provider facade.
- **Gatekeeper** — API Gatekeeper (P5-I09).
- **Fixtures** — offline fixture store.
- **Renderer** — deterministic renderer + secure file I/O.
- **Compiler** — LaTeX build service.
- **Validator** — deterministic `ValidatorService`.
- **Promotion** — explicit promotion operation.
- **Workspace** — `results/<run_id>/`.

---

## Sequence 1 — Successful offline-fixture run

**Mode:** `offline-fixture`. No network, no API keys required, no paid
provider call. Deterministic fixture responses replace live LLM/search,
but **every call still flows through the API Gatekeeper** so that
request policy, accounting, and structured event emission remain
consistent with the live path (see
[ADR-0004](adrs/ADR-0004-provider-vs-gatekeeper.md) §"Offline fixtures
still flow through the Gatekeeper"). The Gatekeeper deterministically
routes the call to the fixture store instead of the network.

```mermaid
sequenceDiagram
    autonumber
    participant Operator
    participant CLI
    participant RunCtx
    participant Registry
    participant Crew
    participant Contracts
    participant Provider
    participant Gatekeeper
    participant Fixtures
    participant Renderer
    participant Compiler
    participant Validator

    Operator->>CLI: run --mode offline-fixture
    CLI->>RunCtx: create run, snapshot config, init workspace
    CLI->>Registry: load prompts/config (verify schema/version)
    Registry-->>CLI: prompt/config bundle (versions pinned)
    CLI->>Crew: kickoff(sequential)
    loop For each task T1..T8
        Crew->>Provider: request (typed)
        Provider->>Gatekeeper: gated call (offline routing, no network)
        Gatekeeper->>Fixtures: lookup recorded response (deterministic)
        Fixtures-->>Gatekeeper: typed normalized response
        Gatekeeper->>RunCtx: usage event (mode=offline-fixture, cost=0)
        Gatekeeper-->>Provider: typed normalized response
        Provider-->>Crew: response
        Crew->>Contracts: parse(output, version)
        Contracts-->>Crew: validated artifact (versioned)
        Crew->>RunCtx: append event + artifact entry
    end
    Crew->>Renderer: render LaTeXProjectSpec v1 → files
    Renderer->>Workspace: atomic writes (path-guarded)
    Renderer->>Compiler: build (compile-only allowed root)
    Compiler-->>RunCtx: build log + exit code
    Crew->>Validator: validate(run_id)
    Validator-->>RunCtx: validation report (PASS)
    Validator-->>Operator: human-readable report
```

Offline-fixture invariants:

- **No external network request** is issued by any container.
- **No provider API key** is read or required.
- The **Gatekeeper still applies request policy** (budget accounting,
  retry classification — vacuously zero-cost — timeout, attempt
  identity) and emits a `usage.jsonl` event for every request with
  `mode=offline-fixture` and `estimated_cost=0`. Policy violations
  (e.g., a configured per-run request cap) are enforced identically to
  the `live` path.
- The Gatekeeper is the **only** component that may route a request to
  `Fixtures`; the provider facade never reads the fixture store
  directly.

---

## Sequence 2 — Successful live run

**Mode:** `live`. Real LLM/search calls routed through provider facade
and API Gatekeeper. Budgets, retries, timeouts enforced.

```mermaid
sequenceDiagram
    autonumber
    participant Operator
    participant CLI
    participant RunCtx
    participant Crew
    participant Contracts
    participant Provider
    participant Gatekeeper
    participant LLM as LLM/Search provider
    participant Renderer
    participant Compiler
    participant Validator

    Operator->>CLI: run --mode live --topic <override?>
    CLI->>RunCtx: create run, snapshot config + env presence
    CLI->>Crew: kickoff(sequential)
    loop For each task T1..T8
        Crew->>Provider: request
        Provider->>Gatekeeper: gated call (budget, timeout, retry policy)
        Gatekeeper->>LLM: HTTP call
        LLM-->>Gatekeeper: response (tokens, latency)
        Gatekeeper->>RunCtx: usage/cost event
        Gatekeeper-->>Provider: typed normalized response
        Provider-->>Crew: response
        Crew->>Contracts: parse + validate (versioned)
        Contracts-->>Crew: parsed artifact
    end
    Crew->>Renderer: render artifacts
    Renderer->>Workspace: atomic writes
    Renderer->>Compiler: build
    Compiler-->>RunCtx: build log
    Crew->>Validator: validate(run_id)
    Validator-->>Operator: PASS report
```

---

## Sequence 3 — Invalid agent output + one bounded repair (success)

**Mode:** any. Stage produces output that fails contract validation;
exactly **one** repair attempt is allowed
([ADR-0002](adrs/ADR-0002-typed-artifact-contracts.md)).

```mermaid
sequenceDiagram
    autonumber
    participant Crew
    participant Contracts
    participant Provider
    participant Gatekeeper
    participant RunCtx

    Crew->>Provider: request task T_n
    Provider->>Gatekeeper: gated call
    Gatekeeper-->>Provider: response
    Provider-->>Crew: raw output
    Crew->>Contracts: parse(output, ContractVersion v1)
    Contracts-->>Crew: ValidationError (preserved)
    Crew->>RunCtx: emit "contract.invalid" event
    Crew->>Provider: repair request (attempt 1/1, include errors)
    Provider->>Gatekeeper: gated call (counts toward budget)
    Gatekeeper-->>Provider: response
    Provider-->>Crew: repaired output
    Crew->>Contracts: parse(output, v1)
    Contracts-->>Crew: validated artifact
    Crew->>RunCtx: emit "contract.repaired" event
```

---

## Sequence 4 — Repair exhaustion (failure)

**Mode:** any. Repair attempt also fails contract validation; run halts
without silently degrading. No downstream stage runs on unvalidated
output.

```mermaid
sequenceDiagram
    autonumber
    participant Crew
    participant Contracts
    participant Provider
    participant RunCtx
    participant Operator

    Crew->>Provider: request task T_n
    Provider-->>Crew: raw output
    Crew->>Contracts: parse(output, v1)
    Contracts-->>Crew: ValidationError
    Crew->>Provider: repair request (1/1)
    Provider-->>Crew: raw output 2
    Crew->>Contracts: parse(output 2, v1)
    Contracts-->>Crew: ValidationError (preserved)
    Crew->>RunCtx: emit "contract.repair_exhausted"
    Crew-->>Operator: halt with actionable error (NFR-18)
    Note over Crew,Operator: Workspace preserved for inspection;<br/>no promotion; no canonical write.
```

---

## Sequence 5 — Provider / budget rejection

**Mode:** `live`. Gatekeeper rejects the call (budget exceeded,
timeout, classified non-retriable error). Provider facade does not
fall back silently to a different model or fixture.

```mermaid
sequenceDiagram
    autonumber
    participant Crew
    participant Provider
    participant Gatekeeper
    participant RunCtx
    participant Operator

    Crew->>Provider: request task T_n
    Provider->>Gatekeeper: gated call
    Gatekeeper->>Gatekeeper: check budget / classify error
    Gatekeeper->>RunCtx: emit "provider.rejected" usage event
    Gatekeeper-->>Provider: GatekeeperRejection
    Provider-->>Crew: GatekeeperRejection (typed)
    Crew->>RunCtx: emit "task.aborted"
    Crew-->>Operator: halt with reason (NFR-18)
    Note over Crew,Operator: No silent model swap;<br/>no silent offline fallback;<br/>no canonical write.
```

---

## Sequence 6 — LaTeX compilation failure

**Mode:** any after T7. Compiler returns non-zero exit code or
parses-build-log indicates a hard error. ValidatorService is not run;
no promotion occurs.

```mermaid
sequenceDiagram
    autonumber
    participant Renderer
    participant Compiler
    participant RunCtx
    participant Operator

    Renderer->>Compiler: invoke LuaLaTeX (fixed args, timeout)
    Compiler->>Compiler: multi-pass build
    Compiler-->>RunCtx: build log (full)
    Compiler-->>Renderer: non-zero exit / parsed error class
    Renderer->>RunCtx: emit "compile.failed"
    Renderer-->>Operator: halt with build-log pointer
    Note over Renderer,Operator: Workspace preserved.<br/>Validator stage skipped.<br/>No canonical write.
```

---

## Sequence 7 — Deterministic validation failure

**Mode:** any. Build succeeded but `ValidatorService` reports a
required-artifact, citation, page-budget, or BiDi failure.

```mermaid
sequenceDiagram
    autonumber
    participant Validator
    participant RunCtx
    participant Operator

    Validator->>Validator: check repo files
    Validator->>Validator: check LaTeX files (FR-17a..d)
    Validator->>Validator: check PDF indicators (image, graph, table,<br/>equation w/ \\ref, theorem-like, BiDi, nomenclature, index)
    Validator->>Validator: check every \\cite{} resolves
    Validator->>Validator: check total + substantive page budget (P10-I03)
    Validator->>RunCtx: validation report (FAIL with itemized failures)
    Validator-->>Operator: human-readable report
    Note over Validator,Operator: ValidatorService is deterministic.<br/>LLM never decides PASS/FAIL (FR-40, NFR-19).<br/>No canonical write on FAIL.
```

---

## Sequence 8 — Explicit artifact promotion

**Mode:** `live` or `offline-fixture` after a PASS. Canonical artifacts
are never written by intermediate stages; they are produced only by an
explicit promotion command driven by the operator.

```mermaid
sequenceDiagram
    autonumber
    participant Operator
    participant CLI
    participant RunCtx
    participant Validator
    participant Promotion
    participant Canonical as Canonical paths

    Operator->>CLI: promote --run-id <id>
    CLI->>RunCtx: load manifest + validation report
    RunCtx-->>CLI: PASS report + artifact manifest
    CLI->>Promotion: promote(run_id)
    Promotion->>Promotion: verify PASS, verify manifest integrity
    Promotion->>Canonical: atomic write (latex_project/, results/final.pdf)
    Promotion->>RunCtx: emit "artifact.promoted" with hashes
    Promotion-->>Operator: promotion summary (run_id, hashes, paths)
    Note over Promotion,Canonical: Promotion is the ONLY writer of canonical roots.<br/>Failed runs cannot promote.<br/>Existing canonical artifacts are never silently overwritten<br/>(ADR-0005).
```

---

## Mode → sequence matrix

| Mode | Primary sequences |
|---|---|
| `dry-run` | Sequence 1 (no fixtures used; agents and tasks simulated; no file writes outside workspace) |
| `offline-fixture` | Sequences 1, 3, 4, 6, 7, 8 |
| `live` | Sequences 2, 3, 4, 5, 6, 7, 8 |
| `compile-only` | Sequences 6, 7 (skips T1–T8; consumes an existing run workspace) |
| `validate-only` | Sequence 7 (consumes an existing run workspace) |
| `resume` | Skips already-PASS stages; re-enters mid-pipeline at the first non-PASS stage (deferred to P5-I11 implementation) |
