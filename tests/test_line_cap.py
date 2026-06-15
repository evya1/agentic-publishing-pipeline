"""Line-cap checker tests."""

from __future__ import annotations

from pathlib import Path

from scripts.check_line_cap import check_roots, main, measured_lines


def test_measured_lines_ignores_blank_and_comment_lines(tmp_path: Path) -> None:
    target = tmp_path / "small.py"
    target.write_text(
        '"""module docstring"""\n\n# comment\n\nVALUE = 1\n',
        encoding="utf-8",
    )
    assert measured_lines(target) == 2


def test_synthetic_over_limit_file_fails(tmp_path: Path) -> None:
    target = tmp_path / "too_big.py"
    target.write_text("\n".join(f"value_{idx} = {idx}" for idx in range(151)), encoding="utf-8")
    assert check_roots([tmp_path], limit=150) == [(target, 151)]
    assert main(["--limit", "150", str(tmp_path)]) == 1


def test_current_source_tree_passes_line_cap() -> None:
    assert main(["--limit", "150", "src"]) == 0
