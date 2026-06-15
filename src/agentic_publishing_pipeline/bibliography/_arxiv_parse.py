"""Parser for arXiv Atom API responses (P7-I02).

The arXiv API at ``http://export.arxiv.org/api/query`` returns an
Atom 1.0 feed. We extract the minimum bibliographic fields needed for
verification: title, ordered author list, published year. The parser
is pure (string in → typed metadata out) so it can be unit-tested
against committed XML fixtures without network access.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from xml.etree import ElementTree as ET

_NS = {
    "a": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


class ArxivParseError(RuntimeError):
    """Raised when an arXiv Atom response cannot be parsed."""


@dataclass(frozen=True)
class ArxivMetadata:
    arxiv_id: str
    title: str
    authors: tuple[str, ...]  # natural order, "Given Family" as published.
    published_year: int
    primary_category: str | None
    doi: str | None


def _norm_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _strip_arxiv_version(arxiv_id: str) -> str:
    return re.sub(r"v\d+$", "", arxiv_id.strip())


def parse_arxiv_feed(xml_bytes: bytes | str, *, expected_id: str) -> ArxivMetadata:
    """Parse an arXiv Atom feed for a single ``id_list=<arxiv_id>`` query."""

    assert expected_id, "expected_id must be non-empty"
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ArxivParseError(f"arXiv response is not valid XML: {exc}") from exc
    entry = root.find("a:entry", _NS)
    if entry is None:
        raise ArxivParseError("arXiv response has no <entry>")
    id_node = entry.find("a:id", _NS)
    if id_node is None or not id_node.text:
        raise ArxivParseError("arXiv entry missing <id>")
    raw_id = id_node.text.strip().rsplit("/", 1)[-1]
    canonical_id = _strip_arxiv_version(raw_id)
    if canonical_id != expected_id:
        raise ArxivParseError(
            f"arXiv id mismatch: expected {expected_id!r}, got {canonical_id!r}"
        )
    title_node = entry.find("a:title", _NS)
    if title_node is None or not title_node.text:
        raise ArxivParseError("arXiv entry missing <title>")
    title = _norm_whitespace(title_node.text)
    authors: list[str] = []
    for author in entry.findall("a:author", _NS):
        name = author.find("a:name", _NS)
        if name is None or not name.text or not name.text.strip():
            raise ArxivParseError("arXiv entry has empty <author>/<name>")
        authors.append(_norm_whitespace(name.text))
    if not authors:
        raise ArxivParseError("arXiv entry has no authors")
    published = entry.find("a:published", _NS)
    if published is None or not published.text:
        raise ArxivParseError("arXiv entry missing <published>")
    year_match = re.match(r"^(\d{4})-", published.text.strip())
    if year_match is None:
        raise ArxivParseError(
            f"arXiv <published> is not ISO-8601: {published.text!r}"
        )
    year = int(year_match.group(1))
    primary = entry.find("arxiv:primary_category", _NS)
    primary_category = primary.get("term") if primary is not None else None
    doi_node = entry.find("arxiv:doi", _NS)
    doi = _norm_whitespace(doi_node.text) if doi_node is not None and doi_node.text else None
    return ArxivMetadata(
        arxiv_id=canonical_id,
        title=title,
        authors=tuple(authors),
        published_year=year,
        primary_category=primary_category,
        doi=doi,
    )


def to_surname_given(author: str) -> str:
    """Convert ``"Given Middle Family"`` to ``"Family, Given Middle"``.

    The repository's manifest stores ``authors:`` as ``"<Surname, Given>"``
    strings (see ``config/article_sources.yaml`` schema comment).
    arXiv ships ``"<Given> <Family>"``. The transform splits on the
    last whitespace; multi-word family names that arXiv ships as a
    single token continue to round-trip correctly.
    """

    name = _norm_whitespace(author)
    if "," in name:
        # Already in "Family, Given" form; leave alone.
        return name
    parts = name.rsplit(" ", 1)
    if len(parts) != 2:
        return name
    given, family = parts[0], parts[1]
    return f"{family}, {given}"
