<!--
Mandatory pull-request template for agentic-publishing-pipeline.

Read CONTRIBUTING.md before opening this PR. The Project Tracking
Synchronization Contract (CONTRIBUTING.md §8) and the PR checklist
(CONTRIBUTING.md §12) are binding on every PR.

Mark items that do not apply with `N/A` and add a one-line reason.
Do not delete checklist sections.
-->

## Summary

<!-- 1–3 sentences: what this PR changes and why. -->

## Linked issue

- Related issue: <!-- Replace with a verified non-closing reference, for example: Refs #123 -->
- Internal issue ID: <!-- e.g. P2-I03 -->
- PRD reference: <!-- e.g. FR-12, NFR-19, AC §14.5 -->
- PLAN phase: <!-- e.g. Phase 2 — Project management setup -->
- TODO item: <!-- e.g. docs/TODO.md §B, "Refresh README.md…" -->
- Milestone: <!-- e.g. Phase 2 — Project management setup -->
- Labels applied: <!-- e.g. docs, architecture — must match the issue labels -->
- Assignee: <!-- same person as the issue assignee -->

> Do not use closing keywords (`Closes`, `Fixes`, `Resolves`) — issue
> closure happens only after artifacts are verified on disk per
> `CONTRIBUTING.md` §8.5 and `docs/TODO.md` §F-6.

## Traceability and ownership

- [x] GitHub issue exists and is referenced via `Refs #<N>` above.
- [x] Internal issue ID is in the PR title (e.g. `[P2-I03]`).
- [x] PR author is the issue's assignee (or an explicit co-assignee
      coordinated in an issue comment).
- [x] Branch was created via `gh issue develop <N>` and appears in the
      issue's Development section (linked branch).
- [x] Milestone and labels on the issue match this PR's scope.
- [x] PR itself has the assignee set (same person as the issue assignee).
- [x] PR itself has labels matching the issue labels.
- [x] All commit hashes cited in this PR body use the 7-character short form
      (e.g. `e145114`), not the full 40-character SHA.
- [x] Dependencies listed in the issue body are satisfied (or the
      blocker is documented and the PR is explicitly scoped to a
      preliminary step).

## Scope

- [x] PR scope matches the issue's Definition of Done.
- [x] No unrelated cleanup, refactor, or feature work is bundled in.
- [x] If new scope was discovered mid-PR, it is captured in a
      follow-up issue (preferred) **or** the original issue body has
      been updated and the updated DoD is reflected here.

### Changed artifacts

<!-- List the files / artifacts this PR adds, modifies, or removes. -->

-

## Tests / lint / build / validator

- [x] `uv run pytest` — result: <!-- passing / failing — details -->
- [x] `uv run ruff check .` — result: <!-- passing / failing — details -->
- [x] LaTeX build (where applicable) — result: <!-- N/A or details -->
- [x] `ValidatorService` run (where applicable) — result: <!-- N/A or details -->
- [x] Manual verification performed (where applicable) — describe:

## Synchronization (CONTRIBUTING.md §8.4)

- [x] `docs/TODO.md` — synchronized / no change required: <!-- describe -->
- [x] `docs/PLAN.md` — synchronized / no change required: <!-- describe -->
- [x] `docs/PRD.md` — synchronized / no change required: <!-- describe -->
- [x] `docs/HW3_REQUIREMENTS.md` — synchronized / no change required.
- [x] `SUBMISSION_CHECKLIST.md` — synchronized / no change required.
- [x] `README.md` and other maintainer docs — synchronized / no change
      required.
- [x] `docs/AI_USAGE.md` — updated where AI was used / not required.
- [x] `docs/PROMPTS.md` — updated where prompts changed / not required.

## Known limitations and follow-ups

<!-- Anything intentionally out of scope, deferred, or marked TODO. -->

-

## Post-merge verification plan

<!-- The assignee runs these on merged `main` and posts an evidence
comment on the issue before closing it. -->

-

## Closure intent

- [x] No premature completion claim. PRD §14, HW3 requirements, and
      `SUBMISSION_CHECKLIST.md` checkboxes are **not** ticked in this
      PR unless their underlying artifact is verified on disk.
- [x] After merge, the assignee will:
    - verify on `main` per the plan above;
    - post an evidence comment on the issue;
    - close the issue manually only after evidence is recorded;
    - reconcile any milestone state if this PR completes the last item
      in its milestone (per `CONTRIBUTING.md` §8.6).
