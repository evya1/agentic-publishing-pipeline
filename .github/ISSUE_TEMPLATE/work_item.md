---
name: Work item
about: A concrete, traceable backlog item that maps to docs/TODO.md and docs/PLAN.md.
title: "P<phase>-I<nn> — <short title matching docs/TODO.md wording>"
labels: []
assignees: []
---

<!--
Read CONTRIBUTING.md before filing this issue.

This template enforces the Project Tracking Synchronization Contract
(CONTRIBUTING.md §8). Every field below is mandatory. Issues with
GitHub-only scope are not allowed — if the work is not already in
docs/TODO.md / docs/PLAN.md / docs/PRD.md, update the appropriate
document via PR first (or alongside this issue, with the PR referenced
in the Source section).
-->

## Source

- **Internal issue ID**: `P<phase>-I<nn>`
- **TODO**: `docs/TODO.md` §<section>, "<TODO wording>"
- **PLAN**: `docs/PLAN.md` Phase <N>, exit criterion: "<paraphrase>"
- **PRD**: <e.g. FR-12, NFR-19, AC §14.5; list every applicable requirement>
- **Mechanism PRD (if any)**: <e.g. `docs/PRD_crewai_pipeline.md` §6>

## Milestone and labels

- **Milestone**: `Phase <N> — <title>` (must match the PLAN phase).
- **Labels**: <from the fixed vocabulary in `CONTRIBUTING.md` §11 —
  `docs`, `architecture`, `crewai`, `latex`, `validation`, `bidi`,
  `bibliography`, `testing`, `submission`, `decision`, `security`>.

## Dependencies

- **Depends on**: <`P<phase>-I<nn>` of any prerequisite issue, or "none">
- **Blocks**: <issues that cannot start until this one is verified, or "none">

**Wire native GitHub relationships after filing** (both sides required):

```sh
gh issue edit <N> --add-blocked-by <M>   # one per "Depends on" entry
gh issue edit <N> --add-blocking <M>     # one per "Blocks" entry
```

Validate: `uv run python scripts/check_github_metadata.py --issue <N>`

## Description

<!--
Describe the scope concretely. Reference the exact files, sections,
build steps, or behaviour that this issue changes. Quote the relevant
PRD/PLAN/TODO wording when it helps disambiguate scope.
-->

## Definition of done

<!-- A concrete list of what must be true for this issue to be considered done. -->

-

## Acceptance criteria

<!--
Checkable items that a reviewer can verify on merged `main`. These are
the conditions for posting the post-merge evidence comment on the
issue. PRD §14 / HW3 / SUBMISSION_CHECKLIST boxes are *not* ticked here
unless their own evidence requirement is independently met.
-->

- [ ]
- [ ]

## Synchronization requirements (CONTRIBUTING.md §8)

<!--
List what local Markdown documents this issue will change, and how the
PR should reconcile both sides. "None" is acceptable only for genuine
no-doc-change work.
-->

- `docs/TODO.md`: <e.g. tick item §C.1; or "no change">
- `docs/PLAN.md`: <e.g. phase status flip; or "no change">
- `docs/PRD.md`: <e.g. amend §22.4; or "no change">
- Other (`docs/AI_USAGE.md`, `docs/PROMPTS.md`, README, …): <…>

## Verification evidence (filled at close time)

<!--
Post-merge: paste here (or in a closing comment) the concrete evidence
that the acceptance criteria are met — paths, command outputs, page
counts, validator report excerpts, etc.
-->

-

## Closure rule (per `docs/TODO.md` §F-6)

This issue may be closed only when the underlying artifact is verified
on disk (or by a passing build, test, or validator run). Closing this
issue does NOT by itself permit ticking a TODO box, a PRD §14
acceptance-criterion checkbox, a `docs/HW3_REQUIREMENTS.md` checkbox,
or a `SUBMISSION_CHECKLIST.md` checkbox.
