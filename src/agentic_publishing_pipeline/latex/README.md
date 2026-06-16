# latex/

Deterministic Phase 9 LaTeX project assembly. Converts human-approved
canonical Markdown into a structured LaTeX source tree. Never compiles
a PDF — compilation belongs to Phase 10 (`tools/latex_build.py`).

## Module responsibilities

| Module | Responsibility |
|--------|----------------|
| `config_loader.py` | Load `config/latex/phase9_project.yaml` with path-traversal protection |
| `config_models.py` | Validated Pydantic models for Phase 9 configuration |
| `approval_loader.py` | Enforce review gate, load exact approved chapter set |
| `preflight.py` | Validate chapter order, word counts, Hebrew content, citations, graph |
| `outline.py` | Extract chapter IDs from the Phase 6 outline |
| `bibliography.py` | Read verified BibLaTeX keys; copy bibliography bytes exactly |
| `markdown_renderer.py` | Strict project Markdown → LaTeX block renderer |
| `inline.py` | Restricted inline Markdown (bold, italic, code, citations only) |
| `hebrew.py` | Render Hebrew paragraphs with Polyglossia LTR runs |
| `templates.py` | Deterministic preamble, macros, main.tex, nomenclature templates |
| `metadata.py` | Title page and metadata command rendering |
| `asset_plan.py` | Translate semantic assets to standalone files and chapter includes |
| `assets_figures.py` | Canonical graph wrapper and standalone TikZ rendering |
| `assets_math.py` | Allowlisted equation, equation_ref, and theorem rendering |
| `assets_table.py` | Standalone table rendering from semantic payload |
| `project_renderer.py` | Assemble full file plan from manuscript + config + assets |
| `file_plan.py` | Validated in-memory file plan with duplicate/unsafe path guards |
| `materialize.py` | Write file plan via FileIO and register artifacts in manifest |
| `project_spec.py` | Build `LaTeXProjectSpec` v1 contract from manuscript + config |
| `standalone.py` | Safe standalone write and tree comparison helpers |
| `phase9_runner.py` | Top-level orchestration: validate → plan → materialize → register |

## Entry points

```python
from agentic_publishing_pipeline.latex import assemble_phase9_project

# Via CLI:
uv run python -m agentic_publishing_pipeline --mode assemble-phase9

# Via inspection script:
uv run python scripts/render_latex_project.py --check-inputs
uv run python scripts/render_latex_project.py --render-to /tmp/preview
uv run python scripts/render_latex_project.py --check-tree /tmp/preview
```

## Boundaries

- Reads only from paths under `repo_root` validated by `config_loader`.
- Writes only through `FileIO` into the run workspace (`WorkspacePaths`).
- Never invokes a TeX compiler; that seam is `tools/latex_build.py`.
- Never regenerates bibliography (Phase 7) or graph (Phase 8) data.
- Stops with `Phase9InputNotReady` if any upstream gate fails.

See `docs/PRD_latex_generation.md` and `docs/architecture/adrs/ADR-0003-deterministic-latex-rendering.md`.
