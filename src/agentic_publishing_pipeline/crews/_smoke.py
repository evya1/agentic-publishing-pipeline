"""Offline-fixture end-to-end smoke run.

Exercises every Phase 5 seam (provider facade, Gatekeeper, FileIO,
search, markdown, graph) and produces a complete run workspace with
typed artifacts. No network, no API keys.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..contracts import (
    AssetSpecs,
    BibliographyBundle,
    BiDiSection,
    ChapterDrafts,
    LaTeXProjectSpec,
    Outline,
    ResearchNotes,
    ReviewerSignal,
)
from ..providers import (
    FixtureModelAdapter,
    FixtureSearchAdapter,
    ModelRequest,
    ModelResponse,
    ProviderFacade,
    SearchRequest,
)
from ..providers.config import load_provider_config
from ..runtime import PipelineRunContext
from ..tools import (
    ApiGatekeeper,
    FileIO,
    load_source_manifest_hits,
    request_identity,
)
from ..visualization import LinePlotSpec, render_line_plot

OFFLINE_MODES: tuple[str, ...] = ("offline-fixture", "dry-run")
FIXTURE_ROOT = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "offline"
TASK_BOUNDARIES = {
    "RESEARCH": ("research_notes", "ResearchNotes", ResearchNotes),
    "OUTLINE": ("outline", "Outline", Outline),
    "WRITE": ("chapter_drafts", "ChapterDrafts", ChapterDrafts),
    "ASSET": ("asset_specs", "AssetSpecs", AssetSpecs),
    "BIDI": ("bidi", "BiDiSection", BiDiSection),
    "BIBLIOGRAPHY": ("bibliography", "BibliographyBundle", BibliographyBundle),
    "LATEX": ("latex_project_spec", "LaTeXProjectSpec", LaTeXProjectSpec),
    "REVIEW": ("reviewer_signal", "ReviewerSignal", ReviewerSignal),
}


def _build_gatekeeper(ctx: PipelineRunContext, manifest_path: Path) -> ApiGatekeeper:
    hits = load_source_manifest_hits(manifest_path)
    config = load_provider_config({})
    fixtures = _load_model_fixtures(FIXTURE_ROOT / "task_responses.json")
    facade = ProviderFacade(
        model=FixtureModelAdapter(fixtures=fixtures),
        search=FixtureSearchAdapter(hits=hits),
    )
    return ApiGatekeeper(facade=facade, config=config, run_context=ctx)


def _load_model_fixtures(path: Path) -> dict[str, ModelResponse]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        key: ModelResponse(
            text=str(value["text"]),
            tokens_in=int(value["tokens_in"]),
            tokens_out=int(value["tokens_out"]),
            latency_ms=float(value["latency_ms"]),
            model_id=str(value["model_id"]),
            finish_reason=str(value.get("finish_reason", "stop")),
        )
        for key, value in payload.items()
    }


def _render_demo_graph(ctx: PipelineRunContext) -> None:
    fio = FileIO(ctx)
    spec = LinePlotSpec(
        series_label="accuracy",
        x_values=[1.0, 2.0, 3.0],
        y_values=[0.6, 0.75, 0.82],
        x_label="round",
        y_label="accuracy",
        title="Demo accuracy",
    )
    render_line_plot(spec, fileio=fio, relative_target="latex_project/figures/demo.png")


def _parse_fixture_contract(ctx: PipelineRunContext, gk: ApiGatekeeper, key: str):
    artifact_id, contract, model_cls = TASK_BOUNDARIES[key]
    response = gk.call_model(
        ModelRequest(
            model_class=key,
            prompt=f"Emit deterministic {contract} fixture payload.",
            metadata={"fixture_key": key},
        ),
        identity=request_identity(key.lower(), key),
    )
    payload = json.loads(response.text)
    model = model_cls.model_validate({"run_id": ctx.run_id, **payload})
    ctx.events.append("task.fixture_parsed", {"task_id": key, "contract": contract})
    return artifact_id, contract, model


def _persist(ctx: PipelineRunContext, *, contract: str, artifact_id: str, model) -> None:
    rel = f"artifacts/{artifact_id}.v1.json"
    ctx.write_artifact_json(rel, model.model_dump(mode="json"))
    ctx.register_artifact(
        artifact_id=artifact_id,
        contract=contract,
        contract_version="v1",
        relative_path=rel,
        produced_by_task=artifact_id,
    )


def run_offline_smoke(ctx: PipelineRunContext, *, manifest_path: Path) -> None:
    """Produce a complete offline workspace with the eight typed artifacts."""

    gk = _build_gatekeeper(ctx, manifest_path)
    gk.call_search(SearchRequest(query="reasoning"), identity=request_identity("research", "T1"))
    for key in TASK_BOUNDARIES:
        artifact_id, contract, model = _parse_fixture_contract(ctx, gk, key)
        _persist(ctx, contract=contract, artifact_id=artifact_id, model=model)
    _render_demo_graph(ctx)
