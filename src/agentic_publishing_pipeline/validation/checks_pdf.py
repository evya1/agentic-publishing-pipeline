"""P11-I04: PDF content indicator checks (deterministic, no LLM)."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from .report import ValidationReport

_MIN_PAGES = 15
_PAGES_RE = re.compile(r"^Pages:\s+(\d+)", re.MULTILINE)


def run_pdf_checks(pdf_path: Path, report: ValidationReport) -> None:
    """Assert the final PDF meets content and page-count requirements."""
    if not pdf_path.is_file():
        report.add("pdf:exists", False, f"File not found: {pdf_path}")
        return

    report.add("pdf:exists", True, f"Found {pdf_path} ({pdf_path.stat().st_size} bytes)")
    _check_page_count(pdf_path, report)
    _check_pdfinfo_readable(pdf_path, report)


def _check_page_count(pdf_path: Path, report: ValidationReport) -> None:
    if not shutil.which("pdfinfo"):
        report.add(
            "pdf:page_count",
            False,
            "pdfinfo not found — install poppler-utils to validate page count",
        )
        return

    try:
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True,
            text=True,
            timeout=15,
        )
        match = _PAGES_RE.search(result.stdout)
        if not match:
            report.add("pdf:page_count", False, "pdfinfo output did not contain page count")
            return
        pages = int(match.group(1))
        passed = pages >= _MIN_PAGES
        report.add(
            "pdf:page_count",
            passed,
            f"{pages} pages (minimum {_MIN_PAGES})" if passed else
            f"Only {pages} pages — need at least {_MIN_PAGES}",
        )
    except subprocess.TimeoutExpired:
        report.add("pdf:page_count", False, "pdfinfo timed out")
    except Exception as exc:
        report.add("pdf:page_count", False, f"pdfinfo error: {exc}")


def _check_pdfinfo_readable(pdf_path: Path, report: ValidationReport) -> None:
    """Confirm pdfinfo exits cleanly (PDF is not corrupted)."""
    if not shutil.which("pdfinfo"):
        return
    try:
        result = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            capture_output=True,
            text=True,
            timeout=15,
        )
        report.add(
            "pdf:readable",
            result.returncode == 0,
            "PDF opened cleanly by pdfinfo" if result.returncode == 0
            else f"pdfinfo error (exit {result.returncode}): {result.stderr[:200]}",
        )
    except Exception as exc:
        report.add("pdf:readable", False, f"pdfinfo exception: {exc}")
