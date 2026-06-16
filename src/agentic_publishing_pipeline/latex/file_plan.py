"""Validated in-memory file plan for Phase 9 source assembly."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath


class FilePlanError(ValueError):
    """Raised on duplicate, empty, or unsafe project paths."""


@dataclass(frozen=True)
class PlannedTextFile:
    relative_path: str
    content: str


@dataclass(frozen=True)
class PlannedBinaryFile:
    relative_path: str
    content: bytes


@dataclass(frozen=True)
class LaTeXFilePlan:
    text_files: tuple[PlannedTextFile, ...]
    binary_files: tuple[PlannedBinaryFile, ...]

    @classmethod
    def build(
        cls,
        *,
        text_files: list[PlannedTextFile],
        binary_files: list[PlannedBinaryFile] | None = None,
    ) -> LaTeXFilePlan:
        seen: set[str] = set()
        texts = [_normal_text(item, seen) for item in text_files]
        binaries = [_normal_binary(item, seen) for item in binary_files or []]
        return cls(
            text_files=tuple(sorted(texts, key=lambda item: item.relative_path)),
            binary_files=tuple(sorted(binaries, key=lambda item: item.relative_path)),
        )


def _path(value: str, seen: set[str]) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not value.strip():
        raise FilePlanError(f"unsafe project path: {value!r}")
    normalized = path.as_posix()
    if normalized in seen:
        raise FilePlanError(f"duplicate project path: {normalized}")
    seen.add(normalized)
    return normalized


def _normal_text(item: PlannedTextFile, seen: set[str]) -> PlannedTextFile:
    return PlannedTextFile(_path(item.relative_path, seen), item.content.rstrip() + "\n")


def _normal_binary(item: PlannedBinaryFile, seen: set[str]) -> PlannedBinaryFile:
    return PlannedBinaryFile(_path(item.relative_path, seen), item.content)
