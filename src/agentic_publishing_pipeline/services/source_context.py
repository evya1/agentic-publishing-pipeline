"""Verified source context supplied to manuscript-generation tasks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


class SourceContextError(ValueError):
    """Raised when the locked source manifest cannot support a run."""

@dataclass(frozen=True)
class SourceRecord:
    citation_key: str
    title: str
    authors: tuple[str, ...]
    year: str
    arxiv_id: str | None
    doi: str | None
    trusted_summary: str


@dataclass(frozen=True)
class SourceContext:
    manifest_path: Path
    records: tuple[SourceRecord, ...]

    @property
    def citation_keys(self) -> tuple[str, ...]:
        return tuple(record.citation_key for record in self.records)

    def as_prompt_text(self) -> str:
        blocks: list[str] = []
        for source in self.records:
            identifiers = _identifiers(source)
            blocks.append(
                "\n".join(
                    (
                        f"citation_key: {source.citation_key}",
                        f"title: {source.title}",
                        f"authors: {', '.join(source.authors) or 'Unknown authors'}",
                        f"year: {source.year}",
                        f"identifiers: {identifiers or 'none'}",
                        f"trusted_context: {source.trusted_summary}",
                    )
                )
            )
        return "\n\n---\n\n".join(blocks)


def load_source_context(manifest_path: Path) -> SourceContext:
    """Load configured sources; never discover or substitute sources."""
    if not manifest_path.is_file():
        raise SourceContextError(f"source manifest missing: {manifest_path}")
    raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    entries = raw.get("sources", []) if isinstance(raw, dict) else []
    if not isinstance(entries, list) or not entries:
        raise SourceContextError("source manifest has no sources")
    records: list[SourceRecord] = []
    seen: set[str] = set()
    for index, entry in enumerate(entries, start=1):
        records.append(_load_record(entry, index, manifest_path.parent, seen))
    return SourceContext(manifest_path=manifest_path.resolve(), records=tuple(records))


def _load_record(
    entry: object,
    index: int,
    base: Path,
    seen: set[str],
) -> SourceRecord:
    if not isinstance(entry, dict):
        raise SourceContextError(f"source #{index} is not a mapping")
    key = _required_text(entry, "citation_key", index)
    title = _required_text(entry, "title", index)
    if key in seen:
        raise SourceContextError(f"duplicate citation key: {key}")
    seen.add(key)
    return SourceRecord(
        citation_key=key,
        title=title,
        authors=_authors(entry.get("authors", entry.get("author", []))),
        year=str(entry.get("year", "")),
        arxiv_id=_optional_text(entry.get("arxiv_id")),
        doi=_optional_text(entry.get("doi")),
        trusted_summary=_trusted_summary(entry, base),
    )


def _trusted_summary(entry: dict[str, object], base: Path) -> str:
    for field in ("verified_abstract", "abstract", "trusted_summary", "summary"):
        value = str(entry.get(field, "")).strip()
        if value:
            return value
    context_path = str(entry.get("context_path", "")).strip()
    if context_path:
        return _read_context_path(base, context_path)
    intended = str(entry.get("intended_use", "")).strip()
    if intended:
        return intended
    raise SourceContextError(
        f"source {entry.get('citation_key', '<unknown>')} has no trusted content"
    )


def _read_context_path(base: Path, context_path: str) -> str:
    candidate = (base / context_path).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError as exc:
        raise SourceContextError(
            f"context path escapes manifest directory: {context_path}"
        ) from exc
    if not candidate.is_file():
        raise SourceContextError(f"source context file missing: {context_path}")
    text = candidate.read_text(encoding="utf-8").strip()
    if not text:
        raise SourceContextError(f"source context file is empty: {context_path}")
    return text


def _authors(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value.strip(),) if value.strip() else ()
    return tuple(str(item).strip() for item in value or [] if str(item).strip())


def _required_text(entry: dict[str, object], field: str, index: int) -> str:
    value = str(entry.get(field, "")).strip()
    if not value:
        raise SourceContextError(f"source #{index} requires {field}")
    return value


def _optional_text(value: object) -> str | None:
    text = str(value or "").strip()
    return text or None


def _identifiers(source: SourceRecord) -> str:
    return ", ".join(
        value
        for value in (
            f"arXiv:{source.arxiv_id}" if source.arxiv_id else "",
            f"DOI:{source.doi}" if source.doi else "",
        )
        if value
    )
