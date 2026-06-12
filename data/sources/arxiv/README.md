# arXiv source archives

Local-only working area for arXiv LaTeX source archives used by the
Bibliography Agent. See `docs/PRD_bibliography_and_citations.md` for the
source-verification and citation-key rules these archives feed into.

## Layout

- `source_zips/` — downloaded archives (e.g., `<arxiv_id>.tar.gz` or
  `.zip`).
- `unpacked/` — optional extracted sources, useful for grepping figure
  files, tables, or references out of the LaTeX source of a paper.
- `raw_eprint/` — optional location for raw e-print captures (kept as
  an escape hatch; may stay empty).

## What is tracked vs. gitignored

- **Tracked:** this README and the manifest at
  `config/article_sources.yaml`.
- **Gitignored:** the archive contents under `source_zips/`,
  `unpacked/`, and `raw_eprint/`. The repository ships with the
  manifest, not the bytes — a fresh clone has empty
  `source_zips/` / `unpacked/` directories that the developer
  repopulates locally.

## Status

Phase 1.5 (demo topic + source manifest lock):

- The 10 arXiv source archives for the canonical demo article topic
  (see `docs/PRD.md` §22) have been placed under `source_zips/`
  **locally**. They are gitignored and **must not be committed**.
- The tracked manifest at `config/article_sources.yaml` records one
  entry per archive (`citation_key`, `title`, `year`, `arxiv_id`,
  `arxiv_url`, `source_archive`, `intended_use`, and a `verification`
  block whose initial `status` is `unverified`).
- No manifest entry has been verified yet. URL/DOI verification, author
  metadata completion, citation-key finalization, and `.bib` extraction
  happen during Phase 7 of `docs/PLAN.md`, owned by the Bibliography
  Agent (`docs/PRD_crewai_pipeline.md` §5,
  `docs/PRD_bibliography_and_citations.md` §5–§9).
- Archive contents are treated as **untrusted external source
  material**: no LaTeX builds are run from third-party archives, and
  no code from archives is executed.
