"""Validation helpers for the typed source manifest loader (P7-I01).

Internal module; the public surface lives in :mod:`.manifest`.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import PurePosixPath


class _ValidationError(RuntimeError):
    """Raised by the validator; re-raised as :class:`SourceManifestError`."""


_VALID_STATUS: frozenset[str] = frozenset({"unverified", "pending", "verified", "rejected"})


def require_str(record: Mapping[str, object], field_name: str, idx: int) -> str:
    value = record.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise _ValidationError(
            f"record #{idx} missing required string field {field_name!r}"
        )
    return value


def optional_str(record: Mapping[str, object], field_name: str) -> str | None:
    value = record.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        return None
    return value


def coerce_authors(value: object, idx: int) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise _ValidationError(f"record #{idx} field 'authors' must be a list")
    authors: list[str] = []
    for offset, name in enumerate(value):
        if not isinstance(name, str) or not name.strip():
            raise _ValidationError(
                f"record #{idx} field 'authors[{offset}]' must be a non-empty string"
            )
        authors.append(name.strip())
    return tuple(authors)


def coerce_year(record: Mapping[str, object], idx: int) -> int:
    year = record.get("year")
    if not isinstance(year, int) or isinstance(year, bool):
        raise _ValidationError(f"record #{idx} field 'year' must be an integer")
    if year < 1900 or year > 2100:
        raise _ValidationError(f"record #{idx} field 'year' out of range: {year}")
    return year


def coerce_archive_path(record: Mapping[str, object], idx: int) -> str | None:
    value = record.get("source_archive")
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise _ValidationError(
            f"record #{idx} field 'source_archive' must be a non-empty string"
        )
    posix = PurePosixPath(value.strip())
    if posix.is_absolute() or any(part == ".." for part in posix.parts):
        raise _ValidationError(
            f"record #{idx} field 'source_archive' must be a safe repo-relative path: {value!r}"
        )
    return str(posix)


def coerce_verification(
    record: Mapping[str, object], idx: int
) -> tuple[str, str, str | None, str | None]:
    raw = record.get("verification")
    if not isinstance(raw, Mapping):
        raise _ValidationError(f"record #{idx} field 'verification' must be a mapping")
    status = raw.get("status")
    if not isinstance(status, str) or status not in _VALID_STATUS:
        raise _ValidationError(
            f"record #{idx} verification.status must be one of "
            f"{sorted(_VALID_STATUS)}; got {status!r}"
        )
    method = raw.get("method")
    if not isinstance(method, str) or not method.strip():
        raise _ValidationError(
            f"record #{idx} verification.method must be a non-empty string"
        )
    verified_at = raw.get("verified_at")
    verified_by = raw.get("verified_by")
    if verified_at is not None and (
        not isinstance(verified_at, str) or not verified_at.strip()
    ):
        raise _ValidationError(
            f"record #{idx} verification.verified_at must be a non-empty string or null"
        )
    if verified_by is not None and (
        not isinstance(verified_by, str) or not verified_by.strip()
    ):
        raise _ValidationError(
            f"record #{idx} verification.verified_by must be a non-empty string or null"
        )
    if (verified_at is None) != (verified_by is None):
        raise _ValidationError(
            f"record #{idx} verification.verified_at and verified_by must be set together"
        )
    return status, method.strip(), verified_at, verified_by
