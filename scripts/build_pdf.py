"""Multi-pass LuaLaTeX build script for the agentic-publishing-pipeline report.

Build sequence (per main.tex header and PRD §16.3):
  lualatex → biber → makeindex (nomenclature) → makeindex (index)
  → lualatex → lualatex

Compiles in-place inside latex_project/ (no -output-directory flag).
Extension-based gitignore rules exclude the generated auxiliary files.

Produces: results/final.pdf
Logs:     results/run_logs/latex_build_<timestamp>.log
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (all relative to the repository root)
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).parent.parent.resolve()
LATEX_DIR = REPO_ROOT / "latex_project"
RESULTS_DIR = REPO_ROOT / "results"
RUN_LOGS_DIR = RESULTS_DIR / "run_logs"
FINAL_PDF = RESULTS_DIR / "final.pdf"


def _run(cmd: list[str], log_fh, cwd: Path) -> int:
    """Run a command, streaming output to both stdout and the log file."""
    label = " ".join(str(c) for c in cmd)
    print(f"\n>>> {label}", flush=True)
    log_fh.write(f"\n>>> {label}\n")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    log_fh.write(result.stdout)
    print(result.stdout, end="", flush=True)
    return result.returncode


def _check_binary(name: str) -> None:
    if not shutil.which(name):
        sys.exit(
            f"ERROR: '{name}' not found on PATH.\n"
            "Install MacTeX (macOS) or TeX Live full (Linux) and ensure the\n"
            "David CLM Hebrew font is available."
        )


def _has_fatal_error(log_path: Path) -> bool:
    """Return True if the LuaLaTeX log contains a fatal error line."""
    try:
        text = log_path.read_text(errors="replace")
        return any(line.lstrip().startswith("!") for line in text.splitlines())
    except FileNotFoundError:
        return False


def _abort_on_fatal(rc: int, pass_name: str, lualatex_log: Path, build_log: Path) -> None:
    if rc != 0 or _has_fatal_error(lualatex_log):
        sys.exit(
            f"ERROR: {pass_name} failed (exit {rc}).\n"
            f"LuaLaTeX log: {lualatex_log}\n"
            f"Build log:    {build_log}"
        )


def main() -> None:
    for binary in ("lualatex", "biber", "makeindex"):
        _check_binary(binary)

    RUN_LOGS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = RUN_LOGS_DIR / f"latex_build_{timestamp}.log"

    print(f"Build log: {log_path.relative_to(REPO_ROOT)}")
    print(f"Output:    {FINAL_PDF.relative_to(REPO_ROOT)}")

    # Compile in-place inside latex_project/ so that makeindex and LuaLaTeX
    # resolve .nls / .ind files consistently from the same working directory.
    lualatex_cmd = ["lualatex", "-interaction=nonstopmode", "main.tex"]
    main_log = LATEX_DIR / "main.log"

    with log_path.open("w") as log_fh:
        log_fh.write(f"LuaLaTeX build — {timestamp}\n")
        log_fh.write(f"LaTeX dir: {LATEX_DIR}\n\n")

        # Pass 1: initial compilation (generates .bcf, .nlo, .idx)
        rc = _run(lualatex_cmd, log_fh, LATEX_DIR)
        _abort_on_fatal(rc, "lualatex pass 1", main_log, log_path)

        # Pass 2: biber (bibliography)
        rc = _run(["biber", "main"], log_fh, LATEX_DIR)
        if rc != 0:
            sys.exit(f"ERROR: biber failed (exit {rc}). See {log_path}")

        # Pass 3: makeindex for nomenclature
        nlo = LATEX_DIR / "main.nlo"
        if nlo.exists():
            rc = _run(
                ["makeindex", "main.nlo", "-s", "nomencl.ist", "-o", "main.nls"],
                log_fh,
                LATEX_DIR,
            )
            if rc != 0:
                print(f"WARNING: makeindex (nomenclature) exited {rc} — continuing")
        else:
            print("WARNING: main.nlo not found; nomenclature will be empty")

        # Pass 4: makeindex for general index
        idx = LATEX_DIR / "main.idx"
        if idx.exists():
            rc = _run(["makeindex", "main.idx"], log_fh, LATEX_DIR)
            if rc != 0:
                print(f"WARNING: makeindex (index) exited {rc} — continuing")
        else:
            print("WARNING: main.idx not found; index will be empty")

        # Pass 5: second LuaLaTeX (resolves bibliography + index)
        rc = _run(lualatex_cmd, log_fh, LATEX_DIR)
        _abort_on_fatal(rc, "lualatex pass 2", main_log, log_path)

        # Pass 6: third LuaLaTeX (finalises cross-refs and TOC)
        rc = _run(lualatex_cmd, log_fh, LATEX_DIR)
        _abort_on_fatal(rc, "lualatex pass 3", main_log, log_path)

        built_pdf = LATEX_DIR / "main.pdf"
        if not built_pdf.exists():
            sys.exit(
                f"ERROR: Expected PDF not found at {built_pdf}.\n"
                f"Check the build log: {log_path}"
            )

        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(built_pdf, FINAL_PDF)
        log_fh.write(f"\nCopied {built_pdf} → {FINAL_PDF}\n")
        print(f"\nSUCCESS: {FINAL_PDF.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
