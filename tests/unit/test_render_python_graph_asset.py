"""CLI tests for canonical graph generation."""

from __future__ import annotations

from pathlib import Path

import yaml

from agentic_publishing_pipeline.visualization.cli import main

from .conftest import valid_graph_spec_payload


def _write_spec(tmp_path: Path) -> Path:
    path = tmp_path / "graph.yaml"
    path.write_text(yaml.safe_dump(valid_graph_spec_payload(), sort_keys=False), encoding="utf-8")
    return path


def test_cli_main_generates_graph(tmp_path: Path) -> None:
    spec_path = _write_spec(tmp_path)
    exit_code = main(
        [
            "--spec",
            str(spec_path),
            "--output-root",
            str(tmp_path),
            "--overwrite-existing",
        ]
    )
    assert exit_code == 0
    figures = list((tmp_path / "latex_project" / "figures").glob("*.png"))
    assert len(figures) == 1


def test_cli_main_reports_validation_errors(tmp_path: Path) -> None:
    spec_path = _write_spec(tmp_path)
    bad_text = spec_path.read_text(encoding="utf-8").replace("grouped_bar_chart", "bad_kind")
    spec_path.write_text(bad_text, encoding="utf-8")
    exit_code = main(["--spec", str(spec_path), "--output-root", str(tmp_path)])
    assert exit_code == 2
