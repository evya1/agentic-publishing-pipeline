"""Persist validated manuscript outputs into an isolated run workspace."""

from __future__ import annotations

from pathlib import Path

from ..runtime import PipelineRunContext
from ..tools.fileio import FileIO
from .result_parser import ManuscriptOutputs

_TYPED_OUTPUTS: tuple[tuple[str, str, str], ...] = (
    ("research", "ResearchNotes.v1", "research"),
    ("outline", "Outline.v1", "outline"),
    ("chapters", "ChapterDrafts.v1", "write"),
    ("assets", "AssetSpecs.v1", "asset"),
    ("bidi", "BiDiSection.v1", "bidi"),
    ("bibliography", "BibliographyBundle.v1", "bibliography"),
    ("reviewer", "ReviewerSignal.v1", "review"),
)


def persist_manuscript_outputs(
    *,
    context: PipelineRunContext,
    outputs: ManuscriptOutputs,
) -> dict[str, Path]:
    """Write validated Pydantic models and candidate Markdown."""
    io = FileIO(context)
    written: dict[str, Path] = {}
    for name, contract, task_id in _TYPED_OUTPUTS:
        model = getattr(outputs, name)
        rel = f"artifacts/typed_outputs/{name}.json"
        written[f"typed:{name}"] = io.write_json(rel, model.model_dump(mode="json"))
        context.register_artifact(
            artifact_id=f"typed:{name}",
            contract=contract,
            contract_version="v1",
            relative_path=rel,
            produced_by_task=task_id,
        )
    _write_chapters(context, io, outputs, written)
    written["outline"] = io.write_text(
        "artifacts/generated_markdown/outline.md",
        _outline_markdown(outputs),
    )
    written["research_notes"] = io.write_text(
        "artifacts/generated_markdown/research_notes.md",
        _research_markdown(outputs),
    )
    return written


def _write_chapters(
    context: PipelineRunContext,
    io: FileIO,
    outputs: ManuscriptOutputs,
    written: dict[str, Path],
) -> None:
    for chapter in outputs.chapters.chapters:
        rel = f"artifacts/generated_markdown/chapters/{chapter.chapter_id}.md"
        written[f"chapter:{chapter.chapter_id}"] = io.write_text(
            rel,
            chapter.body_markdown.rstrip() + "\n",
        )
        context.register_artifact(
            artifact_id=f"chapter:{chapter.chapter_id}",
            contract="ChapterDrafts.v1",
            contract_version="v1",
            relative_path=rel,
            produced_by_task="write",
        )


def _outline_markdown(outputs: ManuscriptOutputs) -> str:
    lines = ["# Outline", ""]
    for chapter in outputs.outline.chapters:
        lines.extend((f"## {chapter.title}", "", chapter.summary, ""))
    return "\n".join(lines).rstrip() + "\n"


def _research_markdown(outputs: ManuscriptOutputs) -> str:
    lines = [f"# Research notes: {outputs.research.topic}", ""]
    for dimension in outputs.research.dimensions:
        lines.extend((f"## {dimension.dimension.replace('_', ' ').title()}", ""))
        lines.extend((dimension.summary, ""))
        lines.extend(f"- {point}" for point in dimension.key_points)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
