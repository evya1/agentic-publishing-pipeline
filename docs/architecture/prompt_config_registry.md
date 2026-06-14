# Prompt/config registry — design

> **Status:** Phase 4 design amendment (P4-I04). Documentation-only.
> Implementation is scheduled for P5-I12.

This document specifies the **machine-readable, versioned runtime
registry** for agent and task prompts and configuration. It also
preserves the role of `docs/PROMPTS.md` as the **human-readable evidence
ledger**, and explains how the two are linked.

## 1. Why two artifacts

`docs/PROMPTS.md` is, and remains, the canonical *human evidence ledger*.
It records every prompt verbatim, who used it, when it was iterated, and
why. It is the artifact a course reviewer or auditor reads.

`docs/PROMPTS.md` is not safe for runtime to load directly:

- it is Markdown, not a parser-friendly schema;
- it contains free-form notes and iteration history alongside live
  text;
- it has no enforced version compatibility — silent drift between the
  ledger and what the code runs is impossible to detect by reading
  Markdown alone.

The **runtime prompt/config registry** solves these problems with a
machine-readable schema, an explicit version, and a compatibility check
that runs at CLI startup.

Each registry entry carries a `ledger_id` pointing to the matching
`docs/PROMPTS.md` entry. This makes the registry the runtime contract
and `docs/PROMPTS.md` the evidence record; the two must stay in sync, and
every release records the registry version that was active.

## 2. Registry layout (planned)

The registry lives in version-controlled files under
`config/prompt_registry/` (planned location; finalized in P5-I12).

```
config/prompt_registry/
├── registry.v1.yaml            # top-level index + version
├── agents/
│   ├── research.v1.yaml
│   ├── outline.v1.yaml
│   ├── writer.v1.yaml
│   ├── technical.v1.yaml
│   ├── bidi.v1.yaml
│   ├── latex.v1.yaml
│   ├── bibliography.v1.yaml
│   └── reviewer.v1.yaml
└── tasks/
    ├── T1_research.v1.yaml
    ├── T2_outline.v1.yaml
    ├── T3_chapter_drafts.v1.yaml
    ├── T4_technical_assets.v1.yaml
    ├── T5_bidi.v1.yaml
    ├── T6_bibliography.v1.yaml
    ├── T7_latex_assembly.v1.yaml
    └── T8_review.v1.yaml
```

`registry.v1.yaml` records the registry's own version and the list of
expected entries:

```yaml
registry_version: v1
generated_at: 2026-06-14
entries:
  agents:
    - id: PROMPT-AGENT-RESEARCH-001
      path: agents/research.v1.yaml
      ledger_id: PROMPT-AGENT-RESEARCH-001
    # … one per agent
  tasks:
    - id: PROMPT-TASK-T1-001
      path: tasks/T1_research.v1.yaml
      ledger_id: PROMPT-TASK-T1-001
    # … one per task
compatibility:
  contract_versions:
    - ResearchNotes.v1
    - Outline.v1
    - ChapterDrafts.v1
    - AssetSpecs.v1
    - BiDiSection.v1
    - BibliographyBundle.v1
    - LaTeXProjectSpec.v1
    - ReviewerSignal.v1
```

## 3. Per-entry schema (agents and tasks)

Each agent or task entry is a small YAML document:

```yaml
id: PROMPT-AGENT-RESEARCH-001
ledger_id: PROMPT-AGENT-RESEARCH-001       # link to docs/PROMPTS.md
kind: agent                                # "agent" | "task" | "tool"
version: v1
prompt:
  role: |
    You are an experienced technical researcher …
  goal: |
    Your goal is to collect comprehensive …
  backstory: |
    …
config:
  model_class: "research"                  # logical class; mapped to model in provider config
  temperature: 0.2
  max_tokens: 4096
  allowed_tools:
    - search.metadata_verification
  emits_contract: null                     # agents emit content; tasks emit artifacts
  consumes_contracts: []
```

Task entries also declare the contracts they emit and consume:

```yaml
id: PROMPT-TASK-T3-001
ledger_id: PROMPT-TASK-T3-001
kind: task
version: v1
prompt:
  description: |
    Using the research notes (T1) and the outline (T2), draft …
  expected_output: |
    Markdown chapter files under results/generated_markdown/chapters/*.md …
config:
  agent: PROMPT-AGENT-WRITER-001
  consumes_contracts:
    - ResearchNotes.v1
    - Outline.v1
  emits_contract: ChapterDrafts.v1
  repair_attempts_allowed: 1
```

## 4. Compatibility check (startup)

At CLI startup, the runtime:

1. Loads `registry.v1.yaml`.
2. Computes a structural fingerprint over the registry contents
   (sorted IDs + versions + contract-version list).
3. Compares the fingerprint to the structural fingerprint expected by
   the deterministic code's compiled-in contract versions.
4. If the registry's `compatibility.contract_versions` does not cover
   every contract the deterministic code requires, the run is refused
   with an actionable error (NFR-18). No silent fallback.
5. The fingerprint and `registry_version` are recorded in the run's
   `config_snapshot.json` and in the artifact manifest. Every emitted
   event carries the registry version.

## 5. Resumption and registry version

`resume` (see [`run_lifecycle.md`](run_lifecycle.md) §5) is refused if
the registry's structural fingerprint has changed between the original
run and the resumption attempt. A fresh run with a fresh run ID is
required so that downstream evidence (manifest, validation report,
sanitized evidence bundle) cannot mix prompts from incompatible
registry versions.

## 6. Ledger ↔ registry update workflow

When a prompt changes:

1. Update the matching entry in `docs/PROMPTS.md` (verbatim text +
   `Notes` describing what changed and why) — this is the human
   evidence record.
2. Bump the registry entry's `version` field and add a new file with
   the updated text. Old versions remain in the tree as long as any
   reachable run workspace pins them.
3. Update `registry.v1.yaml` (or roll to `registry.v2.yaml` if the
   schema itself changes).
4. Run the compatibility check; if it fails, the runtime refuses to
   start.
5. Record the version change in the PR description and in
   `docs/PROMPTS.md`.

## 7. What the registry is not

- It is not a runtime mutation surface. The registry is loaded
  read-only.
- It is not a substitute for `docs/PROMPTS.md`. Both exist; the
  registry is the contract, the ledger is the evidence.
- It does not store secrets. Secrets remain in `.env` (FR-3) and are
  never echoed into the registry, the snapshot, or the manifest.
