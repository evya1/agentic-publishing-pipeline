"""Safe standalone write and deterministic project-tree comparison helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .file_plan import LaTeXFilePlan


@dataclass(frozen=True)
class TreeDrift:
    missing: tuple[str, ...]
    extra: tuple[str, ...]
    changed: tuple[str, ...]

    @property
    def clean(self) -> bool:
        return not (self.missing or self.extra or self.changed)


def write_plan(plan: LaTeXFilePlan, root: Path) -> None:
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    for item in plan.text_files:
        _write(root, item.relative_path, item.content.encode("utf-8"))
    for item in plan.binary_files:
        _write(root, item.relative_path, item.content)


def compare_plan(plan: LaTeXFilePlan, root: Path) -> TreeDrift:
    expected = {item.relative_path: item.content.encode("utf-8") for item in plan.text_files}
    expected.update({item.relative_path: item.content for item in plan.binary_files})
    actual = _tree(root)
    expected_names = set(expected)
    actual_names = set(actual)
    changed = tuple(
        sorted(name for name in expected_names & actual_names if expected[name] != actual[name])
    )
    return TreeDrift(
        missing=tuple(sorted(expected_names - actual_names)),
        extra=tuple(sorted(actual_names - expected_names)),
        changed=changed,
    )


def _tree(root: Path) -> dict[str, bytes]:
    if not root.exists():
        return {}
    allowed = {".tex", ".bib", ".png", ".jpg", ".jpeg"}
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in allowed
    }


def _write(root: Path, relative: str, content: bytes) -> None:
    target = (root / relative).resolve()
    target.relative_to(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp-phase9")
    temporary.write_bytes(content)
    temporary.replace(target)
