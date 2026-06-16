# visualization/

> **Status:** Phase 8 implementation in progress on a feature branch.

This package owns the deterministic Python graph pipeline for canonical
article figures. The production path is:

`config/graphs/*.yaml` -> strict validation -> Matplotlib Agg render ->
workspace writes via `FileIO` -> provenance JSON -> explicit promotion to
`latex_project/figures/`

## Command

```sh
uv run python -m agentic_publishing_pipeline.visualization \
  --spec config/graphs/planning_benchmark_comparison.yaml \
  --overwrite-existing
```

Add `--output-root /tmp/graph-run` to render and promote into an isolated
root for determinism checks.

## Modules

| Module | Purpose |
|---|---|
| `models.py` | Strict typed graph-spec models (`extra="forbid"`) |
| `validator.py` | YAML loading and deterministic validation with field paths |
| `naming.py` | Safe slug/path validation and deterministic filenames |
| `graph.py` | Matplotlib Agg renderers; low-level line-plot helper for smoke runs |
| `provenance.py` | Versioned provenance payload builder |
| `render_pipeline.py` | Workspace render + manifest registration + promotion |
| `cli.py` / `__main__.py` | `python -m` command surface |

## Scope boundary

- Phase 8 owns graph specs, validation, PNG generation, provenance, and
  deterministic regeneration evidence.
- Phase 9 owns LaTeX chapter integration and `\includegraphics`.

## Canonical artifact

- Spec: `config/graphs/planning_benchmark_comparison.yaml`
- Source: `correa2025planningperformance` (`arXiv:2511.09378v2`)
- Output: `latex_project/figures/planning_benchmark_comparison_<hash>.png`
- Provenance: matching `.png.prov.json`
