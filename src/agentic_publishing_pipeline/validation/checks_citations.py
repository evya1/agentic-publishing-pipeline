"""P11-I05: Citation validation — every \\cite{key} must resolve in references.bib."""

from __future__ import annotations

import re
from pathlib import Path

from .report import ValidationReport

_CITE_RE = re.compile(r"\\cite(?:\[.*?\])?\{([^}]+)\}")
_BIB_KEY_RE = re.compile(r"^@\w+\{([^,]+),", re.MULTILINE)


def run_citation_checks(latex_dir: Path, report: ValidationReport) -> None:
    """Assert every cited key is defined in references.bib."""
    bib_file = latex_dir / "references.bib"
    if not bib_file.is_file():
        report.add("citations:bib_exists", False, f"references.bib not found: {bib_file}")
        return
    report.add("citations:bib_exists", True, "references.bib exists")

    bib_keys = _extract_bib_keys(bib_file)
    report.add(
        "citations:bib_non_empty",
        len(bib_keys) > 0,
        f"{len(bib_keys)} entries in references.bib",
    )

    cited_keys = _extract_cited_keys(latex_dir)
    missing = cited_keys - bib_keys
    report.add(
        "citations:all_resolve",
        len(missing) == 0,
        "all citations resolve" if not missing
        else f"unresolved citations: {', '.join(sorted(missing))}",
    )

    _check_build_log_undefined(latex_dir, report)


def _extract_bib_keys(bib_file: Path) -> set[str]:
    text = bib_file.read_text(errors="replace")
    return {m.group(1).strip() for m in _BIB_KEY_RE.finditer(text)}


def _extract_cited_keys(latex_dir: Path) -> set[str]:
    keys: set[str] = set()
    for tex_file in latex_dir.rglob("*.tex"):
        try:
            text = tex_file.read_text(errors="replace")
        except OSError:
            continue
        for match in _CITE_RE.finditer(text):
            for key in match.group(1).split(","):
                stripped = key.strip()
                if stripped:
                    keys.add(stripped)
    return keys


def _check_build_log_undefined(latex_dir: Path, report: ValidationReport) -> None:
    """Scan the latest main.log for 'Citation ... undefined' warnings."""
    log_file = latex_dir / "main.log"
    if not log_file.is_file():
        report.add("citations:no_build_warnings", True, "no main.log present — skipping log scan")
        return
    text = log_file.read_text(errors="replace")
    undefined = re.findall(r"Citation '([^']+)' on page \d+ undefined", text)
    undefined_unique = sorted(set(undefined))
    passed = len(undefined_unique) == 0
    report.add(
        "citations:no_build_warnings",
        passed,
        "no undefined citation warnings in main.log" if passed
        else f"undefined in log: {', '.join(undefined_unique)}",
    )
