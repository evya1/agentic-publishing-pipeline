"""Repository-artifact verification for the committed Phase 8 graph."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from agentic_publishing_pipeline.visualization import generate_graph
from agentic_publishing_pipeline.visualization.naming import build_output_paths
from agentic_publishing_pipeline.visualization.validator import load_graph_spec

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SPEC_PATH = _REPO_ROOT / "config" / "graphs" / "planning_benchmark_comparison.yaml"


def test_committed_graph_matches_spec_and_regenerates(tmp_path: Path) -> None:
    spec_bytes = _SPEC_PATH.read_bytes()
    spec_hash = hashlib.sha256(spec_bytes).hexdigest()
    spec = load_graph_spec(_SPEC_PATH)
    png_relative, provenance_relative = build_output_paths(spec, input_sha256=spec_hash)
    committed_png = _REPO_ROOT / png_relative
    committed_provenance = _REPO_ROOT / provenance_relative
    assert committed_png.exists()
    assert committed_provenance.exists()
    payload = json.loads(committed_provenance.read_text(encoding="utf-8"))
    assert payload["input_sha256"] == spec_hash
    assert payload["output_sha256"] == hashlib.sha256(committed_png.read_bytes()).hexdigest()
    result = generate_graph(spec_path=_SPEC_PATH, output_root=tmp_path, overwrite_existing=True)
    assert result.success
    assert (tmp_path / png_relative).read_bytes() == committed_png.read_bytes()
    regenerated_payload = json.loads((tmp_path / provenance_relative).read_text(encoding="utf-8"))
    assert regenerated_payload["renderer"].pop("python_version")
    assert payload["renderer"].pop("python_version")
    assert regenerated_payload == payload
