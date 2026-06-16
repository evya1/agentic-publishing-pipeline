from pathlib import Path

from agentic_publishing_pipeline.latex.project_renderer import build_project_plan
from agentic_publishing_pipeline.latex.standalone import compare_plan, write_plan


def test_project_plan_contains_all_phase9_structures(tmp_path: Path, config, manuscript) -> None:
    bib = tmp_path / "references.bib"
    graph = tmp_path / "graph.png"
    bib.write_text("@article{known, title={Known}, year={2026}}\n", encoding="utf-8")
    graph.write_bytes(b"png")
    plan = build_project_plan(
        manuscript=manuscript,
        config=config,
        bibliography_path=bib,
        graph_path=graph,
    )
    by_name = {item.relative_path: item.content for item in plan.text_files}
    assert {"main.tex", "preamble.tex", "macros.tex", "titlepage.tex"} <= set(by_name)
    assert "tables/table.tex" in by_name
    assert "figures/loop.tex" in by_name
    assert "components/equation.tex" in by_name
    assert not any(name.startswith("assemblies/") for name in by_name)
    assert "\\input{chapters/01_planning}" in by_name["main.tex"]
    chapter = by_name["chapters/01_planning.tex"]
    assert "\\input{tables/table}" in chapter
    assert "\\input{figures/loop}" in chapter
    assert "\\begin{table}" not in chapter
    assert "\\begin{tikzpicture}" not in chapter
    target = tmp_path / "rendered"
    write_plan(plan, target)
    assert compare_plan(plan, target).clean
