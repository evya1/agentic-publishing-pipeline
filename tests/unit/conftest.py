"""Shared fixtures for visualization unit tests."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from agentic_publishing_pipeline.runtime import PipelineRunContext, generate_run_id


def make_run_context(tmp_path: Path) -> PipelineRunContext:
    return PipelineRunContext(
        run_id=generate_run_id(),
        results_root=tmp_path / "results",
        mode="visualization",
        env={},
    )


def valid_graph_spec_payload() -> dict[str, object]:
    return deepcopy(
        {
            "schema_version": 1,
            "asset_id": "planning_benchmark_comparison",
            "kind": "grouped_bar_chart",
            "slot": "planning_benchmark_comparison",
            "chapter_id": "planning",
            "output_dir": "latex_project/figures",
            "title": "Planning benchmark coverage drops under symbol obfuscation",
            "caption": "Grouped benchmark comparison.",
            "x_label": "Method",
            "y_label": "Solved tasks (out of 360)",
            "metric": {
                "name": "solved_tasks",
                "unit": "tasks",
                "direction": "higher_is_better",
            },
            "data": {
                "categories": ["Planner", "GPT-5"],
                "series": [
                    {"label": "Standard tasks", "values": [234, 205]},
                    {"label": "Obfuscated tasks", "values": [234, 142]},
                ],
            },
            "source": {
                "citation_key": "correa2025planningperformance",
                "identifier": "arXiv:2511.09378v2",
                "publication_url_or_doi": "https://doi.org/10.48550/arXiv.2511.09378",
                "locator": {
                    "page": None,
                    "table": "Tables 1 and 2",
                    "figure": None,
                    "rows": ["Sum (360)"],
                },
                "notes": "Selected totals.",
            },
            "transformations": ["Selected a subset of methods from the source tables."],
            "render": {"width_inches": 7.2, "height_inches": 4.2, "dpi": 200, "seed": 0},
        }
    )
