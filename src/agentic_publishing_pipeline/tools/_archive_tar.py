"""TAR / gzip-TAR backend for the metadata-only archive inspector.

Internal helper for P7-I07; production callers go through
:func:`agentic_publishing_pipeline.tools.archive_inspect.inspect_archive`.
arXiv source archives frequently use gzipped tar even when the
filename suffix is ``.zip``.
"""

from __future__ import annotations

import tarfile
from pathlib import Path


class _TarReject(RuntimeError):
    pass


def iter_members(path: Path):
    """Yield ``(name, size, crc, is_dir)`` for each tar entry.

    Raises :class:`_TarReject` for symlink, hardlink, device, and
    FIFO members. The public inspector wraps this as
    :class:`ArchiveInspectionError`. CRC is reported as 0 because
    tar headers do not carry a per-entry CRC.
    """

    try:
        tf = tarfile.open(path, mode="r:*")  # noqa: SIM115 — guarded by `with` below.
    except tarfile.TarError as exc:
        raise _TarReject(f"archive is not a valid tar: {path}") from exc
    with tf:
        for info in tf.getmembers():
            if info.issym() or info.islnk():
                raise _TarReject(
                    f"archive member is a symlink (rejected): {info.name!r}"
                )
            if info.isdev() or info.isfifo():
                raise _TarReject(
                    f"archive member is a device/fifo (rejected): {info.name!r}"
                )
            yield info.name, info.size, 0, info.isdir()
