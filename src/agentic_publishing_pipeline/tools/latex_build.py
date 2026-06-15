"""LaTeX compilation tool — deterministic LuaLaTeX + biber multi-pass.

Per ADR-0007 and FR-20, the canonical MVP engine is LuaLaTeX. This
tool encapsulates the multi-pass subprocess sequence:

    lualatex (-interaction=nonstopmode -halt-on-error)
    biber
    lualatex
    lualatex

…with fixed command-line arguments, an overall timeout, and a
captured/parsed build log that becomes :class:`BuildResult` v1.

The actual binaries (``lualatex``, ``biber``) are not required for
this module to import or to be tested; tests inject a fake
subprocess runner. The :class:`LaTeXBuildError` separates "the
toolchain is not installed" from "the build failed" so the CLI can
surface the right message.
"""

from __future__ import annotations

import shutil
import subprocess
import time
from collections.abc import Callable
from pathlib import Path

from ..contracts import BuildPass, BuildResult


class LaTeXBuildError(RuntimeError):
    """Raised on missing toolchain or non-zero exit."""


SubprocessRunner = Callable[[list[str], Path, float], tuple[int, str]]


def _default_runner(cmd: list[str], cwd: Path, timeout: float) -> tuple[int, str]:
    completed = subprocess.run(  # noqa: S603
        cmd,
        cwd=str(cwd),
        capture_output=True,
        timeout=timeout,
        check=False,
        text=True,
    )
    log = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode, log


def _ensure_binaries(*, allow_missing: bool) -> None:
    missing = [b for b in ("lualatex", "biber") if shutil.which(b) is None]
    if missing and not allow_missing:
        raise LaTeXBuildError(
            "missing required LaTeX binaries: " + ", ".join(missing)
        )


def _parse_log(log: str) -> tuple[list[str], list[str]]:
    warnings = [line.strip() for line in log.splitlines() if "Warning" in line]
    errors = [line.strip() for line in log.splitlines() if line.startswith("! ")]
    return warnings, errors


def _lualatex_command(main_tex_stem: str) -> list[str]:
    return [
        "lualatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"{main_tex_stem}.tex",
    ]


def _biber_command(main_tex_stem: str) -> list[str]:
    return ["biber", main_tex_stem]


def build_pdf(
    *,
    run_id: str,
    project_dir: Path,
    main_tex_stem: str = "main",
    timeout_per_pass: float = 120.0,
    runner: SubprocessRunner | None = None,
    allow_missing_binaries: bool = False,
) -> BuildResult:
    """Run the LuaLaTeX + biber multi-pass build and return BuildResult v1."""

    assert project_dir.is_dir(), f"project_dir must be a directory: {project_dir}"
    main_tex = project_dir / f"{main_tex_stem}.tex"
    assert main_tex.is_file(), f"missing main tex: {main_tex}"
    _ensure_binaries(allow_missing=allow_missing_binaries or runner is not None)
    run = runner or _default_runner
    passes: list[BuildPass] = []
    full_log: list[str] = []
    commands = [
        _lualatex_command(main_tex_stem),
        _biber_command(main_tex_stem),
        _lualatex_command(main_tex_stem),
        _lualatex_command(main_tex_stem),
    ]
    for command in commands:
        started = time.monotonic()
        exit_code, log = run(command, project_dir, timeout_per_pass)
        duration = time.monotonic() - started
        passes.append(
            BuildPass(
                command=command,
                exit_code=exit_code,
                duration_seconds=round(duration, 4),
                log_excerpt="\n".join(log.splitlines()[-40:]),
            )
        )
        full_log.append(log)
        if exit_code != 0:
            break
    warnings, errors = _parse_log("\n".join(full_log))
    pdf_path = project_dir / f"{main_tex_stem}.pdf"
    pdf_field = str(pdf_path) if pdf_path.exists() else None
    return BuildResult(
        run_id=run_id,
        engine="lualatex",
        passes=passes,
        pdf_path=pdf_field,
        parsed_warnings=warnings,
        parsed_errors=errors,
    )
