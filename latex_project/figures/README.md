# latex_project/figures/

Tracked image artifacts live here once they have been generated through a
deterministic pipeline and promoted into the canonical LaTeX project.

## Canonical Phase 8 artifact

- Spec: `config/graphs/planning_benchmark_comparison.yaml`
- Output: `planning_benchmark_comparison_<spec-hash>.png`
- Provenance: matching `.png.prov.json`
- Source locator: `correa2025planningperformance`, Tables 1 and 2,
  row `Sum (360)`

Regenerate with:

```sh
uv run python -m agentic_publishing_pipeline.visualization \
  --spec config/graphs/planning_benchmark_comparison.yaml \
  --overwrite-existing
```

Phase 8 stops at artifact generation. Chapter-level `\includegraphics`
integration remains Phase 9 work.
