from pathlib import Path

from agentic_publishing_pipeline.latex.preflight import run_phase9_preflight


def _sources(tmp_path: Path) -> tuple[Path, Path, Path]:
    outline = tmp_path / "outline.md"
    bib = tmp_path / "references.bib"
    graph = tmp_path / "graph.png"
    outline.write_text(
        "# Outline\n\n## Planning\n\nSummary\n\n## Memory\n\nSummary\n",
        encoding="utf-8",
    )
    bib.write_text("@article{known,\n title={Known},\n year={2026}\n}\n", encoding="utf-8")
    graph.write_bytes(b"png")
    return outline, bib, graph


def test_complete_synthetic_input_passes(tmp_path: Path, config, manuscript) -> None:
    outline, bib, graph = _sources(tmp_path)
    report = run_phase9_preflight(
        manuscript=manuscript,
        config=config,
        outline_path=outline,
        bibliography_path=bib,
        graph_path=graph,
    )
    assert report.passed
    assert report.hebrew_words >= 2


def test_current_main_shape_is_blocked(tmp_path: Path, config, manuscript) -> None:
    outline, bib, graph = _sources(tmp_path)
    config.minimum_total_words = 4500
    config.minimum_hebrew_words = 120
    config.metadata.authors = []
    config.metadata.group_code = ""
    report = run_phase9_preflight(
        manuscript=manuscript,
        config=config,
        outline_path=outline,
        bibliography_path=bib,
        graph_path=graph,
    )
    assert not report.passed
    assert any("authors" in error for error in report.errors)
    assert any("Hebrew words" in error for error in report.errors)


def test_preflight_enforces_bibliography_and_chapter_citations(
    tmp_path: Path, config, manuscript
) -> None:
    outline, bib, graph = _sources(tmp_path)
    bib.write_text(
        "@article{known, title={Known}, year={2026}}\n"
        "@article{required, title={Required}, year={2026}}\n",
        encoding="utf-8",
    )
    config.require_all_bibliography_entries = True
    config.chapter_citation_requirements = {"memory": ["required"]}
    report = run_phase9_preflight(
        manuscript=manuscript,
        config=config,
        outline_path=outline,
        bibliography_path=bib,
        graph_path=graph,
    )
    assert not report.passed
    assert any("not cited" in error for error in report.errors)
    assert any("memory: required citations missing" in error for error in report.errors)


def test_preflight_rejects_unresolved_placeholder(tmp_path: Path, config, manuscript) -> None:
    outline, bib, graph = _sources(tmp_path)
    manuscript.chapters[0].path.write_text(
        "# Planning\n\nText \\cite{known}.\n\n<!-- FIGURE: unresolved -->\n",
        encoding="utf-8",
    )
    altered = type(manuscript)(
        root=manuscript.root,
        revision=manuscript.revision,
        chapters=(
            type(manuscript.chapters[0])(
                "planning",
                manuscript.chapters[0].path,
                manuscript.chapters[0].path.read_text(encoding="utf-8"),
            ),
            manuscript.chapters[1],
        ),
    )
    report = run_phase9_preflight(
        manuscript=altered,
        config=config,
        outline_path=outline,
        bibliography_path=bib,
        graph_path=graph,
    )
    assert not report.passed
    assert any("unresolved Markdown placeholders" in error for error in report.errors)
