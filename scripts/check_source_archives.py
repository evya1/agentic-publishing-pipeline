"""Verify that source archives are not tracked in git.

Downloaded source archives (tar, gz, zip, etc.) must never be committed.
Exits 1 when any archive file is found in the git index.
"""

from __future__ import annotations

import subprocess
import sys

_ARCHIVE_SUFFIXES = (
    ".tar",
    ".tar.gz",
    ".tgz",
    ".tar.bz2",
    ".tbz2",
    ".tar.xz",
    ".zip",
    ".gz",
    ".bz2",
    ".xz",
)


def _tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.splitlines()


def main() -> int:
    tracked = _tracked_files()
    archives = [f for f in tracked if any(f.endswith(suffix) for suffix in _ARCHIVE_SUFFIXES)]

    if archives:
        print("FAIL: source archive files are tracked in git:")
        for path in archives:
            print(f"  {path}")
        return 1

    print("OK: no source archives tracked in git.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
