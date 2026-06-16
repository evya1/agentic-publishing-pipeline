"""Validation tests for canonical graph specs."""

from __future__ import annotations

import math
from pathlib import Path

import pytest
import yaml

from agentic_publishing_pipeline.visualization import SpecValidationError, load_graph_spec

from .conftest import valid_graph_spec_payload


def _write_spec(tmp_path: Path, payload: dict[str, object]) -> Path:
    path = tmp_path / "graph.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return path


def test_load_graph_spec_accepts_valid_payload(tmp_path: Path) -> None:
    spec = load_graph_spec(_write_spec(tmp_path, valid_graph_spec_payload()))
    assert spec.asset_id == "planning_benchmark_comparison"


@pytest.mark.parametrize(
    ("mutation", "expected_path"),
    [
        (lambda payload: payload.__setitem__("kind", "line_chart"), "kind"),
        (lambda payload: payload["data"].__setitem__("categories", []), "data.categories"),
        (
            lambda payload: payload["data"]["series"][0].__setitem__("values", [234]),
            "data.series[0].values",
        ),
        (lambda payload: payload["data"].__setitem__("series", "bad"), "data.series"),
        (
            lambda payload: payload["data"]["series"][0].__setitem__("values", [None, 205]),
            "data.series[0].values[0]",
        ),
        (
            lambda payload: payload["data"]["series"][0].__setitem__("values", [True, 205]),
            "data.series[0].values[0]",
        ),
        (
            lambda payload: payload["data"]["series"][0].__setitem__("values", [math.nan, 205]),
            "data.series[0].values[0]",
        ),
        (
            lambda payload: payload["data"]["series"][0].__setitem__("values", [math.inf, 205]),
            "data.series[0].values[0]",
        ),
        (
            lambda payload: payload["data"]["series"][0].__setitem__("values", [-math.inf, 205]),
            "data.series[0].values[0]",
        ),
        (lambda payload: payload["render"].__setitem__("dpi", 0), "render.dpi"),
        (lambda payload: payload["render"].__setitem__("width_inches", 0), "render.width_inches"),
        (lambda payload: payload.__setitem__("slot", "../escape"), "slot"),
        (lambda payload: payload.__setitem__("asset_id", ".hidden"), "asset_id"),
        (lambda payload: payload.__setitem__("output_dir", "../escape"), "output_dir"),
        (lambda payload: payload.__setitem__("output_dir", r"..\escape"), "output_dir"),
        (lambda payload: payload.__setitem__("output_dir", "/absolute/path"), "output_dir"),
        (lambda payload: payload.__setitem__("output_dir", ".hidden/path"), "output_dir"),
        (lambda payload: payload.__setitem__("slot", "bad/value"), "slot"),
        (lambda payload: payload.__setitem__("asset_id", "bad\nvalue"), "asset_id"),
        (
            lambda payload: payload["source"]["locator"].__setitem__("table", None),
            "source.locator.table",
        ),
        (
            lambda payload: payload["source"]["locator"].__setitem__("rows", []),
            "source.locator.rows",
        ),
    ],
)
def test_load_graph_spec_rejects_invalid_payloads(
    tmp_path: Path,
    mutation,
    expected_path: str,
) -> None:
    payload = valid_graph_spec_payload()
    mutation(payload)
    with pytest.raises(SpecValidationError) as exc_info:
        load_graph_spec(_write_spec(tmp_path, payload))
    assert any(issue.path == expected_path for issue in exc_info.value.issues)


def test_load_graph_spec_rejects_unexpected_field(tmp_path: Path) -> None:
    payload = valid_graph_spec_payload()
    payload["unexpected"] = "value"
    with pytest.raises(SpecValidationError) as exc_info:
        load_graph_spec(_write_spec(tmp_path, payload))
    assert any(issue.path == "unexpected" for issue in exc_info.value.issues)
