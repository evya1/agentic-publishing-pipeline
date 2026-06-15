# Source-verification ledger

> **Status (P7-I00, 2026-06-16).** This file is the **canonical
> per-source audit trail** for the agentic-publishing-pipeline
> bibliography, fixed under `docs/PRD_bibliography_and_citations.md`
> §13.1. The locked manifest is `config/article_sources.yaml`; the
> verifier is the Bibliography Agent (Phase 7); the boundary policy is
> the untrusted-archive policy (P7-I07).

## 1. Scope and authority

- `docs/SOURCES.md` carries one canonical entry per source from the
  locked manifest, with sufficient evidence to reconstruct
  `final citation key → references.bib entry → verification method →
  authoritative metadata snapshot → local archive presence` for any
  future reviewer.
- `docs/AI_USAGE.md` records AI-assisted activity (model identity,
  prompts used, limitations, human verification, cost). It links here
  by `verification.run_id` and citation key but does **not** duplicate
  per-source bibliographic facts.
- `docs/PROMPTS.md` records prompt-registry contents verbatim.

## 2. Verification procedure (binding)

The procedure is fixed in `docs/PRD_bibliography_and_citations.md` §7.1
and reproduced here for self-containment:

1. **Schema check** of the manifest record.
2. **Locked-manifest membership.** Candidate must be in
   `config/article_sources.yaml`; no silent additions, replacements, or
   model-generated entries.
3. **Authoritative metadata retrieval.** arXiv API/metadata for arXiv
   sources; DOI registration metadata when a DOI genuinely exists;
   publisher metadata otherwise.
4. **Field cross-check.** Title, year, ordered authors compared against
   authoritative response. Any mismatch is recorded; material mismatch
   rejects the entry.
5. **DOI presence** is recorded only when authoritative metadata
   provides one. No synthesis from arXiv identifiers.
6. **Local archive presence.** Archive opened in metadata-only mode per
   the P7-I07 boundary; **not** authoritative for bibliographic facts.
7. **Status flip** (`verified` or `rejected`) with `verified_at` (UTC
   ISO 8601) and `verified_by` per the honest-identity convention
   below.

## 3. Honest-identity convention for `verified_by`

`verified_by = "<verifier-id>:<github-account>"`.

- `<verifier-id>` names the mechanism that actually ran the
  verification (for example `bibliography-agent`,
  `claude-opus-4.7+arxiv-api`, `human-review`).
- `<github-account>` is the authenticated GitHub login that ran the
  pipeline (the assignee of the corresponding issue).
- `<verifier-id>` is `human-review` **only** when a human personally
  inspected the authoritative metadata; otherwise the value names the
  agent or tool that performed the lookup. Misrepresenting a
  machine-assisted verification as `human-review` is a content-policy
  violation under PRD §8.6 / CLAUDE.md.

## 4. Machine-readable mirror

A machine-readable mirror of the canonical entries is maintained at
`results/run_logs/source_verification.json` (one record per locked
source plus a `summary` block). The mirror is generated alongside this
Markdown file by the Phase 7 audit step (P7-I03) so that automated
consistency checks can run without parsing prose.

## 5. Per-source entries

> The ten entries below are **placeholders** populated by the
> verification step (P7-I02) and the audit step (P7-I03). They are
> reserved and ordered to match `config/article_sources.yaml` so a
> reviewer can locate each entry by its provisional or final citation
> key.

<!-- Phase 7 issues populate the entries below. Until P7-I02 completes,
the fields contain the manifest provisional values and the
verification block is marked `pending`. Each entry follows the schema
below. -->

### Entry schema

```yaml
final_citation_key: <authorYYYYkey>          # after P7-I05
previous_citation_key: <tbd…>                # the provisional manifest key
canonical_url: <arxiv abs URL or DOI URL>
arxiv_id: <id>                               # if applicable
doi: <doi or null>                           # only when authoritative
verified_title: <title>
verified_authors:                            # ordered, populated by P7-I02
  - <Surname, Given>
verified_year: <YYYY>
verification:
  status: verified | rejected | pending
  method: arxiv_api | doi | publisher_catalog
  verified_at: <ISO 8601 UTC>
  verified_by: <verifier-id>:<github-account>
  run_id: <run id>
  authoritative_source: <URL or identifier of the metadata response>
  authoritative_snapshot: <path to committed fixture or `null`>
local_archive:
  path: data/sources/arxiv/source_zips/<file>
  present: true | false
  archive_inspection: metadata_only           # per P7-I07
  notes: <freeform>
mismatch_or_rejection_rationale: <text or null>
```

### Reserved entries (placeholders pending P7-I02)

| Provisional key                  | arXiv ID    | Year | Local archive                              |
|----------------------------------|-------------|------|--------------------------------------------|
| `ke2025reasoningfrontiers`      | 2504.09037  | 2025 | `data/sources/arxiv/source_zips/2504.09037.zip` |
| `wu2025agenticreasoningtools`   | 2502.04644  | 2025 | `data/sources/arxiv/source_zips/2502.04644.zip` |
| `correa2025planningperformance`     | 2511.09378  | 2025 | `data/sources/arxiv/source_zips/2511.09378.zip` |
| `huang2025licomemory`              | 2511.01448  | 2025 | `data/sources/arxiv/source_zips/2511.01448.zip` |
| `chen2025telemem`                 | 2601.06037  | 2026 | `data/sources/arxiv/source_zips/2601.06037.zip` |
| `yao2025multimodalsurvey`        | 2510.10991  | 2025 | `data/sources/arxiv/source_zips/2510.10991.zip` |
| `wang2025proactiveretrievalmedical` | 2510.18303 | 2025 | `data/sources/arxiv/source_zips/2510.18303.zip` |
| `liu2025agenticmath`             | 2510.19361  | 2025 | `data/sources/arxiv/source_zips/2510.19361.zip` |
| `ye2024mirai`                   | 2407.01231  | 2024 | `data/sources/arxiv/source_zips/2407.01231.zip` |
| `wei2026agenticreasoning`        | 2601.12538  | 2026 | `data/sources/arxiv/source_zips/2601.12538.zip` |

The verification status for every entry is `pending` until P7-I02
populates this ledger with authoritative metadata, sets `verified` or
`rejected`, and records the run id and timestamp.

## 6. Rejection and replacement

A rejected manifest entry is **not** silently replaced. The procedure
is:

1. Record the rejection here with mismatch evidence, run id, and
   timestamp.
2. Open a follow-up issue describing the rejected source and the
   proposed handling.
3. Update `config/article_sources.yaml` and the canonical ten-source
   citation coverage (`docs/PRD_bibliography_and_citations.md` §10.2)
   only through a reviewed PR.

A rejected entry remains visible in this ledger as historical
evidence; it is **not** removed.

## 7. Re-verification

Verification is idempotent. Re-running over an entry already marked
`verified` must not silently flip its status. If a re-run produces a
material mismatch, that re-run constitutes a rejection event under
§6.

## 8. Cross-references

- `config/article_sources.yaml` — locked source manifest.
- `docs/PRD_bibliography_and_citations.md` §7.1, §7.3, §13.1 —
  binding policy.
- `docs/AI_USAGE.md` — AI-assisted activity log.
- `docs/PROMPTS.md` — prompt registry.
- `latex_project/references.bib` — verified bibliography emission
  target (P7-I04).
- `results/run_logs/source_verification.json` — machine-readable
  mirror (P7-I03).
