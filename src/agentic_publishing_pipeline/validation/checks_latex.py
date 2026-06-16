"""P11-I03: Required LaTeX file checks + FR-17a-d separation enforcement."""

from __future__ import annotations

import contextlib
import re
from pathlib import Path

from .report import ValidationReport

_INLINE_TABLE_RE = re.compile(r"\\begin\{table", re.MULTILINE)
_INLINE_TIKZ_RE = re.compile(r"\\begin\{tikzpicture", re.MULTILINE)
_INPUT_RE = re.compile(r"\\(?:input|RequireAndInput|RequireAndChapter)\{", re.MULTILINE)


def run_latex_checks(latex_dir: Path, report: ValidationReport) -> None:
    """Assert LaTeX project structure per PRD §8.5 and FR-17a-d."""
    _check_required_files(latex_dir, report)
    _check_chapter_separation(latex_dir, report)
    _check_required_tex_content(latex_dir, report)


def _check_required_files(latex_dir: Path, report: ValidationReport) -> None:
    required = ["main.tex", "preamble.tex", "macros.tex", "references.bib"]
    for name in required:
        p = latex_dir / name
        report.add(
            f"latex:{name}",
            p.is_file() and p.stat().st_size > 0,
            "ok" if (p.is_file() and p.stat().st_size > 0) else f"missing or empty: {p}",
        )

    chapters_dir = latex_dir / "chapters"
    chapters = list(chapters_dir.glob("*.tex")) if chapters_dir.is_dir() else []
    report.add("latex:chapters_count", len(chapters) >= 2, f"{len(chapters)} chapter files found")

    tables = list((latex_dir / "tables").glob("*.tex")) if (latex_dir / "tables").is_dir() else []
    report.add("latex:tables_dir", len(tables) >= 1, f"{len(tables)} table files found")

    figs_dir = latex_dir / "figures"
    figs = list(figs_dir.glob("*")) if figs_dir.is_dir() else []
    figs = [f for f in figs if f.suffix in {".tex", ".png", ".pdf", ".jpg"}]
    report.add("latex:figures_dir", len(figs) >= 1, f"{len(figs)} figure assets found")

    main_tex = latex_dir / "main.tex"
    if main_tex.is_file():
        has_input = bool(_INPUT_RE.search(main_tex.read_text(errors="replace")))
        report.add("latex:main_uses_input", has_input, "main.tex uses \\input directives")


def _check_chapter_separation(latex_dir: Path, report: ValidationReport) -> None:
    """FR-17a-d: chapter files must not inline table or TikZ environments."""
    chapters_dir = latex_dir / "chapters"
    if not chapters_dir.is_dir():
        report.add("latex:fr17_separation", False, "chapters/ directory missing")
        return

    violations: list[str] = []
    for tex_file in sorted(chapters_dir.glob("*.tex")):
        text = tex_file.read_text(errors="replace")
        if _INLINE_TABLE_RE.search(text):
            violations.append(f"{tex_file.name}: inline \\begin{{table}}")
        if _INLINE_TIKZ_RE.search(text):
            violations.append(f"{tex_file.name}: inline \\begin{{tikzpicture}}")

    passed = len(violations) == 0
    msg = "ok — no inline tables or TikZ in chapters" if passed else "; ".join(violations)
    report.add("latex:fr17_separation", passed, msg)


def _check_required_tex_content(latex_dir: Path, report: ValidationReport) -> None:
    """Check for required LaTeX features across the project."""
    all_tex = _read_all_tex(latex_dir)

    _check_pattern(all_tex, r"\\eqref\{|\\ref\{eq:", "latex:eqref_present",
                   "\\eqref cross-reference found", "no \\eqref found", report)
    _check_pattern(all_tex, r"\\nomenclature\{", "latex:nomenclature_entries",
                   "\\nomenclature entries found", "no \\nomenclature entries", report)
    _check_pattern(all_tex, r"\\index\{", "latex:index_entries",
                   "\\index entries found", "no \\index entries", report)
    _check_pattern(all_tex, r"[֐-׿]", "latex:hebrew_text",
                   "Hebrew characters found (BiDi)", "no Hebrew characters found", report)


def _read_all_tex(latex_dir: Path) -> str:
    parts: list[str] = []
    for tex_file in latex_dir.rglob("*.tex"):
        with contextlib.suppress(OSError):
            parts.append(tex_file.read_text(errors="replace"))
    return "\n".join(parts)


def _check_pattern(
    text: str,
    pattern: str,
    name: str,
    pass_msg: str,
    fail_msg: str,
    report: ValidationReport,
) -> None:
    found = bool(re.search(pattern, text))
    report.add(name, found, pass_msg if found else fail_msg)
