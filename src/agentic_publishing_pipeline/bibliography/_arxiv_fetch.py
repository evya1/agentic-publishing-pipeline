"""Polite arXiv Atom API fetcher (P7-I02).

Live HTTP I/O kept narrow and stdlib-only so it can be swapped or
mocked from tests. The fetcher is used by the Phase 7 verification
script; the unit tests never call it directly.
"""

from __future__ import annotations

import time
import urllib.error
import urllib.request
from dataclasses import dataclass

_BASE = "http://export.arxiv.org/api/query"
_USER_AGENT = "agentic-publishing-pipeline/0.0 (P7-I02 source verification)"
_POLITE_DELAY_S = 3.0  # arXiv requests >= 3 s between requests.


class ArxivFetchError(RuntimeError):
    """Raised when an arXiv Atom response cannot be retrieved."""


@dataclass(frozen=True)
class ArxivFetchResponse:
    url: str
    status: int
    body: bytes


def fetch_arxiv_metadata(
    arxiv_id: str,
    *,
    timeout_s: float = 30.0,
    polite_delay_s: float = _POLITE_DELAY_S,
    sleeper: object = None,
) -> ArxivFetchResponse:
    """Fetch the arXiv Atom feed for ``arxiv_id``.

    ``polite_delay_s`` honours arXiv's request to wait between
    queries. ``sleeper`` is the ``time.sleep`` injection point used
    by tests.
    """

    assert arxiv_id, "arxiv_id must be non-empty"
    sleep_fn = sleeper or time.sleep
    if polite_delay_s > 0:
        sleep_fn(polite_delay_s)
    url = f"{_BASE}?id_list={arxiv_id}"
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as response:  # noqa: S310 - https arxiv API
            body = response.read()
            status = response.status
    except urllib.error.URLError as exc:
        raise ArxivFetchError(f"arXiv fetch failed for {arxiv_id!r}: {exc}") from exc
    if status != 200:
        raise ArxivFetchError(
            f"arXiv fetch for {arxiv_id!r} returned status {status}"
        )
    return ArxivFetchResponse(url=url, status=status, body=body)
