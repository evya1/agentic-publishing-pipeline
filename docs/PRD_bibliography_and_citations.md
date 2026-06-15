# PRD — Bibliography and Citations

> **Status:** design/specification only. `latex_project/references.bib`
> is currently empty and no citations have been resolved or verified.
> This document defines what will be built; checking any of its
> acceptance-criteria boxes requires the corresponding artifact to
> exist on disk and to have been verified end-to-end.

## 1. Scope and relationship to other documents

This PRD refines `docs/PRD.md` §8.3 (Bibliography Agent), §8.5 (`.bib`
in the LaTeX project), §8.6 (citations and references), §14.2
(rendered bibliography and citations in the PDF), §14.3 (`references.bib`
exists), and §16.3 (LaTeX bibliography toolchain).

Sister mechanism PRDs:

- `docs/PRD_crewai_pipeline.md` — defines the Bibliography Agent as one
  of the eight agents in §8.3 and the task that produces `references.bib`.
- `docs/PRD_latex_generation.md` — defines where `references.bib` lives
  in the LaTeX project, the `biblatex` + `biber` toolchain, and the
  multi-pass build that renders the bibliography.
- `docs/PRD_pdf_validation.md` — defines the deterministic citation /
  bibliography checks that run after the Reviewer Agent.

Planning and tracking:

- `docs/PLAN.md` — Phase 7 implements source-manifest consumption,
  verification, and `references.bib` curation. Automatic source
  discovery is deferred beyond the MVP.
- `docs/TODO.md` — concrete backlog with PRD requirement tags.
- `CLAUDE.md` — repository conventions; the "no fabricated sources"
  rule mirrors this PRD.

## 2. Problem

The final PDF must contain a real bibliography with citations linked
from the body text and rendered as a bibliography section. Fabricated
sources are explicitly disallowed at every stage of the pipeline. We
need a clear ownership model, a defined toolchain, a citation-key
convention, an audit trail, and a deterministic check that every
`\cite{...}` resolves before the PDF is considered valid.

## 3. Goals

- Assign **single ownership** of `latex_project/references.bib` to the
  **Bibliography Agent** defined in `docs/PRD.md` §8.3.
- Lock the toolchain to **`biblatex` + `biber`** under LuaLaTeX
  (`docs/PRD.md` §16.3).
- Define a **citation-key convention** that is stable, human-readable,
  and verifiable.
- Maintain a **verification audit trail** so every entry in
  `references.bib` is traceable to a real source and to the prompt /
  search run that surfaced it.
- Forbid **fabricated sources** at every stage; refuse to insert a
  citation whose source has not been verified.
- Surface **unresolved `\cite{...}`** as build-time / validation-time
  errors via the deterministic `ValidatorService` (FR-40, NFR-19),
  never as warnings.
- Ensure citations rendered inside Hebrew text preserve correct
  character order (NFR-29).

## 4. Non-goals

- Choosing the canonical HW3 source list — that is owned by the topic
  decision (`docs/PRD.md` §22) and stored in
  `config/article_sources.yaml`.
- Implementing automatic source discovery for the MVP. Future discovery
  support may propose candidates for a later verified manifest, but
  unverified discovered sources may not enter the canonical HW3 run.
- Implementing the validator itself — see `docs/PRD_pdf_validation.md`.
- Maintaining the LaTeX preamble or build commands — see
  `docs/PRD_latex_generation.md`.

## 5. Ownership: the Bibliography Agent

The **Bibliography Agent** (`docs/PRD.md` §8.3) is the single owner of
`latex_project/references.bib`. Its responsibilities:

- **Consume** the configured source manifest selected for the run. For
  the canonical HW3 run, that manifest is `config/article_sources.yaml`
  as described in `docs/PRD.md` §22.4–§22.5.
- **Verify** every configured source before it enters `references.bib`
  (see §7). Search/provider calls may verify metadata; they do not
  silently add new sources to the run.
- **Curate** `references.bib`: stable keys, the minimum metadata
  required by the chosen `biblatex` style, no duplicates.
- **Resolve** the citation placeholders left by the Writer Agent and
  the Hebrew/BiDi Agent into real `\cite{...}` commands keyed against
  the verified `.bib` entries.
- **Refuse** to insert a citation whose source has not been verified.
  Do not fabricate sources, silently replace rejected sources, or
  silently discover substitute sources.

No other agent is permitted to add entries to `references.bib`.

## 6. Toolchain and `.bib` location

- **File:** `latex_project/references.bib`. Single source of truth
  (FR-19, AC §14.3).
- **LaTeX package:** `biblatex` (loaded in `preamble.tex`; see
  `docs/PRD_latex_generation.md`).
- **Backend:** `biber`.
- **Bibliography style:** chosen during Phase 7 and recorded back into
  this section; defaults to a numeric or author-year style supported by
  `biblatex` out of the box.

Engine + bibliography processing order in the multi-pass build
(`docs/PRD_latex_generation.md` §16):

```
lualatex → biber → makeindex (idx + nls) → lualatex → lualatex
```

## 7. Source verification

Every entry in `references.bib` must be backed by a real, locatable
source. A "verified" source means at least one of the following is true
and recorded in the audit trail (§8):

- The URL resolves to a public page, paper, preprint, or repository
  whose author / title / year match the `.bib` entry.
- A DOI resolves to the same paper.
- A book / journal / proceedings reference is independently locatable
  (e.g., listed on the publisher's site or in a standard catalog).

If none of the above can be confirmed, the candidate source is rejected
and not added to `references.bib`. **Fabricated entries are forbidden,
without exception** (`docs/PRD.md` content policy, CLAUDE.md).

### 7.1 Verification procedure (fixed in Phase 7 / P7-I00)

For every candidate manifest entry, the Bibliography Agent runs the
following checks **in order**. A failure at any step terminates
verification for that entry and marks it `rejected`.

1. **Schema check.** The record carries every required field
   (`citation_key`, `title`, `authors`, `year`, plus an `arxiv_id` /
   `arxiv_url` pair for arXiv sources). Empty `authors:` is permitted as
   input only because Phase 7 populates the field; downstream consumers
   may not treat an unpopulated `authors:` as verified.
2. **Locked-manifest membership.** The candidate's `arxiv_id` (or
   manifest path) corresponds to a record already present in
   `config/article_sources.yaml`. Phase 7 does not silently introduce
   new sources, replace rejected ones, or accept model-generated
   bibliographies as candidates.
3. **Authoritative metadata retrieval.** For arXiv sources, fetch the
   record from the arXiv API or abstract page identified by `arxiv_id`.
   For genuine DOI-bearing sources, resolve the DOI through DOI
   registration metadata. Other sources resolve through publisher or
   catalog metadata. Filenames, model memory, blog summaries, and
   archive `.tex` source are **not** authoritative for bibliographic
   facts.
4. **Field cross-check.** Compare the manifest's `title`, `year`, and
   (after population) `authors` with the authoritative response. Year
   mismatch, author mismatch, or material title mismatch rejects the
   entry; recording the mismatch is mandatory.
5. **DOI presence.** Record a DOI **only** when authoritative metadata
   genuinely provides one. Do not synthesize a DOI from arXiv IDs.
6. **Local archive presence.** Confirm `source_archive` exists at the
   recorded repository-relative path. The archive is opened in
   metadata-only mode under §7.2; the archive's bytes are **not**
   authoritative for bibliographic facts and may not substitute for
   step 3.
7. **Status flip.** Update `verification.status` to `verified` or
   `rejected`, set `verification.verified_at` (UTC ISO 8601), and set
   `verification.verified_by` per §7.3.

### 7.2 Untrusted-archive boundary (cross-reference)

The archive boundary is normative: a Phase 7 entry may be marked
`verified` even when the local archive cannot be opened safely, **provided**
authoritative remote metadata (step 3) and field cross-check (step 4)
succeed. The archive's role is corroboration and provenance, not
metadata source. The boundary itself is implemented under issue
`P7-I07` (#28) and binds every reader of
`data/sources/arxiv/source_zips/` and `data/sources/arxiv/unpacked/`.

### 7.3 Honest verifier identity

`verification.verified_by` truthfully identifies the entity that ran
the verification. For the canonical Phase 7 run the value is structured
as `"<verifier-id>:<github-account>"`, where:

- `<verifier-id>` names the verification mechanism (for example
  `bibliography-agent`, `claude-opus-4.7+arxiv-api`, or
  `human-review`);
- `<github-account>` is the authenticated GitHub login that ran the
  pipeline (the assignee on the corresponding issue).

`verified_by` does **not** claim that a human personally inspected the
authoritative metadata unless `verifier-id` is `human-review`. The
semantics are reiterated in `docs/SOURCES.md`.

### 7.4 Restatement of the no-fabricated-sources rule

> **Fabricated entries are forbidden, without exception**
> (`docs/PRD.md` content policy, `CLAUDE.md`).

This rule applies at every stage of the pipeline — research, drafting,
review, bibliography curation, citation resolution, LaTeX assembly, and
validation. No agent, tool, or human contributor may introduce a
bibliography entry, citation, or supporting fact whose source has not
passed §7.1.

## 8. Audit trail

The pipeline keeps an audit trail mapping each `.bib` entry to the
source artifact that justifies it:

- **Per-source verification record.** For each entry, the Bibliography
  Agent records: citation key, title, author(s), year, URL or DOI,
  verification method (URL fetch / DOI resolve / catalog lookup), and
  the timestamp / run ID. The recording location is **either**
  `docs/AI_USAGE.md` (one section per run) **or** a dedicated
  `docs/SOURCES.md`. The chosen location is fixed in Phase 7 and noted
  back here.
- **AI/LLM usage.** Every AI/LLM call that surfaces or summarizes a
  candidate source is logged in `docs/AI_USAGE.md` per the
  repository-wide policy (CLAUDE.md).
- **Prompts.** The Bibliography Agent's prompts are captured verbatim
  in `docs/PROMPTS.md`.

The audit trail must let a reviewer reconstruct, for any `\cite{...}`
in the final PDF, the chain from cited key → `.bib` entry →
verification record → source artifact.

## 9. Citation-key convention

- **Format:** `authorYYYYkey`, lowercase, ASCII only.
  - `author` = surname of the first author (lowercase, no diacritics).
  - `YYYY` = four-digit publication year.
  - `key` = a short slug (1–3 words) disambiguating the work.
  - Example: `vaswani2017attention`, `goldberg2017nlp`.
- **Stability.** Once a key is assigned, it does not change. If a
  source is replaced, the new entry gets a new key and the old key is
  removed only after every `\cite{...}` is migrated.
- **Disambiguation.** If two works share author and year, append a
  single lowercase suffix: `smith2020a`, `smith2020b`.
- **No collisions.** Keys are unique across `references.bib`.

The Bibliography Agent emits the citation-key map (placeholder → key)
back to the Writer Agent / BiDi Agent before LaTeX assembly so the
LaTeX project ends up with concrete `\cite{...}` commands.

## 10. Coverage rules

### 10.1 Rules for every run

- **Cited in the body.** Every `\cite{...}` in the LaTeX sources must
  resolve to an entry in `references.bib` (FR-33, AC §14.2).
- **Rendered in the bibliography section.** The bibliography section
  must render every entry that is cited at least once (FR-33, AC §14.2).
- **No unused entries.** Entries that are not cited should be removed
  before submission, or — if intentionally kept — documented in the
  audit trail.
- **No fabricated entries.** This applies at every stage and overrides
  every other convenience consideration.

### 10.2 Canonical HW3 demonstration rules

The canonical HW3 run is configured with the fixed ten-source manifest
in `config/article_sources.yaml` (`docs/PRD.md` §22.4). For that run:

- all ten canonical manifest sources must be cited at least once across
  the complete final article;
- each chapter should target approximately 2–3 relevant verified
  sources, with justified variation allowed;
- the all-ten coverage rule is deterministic because the manifest is
  fixed and known before generation.

These canonical rules do not apply unchanged to every generic run.
Generic runs validate against their selected verified manifest and must
not assume exactly ten sources.

## 11. Handoff to the deterministic ValidatorService

Citation correctness is enforced **deterministically** by the
`ValidatorService` defined in `docs/PRD_pdf_validation.md`. The LLM is
not the source of truth (FR-40, NFR-19). The Reviewer Agent may flag
suspicious citations during qualitative review, but its verdict is
advisory.

The `ValidatorService` is expected to enforce:

- every `\cite{...}` in the LaTeX sources resolves to a `.bib` entry;
- the bibliography section is rendered in the final PDF;
- canonical HW3 runs cite every configured canonical manifest source at
  least once, while generic runs are checked against the selected
  manifest without assuming a ten-source count;
- the verification audit trail covers every entry in `references.bib`
  (where the audit-trail format permits an automated check);
- unresolved citations are **build-time / validation-time errors**, not
  warnings.

## 12. BiDi citation rendering (NFR-29)

When citations appear inside Hebrew sentences, the rendered citation
text must preserve correct character order: the citation label /
number / author-year token stays in its LTR run inside the surrounding
RTL paragraph. The `biblatex` + `polyglossia` combination under
LuaLaTeX is expected to handle this; the BiDi section
(`docs/PRD_latex_generation.md` §12) is the canonical place where this
is exercised.

## 13. Open decisions to capture during implementation

- **Audit-trail location.** `docs/AI_USAGE.md` vs. a dedicated
  `docs/SOURCES.md`. **Fixed by P7-I00:** see §13.1.
- **`biblatex` style.** Numeric, author-year, or a specific style
  package. **Fixed by P7-I00:** see §13.1.
- **Maximum bibliography size.** Whether the article should cap entries
  at, e.g., 20–30 to keep the bibliography reviewable. Fixed by the
  topic/scope decision in Phase 3.

### 13.1 Phase 7 policy decisions (fixed under P7-I00, issue #21)

The decisions below are binding for the canonical HW3 Phase 7 run and
for every downstream Phase 7 issue. Subsequent runs may revisit them
only through a reviewed PR that updates this section.

| Decision                          | Value                                                                                              |
|-----------------------------------|----------------------------------------------------------------------------------------------------|
| Audit-trail canonical location    | `docs/SOURCES.md` (per-source ledger). `docs/AI_USAGE.md` records AI-assisted activity only.       |
| Source-collection policy          | Locked-manifest-only: `config/article_sources.yaml` is authoritative for the candidate source set. |
| Verification authority precedence | arXiv API/metadata → DOI registration metadata → publisher metadata → archive (corroboration only).|
| `biblatex` style                  | `style=numeric`, `sorting=none`, `backend=biber`.                                                  |
| Citation-key format               | `authorYYYYkey` (see §9). Lowercase ASCII. Provisional `tbd…` keys are migrated under P7-I05.      |
| Verifier identity convention      | `verification.verified_by = "<verifier-id>:<github-account>"` (see §7.3).                          |
| Re-verification                   | Verification is idempotent. Re-running over an already-`verified` entry must not silently flip it. |
| Mismatch handling                 | Any field mismatch in §7.1 step 4 marks the entry `rejected` with the mismatch recorded.           |
| Replacement procedure             | Rejected manifest entries are **not** silently replaced. Replacement requires a documented PR.     |
| `references.bib` membership       | Only `verified` entries; one entry per verified source; no provisional, rejected, or fabricated.   |
| Untrusted-archive boundary        | Metadata-only inspection; no extraction, no execution, no compilation (see §7.2 and P7-I07).       |
| Source-collection scope           | No automatic discovery; live lookup is permitted **only** to verify the ten locked records.        |
| `docs/SOURCES.md` rendering       | One §-per-source plus a top-level summary table; machine-readable summary in a tracked JSON file.  |

#### Rationale highlights

- **`docs/SOURCES.md` over `docs/AI_USAGE.md`.** The per-source ledger
  has its own schema (citation key, archive path, verification method,
  timestamp, run id, mismatch evidence). Overloading
  `docs/AI_USAGE.md` would conflate AI activity logging with source
  verification evidence and complicate retrieval.
- **`numeric` `biblatex` style.** Compact citations, predictable
  rendering inside Hebrew/RTL paragraphs (NFR-29), no dependence on a
  custom citation-style package, suitable for a technical survey.
  Sorting is `none` so the bibliography preserves a deterministic
  manifest-ordered listing.
- **`authorYYYYkey` keys.** Deterministic, ASCII, collision-free across
  the locked manifest, derived only from verified metadata, stable
  across reruns. No `tbd` prefix once Phase 7 completes.
- **Honest `verified_by`.** The repository cannot assert that a human
  inspected authoritative metadata when the verification was run by an
  agent. `verifier-id` makes that distinction machine-readable.

## 14. Acceptance criteria

These trace back to `docs/PRD.md` §8.3, §8.5, §8.6, §14.2, §14.3, and
§16.3. **None of these may be ticked until the underlying artifact
exists on disk and has been verified.**

- [ ] `latex_project/references.bib` exists and is the single source of
      truth for bibliography entries (FR-19, AC §14.3).
- [ ] The Bibliography Agent owns `references.bib`; no other agent
      writes to it (`docs/PRD.md` §8.3,
      `docs/PRD_crewai_pipeline.md` §5).
- [ ] `biblatex` + `biber` are configured in `preamble.tex` and used in
      the documented multi-pass build (`docs/PRD.md` §16.3,
      `docs/PRD_latex_generation.md` §16).
- [ ] Citation keys follow the `authorYYYYkey` convention with stable,
      unique keys.
- [ ] Every entry in `references.bib` is backed by a real, verified
      source (URL / DOI / catalog), recorded in the audit trail
      (`docs/AI_USAGE.md` or `docs/SOURCES.md`, fixed in Phase 7).
- [ ] No fabricated entries appear at any stage of the pipeline.
- [ ] Bibliography citations appear in the body text (FR-33, AC §14.2).
- [ ] A rendered bibliography section appears in the final PDF (FR-33,
      AC §14.2).
- [ ] Every `\cite{...}` in the LaTeX sources resolves to an entry in
      `references.bib`, enforced by the deterministic `ValidatorService`
      (FR-40, NFR-19, `docs/PRD_pdf_validation.md`).
- [ ] Unresolved citations are surfaced as build-time / validation-time
      errors, not warnings.
- [ ] Citations rendered inside Hebrew sentences preserve correct
      character order (NFR-29).
- [ ] The Bibliography Agent's prompts are captured verbatim in
      `docs/PROMPTS.md`; every AI/LLM call that surfaces a candidate
      source is logged in `docs/AI_USAGE.md`.
