"""P12-I03: Tests for ValidatorService (P11-I01..I06)."""

from __future__ import annotations

from pathlib import Path

from agentic_publishing_pipeline.validation import ValidationReport, ValidatorService
from agentic_publishing_pipeline.validation.checks_citations import (
    _extract_bib_keys,
    _extract_cited_keys,
)
from agentic_publishing_pipeline.validation.checks_latex import (
    _check_chapter_separation,
)
from agentic_publishing_pipeline.validation.checks_repo import run_repo_checks

# ---------------------------------------------------------------------------
# ValidationReport data type
# ---------------------------------------------------------------------------


def test_report_passes_when_all_checks_pass() -> None:
    report = ValidationReport()
    report.add("foo", True, "ok")
    report.add("bar", True, "ok")
    assert report.passed is True


def test_report_fails_when_any_check_fails() -> None:
    report = ValidationReport()
    report.add("foo", True, "ok")
    report.add("bar", False, "missing")
    assert report.passed is False


def test_report_to_markdown_contains_table(tmp_path: Path) -> None:
    report = ValidationReport(repo_root=tmp_path)
    report.add("alpha", True, "ok")
    report.add("beta", False, "oops")
    md = report.to_markdown()
    assert "| alpha | PASS |" in md
    assert "| beta | FAIL |" in md
    assert "Overall: **FAIL**" in md


# ---------------------------------------------------------------------------
# Repository file checks
# ---------------------------------------------------------------------------


def _make_min_repo(tmp_path: Path) -> Path:
    """Create a minimal directory tree that passes repo checks."""
    (tmp_path / "README.md").write_text("# readme")
    for doc in ["PRD.md", "PLAN.md", "TODO.md", "AI_USAGE.md", "PROMPTS.md"]:
        (tmp_path / "docs" / doc).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs" / doc).write_text(f"# {doc}")
    (tmp_path / ".env-example").write_text("KEY=value")
    for d in [
        "src/agentic_publishing_pipeline",
        "tests",
        "config",
        "latex_project",
        "results/generated_markdown",
        "results/run_logs",
    ]:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    (tmp_path / "results" / "final.pdf").write_bytes(b"%PDF-1.4 fake")
    return tmp_path


def test_repo_checks_pass_on_complete_tree(tmp_path: Path) -> None:
    repo = _make_min_repo(tmp_path)
    report = ValidationReport()
    run_repo_checks(repo, report)
    failing = [r for r in report.results if not r.passed]
    assert failing == [], f"unexpected failures: {[r.name for r in failing]}"


def test_repo_checks_fail_on_missing_pdf(tmp_path: Path) -> None:
    repo = _make_min_repo(tmp_path)
    (repo / "results" / "final.pdf").unlink()
    report = ValidationReport()
    run_repo_checks(repo, report)
    pdf_result = next(r for r in report.results if r.name == "artifact:results/final.pdf")
    assert pdf_result.passed is False


def test_repo_checks_fail_on_missing_env_example(tmp_path: Path) -> None:
    repo = _make_min_repo(tmp_path)
    (repo / ".env-example").unlink()
    report = ValidationReport()
    run_repo_checks(repo, report)
    env_result = next(r for r in report.results if r.name == "file:.env-example")
    assert env_result.passed is False


# ---------------------------------------------------------------------------
# LaTeX structure checks (FR-17a-d separation)
# ---------------------------------------------------------------------------


def _make_latex_dir(tmp_path: Path, chapter_content: str = "") -> Path:
    latex = tmp_path / "latex_project"
    latex.mkdir(parents=True, exist_ok=True)
    for name in ["main.tex", "preamble.tex", "macros.tex"]:
        (latex / name).write_text(r"\input{preamble}" if name == "main.tex" else "% ok")
    (latex / "references.bib").write_text("@article{key,title={T},author={A},year={2024}}")
    (latex / "chapters").mkdir(parents=True)
    (latex / "chapters" / "intro.tex").write_text(chapter_content or r"\chapter{Intro} text")
    (latex / "chapters" / "body.tex").write_text(r"\chapter{Body} more text")
    (latex / "tables").mkdir()
    (latex / "tables" / "t1.tex").write_text(r"\begin{tabular}{c} x \end{tabular}")
    (latex / "figures").mkdir()
    (latex / "figures" / "fig.tex").write_text(r"\begin{tikzpicture}\end{tikzpicture}")
    return latex


def test_latex_separation_passes_clean_chapters(tmp_path: Path) -> None:
    latex = _make_latex_dir(tmp_path)
    report = ValidationReport()
    _check_chapter_separation(latex, report)
    result = next(r for r in report.results if r.name == "latex:fr17_separation")
    assert result.passed is True


def test_latex_separation_fails_inline_table(tmp_path: Path) -> None:
    latex = _make_latex_dir(tmp_path, r"\chapter{X} \begin{table}[h] bad \end{table}")
    report = ValidationReport()
    _check_chapter_separation(latex, report)
    result = next(r for r in report.results if r.name == "latex:fr17_separation")
    assert result.passed is False
    assert "table" in result.message.lower()


def test_latex_separation_fails_inline_tikz(tmp_path: Path) -> None:
    latex = _make_latex_dir(tmp_path, r"\chapter{X} \begin{tikzpicture} bad \end{tikzpicture}")
    report = ValidationReport()
    _check_chapter_separation(latex, report)
    result = next(r for r in report.results if r.name == "latex:fr17_separation")
    assert result.passed is False
    assert "tikz" in result.message.lower()


# ---------------------------------------------------------------------------
# Citation checks
# ---------------------------------------------------------------------------


def _write_bib(tmp_path: Path, keys: list[str]) -> Path:
    path = tmp_path / "references.bib"
    entries = "\n".join(
        f"@article{{{k},\n  title={{T}},\n  author={{A}},\n  year={{2024}}\n}}"
        for k in keys
    )
    path.write_text(entries)
    return path


def test_bib_key_extraction(tmp_path: Path) -> None:
    bib = _write_bib(tmp_path, ["foo2024bar", "baz2025qux"])
    keys = _extract_bib_keys(bib)
    assert keys == {"foo2024bar", "baz2025qux"}


def test_cite_key_extraction(tmp_path: Path) -> None:
    tex = tmp_path / "ch.tex"
    tex.write_text(r"see \cite{foo2024bar} and \cite[p.1]{baz2025qux}")
    keys = _extract_cited_keys(tmp_path)
    assert keys == {"foo2024bar", "baz2025qux"}


def test_undefined_cite_causes_failure(tmp_path: Path) -> None:
    from agentic_publishing_pipeline.validation.checks_citations import run_citation_checks

    _write_bib(tmp_path, ["knownkey"])
    (tmp_path / "ch.tex").write_text(r"\cite{knownkey} and \cite{missingkey}")
    report = ValidationReport()
    run_citation_checks(tmp_path, report)
    result = next(r for r in report.results if r.name == "citations:all_resolve")
    assert result.passed is False
    assert "missingkey" in result.message


def test_all_citations_resolve(tmp_path: Path) -> None:
    from agentic_publishing_pipeline.validation.checks_citations import run_citation_checks

    _write_bib(tmp_path, ["alpha", "beta"])
    (tmp_path / "ch.tex").write_text(r"\cite{alpha} \cite{beta}")
    report = ValidationReport()
    run_citation_checks(tmp_path, report)
    result = next(r for r in report.results if r.name == "citations:all_resolve")
    assert result.passed is True


# ---------------------------------------------------------------------------
# ValidatorService integration (smoke test against the real repo)
# ---------------------------------------------------------------------------


def test_validator_service_passes_on_real_repo() -> None:
    repo_root = Path(__file__).parent.parent.parent
    service = ValidatorService(repo_root=repo_root)
    report = service.run()
    failing = [r for r in report.results if not r.passed]
    assert failing == [], f"failing checks: {[(r.name, r.message) for r in failing]}"
