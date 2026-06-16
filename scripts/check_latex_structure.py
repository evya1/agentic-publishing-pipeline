"""Verify LaTeX project structure follows PRD §8.5 conventions.

Checks that:
- chapters/, tables/, figures/ directories exist
- required structural files are present (preamble.tex, macros.tex, references.bib)
- main.tex does not inline large environments that belong in sub-files

Skips gracefully when:
- latex_project/ does not exist (Phase 9 not yet started)
- main.tex is a placeholder (contains 'PLACEHOLDER TEMPLATE ONLY')

Exits 1 when rules are violated on a non-placeholder project.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
_LATEX_ROOT = _REPO / "latex_project"

_REQUIRED_DIRS = ["chapters", "tables", "figures"]
_REQUIRED_FILES = ["preamble.tex", "macros.tex", "references.bib"]

_INLINE_ENV_RE = re.compile(
    r"\\begin\{(table|figure|tikzpicture|tabular)\}",
    re.IGNORECASE,
)
_PLACEHOLDER_MARKER = "PLACEHOLDER TEMPLATE ONLY"


def main() -> int:
    if not _LATEX_ROOT.exists():
        print("SKIP: latex_project/ absent — Phase 9 not yet started.")
        return 0

    main_tex = _LATEX_ROOT / "main.tex"
    if not main_tex.exists():
        print("SKIP: latex_project/main.tex absent — Phase 9 not yet started.")
        return 0

    main_content = main_tex.read_text(encoding="utf-8", errors="ignore")
    if _PLACEHOLDER_MARKER in main_content:
        print("SKIP: main.tex is a placeholder — Phase 9 structure not yet implemented.")
        return 0

    issues: list[str] = []

    for fname in _REQUIRED_FILES:
        if not (_LATEX_ROOT / fname).exists():
            issues.append(f"Missing required file: latex_project/{fname}")

    for dname in _REQUIRED_DIRS:
        if not (_LATEX_ROOT / dname).is_dir():
            issues.append(f"Missing required directory: latex_project/{dname}/")

    inline_matches = _INLINE_ENV_RE.findall(main_content)
    if inline_matches:
        issues.append(f"main.tex inlines {inline_matches}; move to chapters/, tables/, or figures/")

    if issues:
        print("FAIL: LaTeX structure violations:")
        for issue in issues:
            print(f"  {issue}")
        return 1

    print("OK: LaTeX project structure follows PRD §8.5.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
