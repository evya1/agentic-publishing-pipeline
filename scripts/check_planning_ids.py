"""Verify planning IDs in docs/TODO.md are unique as task definitions.

A task definition is a Markdown table row where a P<phase>-I<nn> ID
appears as the first non-empty cell.  Cross-references in prose do not
count.

Exits 1 when any duplicate definition is found.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

# Matches the first cell of a table row: | P<phase>-I<nn> |
_DEF_ROW_RE = re.compile(r"^\|\s*(P\d+-I\d+)\s*\|")


def main() -> int:
    todo_path = Path(__file__).parent.parent / "docs" / "TODO.md"
    if not todo_path.exists():
        print(f"FAIL: {todo_path} not found.")
        return 1

    ids: list[str] = []
    for line in todo_path.read_text(encoding="utf-8").splitlines():
        m = _DEF_ROW_RE.match(line)
        if m:
            ids.append(m.group(1))

    counts = Counter(ids)
    duplicates = {k: v for k, v in counts.items() if v > 1}

    if duplicates:
        print("FAIL: duplicate planning ID definitions in docs/TODO.md:")
        for pid, count in sorted(duplicates.items()):
            print(f"  {pid}: defined {count} times in table rows")
        return 1

    print(f"OK: {len(counts)} unique planning ID definitions, no duplicates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
