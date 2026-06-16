"""P11-I01: ValidatorService — deterministic artifact validation, no LLM calls."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .checks_citations import run_citation_checks
from .checks_latex import run_latex_checks
from .checks_pdf import run_pdf_checks
from .checks_repo import run_repo_checks
from .report import ValidationReport


class ValidatorService:
    """Run all validation checks and return a structured report.

    All checks are deterministic file-system or text-pattern operations.
    No LLM or network calls are made (NFR-19 / FR-40).
    """

    def __init__(self, repo_root: Path | None = None) -> None:
        self._repo_root = (repo_root or Path.cwd()).resolve()

    def run(self) -> ValidationReport:
        report = ValidationReport(run_at=datetime.now(), repo_root=self._repo_root)

        run_repo_checks(self._repo_root, report)
        run_latex_checks(self._repo_root / "latex_project", report)
        run_pdf_checks(self._repo_root / "results" / "final.pdf", report)
        run_citation_checks(self._repo_root / "latex_project", report)

        return report

    def run_and_save(self, output_dir: Path | None = None) -> tuple[ValidationReport, Path]:
        """Run checks, write the Markdown report, and return both."""
        report = self.run()

        out_dir = output_dir or (self._repo_root / "results" / "run_logs")
        out_dir.mkdir(parents=True, exist_ok=True)

        timestamp = report.run_at.strftime("%Y%m%d-%H%M%S")
        report_path = out_dir / f"validation_report_{timestamp}.md"
        report_path.write_text(report.to_markdown(), encoding="utf-8")

        return report, report_path
