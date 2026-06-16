"""Validation report data types and Markdown formatter."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str


@dataclass
class ValidationReport:
    results: list[CheckResult] = field(default_factory=list)
    run_at: datetime = field(default_factory=datetime.now)
    repo_root: Path = field(default_factory=Path.cwd)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)

    def add(self, name: str, passed: bool, message: str) -> None:
        self.results.append(CheckResult(name, passed, message))

    def to_markdown(self) -> str:
        lines = [
            "# Validation Report",
            "",
            f"**Run:** {self.run_at.strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Commit:** {_git_short_hash(self.repo_root)}  ",
            f"**LuaLaTeX:** {_binary_version('lualatex')}  ",
            f"**biber:** {_binary_version('biber')}  ",
            "",
            "| Check | Status | Message |",
            "|-------|--------|---------|",
        ]
        for r in self.results:
            status = "PASS" if r.passed else "FAIL"
            safe_msg = r.message.replace("|", "\\|")
            lines.append(f"| {r.name} | {status} | {safe_msg} |")

        overall = "**PASS**" if self.passed else "**FAIL**"
        lines += ["", f"Overall: {overall}"]
        return "\n".join(lines)


def _git_short_hash(repo_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short=7", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _binary_version(binary: str) -> str:
    if not shutil.which(binary):
        return "not found"
    try:
        result = subprocess.run(
            [binary, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        first_line = (result.stdout or result.stderr).splitlines()[0]
        return first_line[:80]
    except Exception:
        return "unknown"
