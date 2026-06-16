# CI Protection — Phase 1–7 Regression Guards

Added in issue #84 (P5-I13-ext). These workflows protect completed Phase 1–7 work from regressions during Phases 8–14.

## Workflows

| File | Trigger | Purpose |
|------|---------|---------|
| `ci-core.yml` | PR, push to main, manual | Lint, format, tests (≥85% coverage), line-cap, build, dry-run and offline-fixture smokes |
| `baseline-contracts.yml` | PR, push to main, manual | Deterministic Phase 1–7 contract checks |
| `artifact-pipeline.yml` | PR, push to main, manual | Permanent CI stubs for Phases 8–14 (skip gracefully when not yet implemented) |
| `security.yml` | PR, push to main, weekly | Dependency review, CodeQL, policy checks, workflow linting |

## Supporting scripts

All scripts in `scripts/` exit 0 on success, 1 on failure.

| Script | What it checks |
|--------|---------------|
| `check_docs_present.py` | Required docs exist (README, PRD, PLAN, TODO, mechanism PRDs, SUBMISSION_CHECKLIST) |
| `check_planning_ids.py` | Planning IDs in TODO.md are unique |
| `check_no_secrets.py` | No `.env` files or secret patterns are tracked |
| `check_source_archives.py` | No downloaded source archives are committed |
| `check_phase_order.py` | Phase-order protection for `phase/NN-*` branches |
| `check_workflow_permissions.py` | Workflow files declare minimal permissions |
| `check_latex_structure.py` | LaTeX project follows PRD §8.5 conventions (active in Phase 9+) |
| `check_line_cap.py` | Python files stay within 150-line limit |

## Key design decisions

- **No paid API or LLM calls in CI.** Dry-run and offline-fixture modes are tested explicitly.
- **Third-party Actions pinned to full commit SHAs.** Mutable tags are not used.
- **Artifact pipeline jobs skip gracefully** when a phase is not yet implemented — they never fail on unimplemented future work.
- **Phase-order checks** only run on `phase/NN-*` PR branches; they do not block non-phase work.
- `phase5-validation.yml` is superseded by `ci-core.yml` and kept for backwards compatibility with existing required checks. It will be removed once repository protection is updated to reference the new check names.
