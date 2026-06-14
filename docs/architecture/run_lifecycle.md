# Run lifecycle, workspace, and operational modes

> **Status:** Phase 4 design amendment (P4-I04). Documentation-only.
> Implementation is scheduled for P5-I10 (`PipelineRunContext`,
> workspace, artifact manifest) and P5-I11 (CLI operational modes and
> offline fixtures).

This document specifies the lifecycle of a single pipeline run, the
isolated workspace it owns, the operational modes supported by the CLI,
and the explicit promotion machinery that protects canonical artifacts.

## 1. `PipelineRunContext`

A `PipelineRunContext` is created exactly once per run, at CLI entry.
It is the deterministic owner of:

- a **run ID** (ULID or UUID v4, generated at run start, recorded in
  every emitted event);
- the **isolated workspace** at `results/<run_id>/` — see
  [`artifact_contracts.md`](artifact_contracts.md) §3 for the layout;
- a **configuration snapshot** (`config_snapshot.json`) capturing the
  effective configuration (topic, source manifest path, provider,
  model, budget, registry version, environment-variable presence —
  never values) at the moment of run start;
- a structured **event log** (`events.jsonl`, NFR-16) of major workflow
  stages and state transitions;
- a structured **usage/cost log** (`usage.jsonl`) populated exclusively
  by the API Gatekeeper (P5-I09);
- the **artifact manifest** (`manifest.v1.json`) — the single source of
  truth for what the run produced.

The `PipelineRunContext` is the only component allowed to materialize
new files under `results/<run_id>/`; all other components request file
I/O through the secure file I/O layer, which enforces the run-root
constraint.

## 2. Lifecycle states

A run moves through the following states; transitions emit an event:

```
created → configured → registry_loaded → orchestrating
       → rendering   → compiling        → validating
       → pass | fail | aborted          → promoted (only if pass)
```

| State | Entry condition | Exit condition |
|---|---|---|
| `created` | `PipelineRunContext` instantiated, workspace mkdir'd | configuration snapshot persisted |
| `configured` | configuration snapshot present | registry compatibility check passes |
| `registry_loaded` | registry version pinned | crew kickoff invoked |
| `orchestrating` | tasks T1..T8 executing | every typed artifact validated |
| `rendering` | `LaTeXProjectSpec` v1 validated | renderer emits workspace `.tex` files + hashes |
| `compiling` | renderer complete | compiler exit code 0 + build artifacts present |
| `validating` | compile complete | `ValidationReport` v1 written |
| `pass` | report.result == "pass" | (promotion available) |
| `fail` | any halting condition | workspace preserved; operator notified |
| `aborted` | operator/gatekeeper/budget rejection | workspace preserved; operator notified |
| `promoted` | operator runs `promote --run-id` against a `pass` run | canonical roots updated; `PromotionRecord` v1 written |

States `fail` and `aborted` never produce a `promoted` state. The
canonical roots remain untouched.

## 3. Operational modes

Modes are mutually exclusive top-level CLI selections. Modes interact
with the lifecycle by enabling or skipping particular states.

| Mode | Description | Sequences activated |
|---|---|---|
| `dry-run` | No fixtures, no live calls, no file writes outside workspace. Simulates the pipeline structure to verify configuration, registry compatibility, and workspace creation. | Sequence 1 (skeleton only) |
| `offline-fixture` | Replaces live provider/search calls with deterministic fixture responses. No API keys required. CI-safe. | 1, 3, 4, 6, 7, 8 |
| `live` | Real provider/search calls routed through provider facade + API Gatekeeper. | 2, 3, 4, 5, 6, 7, 8 |
| `compile-only` | Reuses an existing workspace (selected via `--run-id`) and re-runs the renderer + compiler + validator. | 6, 7, 8 |
| `validate-only` | Reuses an existing workspace and re-runs validation only. | 7 |
| `resume` | Continues an unfinished run from its first non-`pass` stage. Requires manifest integrity check. | depends on entry stage |
| `--topic <str>` override | Modifier — overrides the configured topic for any of the above modes. Recorded in the configuration snapshot. | n/a |
| `--manifest <path>` override | Modifier — overrides the configured source manifest path. Recorded in the configuration snapshot. | n/a |

### Mode invariants

- Modes never change deterministic authority. The Validator is still
  deterministic in `dry-run`; the secure file I/O still enforces
  workspace roots in every mode.
- `offline-fixture` and `dry-run` make zero network calls and require
  zero secrets, enabling CI integration (P5-I13).
- `live` requires `.env` secrets per FR-3/FR-4; modes that do not
  require secrets must not fail when `.env` is absent.

## 4. Explicit promotion

Promotion is the only mechanism that moves artifacts from a run
workspace to canonical roots:

- `latex_project/` (entire structured project)
- `results/final.pdf`
- `results/generated_markdown/` (canonical Markdown path, FR-12, PRD §12.3)

Promotion preconditions:

1. The target run is in state `pass` (Validator reported PASS).
2. The artifact manifest passes an integrity check: every recorded
   `sha256` matches the file on disk.
3. The promotion executor recomputes hashes during the copy and records
   them in `PromotionRecord` v1.
4. If a canonical artifact already exists, the executor halts unless
   the operator passed `--force` and a reason; both are recorded.
5. Promotion writes are atomic at the file level (write to a temp path
   under the canonical root, then `rename`).
6. Promotion emits an `artifact.promoted` event in the source run's
   `events.jsonl`.

See [ADR-0005](adrs/ADR-0005-per-run-workspace-and-promotion.md).

## 5. Resumption

`resume` is supported when the workspace and its manifest are intact.
The CLI:

1. Loads `manifest.v1.json`.
2. Validates every recorded `sha256`.
3. Identifies the first stage that did not produce a `pass` artifact.
4. Re-enters the pipeline at that stage with the same effective
   configuration (re-reads `config_snapshot.json`).

Resumption respects the prompt/config registry version that the
original run pinned. If the registry version has advanced and the
recorded compatibility shape is no longer supported, resumption is
refused; a fresh run is required.

## 6. Sanitized evidence bundle (forward reference)

The final evidence bundle (P13-I05) is assembled by selecting one run
ID, then copying:

- the configuration snapshot (with secret values redacted),
- the artifact manifest,
- the validation report,
- the build log summary,
- the usage/cost report,
- the prompt/config registry version + compatibility fingerprint,
- the source manifest,
- the final PDF, and
- the LaTeX project tree.

The evidence bundle must contain **no secrets, no private paths, no
local-only archive bytes** (e.g., `data/sources/arxiv/source_zips/` is
excluded), and **no external repository references or attribution**.

## 7. Failure cleanup

`fail` and `aborted` runs are preserved by default. Operator-driven
cleanup is the only way to remove a failed run's workspace and is a
separate CLI subcommand. Automatic cleanup of failed runs is
explicitly **not** part of the design.
