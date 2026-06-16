"""Naming and path-safety tests for visualization artifacts."""

from __future__ import annotations

from agentic_publishing_pipeline.visualization.models import GroupedBarChartSpec
from agentic_publishing_pipeline.visualization.naming import (
    build_output_paths,
    validate_output_dir,
    validate_slug,
)

from .conftest import valid_graph_spec_payload


def test_build_output_paths_uses_hash_suffix() -> None:
    spec = GroupedBarChartSpec.model_validate(valid_graph_spec_payload())
    png_path, provenance_path = build_output_paths(spec, input_sha256="a" * 64)
    assert png_path == "latex_project/figures/planning_benchmark_comparison_aaaaaaaa.png"
    assert provenance_path.endswith(".png.prov.json")


def test_validate_slug_rejects_unsafe_values() -> None:
    assert validate_slug("../escape", field="asset_id")
    assert validate_slug("a/b", field="slot")
    assert validate_slug(".hidden", field="asset_id")
    assert validate_slug("bad\x00name", field="asset_id")


def test_validate_output_dir_rejects_traversal_and_backslashes() -> None:
    assert validate_output_dir("../escape")
    assert validate_output_dir(r"latex_project\figures")
    assert validate_output_dir("/absolute")
