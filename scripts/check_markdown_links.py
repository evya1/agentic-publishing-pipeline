"""Check that internal file-path links in tracked Markdown files resolve.

Parses inline links [text](path) and reference-style links [text][ref] /
[ref]: path in every tracked .md file and verifies that links pointing to
local paths (not http/https/mailto/# anchors) resolve to an existing file
or directory relative to the repository root.

Exits 1 when any broken local path is found.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent

# Inline links: [text](path) — capture the path part
_INLINE_RE = re.compile(r"\[(?:[^\]]*)\]\(([^)#\s][^)]*)\)")
# Reference definitions: [label]: path
_REF_DEF_RE = re.compile(r"^\[(?:[^\]]+)\]:\s+(\S+)", re.MULTILINE)

_URL_PREFIXES = ("http://", "https://", "mailto:", "ftp://")


def _tracked_md_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "*.md", "**/*.md"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [_REPO / p for p in result.stdout.splitlines() if p.strip()]


def _is_external(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in _URL_PREFIXES) or path.startswith("#")


def _extract_local_paths(text: str) -> list[str]:
    paths: list[str] = []
    for m in _INLINE_RE.finditer(text):
        raw = m.group(1).split("#")[0].strip()  # strip anchor fragment
        if raw and not _is_external(raw):
            paths.append(raw)
    for m in _REF_DEF_RE.finditer(text):
        raw = m.group(1).split("#")[0].strip()
        if raw and not _is_external(raw):
            paths.append(raw)
    return paths


def main() -> int:
    md_files = _tracked_md_files()
    if not md_files:
        print("OK: no tracked Markdown files found.")
        return 0

    broken: list[str] = []
    for md_path in md_files:
        if not md_path.exists():
            continue
        text = md_path.read_text(encoding="utf-8", errors="ignore")
        md_dir = md_path.parent
        for raw in _extract_local_paths(text):
            # Resolve relative to the file's directory first, then repo root
            candidate = (md_dir / raw).resolve()
            if not candidate.exists():
                # Try repo-root-relative
                candidate2 = (_REPO / raw).resolve()
                if not candidate2.exists():
                    broken.append(f"{md_path.relative_to(_REPO)}: broken link → {raw!r}")

    if broken:
        print(f"FAIL: {len(broken)} broken internal Markdown link(s):")
        for b in sorted(broken):
            print(f"  {b}")
        return 1

    print(f"OK: all internal links checked across {len(md_files)} Markdown file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
