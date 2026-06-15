"""Safe metadata-only inspection of untrusted source archives.

Phase 7 (P7-I07) policy: third-party source archives under
``data/sources/arxiv/`` are **untrusted**. This module is the only
sanctioned reader of those archives. It exposes a listing-only API
that reads the archive's directory metadata and refuses every path
that could lead to extraction, execution, compilation, or evaluation
of archive content.

The public surface intentionally provides **no** member-content read.
Bibliographic facts must come from authoritative remote metadata
(`docs/PRD_bibliography_and_citations.md` §7.1 step 3), not from
archive bytes. ZIP and gzipped/uncompressed tarballs are both
supported.
"""

from __future__ import annotations

import tarfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from . import _archive_tar, _archive_zip

_NESTED_SUFFIXES: frozenset[str] = frozenset(
    {".zip", ".tar", ".gz", ".tgz", ".bz2", ".tbz2", ".xz", ".txz", ".7z", ".rar"}
)
_EXEC_SUFFIXES: frozenset[str] = frozenset(
    {".sh", ".py", ".lua", ".pl", ".exe", ".bat", ".cmd", ".ps1"}
)


class ArchiveInspectionError(RuntimeError):
    """Raised when an archive or one of its members is unsafe."""


@dataclass(frozen=True)
class ArchiveMember:
    name: str
    size: int
    crc32: int
    is_dir: bool
    classification: str


@dataclass(frozen=True)
class ArchiveInspection:
    archive_path: Path
    archive_size: int
    member_count: int
    members: tuple[ArchiveMember, ...]
    nested_archive_names: tuple[str, ...] = field(default_factory=tuple)
    executable_hint_names: tuple[str, ...] = field(default_factory=tuple)
    archive_format: str = "zip"


def _ensure_under_root(archive_path: Path, archive_root: Path) -> Path:
    assert archive_root.is_dir(), f"archive root must exist: {archive_root}"
    resolved_root = archive_root.resolve(strict=True)
    try:
        resolved = archive_path.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ArchiveInspectionError(f"archive not found: {archive_path}") from exc
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ArchiveInspectionError(
            f"archive path {archive_path} escapes archive root {archive_root}"
        ) from exc
    if not resolved.is_file():
        raise ArchiveInspectionError(f"archive path is not a regular file: {archive_path}")
    return resolved


def _reject_unsafe_name(name: str) -> None:
    if not name:
        raise ArchiveInspectionError("archive member has empty name")
    if name.startswith("/") or name.startswith("\\"):
        raise ArchiveInspectionError(f"archive member has absolute path: {name!r}")
    if len(name) >= 2 and name[1] == ":":
        raise ArchiveInspectionError(f"archive member has drive-letter path: {name!r}")
    parts = PurePosixPath(name.replace("\\", "/")).parts
    if any(p == ".." for p in parts):
        raise ArchiveInspectionError(f"archive member uses path traversal: {name!r}")


def _classify(name: str, *, is_dir: bool) -> str:
    if is_dir:
        return "directory"
    suffix = PurePosixPath(name).suffix.lower()
    if suffix in _NESTED_SUFFIXES:
        return "nested_archive"
    if suffix in _EXEC_SUFFIXES:
        return "executable_hint"
    return "file"


def _detect_format(path: Path) -> str:
    with path.open("rb") as handle:
        head = handle.read(4)
    if head[:4] == b"PK\x03\x04" or head[:4] == b"PK\x05\x06":
        return "zip"
    if head[:2] == b"\x1f\x8b":
        return "tar"
    if tarfile.is_tarfile(path):
        return "tar"
    raise ArchiveInspectionError(f"archive format is not zip or tar: {path}")


def inspect_archive(archive_path: Path, *, archive_root: Path) -> ArchiveInspection:
    """Return a metadata-only listing of ``archive_path``.

    Raises :class:`ArchiveInspectionError` for any unsafe condition.
    Never opens, extracts, decompresses, executes, or compiles a
    member.
    """

    resolved = _ensure_under_root(archive_path, archive_root)
    fmt = _detect_format(resolved)
    backend = _archive_zip if fmt == "zip" else _archive_tar
    members: list[ArchiveMember] = []
    nested: list[str] = []
    execs: list[str] = []
    try:
        for name, size, crc, is_dir in backend.iter_members(resolved):
            _reject_unsafe_name(name)
            cls = _classify(name, is_dir=is_dir)
            members.append(ArchiveMember(name, size, crc, is_dir, cls))
            if cls == "nested_archive":
                nested.append(name)
            elif cls == "executable_hint":
                execs.append(name)
    except (_archive_zip._ZipReject, _archive_tar._TarReject) as exc:
        raise ArchiveInspectionError(str(exc)) from exc
    return ArchiveInspection(
        archive_path=resolved,
        archive_size=resolved.stat().st_size,
        member_count=len(members),
        members=tuple(members),
        nested_archive_names=tuple(nested),
        executable_hint_names=tuple(execs),
        archive_format=fmt,
    )
