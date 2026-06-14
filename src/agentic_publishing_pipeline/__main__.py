"""Module entry point: ``python -m agentic_publishing_pipeline``."""

from __future__ import annotations

import sys

from .crews import main

if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
