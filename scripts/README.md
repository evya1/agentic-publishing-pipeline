# scripts/

Operator scripts for the project.

## render_latex_project.py — Phase 9 LaTeX inspection tool

Inspect or render the Phase 9 LaTeX project without invoking a TeX compiler.
Three mutually exclusive modes:

```sh
# Check upstream inputs (preflight validation only)
uv run python scripts/render_latex_project.py --check-inputs

# Render a source preview to a temporary directory
uv run python scripts/render_latex_project.py --render-to /tmp/phase9-preview

# Compare a rendered tree against the current plan (detect drift)
uv run python scripts/render_latex_project.py --check-tree /tmp/phase9-preview
```

Exits 0 on success, 2 on preflight failure, 3 on tree drift.
Config defaults to `config/latex/phase9_project.yaml`; pass `--config` to override.

## sync_milestones.py

Verifies that the 13 GitHub milestones for Phases 2–14 match the manifest
in `config/milestones.json`, and (when explicitly confirmed) creates only
the milestones that are missing.

### Operations

The tool has three operations. **Verification is the default; nothing
writes unless `apply --confirm` is passed and the live state already
validates as conflict-free.**

All examples use `uv run python` so the script executes inside the
project's resolved environment.

```sh
# Read-only verification — exits 0 only if live state matches manifest.
uv run python scripts/sync_milestones.py verify

# Show what apply would do without writing.
uv run python scripts/sync_milestones.py dry-run

# Create only the missing milestones (idempotent no-op if state matches).
uv run python scripts/sync_milestones.py apply --confirm
```

### Repository selection

By default the tool resolves the current repository via `gh repo view`.
Pass `--repo OWNER/NAME` to operate against a specific repository. The
selected repository is always echoed before any operation:

```sh
uv run python scripts/sync_milestones.py verify --repo evya1/agentic-publishing-pipeline
```

### Safety guarantees

- `apply` always lists the live milestones first and aborts with **zero
  writes** if any structural conflict is detected: an unexpected extra
  milestone, a duplicate live title, a description mismatch, a non-null
  live `due_on`, or a malformed manifest.
- `apply` only ever **creates** milestones. It never deletes a milestone,
  never modifies an existing description, and never changes open/closed
  state. The project workflow expects milestones to be closed by hand
  when the corresponding PLAN phase wraps up.
- When live state already matches the manifest, `apply --confirm` issues
  **zero API writes** and exits 0. This is the idempotency guarantee
  the issue #2 acceptance criterion calls for.
- The tool does not claim transactional atomicity across network
  failures. It claims that validation conflicts abort before any write
  and that a matching live state is an idempotent no-op.

### Exit codes

| Code | Meaning                                                         |
|-----:|-----------------------------------------------------------------|
|    0 | Operation succeeded (state matches manifest, or apply created the missing milestones). |
|    1 | Live state diverges from manifest (verify, dry-run, or post-apply verification). |
|    2 | Manifest file is missing, unreadable, or invalid.               |
|    3 | `gh` invocation failed or `gh` is not on `PATH`.                |
|    4 | `apply` was called without `--confirm`.                         |
|    5 | `apply` aborted before any write because a structural conflict was detected. |

### Tests

Hermetic tests live in:

- `tests/test_milestone_manifest.py` — manifest parsing/validation;
- `tests/test_milestone_diff.py` — `compute_diff` state classification;
- `tests/test_milestone_verify.py` — `verify` and `dry_run` read-only ops;
- `tests/test_milestone_apply.py` — `apply` idempotency and abort-before-write;
- `tests/test_milestone_cli.py` — `main` dispatch and preflight error paths;
- `tests/test_milestone_gh_adapter.py` — gh subprocess success and error paths;
- `tests/test_milestone_pagination.py` — paginated reads and pre-write output;
- `tests/conftest.py` — shared `FakeClient` and fixtures.

They never invoke `gh` and never touch the network. The CLI and adapter
tests use `monkeypatch` to substitute a fake client or a fake `subprocess.run`.

```sh
uv run pytest tests/test_milestone_apply.py tests/test_milestone_cli.py \
              tests/test_milestone_diff.py tests/test_milestone_gh_adapter.py \
              tests/test_milestone_manifest.py tests/test_milestone_pagination.py \
              tests/test_milestone_verify.py --cov=scripts --cov-report=term-missing
```
