"""ZIP backend for the metadata-only archive inspector (P7-I07).

Internal helper; production callers go through
:func:`agentic_publishing_pipeline.tools.archive_inspect.inspect_archive`.
"""

from __future__ import annotations

import stat
import zipfile
from pathlib import Path


class _ZipReject(RuntimeError):
    pass


def is_symlink_member(info: zipfile.ZipInfo) -> bool:
    if info.create_system not in (0, 3):
        return False
    return stat.S_ISLNK((info.external_attr >> 16) & 0xFFFF)


def iter_members(path: Path):
    """Yield ``(name, size, crc, is_dir)`` for each ZIP central-directory entry.

    Raises :class:`_ZipReject` for symlink and encrypted members. The
    public inspector wraps this rejection as
    :class:`ArchiveInspectionError`.
    """

    try:
        zf = zipfile.ZipFile(path, "r")
    except zipfile.BadZipFile as exc:
        raise _ZipReject(f"archive is not a valid ZIP: {path}") from exc
    with zf:
        for info in zf.infolist():
            if is_symlink_member(info):
                raise _ZipReject(f"archive member is a symlink (rejected): {info.filename!r}")
            if info.flag_bits & 0x1:
                raise _ZipReject(f"archive member is encrypted (rejected): {info.filename!r}")
            yield info.filename, info.file_size, info.CRC, info.is_dir()
