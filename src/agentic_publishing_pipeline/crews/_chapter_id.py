"""Chapter-identifier path safety (P6-I01 follow-up).

Chapter Markdown files live exclusively under
``results/generated_markdown/chapters/<chapter_id>.md``.  ``chapter_id``
must therefore be exactly one safe filesystem path segment.  Everything
else — empty strings, ``.``/``..``, absolute paths, embedded path
separators, drive prefixes, NUL bytes, or shell-style ``~`` — would let
the writer escape the controlled output root.
"""

from __future__ import annotations

import re

_SAFE_CHAPTER_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_\-]{0,127}$")


class UnsafeChapterIdError(ValueError):
    """Raised when a chapter identifier is not one safe path segment."""


def validate_chapter_id(chapter_id: object) -> str:
    """Return ``chapter_id`` only when it is one safe filesystem segment.

    Accepts a single ASCII slug matching
    ``[A-Za-z0-9][A-Za-z0-9_-]{0,127}``.  Rejects every form that could
    escape ``results/generated_markdown/chapters/`` — see module docstring.
    """
    if not isinstance(chapter_id, str):
        raise UnsafeChapterIdError(f"chapter_id must be str, got {type(chapter_id).__name__}")
    if not chapter_id:
        raise UnsafeChapterIdError("chapter_id must not be empty")
    if "\x00" in chapter_id:
        raise UnsafeChapterIdError("chapter_id must not contain NUL bytes")
    if chapter_id in {".", ".."}:
        raise UnsafeChapterIdError(f"chapter_id must not be {chapter_id!r}")
    if "/" in chapter_id or "\\" in chapter_id:
        raise UnsafeChapterIdError(f"chapter_id {chapter_id!r} must not contain path separators")
    if chapter_id.startswith("~"):
        raise UnsafeChapterIdError(f"chapter_id {chapter_id!r} must not start with '~'")
    if len(chapter_id) >= 2 and chapter_id[1] == ":":
        raise UnsafeChapterIdError(f"chapter_id {chapter_id!r} must not look like a drive path")
    if not _SAFE_CHAPTER_ID_RE.fullmatch(chapter_id):
        raise UnsafeChapterIdError(
            f"chapter_id {chapter_id!r} must match {_SAFE_CHAPTER_ID_RE.pattern}"
        )
    return chapter_id
