# TODO — agentic-publishing-pipeline

> **Status:** Phases 0 through 6 are complete and closed. Phase 6
> Markdown-first content generation and human approval merged through
> PR #81; P6-I00 through P6-I03 are verified and closed. Phase 7 is the
> next implementation phase. Do not tick later items until their underlying
> artifacts exist and have been verified on disk (and, where applicable,
> by a passing build, test, or validator run).

## How to read this file

- This file is the **concrete task backlog** for the project. Each item is
  traceable to a requirement in [`docs/PRD.md`](PRD.md) via an `[FR-…]`,
  `[NFR-…]`, `[KPI]`, or `[AC §…]` tag, or to a phase in
  [`docs/PLAN.md`](PLAN.md) via a `[Phase N]` tag.
- The phased roadmap lives in [`docs/PLAN.md`](PLAN.md). This file does not
  duplicate the roadmap — it lists the discrete work needed to discharge
  it.
- GitHub Issues mirror these items per the Traceability section below.
  Keep TODO wording intact when filing issues so titles remain traceable.

## Traceability — TODO ↔ Issue ↔ Milestone ↔ PRD

This section is the canonical mapping between this file and the live
GitHub tracking objects. It satisfies the Phase 2 exit criterion in
[`docs/PLAN.md`](PLAN.md) and is binding under the Project Tracking
Synchronization Contract in [`CONTRIBUTING.md`](../CONTRIBUTING.md) §8.

### Source-of-truth pointer

The canonical source-of-truth hierarchy is documented in full in
[`CONTRIBUTING.md`](../CONTRIBUTING.md) §1. In short: **PRD owns
requirements; PLAN owns phases (mirrored as GitHub Milestones); TODO
owns the backlog (mirrored as GitHub Issues)**. Verified artifacts on
disk are the only source of truth for *completion*.

### Closure rule (binding) — §F-6 restated

A GitHub issue may be closed only when the underlying artifact is
verified on disk (or by a passing build, test, or validator run).
**Closing a GitHub issue does NOT by itself permit ticking** a TODO
checkbox in this file, a PRD §14 acceptance-criterion checkbox in
[`docs/PRD.md`](PRD.md), a checkbox in
[`docs/HW3_REQUIREMENTS.md`](HW3_REQUIREMENTS.md), or a checkbox in
[`SUBMISSION_CHECKLIST.md`](../SUBMISSION_CHECKLIST.md). Each checkbox
type is ticked only after its own evidence requirement is met. The
identical rule is restated in §F-6 below — do not duplicate it when
filing new issues; reference §F-6.

### PRD §19 supersession (historical-only)

`docs/PRD.md` §19 ("Proposed Milestones" M1–M9) is **superseded by**
[`docs/PLAN.md`](PLAN.md) Phases 0–14 and by the GitHub Milestones that
mirror them. PRD §19 remains in `docs/PRD.md` for historical context
and must not be used to drive sequencing, milestone naming, exit
criteria, or status. Treat any conflict between PRD §19 and PLAN as
resolved in PLAN's favour.

### Internal-ID convention

Every TODO work item carries an internal ID of the form
**`P<phase>-I<nn>`** (e.g. `P2-I03`, `P9-I14`). The internal ID is the
stable handle; the GitHub issue **number** (`#N`) is the GitHub-side
identifier and can be found in the mapping below or by the live query:

```sh
gh issue list --search "P9-I14 in:title" --state all
```

When a new work item is added to TODO, allocate the next free `nn`
within its phase and open the GitHub issue under the matching
milestone (`Phase <phase> — <title>`) with the labels from
[`CONTRIBUTING.md`](../CONTRIBUTING.md) §11.

### Live mapping (TODO internal ID → GitHub issue → Milestone)

The mapping below was last reconciled during P2-I04 (#68) after
P2-I00 through P2-I03 were verified and closed with evidence. Use
`gh issue list --milestone "<title>" --state all` to confirm the
current state before acting.

#### Phase 2 — Project management setup ([milestone #1](https://github.com/evya1/agentic-publishing-pipeline/milestone/1))

| Internal ID | Issue | Status | Title (abridged)                                                        |
|-------------|-------|--------|-------------------------------------------------------------------------|
| P2-I00      | [#1](https://github.com/evya1/agentic-publishing-pipeline/issues/1) | Closed with evidence | Apply minimal doc patches before milestone/issue creation |
| P2-I01      | [#2](https://github.com/evya1/agentic-publishing-pipeline/issues/2) | Closed with evidence | Create 13 GitHub milestones (Phases 2–14)                 |
| P2-I02      | [#3](https://github.com/evya1/agentic-publishing-pipeline/issues/3) | Closed with evidence | Create GitHub issues from open TODO items and apply labels |
| P2-I03      | [#4](https://github.com/evya1/agentic-publishing-pipeline/issues/4) | Closed with evidence | Document TODO ↔ issue ↔ milestone ↔ PRD mapping in TODO intro |
| P2-I04      | [#68](https://github.com/evya1/agentic-publishing-pipeline/issues/68) | Closed with evidence | Reconcile verified Phase 2 completion in PLAN and TODO |

#### Phase 3 — Topic and scope ([milestone #2](https://github.com/evya1/agentic-publishing-pipeline/milestone/2))

| Internal ID | Issue | Status | Title (abridged)                                                         |
|-------------|-------|--------|--------------------------------------------------------------------------|
| P3-I01      | [#5](https://github.com/evya1/agentic-publishing-pipeline/issues/5) | Closed with evidence | Decide audience, depth target, BiDi balance, citation density |
| P3-I02      | [#6](https://github.com/evya1/agentic-publishing-pipeline/issues/6) | Closed with evidence | Reflect Phase 3 decisions in PRD §22/§3 and mechanism PRDs |

#### Phase 4 — CrewAI architecture design ([milestone #3](https://github.com/evya1/agentic-publishing-pipeline/milestone/3))

| Internal ID | Issue | Status | Title (abridged)                                                         |
|-------------|-------|--------|--------------------------------------------------------------------------|
| P4-I01      | [#7](https://github.com/evya1/agentic-publishing-pipeline/issues/7) | Closed with evidence | Specify the 8 agents (role/goal/backstory/tools)                        |
| P4-I02      | [#8](https://github.com/evya1/agentic-publishing-pipeline/issues/8) | Closed with evidence | Define ≥5 tasks with context flow; confirm sequential Process           |
| P4-I03      | [#9](https://github.com/evya1/agentic-publishing-pipeline/issues/9) | Closed with evidence | Capture initial Phase 4 prompts verbatim in `docs/PROMPTS.md`           |
| P4-I04      | [#71](https://github.com/evya1/agentic-publishing-pipeline/issues/71) | Closed with evidence | Add C4 views, runtime sequence diagrams, typed artifact boundaries, and ADRs |

#### Phase 5 — Provider/service layer and tools ([milestone #4](https://github.com/evya1/agentic-publishing-pipeline/milestone/4))

| Internal ID | Issue | Status | Title (abridged)                                                         |
|-------------|-------|--------|--------------------------------------------------------------------------|
| P5-I01      | [#10](https://github.com/evya1/agentic-publishing-pipeline/issues/10) | Closed with evidence | Provider/service layer + `.env-example`; secrets only from `.env`     |
| P5-I02      | [#11](https://github.com/evya1/agentic-publishing-pipeline/issues/11) | Closed with evidence | Add real dependencies via `uv add` per tool                           |
| P5-I03      | [#12](https://github.com/evya1/agentic-publishing-pipeline/issues/12) | Closed with evidence | Implement Search tool                                                  |
| P5-I04      | [#13](https://github.com/evya1/agentic-publishing-pipeline/issues/13) | Closed with evidence | Implement File I/O tool                                                |
| P5-I05      | [#14](https://github.com/evya1/agentic-publishing-pipeline/issues/14) | Closed with evidence | Implement Markdown conversion tool                                     |
| P5-I06      | [#15](https://github.com/evya1/agentic-publishing-pipeline/issues/15) | Closed with evidence | Implement LaTeX compilation tool (LuaLaTeX + biber multi-pass)         |
| P5-I07      | [#16](https://github.com/evya1/agentic-publishing-pipeline/issues/16) | Closed with evidence | Implement graph generation tool                                        |
| P5-I08      | [#73](https://github.com/evya1/agentic-publishing-pipeline/issues/73) | Closed with evidence | Implement versioned Pydantic artifact contracts and bounded validation repair |
| P5-I09      | [#74](https://github.com/evya1/agentic-publishing-pipeline/issues/74) | Closed with evidence | Implement API Gatekeeper, budgets, retries, and usage/cost logging |
| P5-I10      | [#75](https://github.com/evya1/agentic-publishing-pipeline/issues/75) | Closed with evidence | Introduce `PipelineRunContext`, isolated workspaces, and artifact manifests |
| P5-I11      | [#76](https://github.com/evya1/agentic-publishing-pipeline/issues/76) | Closed with evidence | Add CLI operational modes and deterministic offline fixtures |
| P5-I12      | [#77](https://github.com/evya1/agentic-publishing-pipeline/issues/77) | Closed with evidence | Implement versioned prompt/config registry and compatibility checks |
| P5-I13      | [#78](https://github.com/evya1/agentic-publishing-pipeline/issues/78) | Closed with evidence | Add baseline CI, lockfile, line-cap, and offline smoke gates |

#### Phase 6 — Markdown-first content pipeline ([milestone #5](https://github.com/evya1/agentic-publishing-pipeline/milestone/5)) *(complete and closed through PR #81)*

| Internal ID | Issue | Title (abridged)                                                         |
|-------------|-------|--------------------------------------------------------------------------|
| P6-I00      | [#17](https://github.com/evya1/agentic-publishing-pipeline/issues/17) | Closed with evidence — retire `content/markdown_drafts/`               |
| P6-I01      | [#18](https://github.com/evya1/agentic-publishing-pipeline/issues/18) | Closed with evidence — generated Markdown drafts                        |
| P6-I02      | [#19](https://github.com/evya1/agentic-publishing-pipeline/issues/19) | Closed with evidence — human review gate approval                       |
| P6-I03      | [#20](https://github.com/evya1/agentic-publishing-pipeline/issues/20) | Closed with evidence — Phase 6 AI usage recorded                        |

#### Phase 7 — Real-source and bibliography pipeline ([milestone #6](https://github.com/evya1/agentic-publishing-pipeline/milestone/6))

| Internal ID | Issue | Title (abridged)                                                         |
|-------------|-------|--------------------------------------------------------------------------|
| P7-I00      | [#21](https://github.com/evya1/agentic-publishing-pipeline/issues/21) | Source-collection policy + verification + audit-trail location        |
| P7-I01      | [#22](https://github.com/evya1/agentic-publishing-pipeline/issues/22) | Bibliography Agent consumes `config/article_sources.yaml`              |
| P7-I02      | [#23](https://github.com/evya1/agentic-publishing-pipeline/issues/23) | Verify manifest entries; populate authors; flip verification status   |
| P7-I03      | [#24](https://github.com/evya1/agentic-publishing-pipeline/issues/24) | Record per-source audit trail per P7-I00                               |
| P7-I04      | [#25](https://github.com/evya1/agentic-publishing-pipeline/issues/25) | Extract `.bib` entries (real only)                                     |
| P7-I05      | [#26](https://github.com/evya1/agentic-publishing-pipeline/issues/26) | Rekey `tbd…` citation keys to `authorYYYYkey`                          |
| P7-I06      | [#27](https://github.com/evya1/agentic-publishing-pipeline/issues/27) | Wire and resolve `\cite{...}` placeholders                             |
| P7-I07      | [#28](https://github.com/evya1/agentic-publishing-pipeline/issues/28) | Codify and enforce untrusted-archive policy                            |

#### Phase 8 — Python graph generation pipeline ([milestone #7](https://github.com/evya1/agentic-publishing-pipeline/milestone/7))

| Internal ID | Issue | Title (abridged)                                                         |
|-------------|-------|--------------------------------------------------------------------------|
| P8-I01      | [#29](https://github.com/evya1/agentic-publishing-pipeline/issues/29) | Implement `visualization/` and ≥1 real graph under `latex_project/figures/` |
| P8-I02      | *(planned — GitHub number TBD)* | Implement validated technical-asset specs and deterministic fallbacks |

#### Phase 9 — LaTeX project assembly ([milestone #8](https://github.com/evya1/agentic-publishing-pipeline/milestone/8))

| Internal ID | Issue | Title (abridged)                                                         |
|-------------|-------|--------------------------------------------------------------------------|
| P9-I01      | [#30](https://github.com/evya1/agentic-publishing-pipeline/issues/30) | Replace placeholder `main.tex` with thin-root `\input{}`              |
| P9-I02      | [#31](https://github.com/evya1/agentic-publishing-pipeline/issues/31) | `preamble.tex` for LuaLaTeX (fontspec + polyglossia + David CLM)      |
| P9-I03      | [#32](https://github.com/evya1/agentic-publishing-pipeline/issues/32) | `macros.tex` with reusable math notation                              |
| P9-I04      | [#33](https://github.com/evya1/agentic-publishing-pipeline/issues/33) | Chapter files (narrative-only; FR-17a–d separation)                   |
| P9-I05      | [#34](https://github.com/evya1/agentic-publishing-pipeline/issues/34) | Include ≥1 image                                                       |
| P9-I06      | [#35](https://github.com/evya1/agentic-publishing-pipeline/issues/35) | Standalone table in `tables/`                                          |
| P9-I07      | [#36](https://github.com/evya1/agentic-publishing-pipeline/issues/36) | Labeled equation with later `\ref`/`\eqref`                            |
| P9-I08      | [#37](https://github.com/evya1/agentic-publishing-pipeline/issues/37) | Theorem-like environment                                               |
| P9-I09      | [#38](https://github.com/evya1/agentic-publishing-pipeline/issues/38) | TikZ figure in `figures/`                                              |
| P9-I10      | [#39](https://github.com/evya1/agentic-publishing-pipeline/issues/39) | Headers/footers via `fancyhdr`                                         |
| P9-I11      | [#40](https://github.com/evya1/agentic-publishing-pipeline/issues/40) | Title/cover page + TOC                                                 |
| P9-I12      | [#41](https://github.com/evya1/agentic-publishing-pipeline/issues/41) | Nomenclature ≥2 symbols                                                |
| P9-I13      | [#42](https://github.com/evya1/agentic-publishing-pipeline/issues/42) | Index ≥1 Hebrew + ≥1 English term                                       |
| P9-I14      | [#43](https://github.com/evya1/agentic-publishing-pipeline/issues/43) | Substantial Hebrew/English BiDi section                                 |

#### Phase 10 — PDF build pipeline ([milestone #9](https://github.com/evya1/agentic-publishing-pipeline/milestone/9))

| Internal ID | Issue | Title (abridged)                                                         |
|-------------|-------|--------------------------------------------------------------------------|
| P10-I01     | [#44](https://github.com/evya1/agentic-publishing-pipeline/issues/44) | Multi-pass build (LuaLaTeX → biber → LuaLaTeX → LuaLaTeX)             |
| P10-I02     | [#45](https://github.com/evya1/agentic-publishing-pipeline/issues/45) | Produce `results/final.pdf` ≥15 pages from clean checkout              |
| P10-I03     | *(planned — GitHub number TBD)* | Calibrate and validate substantive subject-page budget |

#### Phase 11 — Deterministic ValidatorService ([milestone #10](https://github.com/evya1/agentic-publishing-pipeline/milestone/10))

| Internal ID | Issue | Title (abridged)                                                         |
|-------------|-------|--------------------------------------------------------------------------|
| P11-I01     | [#46](https://github.com/evya1/agentic-publishing-pipeline/issues/46) | `ValidatorService` skeleton (entry point + report writer)              |
| P11-I02     | [#47](https://github.com/evya1/agentic-publishing-pipeline/issues/47) | Required repository file checks                                        |
| P11-I03     | [#48](https://github.com/evya1/agentic-publishing-pipeline/issues/48) | Required LaTeX file checks + FR-17a–d enforcement                      |
| P11-I04     | [#49](https://github.com/evya1/agentic-publishing-pipeline/issues/49) | PDF content indicators                                                 |
| P11-I05     | [#50](https://github.com/evya1/agentic-publishing-pipeline/issues/50) | Every `\cite{...}` resolves; bibliography renders                       |
| P11-I06     | [#51](https://github.com/evya1/agentic-publishing-pipeline/issues/51) | Human-readable validation report                                       |

#### Phase 12 — Tests, lint, and reproducibility ([milestone #11](https://github.com/evya1/agentic-publishing-pipeline/milestone/11))

| Internal ID | Issue | Title (abridged)                                                         |
|-------------|-------|--------------------------------------------------------------------------|
| P12-I01     | [#52](https://github.com/evya1/agentic-publishing-pipeline/issues/52) | Unit tests for provider layer + tools                                  |
| P12-I02     | [#53](https://github.com/evya1/agentic-publishing-pipeline/issues/53) | Tests for Markdown→LaTeX conversion                                    |
| P12-I03     | [#54](https://github.com/evya1/agentic-publishing-pipeline/issues/54) | Tests for `ValidatorService`                                           |
| P12-I04     | [#55](https://github.com/evya1/agentic-publishing-pipeline/issues/55) | `uv run pytest` + `uv run ruff check .` green on clean checkout         |
| P12-I05     | *(planned — GitHub number TBD)* | Harden CI with ≥85% coverage and supported-Python matrix |
| P12-I06     | *(planned — GitHub number TBD)* | Prove genericity through a second-topic integration run |

#### Phase 13 — README, AI usage, and prompt log finalization ([milestone #12](https://github.com/evya1/agentic-publishing-pipeline/milestone/12))

| Internal ID | Issue | Title (abridged)                                                         |
|-------------|-------|--------------------------------------------------------------------------|
| P13-I01     | [#56](https://github.com/evya1/agentic-publishing-pipeline/issues/56) | Refresh `README.md`; reconcile `docs/HW3_REQUIREMENTS.md`              |
| P13-I02     | [#57](https://github.com/evya1/agentic-publishing-pipeline/issues/57) | Fill `docs/AI_USAGE.md` with real run history                          |
| P13-I03     | [#58](https://github.com/evya1/agentic-publishing-pipeline/issues/58) | Fill `docs/PROMPTS.md` with actual prompts verbatim                     |
| P13-I04     | [#59](https://github.com/evya1/agentic-publishing-pipeline/issues/59) | Reconcile `SUBMISSION_CHECKLIST.md` with PRD §14 one-for-one           |
| P13-I05     | *(planned — GitHub number TBD)* | Publish a sanitized self-contained final-run evidence bundle |

#### Phase 14 — Final submission packaging ([milestone #13](https://github.com/evya1/agentic-publishing-pipeline/milestone/13))

| Internal ID | Issue | Title (abridged)                                                         |
|-------------|-------|--------------------------------------------------------------------------|
| P14-I01     | [#60](https://github.com/evya1/agentic-publishing-pipeline/issues/60) | Prepare Moodle wrapper PDF from official template                      |
| P14-I02     | [#61](https://github.com/evya1/agentic-publishing-pipeline/issues/61) | Verify `<GROUP_CODE>-ex03.pdf` filename + each member submits          |
| P14-I03     | [#62](https://github.com/evya1/agentic-publishing-pipeline/issues/62) | Verify every `SUBMISSION_CHECKLIST.md` checkbox individually            |

### Drift-resolution pointer

If a row in the mapping above disagrees with live GitHub state, follow
[`CONTRIBUTING.md`](../CONTRIBUTING.md) §9 (Drift handling):
verified artifacts win, both trackers are reconciled, and the
correction is recorded in an issue comment. Do not silently re-edit
this mapping in place to "explain away" a disagreement.

## A. Already completed scaffold work *(verified on disk)*

- [x] Repository tree, `.gitignore`, `pyproject.toml` (uv-managed, dev
      group only). [Phase 0]
- [x] Placeholder Python package tree at
      `src/agentic_publishing_pipeline/` with the seven subpackages
      `agents/`, `tasks/`, `crews/`, `tools/`, `latex/`, `validation/`,
      `visualization/` (each with `__init__.py` and a README). [Phase 0]
- [x] Placeholder artifact directories: `content/`,
      `content/markdown_drafts/` (transitional), `latex_project/`
      (`chapters/`, `figures/`, `tables/`, `styles/`), `assets/`,
      `results/`, `submission/`. [Phase 0]
- [x] Smoke test `tests/test_scaffold.py` (import-only). [Phase 0]
- [x] Scaffold docs **exist** (not necessarily aligned — see §B):
      `README.md`, `SUBMISSION_CHECKLIST.md`, `CLAUDE.md`, `docs/PRD.md`,
      `docs/HW3_REQUIREMENTS.md`, `docs/AI_USAGE.md`, `docs/PROMPTS.md`,
      and the four mechanism PRDs. [Phase 0]
- [x] Placeholder `latex_project/main.tex` (TODO-only template) and
      empty `latex_project/references.bib`. [Phase 0]

## B. Documentation and planning work *(open)*

These docs **exist** but **require update/review** to match the current
`docs/PRD.md`.

- [x] Reconcile `docs/PRD_crewai_pipeline.md` with `docs/PRD.md` §8.3:
      replace the 5-agent list with the eight agents (Researcher, Outline,
      Writer, Technical-Asset, Hebrew/BiDi, LaTeX, Bibliography,
      Reviewer); reflect FR-8 sequential default; reflect FR-40 / NFR-19
      deterministic validation after the Reviewer Agent. [Phase 1]
      [FR-5, FR-6, FR-8, FR-40, NFR-19, AC §14.5]
      *Done — commit `4e5517c`.*
- [x] Reconcile `docs/PRD_latex_generation.md` with `docs/PRD.md` §8.5:
      lock LuaLaTeX as the required MVP engine; record `David CLM` +
      `Latin Modern Roman` font preferences via `fontspec` + `polyglossia`;
      codify FR-17a–d separation of tables/TikZ into dedicated `.tex`
      files. [Phase 1] [FR-15..FR-20, FR-17a, FR-17b, FR-17c, FR-17d,
      AC §14.3] *Done — commit `4e5517c`.*
- [x] Reconcile `docs/PRD_pdf_validation.md` with `docs/PRD.md` FR-40 /
      NFR-19: validator is **deterministic**, runs after the Reviewer
      Agent, and is **not** an LLM source-of-truth. [Phase 1] [FR-34..FR-40,
      NFR-19, AC §14.5] *Done — commit `4e5517c`.*
- [x] Reconcile `docs/PRD_bibliography_and_citations.md` with
      `docs/PRD.md` §8.6: no fabricated sources; unresolved `\cite{...}`
      must surface as build-time errors. [Phase 1] [FR-33, AC §14.2]
      *Done — commit `4e5517c`.*
- [ ] Refresh `README.md` to point at the canonical Markdown path
      `results/generated_markdown/` (per FR-12 and §12.3), describe the
      8-agent flow, and call out LuaLaTeX + `David CLM` as a
      reproducibility prerequisite. [Phase 1, Phase 13]
- [ ] Refresh `SUBMISSION_CHECKLIST.md` so its bullets match the PRD
      §14 acceptance criteria one-for-one. [Phase 1] [AC §14.*]
- [ ] Decide whether to retire `content/markdown_drafts/` once Phase 6
      begins, or keep it as an alias of `results/generated_markdown/`.
      Record the decision in `docs/PRD_crewai_pipeline.md`. [Phase 1,
      Phase 6] [FR-12]
- [ ] Confirm `docs/HW3_REQUIREMENTS.md` still matches the official
      assignment text and capture any deltas in the PRDs. [Phase 1]

## B.5 Phase 1.5 — Demo topic and source manifest lock *(complete — commit `303a425`; downstream follow-ups tracked below and in §C.5)*

The default demo runtime topic and the arXiv source set were locked in
commit `303a425`. Items marked `[x]` are verified on disk; items
marked `[ ]` are downstream follow-ups owned by Phase 3 / Phase 7 and
do not block the Phase 1.5 lock.

- [x] Add `docs/PRD.md` §22 "Canonical Demo Article Topic" with the
      working title, target angle, scope, source-set summary, and
      manifest pointer; mark the topic as a runtime default
      (NFR-27), not a hardcoded implementation detail. [Phase 1.5]
- [x] Populate `config/article_sources.yaml` with one entry per source
      in the manifest: `citation_key` (provisional, `tbd…` prefix),
      `title`, `year`, `arxiv_id`, `arxiv_url`, `source_archive`,
      `intended_use`, and `verification: {status: unverified, ...}`.
      [Phase 1.5] [FR-19, FR-33]
- [x] Confirm the 10 arXiv archive files live under
      `data/sources/arxiv/source_zips/` locally and are gitignored
      (not staged, not committed). [Phase 1.5]
- [x] Update `data/sources/arxiv/README.md` so it reflects that
      archives are present locally while remaining gitignored.
      [Phase 1.5]
- [x] Confirm `.gitignore` covers `data/sources/arxiv/source_zips/`,
      `data/sources/arxiv/unpacked/`, `data/sources/arxiv/raw_eprint/`,
      `__pycache__/`, `*.pyc`, `.DS_Store`. [Phase 1.5]
- [ ] Populate `authors:` for each entry in
      `config/article_sources.yaml` once authoritative metadata
      (arXiv API or paper PDF metadata) is verified. No fabricated
      authors. [Phase 1.5 → Phase 7] [`docs/PRD_bibliography_and_citations.md`]
- [ ] Rekey provisional `tbd…` citation keys to the
      `authorYYYYkey` convention once authors are verified. Owned by
      the Bibliography Agent in Phase 7.
      [Phase 7] [`docs/PRD_bibliography_and_citations.md` §9]
- [x] Resolve the remaining Phase 3 open questions (audience, depth
      target, BiDi balance, citation density target) and record them
      in `docs/PRD.md` §22.6–§22.9. The synchronized mechanism-PRD
      reconciliation landed via PR #70; P3-I01 (#5) and P3-I02 (#6)
      are closed with evidence; milestone #2 is closed.
      [Phase 3] [PRD §21 open questions]

## C. Future implementation work *(open)*

### C.1 Topic and scope

- [x] Lock the default demo article topic, the working title, and the
      arXiv source set in `docs/PRD.md` §22 and
      `config/article_sources.yaml`. [Phase 1.5]
- [x] Decide audience, depth target, BiDi balance, and citation
      density target per chapter. Decisions recorded in `docs/PRD.md`
      §22.6–§22.9; mechanism-PRD synchronization landed via PR #70;
      P3-I01 (#5) and P3-I02 (#6) closed with evidence; milestone #2
      closed. [Phase 3] [PRD §21 open questions, PRD §22]

### C.2 CrewAI architecture and prompts

- [x] Specify all eight agents from PRD §8.3 with explicit `role`, `goal`,
      `backstory`, and tools. [Phase 4] [FR-5, AC §14.5]
- [x] Define ≥5 tasks with `description`, `expected_output`, `agent`, and
      `context`. At least three tasks must consume earlier task outputs
      via `context`. [Phase 4] [FR-6, KPI, AC §14.5]
- [x] Confirm `Process` is sequential or justify any deviation in
      `docs/PRD_crewai_pipeline.md`. [Phase 4] [FR-8]
- [x] Capture initial prompts (agent `backstory` + `goal`, task
      `description` + `expected_output`, tool prompts) verbatim in
      `docs/PROMPTS.md`. [Phase 4, Phase 13]
- [x] **P4-I04** — Add C4 system-context, container, and component
      views; runtime sequence diagrams (offline-fixture success, live
      success, invalid-output + one bounded repair, repair-exhaustion
      failure, provider/budget rejection, LaTeX compilation failure,
      deterministic validation failure, explicit artifact promotion);
      named, versioned typed artifact contracts for every task edge;
      prompt/config identifier for every agent and task; permitted
      tools, side effects, and run-relative artifact roots; one
      bounded repair attempt policy; deterministic rendering /
      file-authority boundary; run lifecycle, isolated workspace,
      configuration snapshot, structured event log, usage/cost log,
      artifact manifest, and explicit promotion; operational modes
      (`dry-run`, `offline-fixture`, `live`, `compile-only`,
      `validate-only`, `--topic`/`--manifest` override, `resume`);
      machine-readable, versioned prompt/config registry distinct
      from `docs/PROMPTS.md`; and initial ADRs ADR-0001 through
      ADR-0007. Documentation-only; no runtime source code.
      [Phase 4] [FR-41..FR-49, NFR-33, NFR-34]
      *Merged, verified, and closed with evidence before Phase 5.*

### C.3 Provider/service layer, configuration, and tools *(Phase 5 complete and closed through PR #79)*

P5-I01 through P5-I13 are merged through PR #79, verified, and closed with
evidence. The Phase 5 milestone is closed; Phase 6 is complete and Phase 7
is next.

- [x] Implement a controlled provider/service layer for model and search
      calls. [Phase 5] [NFR-23, NFR-24]
      *Merged through PR #79 — `src/agentic_publishing_pipeline/providers/`
      ships the typed facade, fixture adapters, and env-driven
      `ProviderConfig`.*
- [x] Add `.env-example` documenting required environment variables.
      [Phase 5] [FR-4, NFR-21]
      *Done — see `.env.example` at repo root.*
- [x] Load all secrets from `.env` only; never hardcode. [Phase 5]
      [FR-3, NFR-20]
      *Done — provider config reads exclusively from env; run snapshots
      store only allowlisted settings and credential-presence markers
      (P5-I10).*
- [x] Track a reproducible `uv.lock` baseline and codify the per-tool,
      no-speculative-install dependency policy. Heavy SDKs (`crewai`,
      model/search SDKs, `matplotlib` where applicable) are added by
      the issue that consumes them, not preemptively. [Phase 5]
      *Merged through PR #79 — `uv.lock` is tracked and
      `CONTRIBUTING.md §11.5` is the binding rule.*
- [x] Implement agent tools under
      `src/agentic_publishing_pipeline/tools/`:
  - [x] Search tool for configured-source metadata verification; automatic
        source discovery is deferred beyond the MVP. [Phase 5, Phase 7]
        [FR-5]
        *Merged through PR #79 — `tools/search.py` reads
        `config/article_sources.yaml`, exposes `SearchHit`s through
        the `FixtureSearchAdapter`, and surfaces `verify_arxiv_id`
        + `manifest_coverage` helpers for the Bibliography Agent.*
  - [x] File I/O tool. [Phase 5]
        *Merged through PR #79 — `tools/fileio.FileIO` provides
        atomic writes, path-traversal refusal, and a `fileio.wrote`
        audit event into the run-context event log.*
  - [x] Markdown conversion tool (used by the Markdown→LaTeX path).
        [Phase 5, Phase 9]
        *Merged through PR #79 — `tools/markdown.py` provides
        deterministic placeholder parsing
        (`parse_placeholders`/`strip_placeholders`/`has_placeholder`)
        and LaTeX special-character escaping. Phase 9 reuses the
        same seam.*
  - [x] LaTeX compilation tool (LuaLaTeX + biber multi-pass). [Phase 5,
        Phase 10] [FR-20]
        *Merged through PR #79 — `tools/latex_build.build_pdf`
        runs the deterministic 4-pass sequence
        (lualatex → biber → lualatex → lualatex) with fixed args,
        timeouts, captured & parsed build log, and returns a
        `BuildResult v1`. Refuses on missing binaries unless an
        injected runner is supplied.*
  - [x] Graph generation tool. [Phase 5, Phase 8] [FR-29, FR-30]
        *Merged through PR #79 — `visualization/graph.render_line_plot`
        and `render_python_graph_asset` use Matplotlib (Agg
        backend, no GUI). Outputs land under
        `latex_project/figures/` through the FileIO tool, audited,
        and emit a JSON provenance file next to each PNG.*
- [x] **P5-I08** — Implement versioned Pydantic artifact contracts
      (ResearchNotes, Outline, ChapterDrafts, AssetSpecs, BiDiSection,
      BibliographyBundle, LaTeXProjectSpec, ReviewerSignal, BuildResult,
      ValidationReport, PromotionRecord) and bounded validation repair
      (≤1 attempt). No stage may consume unvalidated raw LLM output.
      [Phase 5] [FR-41, FR-42, NFR-19, ADR-0002]
      *Merged through PR #79 — `src/agentic_publishing_pipeline/contracts/`
      ships the E1..E12
      models with a single `parse_with_repair` helper; pydantic added
      to runtime deps.*
- [x] **P5-I09** — Implement API Gatekeeper: budgets, retries,
      timeouts, retry classification, structured usage/cost events
      carrying `run_id`, `agent_id`, `task_id`, `attempt`, model,
      tokens, latency, status, estimated cost. Provider facade
      separate from policy. [Phase 5] [FR-44, NFR-23, NFR-24, ADR-0004]
      *Merged through PR #79 — `tools/gatekeeper.py` (policy) +
      `tools/_gatekeeper_policy.py` (budget/identity/cost helpers).
      Offline-fixture mode emits cost=0 usage events through the
      same Gatekeeper path as live.*
- [x] **P5-I10** — Introduce `PipelineRunContext`: unique run ID,
      isolated workspace under `results/<run_id>/`, configuration
      snapshot, structured event log, usage/cost log, artifact
      manifest, safe path resolution, explicit promote/publish
      operations. Failed runs preserved or removed only by explicit
      cleanup. Canonical artifacts never silently overwritten.
      [Phase 5] [FR-45, FR-48, NFR-16, NFR-17, ADR-0005]
      *Merged through PR #79 — `src/agentic_publishing_pipeline/runtime/`
      ships the workspace,
      manifest, logs, and explicit promotion path.*
- [x] **P5-I11** — Add CLI operational modes (`dry-run`,
      `offline-fixture`, `live`, `compile-only`, `validate-only`,
      `--topic`/`--manifest` override, `resume`) and deterministic
      offline fixtures. Offline mode requires no API keys and makes
      no network or paid-provider calls. Includes deterministic
      fixtures and integration tests. [Phase 5] [FR-46]
      *Merged through PR #79, verified, and closed with evidence.*
- [x] **P5-I12** — Implement machine-readable, versioned prompt/config
      registry under `config/prompt_registry/`; validate schema/version
      compatibility at startup; refuse to start on mismatch. Preserve
      `docs/PROMPTS.md` as the human evidence ledger. Link recorded
      runs to exact registry versions. [Phase 5] [FR-47]
      *Merged through PR #79 — registry YAML tree under
      `config/prompt_registry/` + loader and `verify_compatibility`
      in `runtime/registry.py`; pyyaml added to runtime deps.*
- [x] **P5-I13** — Add baseline CI for PR/main: frozen dependency
      sync, Ruff, tests, current coverage gate, automated 150-line
      cap, deterministic offline smoke run. Do not introduce a
      Python-version matrix here (deferred to P12-I05). [Phase 5,
      Phase 12]
      *Merged through PR #79, verified, and closed with evidence.*

### C.4 Markdown-first content pipeline

- [x] Generate Markdown drafts at `results/generated_markdown/`. [Phase 6]
      [FR-11, FR-12, §12.3]
- [x] Markdown drafts include headings, figure placeholders, table
      placeholders, equation placeholders, and citation placeholders.
      [Phase 6] [FR-13]
- [x] Run the human review gate before any LaTeX conversion. [Phase 6]
      [FR-14, NFR-19]
- [x] Record the run in `docs/AI_USAGE.md`. [Phase 6, Phase 13]
      *Merged through PR #81, verified on `main`, and closed with evidence.*

### C.5 Real-source and bibliography pipeline

- [ ] Define the source-collection policy and the verification procedure.
      [Phase 7] [`docs/PRD_bibliography_and_citations.md` §7]
      *P7-I00 (issue #21):* policy text fixed in
      `docs/PRD_bibliography_and_citations.md` §7.1, §7.3, §13.1 and
      mirrored in `docs/SOURCES.md`. Box stays unchecked until the
      Phase 7 PR is merged and post-merge evidence is recorded
      (`docs/TODO.md` §F-6).
- [ ] Consume `config/article_sources.yaml` from the Research Agent (T1)
      and the Bibliography Agent (T6) per
      `docs/PRD_crewai_pipeline.md` §6. [Phase 6, Phase 7]
- [ ] Verify each manifest entry: URL/DOI resolution, title/author/year
      cross-check, archive-file presence under
      `data/sources/arxiv/source_zips/`. Update
      `config/article_sources.yaml` `verification.status` to
      `verified` (or `rejected`) and record `verified_at` /
      `verified_by`. [Phase 7] [`docs/PRD_bibliography_and_citations.md` §7]
- [ ] Record the per-source audit trail (citation key → archive →
      verification method → timestamp / run id) in `docs/AI_USAGE.md`
      (or `docs/SOURCES.md` if that location is chosen).
      [Phase 7] [`docs/PRD_bibliography_and_citations.md` §8]
- [ ] Extract `.bib` entries from the verified arXiv sources into
      `latex_project/references.bib` (stable keys, no fabricated
      entries). [Phase 7] [FR-19, FR-33]
- [ ] Rekey provisional `tbd…` citation keys in
      `config/article_sources.yaml` and in any Markdown placeholders to
      the final `authorYYYYkey` convention. [Phase 7]
      [`docs/PRD_bibliography_and_citations.md` §9]
- [ ] Wire `\cite{...}` placeholders in Markdown drafts and resolve them
      into the LaTeX project so every citation links to a real `.bib`
      entry. [Phase 7, Phase 9] [FR-33, AC §14.2]
- [ ] Treat all archive contents under
      `data/sources/arxiv/source_zips/` and
      `data/sources/arxiv/unpacked/` as **untrusted external source
      material**: no LaTeX builds run from third-party archives, no
      code from archives is executed, and unpacked content is only
      read for metadata / citation extraction. [Phase 7] [security]

### C.6 Python graph generation pipeline

- [ ] Implement `src/agentic_publishing_pipeline/visualization/` and
      produce at least one graph image saved under
      `latex_project/figures/`, consumed by a chapter via
      `\includegraphics`. [Phase 8] [FR-29, FR-30, AC §14.2]
- [ ] **P8-I02** — Define typed graph/table/TikZ/image specs,
      deterministic renderers, provenance metadata, path safety, and
      explicit failure/fallback behavior that cannot silently change
      factual content. Ties to ADR-0002 and ADR-0003. [Phase 8]

### C.7 LaTeX project assembly (LuaLaTeX MVP)

- [ ] Replace the placeholder `latex_project/main.tex` with a thin root
      that only `\input{}`s other files. [Phase 9] [FR-16]
- [ ] Create `preamble.tex` configured for LuaLaTeX with `fontspec` +
      `polyglossia`, `\setmainfont{Latin Modern Roman}`,
      `\newfontfamily\hebrewfont[Script=Hebrew]{David CLM}`. [Phase 9]
      [FR-20, §16.3]
- [ ] Create `macros.tex` with reusable math/notation commands.
      [Phase 9] [FR-18]
- [ ] Generate chapter files under `chapters/` — narrative text only.
      [Phase 9] [FR-23, NFR-6a]
- [ ] Put each substantial table in its own file under `tables/` and each
      TikZ figure in its own file under `figures/`; include them from
      chapters with `\input{...}`. [Phase 9] [FR-17a..FR-17d, AC §14.3]
- [ ] Include at least one image in the PDF. [Phase 9] [FR-28]
- [ ] Include at least one table (own `.tex` file, wrapped in a `table`
      environment with a caption). [Phase 9] [FR-31]
- [ ] Include at least one mathematical equation with a label, and
      reference it later with `\ref` / `\eqref`. [Phase 9] [FR-25, FR-32,
      AC §14.2]
- [ ] Include at least one theorem-like environment (`definition`,
      `theorem`, `lemma`, or `example`). [Phase 9] [FR-24, AC §14.2]
- [ ] Include at least one TikZ figure (e.g., simple automaton).
      [Phase 9] [AC §14.2]
- [ ] Configure headers and footers (e.g., `fancyhdr`). [Phase 9]
      [FR-21]
- [ ] Build a real cover/title page with topic, author/team, course, and
      date. [Phase 9] [FR-22, AC §14.2]
- [ ] Generate the table of contents. [Phase 9] [FR-22]
- [ ] Add a nomenclature section with at least two symbols. [Phase 9]
      [FR-26, AC §14.2]
- [ ] Add an index with at least one Hebrew term and one English term.
      [Phase 9] [FR-27, AC §14.2]
- [ ] Include at least one substantial Hebrew/English BiDi section with
      correct RTL alignment, embedded English technical terms, and
      readable Hebrew. [Phase 9] [§8.6, AC §14.4, NFR-28..NFR-31]

### C.8 PDF build

- [ ] Document and script the multi-pass build (LuaLaTeX → biber →
      LuaLaTeX → LuaLaTeX, plus `makeindex` /
      `makenomenclature` as needed). [Phase 10] [FR-20, §16.3]
- [ ] Produce `results/final.pdf` (≥15 pages). [Phase 10] [FR-38, KPI,
      AC §14.2]
- [ ] **P10-I03** — Define front/back-matter exclusions, report total
      and substantive page counts separately, calibrate the canonical
      article to satisfy the assignment, and add deterministic page
      checks in the ValidatorService. [Phase 10, Phase 11] [FR-49]

## D. Future validation and submission work *(open)*

### D.1 Deterministic ValidatorService

- [ ] Implement `src/agentic_publishing_pipeline/validation/` as a
      deterministic `ValidatorService` that runs **after** the Reviewer
      Agent. The LLM must not be the source of truth. [Phase 11]
      [FR-40, NFR-19]
- [ ] Validate required repository files. [Phase 11] [FR-34, AC §14.1]
- [ ] Validate required LaTeX files (`main.tex`, `preamble.tex`,
      `macros.tex`, `references.bib`, chapters, `tables/`, `figures/`).
      [Phase 11] [FR-35, AC §14.3]
- [ ] Validate PDF content indicators where feasible: page count,
      bibliography presence, BiDi section presence, nomenclature, index,
      equation cross-reference, image/graph/table presence. [Phase 11]
      [FR-36, AC §14.2, AC §14.4]
- [ ] Validate every `\cite{...}` resolves to a `references.bib` entry,
      and that bibliography renders. [Phase 11] [FR-33, AC §14.2]
- [ ] Produce a human-readable validation report after the run.
      [Phase 11] [FR-37]

### D.2 Tests, lint, reproducibility

- [ ] Real unit tests for the provider layer and each tool. [Phase 12]
- [ ] Tests for `ValidatorService`. [Phase 12]
- [ ] Tests for the Markdown→LaTeX conversion. [Phase 12]
- [ ] `uv run pytest` passes on a clean checkout. [Phase 12]
- [ ] `uv run ruff check .` passes on a clean checkout. [Phase 12]
- [ ] README documents the LaTeX-distribution requirement (LuaLaTeX) and
      the `David CLM` Hebrew font requirement so reproduction is
      possible. [Phase 12, Phase 13]
- [ ] **P12-I05** — Raise/enforce coverage to at least 85%, test the
      supported Python-version matrix, preserve frozen dependency
      installation, line-cap enforcement, and offline integration.
      [Phase 12]
- [ ] **P12-I06** — Run the same pipeline with a second topic and a
      different verified manifest without source-code changes. Verify
      no canonical paper IDs, chapter names, or prompt assumptions are
      hardcoded. [Phase 12] [NFR-34, ADR-0006]

### D.3 Documentation finalization

- [ ] Update `README.md` to describe the running system: installation,
      configuration, the 8-agent flow, run commands, LaTeX build
      commands, and limitations. [Phase 13] [AC §14.1]
- [ ] Fill `docs/AI_USAGE.md` with the real run history (model, prompts
      summary, outputs, human verification, cost). [Phase 13]
- [ ] Fill `docs/PROMPTS.md` with the actual prompts used in the run.
      [Phase 13]
- [ ] **P13-I05** — Publish a sanitized, self-contained final-run
      evidence bundle: selected run ID, configuration snapshot,
      prompt/config registry version, source manifest, artifact
      manifest, validation report, build log summary, usage/cost
      report, screenshots, and final PDF/LaTeX references. Verify no
      secrets, no local-only archives, no private paths, no external
      repository references or attribution. [Phase 13] [NFR-33]

### D.4 Final submission packaging

- [ ] Prepare the Moodle wrapper PDF from the official template.
      [Phase 14]
- [ ] Verify the `<GROUP_CODE>-ex03.pdf` filename convention.
      [Phase 14]
- [ ] Confirm each group member submits separately in Moodle.
      [Phase 14]
- [ ] Verify every checkbox in `SUBMISSION_CHECKLIST.md` is satisfied
      individually. [Phase 14] [AC §14.*]

## E. Cross-cutting policies *(always apply, not phase-gated)*

- [ ] Every AI/LLM call is recorded in `docs/AI_USAGE.md` as it happens.
      [Phase 6, Phase 13]
- [ ] Every prompt is recorded verbatim in `docs/PROMPTS.md`.
      [Phase 4, Phase 13]
- [ ] No secrets committed; `.env` only. [Phase 5] [NFR-20, NFR-21]
- [ ] Python files stay ≤150 lines; long files are split by
      responsibility. [NFR-2]
- [ ] All functions have type hints including return types. [NFR-7]
- [ ] Inputs validated explicitly (e.g., `assert`). [NFR-13]
- [ ] DRY and minimal classes/moving parts; extract small named helpers
      instead of long inline blocks. [NFR-5, NFR-6, NFR-12]
- [ ] f-strings for interpolation; comprehensions only where they
      improve readability. [NFR-9, NFR-10]

## F. GitHub project management *(Phase 2 — complete and closed; milestone #1 closed)*

The local Markdown plan is mirrored into GitHub as the GUI tracking
layer. The discrete Phase 2 work (`P2-I00` … `P2-I03`) created the
milestones, the issues, the label vocabulary, the contribution
workflow, and the mapping back into this file. `P2-I04` (#68) was the
final Phase 2 reconciliation step; it recorded the verified closure
state in `docs/PLAN.md` and this file, was merged via PR #69, and is
closed with evidence. The Phase 2 milestone (milestone #1) is closed.
The items below are ticked once the underlying GitHub or repository
artifact is demonstrably present; closing the corresponding **issue**
still requires evidence per §F-6.

- [x] Create one **GitHub Milestone** per open phase in `docs/PLAN.md`
      (Phases 2 through 14). Milestone titles match phase titles. Phases 0,
      1, and 1.5 do not get milestones because they are already complete.
      [Phase 2] — verified: 13 milestones exist (`gh api
      repos/evya1/agentic-publishing-pipeline/milestones`). Owned by
      **P2-I01** (#2).
- [x] Create **GitHub Issues** from every open item in §B, §C, §D, and
      §E above. Preserve the TODO wording in the issue title so the
      mapping back to this file is obvious. [Phase 2] — verified: 62
      issues (#1–#62) exist with TODO wording in titles. Owned by
      **P2-I02** (#3).
- [x] Assign each issue to the milestone for its phase tag (e.g.,
      `[Phase 9]` items go to the "Phase 9 — LaTeX project assembly"
      milestone). [Phase 2] — verified: every issue carries its
      expected milestone. Owned by **P2-I02** (#3).
- [x] Apply labels from this fixed vocabulary as appropriate:
      `docs`, `architecture`, `crewai`, `latex`, `validation`, `bidi`,
      `bibliography`, `submission`, plus `testing`, `decision`, and
      `security` added during P2-I02 (canonical vocabulary now lives in
      [`CONTRIBUTING.md`](../CONTRIBUTING.md) §11). [Phase 2] — verified:
      11 custom labels present. Owned by **P2-I02** (#3).
- [x] Document the mapping TODO ↔ issue ↔ milestone ↔ PRD requirement
      in this file's introduction once the issues are filed. [Phase 2]
      — verified: see the **Traceability** section near the top of this
      file. Owned by **P2-I03** (#4), closed with evidence.
- [x] An issue may be closed **only** when the underlying artifact is
      verified on disk (or by a passing build, test, or validator run).
      Closing an issue does **not** by itself allow ticking a TODO box,
      a PRD acceptance-criterion checkbox in `docs/PRD.md` §14, a
      `docs/HW3_REQUIREMENTS.md` checkbox, or a `SUBMISSION_CHECKLIST.md`
      checkbox. [Phase 2, all later phases] — codified as the §F-6
      closure rule in the Traceability section above and in
      [`CONTRIBUTING.md`](../CONTRIBUTING.md) §6. Owned by **P2-I03**
      (#4); the rule remains in force for every later phase.
