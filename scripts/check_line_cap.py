"""Check production Python source files against the project line cap."""

from __future__ import annotations

import argparse
import sys
import tokenize
from pathlib import Path

DEFAULT_LIMIT = 150


def measured_lines(path: Path) -> int:
    """Count non-blank, non-comment logical source lines."""

    lines: set[int] = set()
    with path.open("rb") as handle:
        for token in tokenize.tokenize(handle.readline):
            if token.type in {
                tokenize.ENCODING,
                tokenize.ENDMARKER,
                tokenize.NEWLINE,
                tokenize.NL,
                tokenize.INDENT,
                tokenize.DEDENT,
                tokenize.COMMENT,
            }:
                continue
            lines.update(range(token.start[0], token.end[0] + 1))
    return len(lines)


def python_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix == ".py" else []
    return sorted(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)


def check_roots(roots: list[Path], *, limit: int) -> list[tuple[Path, int]]:
    violations: list[tuple[Path, int]] = []
    for root in roots:
        for path in python_files(root):
            count = measured_lines(path)
            if count > limit:
                violations.append((path, count))
    return violations


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Enforce the production source line cap.")
    parser.add_argument("roots", nargs="*", type=Path, default=[Path("src")])
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    violations = check_roots(args.roots, limit=args.limit)
    if not violations:
        print(f"Line cap passed: <= {args.limit} measured lines")
        return 0
    for path, count in violations:
        print(f"{path}: {count} measured lines > limit {args.limit}", file=sys.stderr)
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
