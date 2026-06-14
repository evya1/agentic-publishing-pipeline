# Contributing to agentic-publishing-pipeline

> **Audience.** Every human contributor, project partner, future maintainer,
> and every AI agent operating on this repository (Claude Code sessions and
> any other LLM-driven tooling). Reading this file is mandatory before you
> change any artifact in the repository or any GitHub tracking object.

This document is the **canonical detailed workflow** for the project. It
governs how the local Markdown documents (`docs/PRD.md`, `docs/PLAN.md`,
`docs/TODO.md`, `docs/HW3_REQUIREMENTS.md`, `SUBMISSION_CHECKLIST.md`, the
mechanism PRDs) and the GitHub tracking objects (issues, milestones,
labels, branches, pull requests) operate as **one coordinated workflow**.

Neither the Markdown documents nor GitHub is allowed to drift into being
the only place where project status is recorded. The Synchronization
Contract in §8 is the binding rule that keeps the two sides aligned.

---

## 1. Source-of-truth hierarchy

The repository has a single, ordered source-of-truth hierarchy. Read these
in order whenever you need to answer "what is true about this project?":

```text
docs/PRD.md                 approved product and engineering requirements
docs/PLAN.md                phases, sequencing, and phase exit criteria
docs/TODO.md                concrete checkable backlog (mirrors GitHub Issues)
GitHub Milestones           GUI mirror of PLAN phases
GitHub Issues               GUI mirror of TODO work items
branches and pull requests  implementation and review history
verified artifacts          evidence of actual completion (files, builds,
                            tests, validator runs, rendered PDF)
```

Rules:

- The Markdown documents own **requirements, phases, and the discrete
  task backlog**. They are authoritative for *what should be true*.
- GitHub Milestones and Issues own **active tracking**. They are
  authoritative for *who is working on what right now*.
- Neither side is authoritative about *completion*. Completion is
  established by **verified artifacts on disk** (or by a passing build,
  test, or validator run). See [`docs/TODO.md`](docs/TODO.md) §F-6 for the closure rule.
- PRD §19 ("Proposed Milestones" M1–M9) is **superseded by**
  [`docs/PLAN.md`](docs/PLAN.md) Phase 0–14 and the GitHub Milestones that mirror them.
  PRD §19 remains in the document only as historical context.

---

## 2. New contributor onboarding

Every new contributor — whether a human team member, a project partner,
or an AI session — must complete the following onboarding sequence
before performing any project work. AI agents must follow the same
sequence under the authenticated human account they are operating with;
see `CLAUDE.md` for AI-specific rules.

1. Read [`README.md`](README.md).
2. Read this file (`CONTRIBUTING.md`).
3. Read [`CLAUDE.md`](CLAUDE.md) **if using an AI agent**.
4. Read the relevant sections of [`docs/PRD.md`](docs/PRD.md) for the
   work area (requirements, acceptance criteria).
5. Read the current PLAN phase in [`docs/PLAN.md`](docs/PLAN.md).
6. Read the relevant TODO item in [`docs/TODO.md`](docs/TODO.md).
7. Read the full GitHub issue and **all** existing comments.
8. Inspect the issue's milestone, labels, dependencies, linked
   branches, and linked pull requests.
9. Verify local `main` is clean and synchronized with `origin/main`.
10. Self-assign the issue (`gh issue edit <N> --add-assignee "@me"`).
11. Create or check out the **linked issue branch**
    (`gh issue develop <N> --name <branch> --base main --checkout`).
12. Leave a start-of-work comment on the issue.

### First-comment template

Your first comment on an issue you are picking up should confirm:

```markdown
- Required project documentation read.
- Issue scope and dependencies reviewed.
- Assignment/ownership confirmed.
- Local main synchronized.
- Linked branch created or branch exception documented.
```

This requirement applies equally to project owners, partners, new
developers, and AI-assisted sessions.

---

## 3. Issue selection and ownership

### 3.1 Selecting an issue

- Work may not begin without a GitHub issue. If no issue exists for the
  work, **first create one** following §7 (Issue creation) and ensure
  the corresponding TODO/PLAN/PRD entries exist or are added via PR.
- Prefer issues whose dependencies are satisfied (see the issue body's
  `Dependencies` section).
- Respect milestone ordering: the open phase milestone with the lowest
  number is normally where the next work happens.

### 3.2 Self-assignment

- The active contributor must assign themselves before starting:
  `gh issue edit <N> --add-assignee "@me"`.
- Assignment means **active ownership**, not completion.
- AI assistance: the authenticated **human account** remains the GitHub
  assignee. The start-of-work comment must note that AI assistance is
  being used where project policy requires it.

### 3.3 Ownership conflicts

- An issue already assigned to another contributor may **not** be taken
  over silently.
- Collaboration on an issue requires **explicit co-assignment** or a
  written coordination comment from both parties.
- If the current assignee appears inactive, resolve through a **handoff
  comment** (see §13) before reassigning.
- Future-phase issues should **not** be bulk-assigned in advance.

---

## 4. Branch and pull-request policy

### 4.1 Branch naming

Every repository-changing issue gets one dedicated **linked** branch:

```text
<type>/<github-number>-<internal-issue-id>-<short-slug>
```

- Allowed `<type>` prefixes: `feat`, `fix`, `docs`, `refactor`, `test`,
  `chore`, `build`, `ci`, `security`.
- `<github-number>` is the GitHub issue number (e.g. `4`).
- `<internal-issue-id>` is the TODO/PLAN ID (e.g. `p2-i03`), lowercased.
- `<short-slug>` is 2–5 lowercase kebab-case words describing the scope.
- The branch must be created **from current remote `main`**.
- The branch must be **linked** to its issue through GitHub's Development
  metadata, created via:

  ```sh
  gh issue develop <N> --name <branch> --base main --checkout
  ```

  Verify with `gh issue develop --list <N>`. The branch must appear in
  the issue's "Development" section in the GitHub UI.

Do **not** substitute an ordinary unlinked branch for a linked one.

### 4.2 No-branch exceptions

Some issues do not change repository artifacts. They may be discharged
without a branch or PR. Exceptions still require assignment, an
explanatory issue comment, evidence, and synchronization per §8.
Recognised exceptions:

- decision-only issues (record the decision in PRD/PLAN via a separate
  follow-up PR if it changes documentation);
- GitHub-administration-only issues (label, milestone, ruleset changes);
- historical verification or closure issues;
- any other issue that does not change a file in the repository.

### 4.3 Pull-request workflow

- Repository-changing work uses a pull request targeting `main`.
- The PR title should end with the internal issue ID in brackets,
  e.g. `docs: establish synchronized project workflow [P2-I03]`.
- The PR body must use the synchronization checklist from
  `.github/pull_request_template.md` (§12 of this document).
- Reference the issue with `Refs #<N>`. Do **not** use an automatic
  closing keyword (`Closes`, `Fixes`, `Resolves`) — closure happens only
  after artifacts are verified on disk per §8.5 and [`docs/TODO.md`](docs/TODO.md) §F-6.
- Keep the PR scoped to the issue. If you discover unrelated cleanup,
  file a follow-up issue; do not silently expand scope.
- Resolve every PR review conversation before merge.

---

## 5. Scope discipline

- One issue → one branch → one PR is the default.
- Material new scope discovered mid-PR requires **either** a new issue
  (preferred) **or** an explicit issue comment expanding the original
  scope and an updated DoD before code lands.
- Do not delete or rewrite unrelated artifacts to "tidy up" while
  working on an issue.
- Do not bulk-edit the 62 planned issues or their bodies merely to
  introduce a new template; templates apply prospectively.

---

## 6. Verification and closure

- A PR may be merged when scope, tests, lint, and synchronization
  checks pass and reviewers approve.
- After merge, the assignee verifies the change on merged `main` (build,
  test, validator, or file inspection — whatever the artifact requires)
  and posts an **evidence comment** on the issue.
- Close the issue only after evidence is recorded. If GitHub auto-closes
  the issue from a closing keyword you did not intend to use, reopen it,
  post the missing evidence, and close manually.
- Phase milestones are closed only after **every** TODO item in the
  phase is verified and the PLAN exit criterion is met. See §8.6.

---

## 7. Issue creation

When you create a new issue, ensure it carries enough metadata for the
Synchronization Contract to function. The issue template under
`.github/ISSUE_TEMPLATE/work_item.md` requests the necessary fields:

- internal issue ID (`P<phase>-I<nn>`);
- PRD requirement reference (`FR-*`, `NFR-*`, `AC §14.*`);
- PLAN phase;
- TODO source line;
- milestone (must match the PLAN phase);
- labels from the fixed vocabulary in §11;
- dependencies (`Depends on:` / `Blocks:`);
- description;
- definition of done;
- acceptance criteria;
- synchronization requirements;
- closure rule ([`docs/TODO.md`](docs/TODO.md) §F-6).

If the new issue represents scope not already captured in
[`docs/TODO.md`](docs/TODO.md) / [`docs/PLAN.md`](docs/PLAN.md) / [`docs/PRD.md`](docs/PRD.md), update the appropriate
local document **through a reviewed PR** rather than creating GitHub-only
scope.

---

## 8. Project Tracking Synchronization Contract

This contract is binding on every contributor and AI agent.

### 8.1 At issue creation

Before opening an issue, confirm:

- the issue has an internal ID matching the TODO numbering;
- the corresponding TODO item exists;
- the PLAN phase exists and is consistent with the milestone;
- labels match the work type from §11;
- PRD requirements are referenced;
- definition of done and acceptance criteria exist.

Unilateral GitHub-only scope is not allowed. New scope must be
reflected in the appropriate Markdown document via PR.

### 8.2 At issue start

Update GitHub:

- self-assignment;
- start-of-work comment (§2 template);
- correct labels and milestone;
- linked branch (or documented branch exception per §4.2).

Do **not** mark a TODO item complete or change PLAN phase status merely
because work has started.

### 8.3 During work

Update the **issue** when there is:

- a blocker;
- a material discovery;
- an approved decision;
- a dependency change;
- a scope change;
- a handoff;
- a linked PR.

Update **repository documents** when there is:

- an approved requirement change;
- an architecture decision;
- a changed task definition;
- a changed phase outcome;
- user-facing or maintainer-facing behavior;
- required prompt or AI-usage evidence.

A material GitHub scope change must not exist without the corresponding
repository-document change. A material repository planning change must
not exist without the corresponding GitHub reconciliation.

### 8.4 In the pull request

The same PR that implements an issue should also include all required
local synchronization changes, where applicable:

- TODO checkbox or task status;
- TODO wording;
- PLAN phase status;
- PRD changes;
- README or maintainer documentation;
- AI usage (`docs/AI_USAGE.md`);
- prompt records (`docs/PROMPTS.md`);
- tests;
- validation evidence.

Do **not** postpone obvious local tracking updates to an unrelated
future PR.

### 8.5 After merge

Verify merged `main`, then on the issue:

- add an evidence comment;
- confirm acceptance criteria;
- correct accidental automatic closure if verification has not passed;
- close the issue **only after** evidence is complete.

### 8.6 At phase completion

Reconcile:

- every issue in the milestone (verify state and evidence);
- every TODO item in the PLAN phase (verify artifact on disk);
- the PLAN phase exit criterion;
- required PRD acceptance criteria;
- tests, builds, and validator runs;
- milestone issue counts and states.

Only after all of the above:

- mark the PLAN phase complete in [`docs/PLAN.md`](docs/PLAN.md);
- close the corresponding GitHub milestone.

### 8.7 Before every contributor stops

Run a final reconciliation **before ending the session**:

- repository working-tree state (`git status --short` clean);
- branch push state (local matches `origin/<branch>`);
- issue assignment is correct;
- issue state reflects current progress;
- linked branch is present;
- linked PR is present (or branch exception documented);
- TODO item status matches reality;
- PLAN status matches reality;
- milestone state matches reality;
- outstanding blockers are recorded in an issue comment;
- a handoff is posted if work is unfinished (§13).

No session — human or AI — may end with known silent drift.

---

## 9. Drift handling

Inconsistencies between the Markdown documents and GitHub will happen.
Resolve them, do not paper over them.

Common drift patterns:

- TODO checked but issue open;
- issue closed but TODO unchecked;
- issue in wrong milestone;
- issue scope differs from TODO;
- PLAN says phase complete while milestone is open;
- milestone closed with unresolved required issue;
- branch exists but is not linked to its issue;
- PR merged but issue lacks evidence;
- issue assigned to inactive contributor.

Resolution rules:

1. Stop new dependent work.
2. Identify the **verified artifact state** on disk and via tests.
3. Treat artifacts and test results as the **completion evidence** — not
   the checkboxes, not the issue state.
4. Reconcile both local documentation **and** GitHub.
5. Record the correction in an issue comment.
6. Use a dedicated issue-linked branch when repository files must change.
7. Never silently choose one tracker and ignore the other.

---

## 10. Ownership rules (summary)

- Work may not begin without an issue.
- The active contributor must self-assign.
- An issue assigned to another person may not be taken over silently.
- Collaboration requires explicit co-assignment or written
  coordination.
- Future-phase issues should not be bulk-assigned.
- Assignment means active ownership, not completion.
- Inactive ownership is resolved through a handoff comment (§13)
  before reassignment.
- For AI-assisted work, the **authenticated human account** is the
  GitHub assignee.

---

## 11. Label vocabulary

Issues use the fixed vocabulary below (in addition to GitHub default
labels where useful). Add or remove labels only through a reviewed
governance change.

| Label          | Use                                                        |
|----------------|------------------------------------------------------------|
| `docs`         | Documentation, Markdown, PRD work.                         |
| `architecture` | Project structure, mechanism design.                       |
| `crewai`       | CrewAI agents, tasks, prompts, crew assembly.              |
| `latex`        | LaTeX project, preamble, macros, build wiring.             |
| `validation`   | Deterministic `ValidatorService` and PDF/content checks.   |
| `bidi`         | Hebrew/English BiDi formatting and fonts.                  |
| `bibliography` | `references.bib`, citations, source verification.          |
| `testing`      | Tests, lint, reproducibility.                              |
| `submission`   | Final Moodle bundle, wrapper PDF, checklist.               |
| `decision`     | Decision-only issues with no repository artifact change.   |
| `security`     | Secrets handling, sandboxing, untrusted-source policy.     |

---

## 12. Pull-request synchronization checklist

The PR template at `.github/pull_request_template.md` requires the
author to confirm:

- GitHub issue number;
- internal issue ID;
- PRD reference;
- PLAN phase;
- TODO item;
- assignee confirmed;
- linked branch confirmed;
- milestone and labels confirmed;
- dependencies satisfied;
- scope respected;
- changed artifacts listed;
- tests / lint / build / validator results;
- TODO synchronized;
- PLAN synchronized where relevant;
- PRD synchronized where relevant;
- README and maintainer docs synchronized;
- AI usage and prompts updated where required;
- known limitations recorded;
- no premature completion claim;
- post-merge verification required;
- issue and milestone state reconciled.

Do not delete sections of the checklist when none are applicable —
mark them `N/A` and add one line explaining why.

---

## 13. Handoff protocol

When work is unfinished — at the end of a session, on a blocker, or
when transferring ownership — the assignee posts a handoff comment on
the issue. Use this template:

```markdown
## Handoff — <reason>

- Issue: #<N> (`P<phase>-I<nn>`), URL: <issue-url>
- Milestone: <milestone title>
- Labels: <labels>
- Assignee(s): <login(s)>
- Branch: `<branch-name>` (linked: yes/no)
- Current commit: <short-sha> on `<branch>`
- PR: #<PR-N>, URL: <pr-url> (or "not yet opened")

### Completed
- ...

### Remaining
- ...

### Modified files
- ...

### Tests already run
- `uv run pytest` — <result>
- `uv run ruff check .` — <result>
- other: <result>

### Tests still required
- ...

### Blockers
- ...

### Decisions
- ...

### Local tracking status
- `docs/TODO.md`: <up-to-date / pending update — describe>
- `docs/PLAN.md`: <up-to-date / pending update — describe>
- `docs/PRD.md`: <up-to-date / not affected>

### GitHub tracking status
- Issue state: <open/closed>, assignee correct: <yes/no>
- Milestone state: <open/closed>
- Linked branch / PR present: <yes/no>

### Working tree / push state
- `git status --short`: <output or "clean">
- local branch vs `origin/<branch>`: <ahead/behind/synced>

### Exact next action
- ...
```

A complete handoff is the only acceptable way to leave an issue in an
inconsistent state across sessions. Drift without a handoff is a
contract violation under §8.7.

---

## 14. Drift recovery for already-open issues

The 62 existing issues opened during P2-I02 predate this contract. They
are **not** retroactively rewritten. As each issue is picked up:

- the assignee reads its body for `Source`, `Description`,
  `Dependencies`, `Definition of done`, `Acceptance criteria`, and
  `Closure rule`;
- the start-of-work comment confirms onboarding (§2 template);
- the PR carries the synchronization checklist;
- evidence is recorded on the issue after merge.

If an existing issue body lacks any of the structured sections, do not
rewrite it in place. File a small follow-up issue tagged `docs` that
fixes the metadata, or extend the closure comment with the missing
information.

---

## 15. Emergency exceptions

Genuine emergencies (broken `main`, leaked secret, accidental force
push) may require bypassing parts of this workflow. When that happens:

- act quickly to contain the damage;
- create a follow-up `security` or `chore` issue **within the same
  session** describing what was bypassed and why;
- record the emergency in the next PR's description and in the issue's
  closure evidence;
- review and tighten the contract afterwards if a structural gap was
  found.

No emergency exception is allowed to silently change the rules in this
document. Permanent rule changes require a PR.

---

## 16. Quick reference

```sh
# Onboarding (per issue)
gh issue view <N>
gh issue view <N> --comments
gh issue edit <N> --add-assignee "@me"
gh issue develop <N> --name <branch> --base main --checkout

# Working
git status --short
git fetch origin --no-tags
uv run pytest
uv run ruff check .

# Stopping (sync contract §8.7)
git status --short
git push origin <branch>
gh issue view <N>
gh issue develop --list <N>
gh pr list --head <branch>

# Phase completion
gh issue list --milestone "<title>" --state all
# verify each TODO item in docs/TODO.md is satisfied on disk
# update docs/PLAN.md phase status
gh api repos/<owner>/<repo>/milestones/<num> -X PATCH -f state=closed
```

---

Last reviewed: 2026-06-13 under issue P2-I03 (#4).
