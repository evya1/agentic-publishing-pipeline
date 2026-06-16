from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from agentic_publishing_pipeline.contracts import (
    AssetSpec,
    AssetSpecs,
    BibEntry,
    BibliographyBundle,
    BiDiSection,
    ChapterDraft,
    ChapterDrafts,
    Outline,
    ResearchNotes,
    ReviewerSignal,
)
from agentic_publishing_pipeline.crews import live_runner
from agentic_publishing_pipeline.crews.live_runner import (
    ManuscriptPreflightFailed,
    _llm_factory,
    run_live_manuscript,
)
from agentic_publishing_pipeline.runtime import PipelineRunContext
from agentic_publishing_pipeline.tasks import REQUIRED_CHAPTER_IDS
from agentic_publishing_pipeline.tasks.completeness import ManuscriptPreflightReport


def _context(tmp_path: Path) -> PipelineRunContext:
    return PipelineRunContext.create(
        results_root=tmp_path.resolve(),
        mode="live",
        topic="Reasoning",
    )


def _hebrew() -> str:
    return " ".join(["זיכרון", "סוכן", "תכנון", "הקשר"] * 12) + " reasoning"


def _outputs(run_id: str):
    chapters = []
    for chapter_id in REQUIRED_CHAPTER_IDS:
        body = f"# {chapter_id}\n\nword"
        if chapter_id == "memory":
            body += (
                " <!-- FIGURE: memory figure --> <!-- TABLE: memory table --> "
                "<!-- EQUATION: memory equation --> <!-- CITATION: k1 -->"
            )
        chapters.append(ChapterDraft(chapter_id=chapter_id, heading=chapter_id, body_markdown=body))
    values = [
        ResearchNotes(
            run_id=run_id,
            topic="t",
            dimensions=[{"dimension": "memory", "summary": "s"}],
        ),
        Outline(
            run_id=run_id,
            chapters=[{"chapter_id": "memory", "title": "Memory", "summary": "s"}],
            target_total_pages=1,
        ),
        ChapterDrafts(run_id=run_id, chapters=chapters),
        AssetSpecs(
            run_id=run_id,
            assets=[
                AssetSpec(kind="image", slot="memory/figure-1", chapter_id="memory"),
                AssetSpec(kind="table", slot="memory/table-2", chapter_id="memory"),
                AssetSpec(kind="equation", slot="memory/equation-3", chapter_id="memory"),
            ],
        ),
        BiDiSection(
            run_id=run_id,
            chapter_id="memory",
            hebrew_body=_hebrew(),
            inline_english_terms=["reasoning"],
        ),
        BibliographyBundle(
            run_id=run_id,
            entries=[
                BibEntry(
                    citation_key="k1",
                    entry_type="article",
                    title="Locked Source",
                    year=2025,
                    verification_status="verified",
                )
            ],
            placeholder_resolution={"k1": "k1"},
            manifest_coverage=["k1"],
        ),
        ReviewerSignal(run_id=run_id, signal="pass"),
    ]
    return SimpleNamespace(tasks_output=[SimpleNamespace(pydantic=value) for value in values])


def _patch_builders(monkeypatch: pytest.MonkeyPatch, result: object) -> None:
    class FakeCrew:
        def kickoff(self, inputs: dict[str, str]) -> object:
            assert inputs["topic"] == "Reasoning"
            return result

    monkeypatch.setattr(live_runner, "build_agents", lambda **_: {})
    monkeypatch.setattr(live_runner, "build_manuscript_tasks", lambda **_: [])
    monkeypatch.setattr(live_runner, "build_manuscript_crew", lambda **_: FakeCrew())


def _run(ctx: PipelineRunContext):
    return run_live_manuscript(
        context=ctx,
        registry=SimpleNamespace(),
        gatekeeper=SimpleNamespace(),
        topic="Reasoning",
        source_context_text="citation_key: k1",
        citation_keys=("k1",),
        target_pages=1,
        target_words=1,
        min_words_per_chapter=1,
    )


def test_live_runner_composes_persists_and_awaits_review(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ctx = _context(tmp_path)
    _patch_builders(monkeypatch, _outputs(ctx.run_id))
    outputs, report = _run(ctx)
    status = json.loads((ctx.paths.root / "status.json").read_text(encoding="utf-8"))
    memory = (ctx.paths.root / "generated_markdown/chapters/memory.md").read_text()
    assert report.passed
    assert status["stage"] == "awaiting_human_review"
    assert outputs.bidi.hebrew_body in memory
    assert (ctx.paths.root / "typed_outputs/chapter_drafts.json").is_file()
    assert (ctx.paths.root / "preflight_report.json").is_file()


def test_live_runner_records_generation_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingCrew:
        def kickoff(self, inputs: dict[str, str]) -> object:
            raise RuntimeError("model exploded")

    ctx = _context(tmp_path)
    monkeypatch.setattr(live_runner, "build_agents", lambda **_: {})
    monkeypatch.setattr(live_runner, "build_manuscript_tasks", lambda **_: [])
    monkeypatch.setattr(live_runner, "build_manuscript_crew", lambda **_: FailingCrew())
    with pytest.raises(RuntimeError, match="model exploded"):
        _run(ctx)
    status = json.loads((ctx.paths.root / "status.json").read_text(encoding="utf-8"))
    assert status["stage"] == "generation_failed"


def test_live_runner_records_parsing_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ctx = _context(tmp_path)
    _patch_builders(monkeypatch, SimpleNamespace(tasks_output=[]))
    with pytest.raises(Exception):
        _run(ctx)
    status = json.loads((ctx.paths.root / "status.json").read_text(encoding="utf-8"))
    assert status["stage"] == "parsing_failed"


def test_live_runner_records_persistence_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ctx = _context(tmp_path)
    _patch_builders(monkeypatch, _outputs(ctx.run_id))
    monkeypatch.setattr(
        live_runner,
        "persist_manuscript_outputs",
        lambda **_: (_ for _ in ()).throw(RuntimeError("disk full")),
    )
    with pytest.raises(RuntimeError, match="disk full"):
        _run(ctx)
    status = json.loads((ctx.paths.root / "status.json").read_text(encoding="utf-8"))
    assert status["stage"] == "persistence_failed"


def test_live_runner_records_preflight_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ctx = _context(tmp_path)
    _patch_builders(monkeypatch, _outputs(ctx.run_id))
    monkeypatch.setattr(
        live_runner,
        "run_manuscript_preflight",
        lambda *_, **__: ManuscriptPreflightReport(
            passed=False,
            word_counts={},
            total_words=0,
            cited_keys=(),
            missing_source_keys=("k1",),
            errors=("bad manuscript",),
        ),
    )
    with pytest.raises(ManuscriptPreflightFailed, match="bad manuscript"):
        _run(ctx)
    status = json.loads((ctx.paths.root / "status.json").read_text(encoding="utf-8"))
    assert status["stage"] == "preflight_failed"


def test_live_runner_records_preflight_exception(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ctx = _context(tmp_path)
    _patch_builders(monkeypatch, _outputs(ctx.run_id))
    monkeypatch.setattr(
        live_runner,
        "run_manuscript_preflight",
        lambda *_, **__: (_ for _ in ()).throw(ValueError("bad preflight")),
    )
    with pytest.raises(ValueError, match="bad preflight"):
        _run(ctx)
    status = json.loads((ctx.paths.root / "status.json").read_text(encoding="utf-8"))
    assert status["stage"] == "preflight_failed"


def test_llm_factory_applies_task_repair_configuration() -> None:
    class FakePrompt:
        version = "v3"
        config = {"repair_attempts_allowed": 2}

    class FakeRegistry:
        def get_agent(self, prompt_id: str) -> FakePrompt:
            return FakePrompt()

        def get_task(self, prompt_id: str) -> FakePrompt:
            return FakePrompt()

    calls = {}

    def builder(**kwargs):
        calls.update(kwargs)
        return "llm"

    factory = _llm_factory(
        registry=FakeRegistry(),
        gatekeeper=object(),
        run_id="RUN-20260616-000000-aaaaaaaa",
        llm_builder=builder,
    )
    assert factory("writer", "write", "writer-model") == "llm"
    assert calls["prompt_version"] == "v3"
    assert calls["max_attempts"] == 3
    assert calls["max_repairs"] == 2
