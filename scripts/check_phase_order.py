"""Phase-order protection check.

For phase/NN-* branches, verifies that Phase NN-1 is complete on the *base*
branch by reading docs/PLAN.md from the base commit via git show.  This
prevents a PR from marking its own predecessor complete and then passing the
check on its own modified text.

Usage:
    python scripts/check_phase_order.py <branch-name> [<base-commit-sha>]

When <base-commit-sha> is omitted the script reads PLAN.md from the working
tree (suitable for local ad-hoc checks but not for CI phase-order enforcement).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_PHASE_BRANCH_RE = re.compile(r"^phase/0*(\d+)")
_COMPLETE_RE = re.compile(r"Phase\s+(\d+)[^\n]*\*\(complete", re.IGNORECASE)


def _plan_text_from_base(base_sha: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{base_sha}:docs/PLAN.md"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git show {base_sha}:docs/PLAN.md failed: {result.stderr.strip()}")
    return result.stdout


def _plan_text_from_working_tree() -> str:
    plan_path = Path(__file__).parent.parent / "docs" / "PLAN.md"
    if not plan_path.exists():
        raise RuntimeError("docs/PLAN.md not found.")
    return plan_path.read_text(encoding="utf-8")


def _completed_phases(plan_text: str) -> set[int]:
    return {int(m.group(1)) for m in _COMPLETE_RE.finditer(plan_text)}


def main(argv: list[str]) -> int:
    if not argv:
        print("Usage: check_phase_order.py <branch-name> [<base-commit-sha>]")
        return 1

    branch = argv[0]
    base_sha = argv[1] if len(argv) > 1 else None

    m = _PHASE_BRANCH_RE.match(branch)
    if not m:
        print(f"OK: '{branch}' is not a phase/* branch — no order check needed.")
        return 0

    phase_num = int(m.group(1))
    if phase_num <= 1:
        print(f"OK: phase {phase_num} has no predecessor to verify.")
        return 0

    required_predecessor = phase_num - 1

    try:
        if base_sha:
            plan_text = _plan_text_from_base(base_sha)
            source = f"base commit {base_sha[:12]}"
        else:
            plan_text = _plan_text_from_working_tree()
            source = "working tree"
    except RuntimeError as exc:
        print(f"FAIL: {exc}")
        return 1

    completed = _completed_phases(plan_text)
    if required_predecessor not in completed:
        print(
            f"FAIL: branch is for Phase {phase_num} but Phase {required_predecessor} "
            f"is not marked complete in docs/PLAN.md ({source})."
        )
        return 1

    print(f"OK: Phase {required_predecessor} complete on {source}; Phase {phase_num} may proceed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
