"""Tests for the P7-I07 untrusted-archive metadata-only inspector."""

from __future__ import annotations

import gzip
import io
import struct
import tarfile
import zipfile
from pathlib import Path

import pytest

from agentic_publishing_pipeline.tools import (
    ArchiveInspection,
    ArchiveInspectionError,
    inspect_archive,
)
from agentic_publishing_pipeline.tools._archive_zip import is_symlink_member


def _build_tar_gz(path: Path, entries: list[tuple[str, bytes]]) -> Path:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tf:
        for name, data in entries:
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    path.write_bytes(gzip.compress(raw.getvalue()))
    return path


def _build_tar_with_symlink(path: Path) -> Path:
    with tarfile.open(path, mode="w") as tf:
        info = tarfile.TarInfo(name="link")
        info.type = tarfile.SYMTYPE
        info.linkname = "../target"
        tf.addfile(info)
    return path


def _build_zip(path: Path, entries: list[tuple[str, bytes]]) -> Path:
    with zipfile.ZipFile(path, "w") as zf:
        for name, data in entries:
            zf.writestr(name, data)
    return path


def _make_root(tmp_path: Path) -> Path:
    root = tmp_path / "archives"
    root.mkdir()
    return root


def test_inspects_normal_archive_listing_only(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    archive = _build_zip(
        root / "ok.zip",
        [("paper/main.tex", b"% body\n"), ("paper/refs.bib", b"@misc{x,}\n")],
    )
    result = inspect_archive(archive, archive_root=root)
    assert isinstance(result, ArchiveInspection)
    assert result.member_count == 2
    assert {m.name for m in result.members} == {"paper/main.tex", "paper/refs.bib"}
    assert all(m.classification == "file" for m in result.members)
    assert result.nested_archive_names == ()


def test_rejects_path_traversal_member(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    archive = _build_zip(root / "bad.zip", [("../etc/passwd", b"x")])
    with pytest.raises(ArchiveInspectionError, match="path traversal"):
        inspect_archive(archive, archive_root=root)


def test_rejects_absolute_member(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    archive = _build_zip(root / "abs.zip", [("/etc/passwd", b"x")])
    with pytest.raises(ArchiveInspectionError, match="absolute path"):
        inspect_archive(archive, archive_root=root)


def test_rejects_drive_letter_member(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    archive = _build_zip(root / "drv.zip", [("C:windows", b"x")])
    with pytest.raises(ArchiveInspectionError, match="drive-letter"):
        inspect_archive(archive, archive_root=root)


def test_rejects_encrypted_member(tmp_path: Path) -> None:
    """Force the encryption flag bit after the writer has cleared it."""

    root = _make_root(tmp_path)
    archive = root / "enc.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("secret.txt", b"opaque")
    raw = bytearray(archive.read_bytes())
    # ZipFile.infolist() reads the central-directory headers (signature
    # PK\x01\x02). Patch flag_bits at offset 8 of that header to turn
    # the encryption bit on; also patch the local file header at
    # offset 6 to keep formats consistent.
    struct.pack_into("<H", raw, 6, struct.unpack_from("<H", raw, 6)[0] | 0x1)
    cd_off = raw.index(b"PK\x01\x02")
    struct.pack_into("<H", raw, cd_off + 8, struct.unpack_from("<H", raw, cd_off + 8)[0] | 0x1)
    archive.write_bytes(bytes(raw))
    with pytest.raises(ArchiveInspectionError, match="encrypted"):
        inspect_archive(archive, archive_root=root)


def test_rejects_symlink_member(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    archive = root / "sym.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        info = zipfile.ZipInfo("link")
        info.create_system = 3  # UNIX
        info.external_attr = (0o120777 & 0xFFFF) << 16
        zf.writestr(info, b"target")
    with pytest.raises(ArchiveInspectionError, match="symlink"):
        inspect_archive(archive, archive_root=root)


def test_flags_nested_archive_without_opening(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    archive = _build_zip(root / "wrap.zip", [("inner.zip", b"opaque"), ("ok.tex", b"")])
    result = inspect_archive(archive, archive_root=root)
    assert result.nested_archive_names == ("inner.zip",)


def test_flags_executable_hint_members(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    archive = _build_zip(root / "exec.zip", [("install.sh", b"#!/bin/sh"), ("paper.tex", b"")])
    result = inspect_archive(archive, archive_root=root)
    assert result.executable_hint_names == ("install.sh",)


def test_rejects_archive_outside_root(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    elsewhere = tmp_path / "other"
    elsewhere.mkdir()
    archive = _build_zip(elsewhere / "x.zip", [("a.tex", b"")])
    with pytest.raises(ArchiveInspectionError, match="escapes archive root"):
        inspect_archive(archive, archive_root=root)


def test_rejects_missing_archive(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    with pytest.raises(ArchiveInspectionError, match="archive not found"):
        inspect_archive(root / "nope.zip", archive_root=root)


def test_rejects_non_zip_file(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    bogus = root / "bogus.zip"
    bogus.write_bytes(b"not a zip at all")
    with pytest.raises(ArchiveInspectionError, match="not zip or tar"):
        inspect_archive(bogus, archive_root=root)


def test_does_not_call_zip_read_methods(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The inspector must never call read/open/extract on the ZipFile."""

    root = _make_root(tmp_path)
    archive = _build_zip(root / "spy.zip", [("a.tex", b"hello")])

    calls: list[str] = []

    def _trap(name: str):
        def _raise(*_a: object, **_kw: object) -> None:
            calls.append(name)
            raise AssertionError(f"unexpected call to ZipFile.{name}")

        return _raise

    monkeypatch.setattr(zipfile.ZipFile, "read", _trap("read"))
    monkeypatch.setattr(zipfile.ZipFile, "open", _trap("open"))
    monkeypatch.setattr(zipfile.ZipFile, "extract", _trap("extract"))
    monkeypatch.setattr(zipfile.ZipFile, "extractall", _trap("extractall"))

    result = inspect_archive(archive, archive_root=root)
    assert result.member_count == 1
    assert calls == []


def test_archive_root_must_exist(tmp_path: Path) -> None:
    root = tmp_path / "missing"
    with pytest.raises(AssertionError, match="archive root must exist"):
        inspect_archive(tmp_path / "x.zip", archive_root=root)


def test_symlink_detection_helper_handles_non_unix(tmp_path: Path) -> None:
    info = zipfile.ZipInfo("dummy")
    info.create_system = 11  # not UNIX, not DOS
    info.external_attr = (0o120777 & 0xFFFF) << 16
    assert is_symlink_member(info) is False


def test_classification_treats_directory_entries(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    archive = root / "dir.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        info = zipfile.ZipInfo("paper/")
        info.external_attr = 0o755 << 16
        zf.writestr(info, b"")
        zf.writestr("paper/main.tex", b"")
    result = inspect_archive(archive, archive_root=root)
    dirs = [m for m in result.members if m.classification == "directory"]
    assert len(dirs) == 1 and dirs[0].name == "paper/"


def test_real_arxiv_archive_listing_smoke(tmp_path: Path) -> None:
    """If a local arXiv archive is present, the inspector lists it safely."""

    candidate = Path("data/sources/arxiv/source_zips/2504.09037.zip")
    if not candidate.is_file():
        pytest.skip("local arXiv archive not available")
    result = inspect_archive(candidate, archive_root=candidate.parent)
    assert result.member_count > 0
    assert result.archive_size > 0
    assert result.archive_format in {"zip", "tar"}
    # Sanity-touch struct so the import stays exercised across editors.
    assert struct.calcsize("I") == 4


def test_inspects_gzip_tar_archive(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    archive = _build_tar_gz(root / "src.zip", [("paper/main.tex", b"% body")])
    result = inspect_archive(archive, archive_root=root)
    assert result.archive_format == "tar"
    assert {m.name for m in result.members} == {"paper/main.tex"}


def test_rejects_tar_symlink_member(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    archive = _build_tar_with_symlink(root / "sym.tar")
    with pytest.raises(ArchiveInspectionError, match="symlink"):
        inspect_archive(archive, archive_root=root)


def test_rejects_tar_path_traversal_member(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    archive = _build_tar_gz(root / "trav.zip", [("../etc/passwd", b"x")])
    with pytest.raises(ArchiveInspectionError, match="path traversal"):
        inspect_archive(archive, archive_root=root)


def test_rejects_tar_device_member(tmp_path: Path) -> None:
    root = _make_root(tmp_path)
    archive = root / "dev.tar"
    with tarfile.open(archive, mode="w") as tf:
        info = tarfile.TarInfo(name="zero")
        info.type = tarfile.CHRTYPE
        info.devmajor = 1
        info.devminor = 5
        tf.addfile(info)
    with pytest.raises(ArchiveInspectionError, match="device/fifo"):
        inspect_archive(archive, archive_root=root)


def test_does_not_call_tarfile_extract_methods(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The inspector must never call extract*/extractfile on the tarfile."""

    root = _make_root(tmp_path)
    archive = _build_tar_gz(root / "ext.zip", [("a.tex", b"hi")])

    calls: list[str] = []

    def _trap(name: str):
        def _raise(*_a: object, **_kw: object) -> None:
            calls.append(name)
            raise AssertionError(f"unexpected call to TarFile.{name}")

        return _raise

    monkeypatch.setattr(tarfile.TarFile, "extract", _trap("extract"))
    monkeypatch.setattr(tarfile.TarFile, "extractall", _trap("extractall"))
    monkeypatch.setattr(tarfile.TarFile, "extractfile", _trap("extractfile"))

    result = inspect_archive(archive, archive_root=root)
    assert result.member_count == 1 and calls == []
