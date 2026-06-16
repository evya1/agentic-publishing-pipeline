"""Entry point: uv run python -m agentic_publishing_pipeline.validation"""

from __future__ import annotations

import sys
from pathlib import Path

from .validator_service import ValidatorService


def main() -> None:
    repo_root = Path(__file__).parent.parent.parent.parent.resolve()
    service = ValidatorService(repo_root=repo_root)
    report, report_path = service.run_and_save()

    print(report.to_markdown())
    print(f"\nReport saved: {report_path.relative_to(repo_root)}")

    sys.exit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
