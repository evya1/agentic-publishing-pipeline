"""Provisional → final citation-key migration (P7-I05).

The Phase 7 verification step (P7-I02) populates every manifest
record's ``authors`` with authoritative arXiv data. P7-I05 then
rekeys the provisional ``tbd…`` placeholders to the project's stable
``authorYYYYkey`` convention from
``docs/PRD_bibliography_and_citations.md`` §9 / §13.1.

The migration is **deterministic** and **transparent**:

- the final key is derived from the verified first author's family
  name (ASCII-lowercase, diacritics stripped), the verified
  publication year, and the slug suffix of the provisional key;
- collisions across the migrated map are rejected loudly;
- text substitutions use word-boundary regex so that
  ``tbd2026agenticreasoning`` does not partially match
  ``tbd2025agenticreasoningtools``;
- the entrypoint refuses to migrate a manifest that still has
  unverified or rejected records.

The migration touches **active** artifacts (manifest, generated
Markdown, static templates, offline fixtures, audit ledger). It does
**not** rewrite historical run-log evidence (the Phase 6 review
packet or its review record), so the Phase 6 review gate will
correctly observe that the approved hash no longer matches the
migrated Markdown and request honest reapproval.
"""

from __future__ import annotations

import re
import unicodedata

from .manifest import SourceManifest, SourceRecord


class RekeyError(RuntimeError):
    """Raised when the key migration cannot proceed safely."""


_DIACRITIC_NFKD = "NFKD"
_NON_ASCII_LETTER = re.compile(r"[^a-z]")


def _surname(author: str) -> str:
    """Return the family name from a ``"Family, Given"`` author string."""

    if not author or "," not in author:
        raise RekeyError(
            f"first author must be in 'Family, Given' form for rekey; got {author!r}"
        )
    family = author.split(",", 1)[0]
    decomposed = unicodedata.normalize(_DIACRITIC_NFKD, family)
    ascii_family = "".join(c for c in decomposed if not unicodedata.combining(c))
    ascii_lower = ascii_family.lower()
    stripped = _NON_ASCII_LETTER.sub("", ascii_lower)
    if not stripped:
        raise RekeyError(
            f"family name {family!r} has no ASCII letters after normalization"
        )
    return stripped


def _slug_from_provisional(provisional_key: str, year: int) -> str:
    """Return the slug suffix from a provisional ``tbdYYYY<slug>`` key."""

    expected_prefix = f"tbd{year}"
    if provisional_key.startswith(expected_prefix):
        return provisional_key[len(expected_prefix) :]
    # Fall back to "tbd" + any year-like number prefix.
    match = re.match(r"^tbd\d{4}(.+)$", provisional_key)
    if not match:
        raise RekeyError(f"cannot derive slug from key {provisional_key!r}")
    return match.group(1)


def derive_final_key(record: SourceRecord) -> str:
    """Compute the deterministic ``authorYYYYkey`` for one verified record."""

    if record.verification.status != "verified":
        raise RekeyError(
            f"record {record.citation_key!r} is not verified; rekey refused"
        )
    if not record.authors:
        raise RekeyError(
            f"record {record.citation_key!r} has no authors; rekey refused"
        )
    family = _surname(record.authors[0])
    slug = _slug_from_provisional(record.citation_key, record.year)
    return f"{family}{record.year}{slug}"


def build_key_map(manifest: SourceManifest) -> dict[str, str]:
    """Return the provisional → final key map for an entire verified manifest."""

    mapping: dict[str, str] = {}
    seen_finals: dict[str, str] = {}
    for record in manifest.records:
        final = derive_final_key(record)
        if final in seen_finals:
            raise RekeyError(
                f"final key collision: {final!r} produced by both "
                f"{seen_finals[final]!r} and {record.citation_key!r}"
            )
        seen_finals[final] = record.citation_key
        mapping[record.citation_key] = final
    return mapping


def _compile_pattern(provisional_keys: list[str]) -> re.Pattern[str]:
    # Longest first so prefixes never shadow longer keys; also use word
    # boundaries so accidental substring matches are impossible.
    keys_sorted = sorted(provisional_keys, key=len, reverse=True)
    alternation = "|".join(re.escape(k) for k in keys_sorted)
    return re.compile(rf"\b({alternation})\b")


def apply_key_map(text: str, key_map: dict[str, str]) -> tuple[str, int]:
    """Apply ``key_map`` to ``text``; return ``(new_text, replacements_count)``."""

    if not key_map:
        return text, 0
    pattern = _compile_pattern(list(key_map.keys()))
    count = 0

    def _sub(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        return key_map[match.group(1)]

    return pattern.sub(_sub, text), count
