"""LaTeX compilation-tool tests using a fake subprocess runner."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_publishing_pipeline.tools import LaTeXBuildError, build_pdf


def _seed_project(tmp_path: Path) -> Path:
    project = tmp_path / "latex_project"
    project.mkdir()
    (project / "main.tex").write_text(
        "\\documentclass{article}\n\\begin{document}\nHi\n\\end{document}\n",
        encoding="utf-8",
    )
    return project


def _fake_pdf_runner(commands_observed: list[list[str]], *, fail_at: int | None = None):
    def runner(cmd: list[str], cwd: Path, timeout: float) -> tuple[int, str]:
        commands_observed.append(cmd)
        if fail_at is not None and len(commands_observed) >= fail_at:
            return 1, "! LaTeX Error: synthetic\n"
        if cmd[0] == "lualatex":
            (cwd / "main.pdf").write_bytes(b"%PDF-1.5\n%%EOF\n")
        return 0, "Output written on main.pdf (1 page).\nLaTeX Warning: minor\n"
    return runner


def test_build_succeeds_with_fake_runner(tmp_path: Path) -> None:
    project = _seed_project(tmp_path)
    observed: list[list[str]] = []
    result = build_pdf(
        run_id="RUN-20260615-000000-aaaaaaaa",
        project_dir=project,
        runner=_fake_pdf_runner(observed),
    )
    assert result.succeeded is True
    assert result.engine == "lualatex"
    assert len(observed) == 4
    assert observed[0][0] == "lualatex"
    assert observed[1][0] == "biber"
    assert result.parsed_warnings


def test_build_stops_on_first_failure(tmp_path: Path) -> None:
    project = _seed_project(tmp_path)
    observed: list[list[str]] = []
    result = build_pdf(
        run_id="RUN-20260615-000000-bbbbbbbb",
        project_dir=project,
        runner=_fake_pdf_runner(observed, fail_at=2),
    )
    assert result.succeeded is False
    assert len(result.passes) == 2
    assert result.parsed_errors


def test_build_missing_main_tex_refused(tmp_path: Path) -> None:
    project = tmp_path / "latex_project"
    project.mkdir()
    with pytest.raises(AssertionError):
        build_pdf(
            run_id="RUN-20260615-000000-cccccccc",
            project_dir=project,
            runner=_fake_pdf_runner([]),
        )


def test_build_pdf_path_is_none_without_pdf(tmp_path: Path) -> None:
    project = _seed_project(tmp_path)

    def runner(cmd: list[str], cwd: Path, timeout: float) -> tuple[int, str]:
        return 0, "no pdf produced\n"

    result = build_pdf(
        run_id="RUN-20260615-000000-dddddddd",
        project_dir=project,
        runner=runner,
    )
    assert result.pdf_path is None
    assert result.succeeded is False


def test_missing_binaries_refused_without_override(tmp_path: Path) -> None:
    project = _seed_project(tmp_path)
    # Default runner pathway with no runner provided AND binaries absent.
    import shutil
    if shutil.which("lualatex") and shutil.which("biber"):
        pytest.skip("real LaTeX toolchain present; cannot exercise missing-binaries path")
    with pytest.raises(LaTeXBuildError):
        build_pdf(run_id="RUN-20260615-000000-eeeeeeee", project_dir=project)
