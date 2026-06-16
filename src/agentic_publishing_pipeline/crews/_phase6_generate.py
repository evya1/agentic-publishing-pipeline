"""Phase 6 canonical Markdown generation (P6-I01).

Reads the offline fixture pipeline, extracts manifest citation keys,
writes per-chapter Markdown files to results_root/generated_markdown/,
copies the canonical outline.md and research_notes.md templates from
the bundled package data alongside them, and records a run-log summary
at results_root/run_logs/<run_id>.jsonl.

Every CITATION placeholder description must match a key present in
config/article_sources.yaml (FR-13 / issue #18 acceptance criterion).
No LaTeX artifact is produced here; the human review gate (P6-I02)
enforces that boundary.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import yaml

from ..contracts import ChapterDrafts
from ._chapter_id import UnsafeChapterIdError, validate_chapter_id
from ._phase6_static import write_static_templates
from ._smoke import FIXTURE_ROOT, _load_model_fixtures

CANONICAL_MD = "generated_markdown"
CANONICAL_RUNLOGS = "run_logs"
CANONICAL_CHAPTERS_SUBDIR = "chapters"

__all__ = [
    "CANONICAL_CHAPTERS_SUBDIR",
    "CANONICAL_MD",
    "CANONICAL_RUNLOGS",
    "Phase6RunRecord",
    "UnsafeChapterIdError",
    "extract_manifest_keys",
    "run_phase6_generate",
]


@dataclass
class Phase6RunRecord:
    run_id: str
    generated_at: str
    manifest_path: str
    manifest_citation_keys: list[str] = field(default_factory=list)
    chapters_written: list[str] = field(default_factory=list)
    static_files_written: list[str] = field(default_factory=list)
    citation_keys_used: list[str] = field(default_factory=list)
    all_placeholder_kinds: list[str] = field(default_factory=list)


def extract_manifest_keys(manifest_path: Path) -> list[str]:
    """Return sorted citation_key values from article_sources.yaml."""
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    return sorted(
        str(entry["citation_key"])
        for entry in data.get("sources", [])
        if isinstance(entry, dict) and entry.get("citation_key")
    )


def _parse_write_fixture() -> ChapterDrafts:
    fixtures = _load_model_fixtures(FIXTURE_ROOT / "task_responses.json")
    response = fixtures.get("WRITE")
    assert response is not None, "WRITE fixture missing from task_responses.json"
    payload = json.loads(response.text)
    return ChapterDrafts.model_validate({"run_id": "offline-fixture", **payload})


def _write_chapter(md_root: Path, chapter_id: str, body: str) -> Path:
    safe_id = validate_chapter_id(chapter_id)
    chapters_root = (md_root / CANONICAL_CHAPTERS_SUBDIR).resolve()
    target = (chapters_root / f"{safe_id}.md").resolve()
    try:
        target.relative_to(chapters_root)
    except ValueError as exc:
        raise UnsafeChapterIdError(
            f"resolved chapter path {target} escapes {chapters_root}"
        ) from exc
    if target.parent != chapters_root:
        raise UnsafeChapterIdError(
            f"resolved chapter path {target} is not directly under {chapters_root}"
        )
    chapters_root.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".md.tmp-p6")
    tmp.write_text(body, encoding="utf-8")
    tmp.replace(target)
    return target


def _write_run_log(log_root: Path, record: Phase6RunRecord) -> Path:
    log_root.mkdir(parents=True, exist_ok=True)
    log_file = log_root / f"{record.run_id}.jsonl"
    entry = {
        "ts": record.generated_at,
        "kind": "phase6.generate.completed",
        "run_id": record.run_id,
        "manifest_path": record.manifest_path,
        "manifest_citation_keys": record.manifest_citation_keys,
        "chapters_written": record.chapters_written,
        "static_files_written": record.static_files_written,
        "citation_keys_used": record.citation_keys_used,
        "all_placeholder_kinds": record.all_placeholder_kinds,
    }
    log_file.write_text(json.dumps(entry, sort_keys=True) + "\n", encoding="utf-8")
    return log_file


def _validate_citation_keys(
    citation_descriptions: list[str],
    manifest_keys: list[str],
) -> None:
    manifest_set = set(manifest_keys)
    bad = [d for d in citation_descriptions if d not in manifest_set]
    if bad:
        raise ValueError(
            f"CITATION placeholder(s) reference keys absent from manifest: {bad}. "
            f"Valid keys: {sorted(manifest_set)}"
        )


def run_phase6_generate(
    results_root: Path,
    manifest_path: Path,
    *,
    run_id: str = "phase6-p6i01-offline-fixture",
) -> Phase6RunRecord:
    """Generate canonical Markdown drafts and a run-log record.

    Writes to:
    - results_root / "generated_markdown" / chapters / <id>.md
    - results_root / "run_logs" / <run_id>.jsonl
    """
    assert results_root.is_absolute(), "results_root must be absolute"
    manifest_keys = extract_manifest_keys(manifest_path)
    drafts = _parse_write_fixture()
    citation_descs = [
        ph.description for ph in drafts.placeholder_index if str(ph.kind) == "CITATION"
    ]
    _validate_citation_keys(citation_descs, manifest_keys)
    md_root = results_root / CANONICAL_MD
    chapters_written: list[str] = []
    for chapter in drafts.chapters:
        path = _write_chapter(md_root, chapter.chapter_id, chapter.body_markdown)
        chapters_written.append(str(path.relative_to(results_root)))
    static_written, static_cites = write_static_templates(md_root, manifest_keys)
    static_rel = [str((md_root / name).relative_to(results_root)) for name in static_written]
    placeholder_kinds = sorted({str(ph.kind) for ph in drafts.placeholder_index})
    record = Phase6RunRecord(
        run_id=run_id,
        generated_at=datetime.now(UTC).isoformat(),
        manifest_path=str(manifest_path),
        manifest_citation_keys=manifest_keys,
        chapters_written=chapters_written,
        static_files_written=static_rel,
        citation_keys_used=sorted(set(citation_descs) | set(static_cites)),
        all_placeholder_kinds=placeholder_kinds,
    )
    _write_run_log(results_root / CANONICAL_RUNLOGS, record)
    return record
