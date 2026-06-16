"""Check that no .env files or secrets patterns are tracked in git.

Scans tracked files for known secret patterns and reports findings.
Exits 1 when any issue is found.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_BANNED_FILES = {
    ".env",
}

_SECRET_RE = re.compile(
    r'(?i)(api[_\-]?key|secret[_\-]?key|password|token|credential)\s*=\s*["\']?[A-Za-z0-9+/]{16,}',
)

_IGNORED_SUFFIXES = {".pyc", ".png", ".jpg", ".jpeg", ".pdf", ".gz", ".tar", ".zip"}


def _tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [Path(p) for p in result.stdout.splitlines() if p.strip()]


def main() -> int:
    issues: list[str] = []

    for path in _tracked_files():
        if path.name in _BANNED_FILES:
            issues.append(f"Tracked secret file: {path}")
            continue

        if path.suffix in _IGNORED_SUFFIXES:
            continue

        if not path.exists():
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for lineno, line in enumerate(text.splitlines(), 1):
            if _SECRET_RE.search(line):
                issues.append(f"Possible secret at {path}:{lineno}")

    if issues:
        print("FAIL: potential secrets or banned files found:")
        for issue in issues:
            print(f"  {issue}")
        return 1

    print("OK: no tracked secrets or .env files found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
