"""Versioned provenance records for rendered graph assets."""

from __future__ import annotations

import platform

import matplotlib

from .models import GroupedBarChartSpec


def build_provenance(
    spec: GroupedBarChartSpec,
    *,
    input_sha256: str,
    output_sha256: str,
    relative_png_path: str,
    commit_sha: str | None,
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "asset_id": spec.asset_id,
        "kind": spec.kind,
        "slot": spec.slot,
        "chapter_id": spec.chapter_id,
        "title": spec.title,
        "caption": spec.caption,
        "path": relative_png_path,
        "metric": {
            "name": spec.metric.name,
            "unit": spec.metric.unit,
            "direction": spec.metric.direction,
        },
        "data": {
            "categories": spec.data.categories,
            "series": [
                {"label": series.label, "values": [float(value) for value in series.values]}
                for series in spec.data.series
            ],
        },
        "source": {
            "citation_key": spec.source.citation_key,
            "identifier": spec.source.identifier,
            "publication_url_or_doi": spec.source.publication_url_or_doi,
            "locator": spec.source.locator.model_dump(mode="json"),
            "notes": spec.source.notes,
        },
        "transformations": spec.transformations,
        "render": spec.render.model_dump(mode="json"),
        "renderer": {
            "name": "matplotlib_grouped_bar_chart",
            "version": matplotlib.__version__,
            "backend": matplotlib.get_backend(),
            "python_version": platform.python_version(),
            "commit_sha": commit_sha,
        },
        "input_sha256": input_sha256,
        "output_sha256": output_sha256,
    }
