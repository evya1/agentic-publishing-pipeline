# PLAN — agentic-publishing-pipeline

> **Status:** Phases 0, 1, 1.5, 2, 3, 4, 5, 6, 7, and 8 are complete and
> closed. Phase 6 corrective recovery is complete through PR #96; P6-I04
> and P6-I05 are closed with evidence. Phase 7 landed through PR #83,
> verifying the canonical source manifest and generating
> `latex_project/references.bib`. Phase 8 landed through PR #92, delivering
> the deterministic Python graph pipeline and committing a canonical PNG
> artifact to `latex_project/figures/`. Phase 9 assembly proceeds once the
> maintainer approves the review packet produced by PR #96. Phases 9-14
> remain open.

## How PRD, PLAN, TODO, and GitHub fit together

These artifacts have distinct, non-overlapping roles. Keep them in sync, do
not duplicate content:

| Artifact | Role |
|---|---|
| [`docs/PRD.md`](PRD.md) | Source of truth for **requirements** (FRs, NFRs, acceptance criteria). |
| [`docs/PLAN.md`](PLAN.md) (this file) | **Phased roadmap / milestones** from scaffold to submission. |
| [`docs/TODO.md`](TODO.md) | **Concrete task backlog** with checkable items, each traceable to a PRD requirement. |
| GitHub **Milestones** | GUI mirror of PLAN phases. Created later (see Phase 2). |
| GitHub **Issues** | GUI mirror of TODO items. Created later (see Phase 2). |
| [`CLAUDE.md`](../CLAUDE.md) | Repository conventions for AI assistants. Aligned with `docs/PRD.md`. |
| HW3 mechanism PRDs (`docs/PRD_*.md`) | Per-mechanism refinements of `docs/PRD.md`. Currently scaffold-level placeholders — see Phase 1. |

GitHub Milestones/Issues are a GUI representation of this plan and TODO; they
are **not** a replacement for these documents. The Markdown files remain
authoritative.

### Phase ↔ Milestone synchronization rules

These rules are the PLAN-side of the Project Tracking Synchronization
Contract documented in full in [`CONTRIBUTING.md`](../CONTRIBUTING.md) §8.

- **One PLAN phase ↔ one GitHub Milestone.** Each open phase has a
  milestone named `Phase <N> — <title>` mirroring the phase heading in
  this file. Completed phases (Phase 0, 1, 1.5) intentionally do not
  have milestones — completion is captured here, not in GitHub.
- **Phase status changes here.** Status text in this file (`*(open)*`,
  `*(partially resolved …)*`, `*(complete — commit <sha>)*`) is the
  authoritative phase status. Closing a GitHub Milestone does **not**
  by itself permit changing phase status here.
- **Milestone closure rule.** A milestone may be closed only after:
  every issue in it has been verified per `docs/TODO.md` §F-6; every
  TODO item in the phase is satisfied on disk; the phase's exit
  criterion in this file is met; required PRD acceptance criteria
  (`docs/PRD.md` §14) are met; tests, builds, and validators relevant
  to the phase pass. Then mark the phase complete here **and** close
  the milestone in the same reconciliation step.
- **Moving work between milestones.** If scope must move between
  phases, edit `docs/TODO.md` to relocate the item, update its issue's
  milestone, and record the reason in the issue comments. A single PR
  should carry both edits. Do not relocate scope only on the GitHub
  side.
- **New phases or renamed phases.** Adding a new phase or renaming an
  existing one is a PRD/PLAN change. Update this file first via PR,
  then create or rename the milestone to match. The reverse order is
  not allowed.
- **Supersession of PRD §19.** `docs/PRD.md` §19 ("Proposed Milestones"
  M1–M9) is **superseded by** this file's Phase 0–14 model and the
  corresponding milestones. Treat PRD §19 as historical context only.

## Canonical paths

`docs/PRD.md` §12.3, §13, and FR-12 designate
**`results/generated_markdown/`** as the canonical location for Markdown
drafts. The scaffold currently also has `content/markdown_drafts/` for
historical reasons; treat that as a transitional placeholder that will either
be removed or aliased once the Markdown pipeline is implemented. New planning
text in this repo should use `results/generated_markdown/`.

## Phases

The phases below are ordered. Each phase has an explicit exit criterion. Do
**not** mark a phase complete until its exit criterion is *verifiably* met by
artifacts on disk and (where relevant) by a passing build, test, or
validator run. Detailed task checklists live in [`docs/TODO.md`](TODO.md),
not here.

### Phase 0 — Scaffold setup *(complete)*

Only items below were verified on disk and are marked complete. Everything
beyond Phase 0 is open.

- Repository tree, `.gitignore`, `pyproject.toml` (uv-managed, dev group
  only — no `crewai` / LLM / search SDKs yet by design).
- Placeholder package tree under `src/agentic_publishing_pipeline/`
  (`agents/`, `tasks/`, `crews/`, `tools/`, `latex/`, `validation/`,
  `visualization/`), each with `__init__.py` and a README.
- Placeholder artifact directories: `content/`, `latex_project/`
  (`chapters/`, `figures/`, `tables/`, `styles/`), `assets/`, `results/`,
  `submission/`.
- Smoke test at `tests/test_scaffold.py` (imports only; no behavioural
  coverage).
- Top-level docs that **exist** as scaffolds: `README.md`,
  `SUBMISSION_CHECKLIST.md`, `CLAUDE.md`, `docs/PRD.md` (expanded),
  `docs/HW3_REQUIREMENTS.md`, `docs/AI_USAGE.md`, `docs/PROMPTS.md`,
  the four mechanism PRDs (`PRD_crewai_pipeline.md`,
  `PRD_latex_generation.md`, `PRD_bibliography_and_citations.md`,
  `PRD_pdf_validation.md`).

**Exit criterion (met):** `uv sync` succeeds, `uv run pytest` passes the
smoke suite, `uv run ruff check .` is clean. Note that scaffold "complete"
means *the scaffold itself* is complete, not that any HW3 requirement is
satisfied.

### Phase 1 — Documentation alignment *(mechanism PRDs complete; README / SUBMISSION_CHECKLIST refresh deferred to Phase 13)*

Reconcile the four mechanism PRDs and supporting docs with the current
`docs/PRD.md`. They previously described a 5-agent flow
(`PRD_crewai_pipeline.md`), did not lock LuaLaTeX as the default
(`PRD_latex_generation.md`), and did not codify FR-40 / NFR-19's
deterministic `ValidatorService` (`PRD_pdf_validation.md`). The mechanism
PRDs were rewritten in commit `4e5517c` and now reflect the eight-agent
flow, LuaLaTeX-as-MVP, the deterministic `ValidatorService`, the
Markdown-first canonical path, and the FR-17a–d separation rules.

The `README.md` and `SUBMISSION_CHECKLIST.md` refresh that the original
exit criterion called for is **carried forward into Phase 13** (README,
AI-usage, and prompt-log finalization), where it is already tracked by
the existing items in `docs/TODO.md` §B.

**Exit criterion (met for mechanism PRDs):** every mechanism PRD
references the same agent list, engine choice, separation-of-
responsibilities rules, validation policy, and acceptance criteria as
`docs/PRD.md`. `README.md` and `SUBMISSION_CHECKLIST.md` refresh is
explicitly deferred to Phase 13 and remains tracked in TODO.

### Phase 1.5 — Demo article topic and source manifest lock *(complete — commit `303a425`)*

Lock the default demo runtime topic, the source set, and the local-only
archive layout so the Research Agent (Phase 6) and the Bibliography
Agent (Phase 7) have a fixed input to consume. This is **not** topic
implementation work — it is the documentation / configuration step that
records what the default run targets.

Locked artifacts (this phase):

- `docs/PRD.md` §22 ("Canonical Demo Article Topic") records the
  working title, target angle, article scope, source-set summary, and
  the location of the tracked manifest. The PRD section explicitly
  marks the topic as a **runtime default**, not a hardcoded
  implementation detail (NFR-27).
- `config/article_sources.yaml` contains one entry per source in the
  manifest, with `citation_key` (provisional, `tbd…` prefix until
  Phase 7 verification), `title`, `year`, `arxiv_id`, `arxiv_url`,
  `source_archive`, `intended_use`, and a `verification` block whose
  initial status is `unverified`. Author metadata is `[]` where it is
  not yet authoritatively known; populating it is tracked in TODO.
- `data/sources/arxiv/source_zips/` contains the 10 downloaded arXiv
  LaTeX source archives, locally only. These bytes are gitignored and
  **must not be committed**.
- `data/sources/arxiv/README.md` documents the layout and reflects
  that archives are now present locally while remaining gitignored.
- `.gitignore` continues to cover `data/sources/arxiv/source_zips/`,
  `data/sources/arxiv/unpacked/`, and `data/sources/arxiv/raw_eprint/`.

What this phase does **not** do:

- It does not run any LaTeX build from the third-party archives.
- It does not execute anything inside the archives.
- It does not verify the sources (URL/DOI checks happen in Phase 7).
- It does not perform research synthesis or write any article content.
- It does not finalize citation keys; `tbd…` provisional keys are
  rekeyed during Phase 7 once authors are confirmed.

**Exit criterion:** `docs/PRD.md` §22 exists,
`config/article_sources.yaml` lists the 10 sources with provisional
citation keys and `verification.status: unverified`,
`data/sources/arxiv/source_zips/` contains the archives locally
(gitignored and not staged), `data/sources/arxiv/README.md` no longer
claims the directory is empty, and `docs/TODO.md` tracks the follow-up
work for author metadata, URL/DOI verification, audit trail, and
bibliography extraction.

### Phase 2 — Project management setup *(complete and closed — P2-I04 reconciled via PR #69; milestone #1 closed)*

Set up GitHub as the GUI tracking layer for this plan and TODO, and
establish the contribution / synchronization / handoff governance that
every later phase will rely on.

Verified state:

- **P2-I00 (#1) — Apply minimal doc patches before milestone/issue
  creation.** Closed with evidence. Landed on `main` as commit
  `2b0baeb`.
- **P2-I01 (#2) — Create 13 GitHub Milestones (Phases 2–14).**
  Closed with evidence. Verified via `gh api repos/.../milestones`;
  one milestone per still-open phase; titles match phase titles. Phase
  0, Phase 1, and Phase 1.5 intentionally have no milestone.
- **P2-I02 (#3) — Create GitHub Issues from open TODO items and apply
  labels.** Closed with evidence. Verified: 62 issues (#1–#62) carry
  TODO wording in titles, correct milestones, and labels from the
  11-entry vocabulary now codified in
  [`CONTRIBUTING.md`](../CONTRIBUTING.md) §11 (`docs`, `architecture`,
  `crewai`, `latex`, `validation`, `bidi`, `bibliography`, `testing`,
  `submission`, `decision`, `security`).
- **P2-I03 (#4) — Document the mapping in TODO intro and establish
  the contribution workflow.** Closed with evidence. Adds the
  Traceability section to `docs/TODO.md`, `CONTRIBUTING.md`, AI-agent
  rules in `CLAUDE.md`, a contributing section in `README.md`, the
  Phase ↔ Milestone rules above, `.github/pull_request_template.md`,
  and `.github/ISSUE_TEMPLATE/work_item.md` + `config.yml`.
- **P2-I04 (#68) — Reconcile verified Phase 2 completion in PLAN and
  TODO.** Closed with evidence after PR #69 merged. Milestone #1 was
  closed in the same reconciliation step.

**Exit criterion (verified complete and milestone closed):** milestones
for every still-open phase exist; every open TODO item has a tracking
issue with the right labels; the mapping TODO ↔ issue ↔ milestone ↔
PRD requirement is documented in `docs/TODO.md`'s introduction
(Traceability section); P2-I00 through P2-I04 are independently
verified and closed with evidence; the Phase 2 milestone is closed.

### Phase 3 — Topic and scope *(complete and closed — P3-I01/P3-I02 reconciled via PR #70; milestone #2 closed)*

Phase 1.5 locks the **default demo topic** in `docs/PRD.md` §22 and the
source set in `config/article_sources.yaml`. Phase 3 resolves the
remaining open questions from PRD §21 and records them in
`docs/PRD.md` §22.6–§22.9:

- **Audience (§22.6).** Practitioner-facing technical reader.
  Assumes ML/LLM basics; targets engineers and researchers.
- **Depth target (§22.7).** Survey-style across all five reasoning
  dimensions (planning, memory, retrieval, tool use, multimodal).
  Each dimension gets ~2–3 pages; total 15–20 pages.
- **BiDi balance (§22.8).** Mostly English with one Hebrew/English
  BiDi section placed in the Memory dimension chapter.
- **Citation density (§22.9).** Canonical HW3 target of approximately
  2–3 verified sources per chapter; all 10 canonical manifest sources
  cited at least once across that demonstration article.

Reconciliation for P3-I01 (#5) and P3-I02 (#6) clarified the generic
configurable product contract versus the canonical HW3 demonstration
run and synchronized the mechanism PRDs that depend on these
decisions. PR #70 merged the reconciliation on `main`
(`91ae128`); both issues are closed with evidence; milestone #2 is
closed.

**Exit criterion (verified complete and milestone closed):** all four
decisions are recorded in `docs/PRD.md` §22.6–§22.9 and reflected in
the mechanism PRDs whose behavior depends on them; P3-I01 and P3-I02
are closed with evidence; the Phase 3 milestone is closed.

### Phase 4 — CrewAI architecture design *(complete and closed — P4-I04 reconciled before Phase 5; milestone #3 closed)*

Phase 4 originally captured the **eight** agents from `docs/PRD.md` §8.3
— Researcher, Outline, Writer, Technical-Asset, Hebrew/BiDi, LaTeX,
Bibliography, Reviewer — with explicit `role`, `goal`, `backstory`, and
tool list each (P4-I01 / #7, closed), defined the eight-task graph with
sequential `Process` (P4-I02 / #8, closed), and captured initial
verbatim prompts in `docs/PROMPTS.md` (P4-I03 / #9, closed).

P4-I04 extended Phase 4 with the additional runtime architecture
contracts required before Phase 5 could begin:

- C4 system-context, container, and component views;
- runtime sequence diagrams (offline-fixture success, live success,
  invalid-output + one bounded repair, repair-exhaustion failure,
  provider/budget rejection, LaTeX compilation failure, deterministic
  validation failure, explicit artifact promotion);
- named, versioned typed artifact contracts for every task edge;
- prompt/config identifier for every agent and task;
- permitted tools, side effects, and run-relative artifact roots;
- one bounded repair attempt policy;
- deterministic rendering / file-authority boundary;
- run lifecycle, isolated workspace, configuration snapshot,
  structured event log, usage/cost log, artifact manifest, and
  explicit promotion;
- operational modes (`dry-run`, `offline-fixture`, `live`,
  `compile-only`, `validate-only`, `--topic`/`--manifest` override,
  `resume`);
- machine-readable, versioned prompt/config registry distinct from
  `docs/PROMPTS.md` (preserved as the human evidence ledger);
- initial ADRs ADR-0001 through ADR-0007.

Deliverable tree:

- `docs/architecture/c4_views.md`
- `docs/architecture/runtime_sequences.md`
- `docs/architecture/artifact_contracts.md`
- `docs/architecture/run_lifecycle.md`
- `docs/architecture/prompt_config_registry.md`
- `docs/architecture/adrs/ADR-0001..ADR-0007*.md`

**Exit criterion (verified complete and milestone closed):**

1. Original P4-I01, P4-I02, and P4-I03 closure evidence is preserved
   (`docs/PRD_crewai_pipeline.md`, `docs/PROMPTS.md`).
2. P4-I04 landed the architecture documents listed above; PRDs, PLAN,
   and TODO agreed.
3. The amendment introduced no runtime source code.
4. The Phase 4 milestone was closed after the P4-I04 PR was merged,
   post-merge verified on `main`, P4-I04 was closed with evidence, and
   no other Phase 4 work remained.

### Phase 5 — Provider/service layer and tools *(complete and closed — PR #79; milestone #4 closed)*

Phase 5 implemented the controlled provider/service layer (NFR-23) so model
and search calls route through one place. It added `.env-example` (FR-4),
loads secrets exclusively via environment (FR-3), and implements the Phase 5
tool seams: search, file I/O, Markdown conversion, LaTeX compilation, and
graph generation. Real dependencies enter `pyproject.toml` only as each tool
is implemented — `uv add` per package, no speculative installs.

Phase 5 also implements the runtime foundations designed under P4-I04,
in this dependency order (see [`docs/architecture/`](architecture/)):

- **P5-I08** — typed Pydantic artifact contracts (E1..E12) with
  one bounded repair attempt (ADR-0002, FR-41, FR-42).
- **P5-I10** — `PipelineRunContext`, isolated workspace, configuration
  snapshot, event log, usage log, artifact manifest, explicit
  promotion (ADR-0005, FR-45, FR-48).
- **P5-I12** — machine-readable, versioned prompt/config registry with
  startup compatibility check (FR-47), preserving `docs/PROMPTS.md` as
  the human evidence ledger.
- **provider facade** — typed normalized model/search responses,
  separated from policy (existing P5-I01 / #10 amended; ADR-0004).
- **P5-I09** — API Gatekeeper with budgets, retries, timeouts, and
  structured usage/cost events (FR-44, ADR-0004).
- **P5-I11** — CLI operational modes (`dry-run`, `offline-fixture`,
  `live`, `compile-only`, `validate-only`, `--topic`/`--manifest`
  override, `resume`) and deterministic offline fixtures (FR-46).
- **secure file I/O** — path guards, atomic writes, write-audit
  (existing P5-I04 / #13 amended).
- **deterministic renderer** — semantic `LaTeXProjectSpec v1` →
  `.tex` files (existing P5-I05 / #14 amended; ADR-0003, FR-43).
- **compilation service** — LuaLaTeX + biber multi-pass with fixed
  args, timeout, bounded attempts, captured/parsed build log
  (existing P5-I06 / #15 amended; ADR-0007).
- **graph and asset tooling** — typed graph/asset specs and
  deterministic rendering (existing P5-I07 / #16 amended; ties to
  P8-I01).
- **P5-I13** — baseline CI on PR/main with frozen dependency sync,
  Ruff, tests, current coverage gate, automated 150-line cap, and
  offline smoke run.

**Exit criterion (verified complete and milestone closed):** `.env-example`
is committed, the provider layer is importable, every Phase 5 tool seam is
exercised by tests, and every typed contract and operational mode listed
above is implemented and tested. PR #79 merged the work to `main`; the
offline-fixture path and baseline CI gates are green; P5-I01 through P5-I13
are closed with evidence; the Phase 5 milestone is closed.

### Phase 6 — Markdown-first content pipeline *(corrective recovery complete — PR #96; pending maintainer review-gate approval before Phase 9)*

Writer/Outline/Reviewer agents produce Markdown drafts at
`results/generated_markdown/` (canonical, per FR-12 and §12.3). The
`content/markdown_drafts/` scaffold has been retired. Markdown must include
heading structure, figure placeholders, table placeholders, equation
placeholders, and citation placeholders (FR-13). A human review gate runs
before any LaTeX conversion.

**Corrective scope:** PR #81 delivered a partial offline Markdown path, but
not the real CrewAI kickoff or the complete PRD §22.7 manuscript. Phase 6 is
therefore re-opened for P6-I04 (#94) and P6-I05 (#95). The existing
`results/run_logs/review_record.json` is stale because the canonical Markdown
bytes changed after approval; any downstream renderer must require fresh,
hash-bound human approval before consuming the canonical manuscript.

**Phase-level PR exception:** P6-I04 and P6-I05 are implemented on one
phase-level branch and pull request because P6-I05 depends on the orchestration
introduced by P6-I04 and both issues share the same human-review checkpoint.
The default one-issue-one-PR rule remains unchanged for unrelated work.

**Exit criterion (met — pending human review gate):** a real sequential CrewAI
kickoff is wired through the controlled provider and gatekeeper seams
(P6-I04, PR #96); a complete eight-chapter candidate manuscript is generated
in an isolated run workspace; deterministic preflight passes; and the run
stops at the maintainer-owned human review gate with a review packet and exact
aggregate hash. Phase 9 may begin once the maintainer approves that packet.

### Phase 7 — Real-source and bibliography pipeline *(complete and closed — PR #83)*

Implement the Bibliography Agent's configured-manifest consumption,
source verification, and `references.bib` curation per
`docs/PRD_bibliography_and_citations.md`. Automatic source discovery is
deferred beyond the MVP. **No fabricated sources, ever** — citation
insertion must refuse unverified sources and surface unresolved
`\cite{...}` as build-time errors.

**P7-I00 (binding decisions fixed 2026-06-16):** the canonical
per-source ledger is `docs/SOURCES.md` (with `docs/AI_USAGE.md`
reserved for AI-assisted activity logging); `biblatex` is configured
`style=numeric`, `sorting=none`, `backend=biber`; citation keys follow
`authorYYYYkey`; verifier identity uses the honest
`<verifier-id>:<github-account>` convention; archive contents under
`data/sources/arxiv/` are treated as untrusted and inspected with
metadata-only readers (P7-I07). Full policy text is in
`docs/PRD_bibliography_and_citations.md` §7.1, §7.3, §13.1, and
`docs/SOURCES.md`.

**Exit criterion:** `latex_project/references.bib` contains only verified
real entries; every `\cite{...}` in the LaTeX sources resolves.

### Phase 8 — Python graph generation pipeline *(complete and closed — PR #92)*

Implement `src/agentic_publishing_pipeline/visualization/`. It must produce
at least one graph image saved under `latex_project/figures/` (FR-29,
FR-30). The graph renderer owns spec validation, deterministic Python
rendering, provenance, and reproducibility evidence; chapter inclusion
remains Phase 9 work.

**Exit criterion:** a real Python-generated graph file exists under
`latex_project/figures/`, produced from a validated versioned graph spec
with deterministic regeneration evidence and provenance beside the PNG.

### Phase 9 — LaTeX project assembly *(open)*

Convert approved Markdown into the structured LaTeX project per PRD §8.5 /
§14.3:

- `main.tex` is a thin root that `\input{}`s everything else; current
  `latex_project/main.tex` is still the TODO-only placeholder.
- `preamble.tex`, `macros.tex` (reusable math notation per FR-18),
  `references.bib`, chapter files under `chapters/`.
- Tables live in dedicated files under `tables/`, TikZ figures in
  dedicated files under `figures/`; chapter files `\input{...}` them
  (FR-17a–d). Regular `\includegraphics` images may use a short `figure`
  wrapper inside the chapter.
- LuaLaTeX is the **required MVP engine** (FR-20). Hebrew font preference
  `David CLM`, English `Latin Modern Roman`, via `fontspec` + `polyglossia`.
- Required content: at least one image (FR-28), Python-generated graph
  (FR-29), table (FR-31), equation with `\ref`/`\eqref` cross-reference
  (FR-25, FR-32), theorem-like environment (FR-24), TikZ figure (AC §14.2),
  nomenclature with ≥2 symbols (FR-26), index with ≥1 Hebrew and ≥1 English
  term (FR-27), headers/footers (FR-21), title page and TOC (FR-22), and at
  least one substantial Hebrew/English BiDi section (FR-15-onward + AC
  §14.4).

**Exit criterion:** the LaTeX project compiles cleanly with LuaLaTeX using
the documented build command, and every PRD §14.3 / §14.4 acceptance
checkbox is verifiable in the resulting PDF.

### Phase 10 — PDF build pipeline *(open)*

Document and script the multi-pass build (LuaLaTeX → biber → LuaLaTeX →
LuaLaTeX, plus `makeindex` / `makenomenclature` as needed). Output is
`results/final.pdf` (FR-38, §12.3). Build commands are documented in
`README.md` so a new developer can reproduce.

**P10-I03 (planned):** define front/back-matter exclusions, report
total **and** substantive page counts, calibrate the canonical article
to satisfy the assignment page-count requirement, and add deterministic
page checks in the ValidatorService (FR-49).

**Exit criterion:** `results/final.pdf` exists, opens cleanly, is ≥15 pages
(KPI) by both total and substantive page rules, and is regenerable from
a clean checkout via documented commands.

### Phase 11 — Deterministic ValidatorService *(open)*

Implement the deterministic `ValidatorService` in
`src/agentic_publishing_pipeline/validation/` per FR-40 / NFR-19. It runs
**after** the Reviewer Agent and is **not** an LLM. It checks: required
repository files, required LaTeX files (PRD §14.1, §14.3), generated
artifacts (Markdown drafts, graph files, run logs), LaTeX build outputs,
PDF page count, embedded image / graph / table / equation indicators where
feasible, presence of a BiDi section, presence of bibliography /
nomenclature / index, and resolution of every `\cite{...}` (PRD
`PRD_pdf_validation.md`, `PRD_bibliography_and_citations.md`). Output is a
human-readable validation report (FR-37).

**Exit criterion:** the validator runs from a documented entry point,
produces a report, and fails loudly on missing artifacts; it does not
delegate any decision to an LLM.

### Phase 12 — Tests, lint, and reproducibility *(open)*

Replace smoke-only coverage with real tests for the provider layer, tools,
Markdown→LaTeX conversion, visualization, and `ValidatorService`. Keep
`uv run ruff check .` and `uv run pytest` green. Document reproducibility
in `README.md`: install steps, LaTeX distribution requirements (LuaLaTeX +
`David CLM` font), regeneration commands, and cost/usage notes.

**P12-I05 (merged — PR #86, issue #85):** hardened CI with ≥85% coverage,
preserved frozen dependency installation, line-cap enforcement, and offline
integration (extends P5-I13's baseline). Closed with evidence.

**P12-I06 (planned):** prove genericity by running the same pipeline
against a second verified topic and a different verified manifest
without source-code changes; verify no canonical paper IDs, chapter
names, or prompt assumptions are hardcoded (NFR-34, ADR-0006).

**Exit criterion:** `uv run pytest` and `uv run ruff check .` both pass on
a clean checkout; `README.md` reproducibility instructions are accurate;
P12-I05 coverage gate is enforced in CI; P12-I06 second-topic run
completes successfully.

### Phase 13 — README, AI usage, and prompt log finalization *(open)*

Bring `README.md` to current architecture (8-agent flow, real commands,
real run output), and fill `docs/AI_USAGE.md` and `docs/PROMPTS.md` with
the actual prompts, models, costs, and human verification notes used to
generate the final PDF.

**P13-I05 (planned):** publish a sanitized, self-contained final-run
evidence bundle containing the selected run ID, configuration snapshot,
prompt/config registry version, source manifest, artifact manifest,
validation report, build log summary, usage/cost report, screenshots,
and final PDF/LaTeX references. The bundle must contain no secrets, no
local-only archive bytes, no private paths, and no external repository
references or attribution (NFR-33).

**Exit criterion:** README accurately describes the running system; AI
usage and prompt log are complete and current at submission time;
P13-I05 sanitized evidence bundle is published.

### Phase 14 — Final submission packaging *(open)*

Prepare the Moodle wrapper PDF from the official template, confirm the
`<GROUP_CODE>-ex03.pdf` filename convention, and confirm each group member
submits separately in Moodle (per `SUBMISSION_CHECKLIST.md`).

**Exit criterion:** the wrapper PDF exists under `submission/`, the
`SUBMISSION_CHECKLIST.md` checkboxes are individually verified, and each
group member has submitted in Moodle.

## Notes

- Phase 1 is complete (mechanism PRDs reconciled — commit `4e5517c`).
  Phase 1.5 is complete (demo topic and source manifest locked —
  commit `303a425`). Phases 2, 3, 4, 5, 6, 7, and 8 are complete and
  closed (milestones #1 through #7 closed; Phase 6 re-closed via PR #96).
  Phase 9 is the next open implementation phase and may begin once the
  maintainer approves the Phase 6 review packet. Phases 9 through 14
  remain open and pending future implementation. None of the currently-open
  phases is allowed to be marked complete preemptively.
  PRD acceptance-criteria checkboxes (`docs/PRD.md` §14,
  `docs/HW3_REQUIREMENTS.md`, `SUBMISSION_CHECKLIST.md`) are ticked
  only after the underlying artifact is verified on disk and, where
  applicable, by a passing build, test, or validator run.
- Real Python dependencies (`crewai`, model SDKs, search SDKs,
  `matplotlib`, etc.) are added via `uv add` only when the phase that
  needs them begins.
- LaTeX compilation is not wired up yet. Do not assume a TeX distribution
  is installed locally; the README must call out the LuaLaTeX + David CLM
  requirement before Phase 10 can be validated on another machine.
