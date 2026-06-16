"""CLI mode tests."""

from __future__ import annotations

import json
import socket
from pathlib import Path

import pytest

import agentic_publishing_pipeline.crews.live_cli as live_cli_module
from agentic_publishing_pipeline.crews import (
    LiveAdapterUnavailable,
    build_parser,
    run_cli,
)
from agentic_publishing_pipeline.crews._review_gate import (
    compute_draft_revision,
    make_review_record,
    write_review_record,
)
from agentic_publishing_pipeline.runtime import PipelineStage, StageState, write_stage
from agentic_publishing_pipeline.tasks.completeness import ManuscriptPreflightReport
from agentic_publishing_pipeline.tools.fileio import FileIO

REPO_ROOT = Path(__file__).resolve().parents[2]


def _registry() -> Path:
    return REPO_ROOT / "config" / "prompt_registry"


def _manifest() -> Path:
    return REPO_ROOT / "config" / "article_sources.yaml"


def _run_offline_fixture(tmp_path: Path) -> tuple[int, Path]:
    results = tmp_path / "results"
    rc = run_cli(
        [
            "--mode",
            "offline-fixture",
            "--registry",
            str(_registry()),
            "--manifest",
            str(_manifest()),
            "--results-root",
            str(results),
            "--topic",
            "Reasoning",
        ],
        env={},
    )
    workspaces = [p for p in results.iterdir() if p.name.startswith("RUN-")]
    assert workspaces, "no RUN-* workspace found in results"
    return rc, workspaces[0]


def _approve_drafts(results: Path) -> None:
    """Write a valid human review record so compile-only can pass the gate."""
    md_root = results / "generated_markdown"
    log_root = results / "run_logs"
    rec = make_review_record(
        reviewer="Test Reviewer", generated_md_root=md_root, verdict="approved"
    )
    write_review_record(rec, log_root)


def test_parser_known_modes() -> None:
    parser = build_parser()
    modes = ["dry-run", "offline-fixture", "live", "compile-only", "validate-only", "resume"]
    for mode in modes:
        args = parser.parse_args(["--mode", mode, "--topic", "x", "--manifest", "m"])
        assert args.mode == mode
        assert args.topic == "x"
        assert args.manifest == "m"


def test_dry_run_creates_workspace_without_artifacts(tmp_path: Path) -> None:
    rc = run_cli(
        [
            "--mode",
            "dry-run",
            "--registry",
            str(_registry()),
            "--manifest",
            str(_manifest()),
            "--results-root",
            str(tmp_path / "results"),
        ],
        env={},
    )
    assert rc == 0
    runs = list((tmp_path / "results").iterdir())
    assert len(runs) == 1
    assert not list((runs[0] / "artifacts").iterdir())


def test_cli_defaults_resolve_from_outside_repo_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.chdir(outside)
    rc = run_cli(
        [
            "--mode",
            "dry-run",
            "--results-root",
            str(tmp_path / "results"),
        ],
        env={},
    )
    assert rc == 0


def test_offline_fixture_run_creates_full_workspace(tmp_path: Path) -> None:
    rc, workspace = _run_offline_fixture(tmp_path)
    assert rc == 0
    artifacts = {p.name for p in (workspace / "artifacts").iterdir()}
    expected = {
        "research_notes.v1.json",
        "outline.v1.json",
        "chapter_drafts.v1.json",
        "asset_specs.v1.json",
        "bidi.v1.json",
        "bibliography.v1.json",
        "latex_project_spec.v1.json",
        "reviewer_signal.v1.json",
    }
    assert expected.issubset(artifacts)
    assert (workspace / "latex_project" / "figures" / "demo.png").exists()
    manifest = json.loads((workspace / "manifest.v1.json").read_text(encoding="utf-8"))
    assert manifest["completed_at"]


def test_offline_fixture_routes_all_task_boundaries_through_gatekeeper(tmp_path: Path) -> None:
    rc, workspace = _run_offline_fixture(tmp_path)
    assert rc == 0
    usage = [
        json.loads(line)
        for line in (workspace / "usage.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    task_ids = {record["task_id"] for record in usage}
    assert {
        "RESEARCH",
        "OUTLINE",
        "WRITE",
        "ASSET",
        "BIDI",
        "BIBLIOGRAPHY",
        "LATEX",
        "REVIEW",
    }.issubset(task_ids)
    assert all(record["estimated_cost_usd"] == 0.0 for record in usage)
    assert all(record["mode"] == "offline-fixture" for record in usage)


def test_offline_fixture_file_contains_eight_task_responses() -> None:
    fixture = REPO_ROOT / "tests" / "fixtures" / "offline" / "task_responses.json"
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    assert set(payload) == {
        "RESEARCH",
        "OUTLINE",
        "WRITE",
        "ASSET",
        "BIDI",
        "BIBLIOGRAPHY",
        "LATEX",
        "REVIEW",
    }


def test_live_mode_refused_without_paid_call_ack() -> None:
    with pytest.raises(SystemExit, match="i-understand-this-makes-paid-calls"):
        run_cli(
            ["--mode", "live", "--registry", str(_registry())],
            env={"OPENAI_API_KEY": "present"},
        )


def test_live_mode_refused_without_credentials() -> None:
    with pytest.raises(SystemExit, match="requires ANTHROPIC_API_KEY"):
        run_cli(
            [
                "--mode",
                "live",
                "--registry",
                str(_registry()),
                "--i-understand-this-makes-paid-calls",
            ],
            env={},
        )


def test_live_mode_refused_without_supported_adapter() -> None:
    with pytest.raises(LiveAdapterUnavailable, match="no supported 'anthropic' adapter"):
        run_cli(
            [
                "--mode",
                "live",
                "--registry",
                str(_registry()),
                "--i-understand-this-makes-paid-calls",
            ],
            env={"OPENAI_API_KEY": "present", "APP_LLM_PROVIDER": "anthropic"},
        )


def test_live_mode_openai_writes_review_packet_at_human_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeOpenAIAdapter:
        name = "fake-openai"

        def __init__(self, **_: object) -> None:
            pass

    def fake_run_live_manuscript(**kwargs):
        context = kwargs["context"]
        write_stage(
            FileIO(context),
            StageState(PipelineStage.AWAITING_HUMAN_REVIEW, context.run_id),
        )
        md_root = context.paths.child("generated_markdown")
        chapters = md_root / "chapters"
        chapters.mkdir(parents=True, exist_ok=True)
        (chapters / "memory.md").write_text(
            "# Memory\n\nBody with <!-- CITATION: chen2025telemem -->.\n",
            encoding="utf-8",
        )
        (md_root / "outline.md").write_text("# Outline\n", encoding="utf-8")
        return object(), ManuscriptPreflightReport(
            passed=True,
            word_counts={"memory": 4},
            total_words=4,
            cited_keys=("chen2025telemem",),
            missing_source_keys=(),
        )

    monkeypatch.setattr(live_cli_module, "OpenAIChatAdapter", FakeOpenAIAdapter)
    monkeypatch.setattr(live_cli_module, "run_live_manuscript", fake_run_live_manuscript)
    results = tmp_path / "results"
    rc = run_cli(
        [
            "--mode",
            "live",
            "--registry",
            str(_registry()),
            "--manifest",
            str(_manifest()),
            "--results-root",
            str(results),
            "--i-understand-this-makes-paid-calls",
        ],
        env={"OPENAI_API_KEY": "present", "APP_LLM_PROVIDER": "openai"},
    )
    workspace = next(path for path in results.iterdir() if path.name.startswith("RUN-"))
    aggregate = compute_draft_revision(workspace / "generated_markdown")
    packet = (workspace / "review_packet.md").read_text(encoding="utf-8")
    status = json.loads((workspace / "status.json").read_text(encoding="utf-8"))
    assert rc == 0
    assert status["stage"] == "awaiting_human_review"
    assert f'"draft_sha256": "{aggregate}"' in packet
    assert json.loads((workspace / "hashes.json").read_text(encoding="utf-8"))[
        "generated_markdown_sha256"
    ] == aggregate


def test_live_workspace_contract_paths_are_stable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run_live_manuscript(**kwargs):
        context = kwargs["context"]
        write_stage(
            FileIO(context),
            StageState(PipelineStage.AWAITING_HUMAN_REVIEW, context.run_id),
        )
        typed = context.paths.child("typed_outputs")
        typed.mkdir(parents=True, exist_ok=True)
        for name in (
            "research_notes",
            "outline",
            "chapter_drafts",
            "asset_specs",
            "bidi_section",
            "bibliography",
            "reviewer_signal",
        ):
            (typed / f"{name}.json").write_text("{}", encoding="utf-8")
        md_root = context.paths.child("generated_markdown")
        chapters = md_root / "chapters"
        chapters.mkdir(parents=True, exist_ok=True)
        (chapters / "memory.md").write_text(
            "# Memory\n\nBody with <!-- CITATION: chen2025telemem -->.\n",
            encoding="utf-8",
        )
        (md_root / "outline.md").write_text("# Outline\n", encoding="utf-8")
        (md_root / "research_notes.md").write_text("# Research\n", encoding="utf-8")
        context.write_artifact_json("raw_outputs/crew_result.json", {"repr": "fake"})
        context.write_artifact_json("preflight_report.json", {"passed": True})
        return object(), ManuscriptPreflightReport(
            passed=True,
            word_counts={"memory": 4},
            total_words=4,
            cited_keys=("chen2025telemem",),
            missing_source_keys=(),
        )

    monkeypatch.setattr(live_cli_module, "run_live_manuscript", fake_run_live_manuscript)
    results = tmp_path / "results"
    rc = run_cli(
        [
            "--mode",
            "live",
            "--registry",
            str(_registry()),
            "--manifest",
            str(_manifest()),
            "--results-root",
            str(results),
            "--i-understand-this-makes-paid-calls",
        ],
        env={"OPENAI_API_KEY": "present", "APP_LLM_PROVIDER": "openai"},
    )
    workspace = next(path for path in results.iterdir() if path.name.startswith("RUN-"))
    expected = {
        "manifest.json",
        "manifest.v1.json",
        "status.json",
        "review_packet.md",
        "hashes.json",
        "preflight_report.json",
        "logs/events.jsonl",
        "typed_outputs/research_notes.json",
        "typed_outputs/outline.json",
        "typed_outputs/chapter_drafts.json",
        "typed_outputs/asset_specs.json",
        "typed_outputs/bidi_section.json",
        "typed_outputs/bibliography.json",
        "typed_outputs/reviewer_signal.json",
        "raw_outputs/crew_result.json",
        "generated_markdown/outline.md",
        "generated_markdown/research_notes.md",
        "generated_markdown/chapters/memory.md",
    }
    actual = {p.relative_to(workspace).as_posix() for p in workspace.rglob("*") if p.is_file()}
    assert rc == 0
    assert expected <= actual


def test_live_cli_reviewer_instructions_require_template(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="review template missing"):
        live_cli_module._reviewer_instructions(tmp_path / "missing.md", "0" * 64)
    bad = tmp_path / "bad.md"
    bad.write_text("no response templates here", encoding="utf-8")
    with pytest.raises(SystemExit, match="Response templates"):
        live_cli_module._reviewer_instructions(bad, "0" * 64)


def test_live_cli_positive_int_validation() -> None:
    assert live_cli_module._positive_int({}, "APP_VALUE", 7) == 7
    with pytest.raises(SystemExit, match="must be an integer"):
        live_cli_module._positive_int({"APP_VALUE": "x"}, "APP_VALUE", 7)
    with pytest.raises(SystemExit, match="must be positive"):
        live_cli_module._positive_int({"APP_VALUE": "0"}, "APP_VALUE", 7)


def test_compile_only_requires_run_id() -> None:
    with pytest.raises(SystemExit):
        run_cli(
            ["--mode", "compile-only", "--registry", str(_registry())],
            env={},
        )


def test_validate_only_reuses_workspace_and_updates_snapshot(tmp_path: Path) -> None:
    rc, workspace = _run_offline_fixture(tmp_path)
    assert rc == 0
    rc = run_cli(
        [
            "--mode",
            "validate-only",
            "--registry",
            str(_registry()),
            "--results-root",
            str(tmp_path / "results"),
            "--run-id",
            workspace.name,
        ],
        env={},
    )
    assert rc == 0
    report = json.loads((workspace / "validation" / "report.v1.json").read_text())
    snapshot = json.loads((workspace / "config_snapshot.json").read_text())
    assert report["result"] == "pass"
    assert snapshot["last_cli_invocation"]["mode"] == "validate-only"


def test_compile_only_reports_missing_project_input(tmp_path: Path) -> None:
    rc, workspace = _run_offline_fixture(tmp_path)
    assert rc == 0
    _approve_drafts(tmp_path / "results")
    with pytest.raises(SystemExit, match="requires existing latex_project/main.tex"):
        run_cli(
            [
                "--mode",
                "compile-only",
                "--registry",
                str(_registry()),
                "--results-root",
                str(tmp_path / "results"),
                "--run-id",
                workspace.name,
            ],
            env={},
        )
    assert "compile.failed" in (workspace / "events.jsonl").read_text(encoding="utf-8")


def test_compile_only_reruns_build_and_validation_when_project_exists(tmp_path: Path) -> None:
    rc, workspace = _run_offline_fixture(tmp_path)
    assert rc == 0
    _approve_drafts(tmp_path / "results")
    (workspace / "latex_project" / "main.tex").write_text(
        "\\documentclass{article}\n\\begin{document}\nOffline fixture\n\\end{document}\n",
        encoding="utf-8",
    )
    rc = run_cli(
        [
            "--mode",
            "compile-only",
            "--registry",
            str(_registry()),
            "--results-root",
            str(tmp_path / "results"),
            "--run-id",
            workspace.name,
        ],
        env={},
    )
    assert rc == 0
    assert (workspace / "latex_project" / "main.pdf").exists()
    build = json.loads((workspace / "build" / "build.v1.json").read_text())
    report = json.loads((workspace / "validation" / "report.v1.json").read_text())
    assert len(build["passes"]) == 4
    assert report["result"] == "pass"


def test_resume_reenters_at_validation_when_no_pass_report(tmp_path: Path) -> None:
    rc, workspace = _run_offline_fixture(tmp_path)
    assert rc == 0
    rc = run_cli(
        [
            "--mode",
            "resume",
            "--registry",
            str(_registry()),
            "--results-root",
            str(tmp_path / "results"),
            "--run-id",
            workspace.name,
        ],
        env={},
    )
    assert rc == 0
    events = (workspace / "events.jsonl").read_text(encoding="utf-8")
    assert "resume.reenter" in events
    assert (workspace / "validation" / "report.v1.json").exists()


def test_offline_fixture_makes_no_network_calls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = socket.socket.connect

    def fail(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("offline-fixture mode opened a socket")

    monkeypatch.setattr(socket.socket, "connect", fail)
    try:
        rc = run_cli(
            [
                "--mode",
                "offline-fixture",
                "--registry",
                str(_registry()),
                "--manifest",
                str(_manifest()),
                "--results-root",
                str(tmp_path / "results"),
            ],
            env={},
        )
    finally:
        monkeypatch.setattr(socket.socket, "connect", original)
    assert rc == 0


def test_dry_run_makes_no_network_calls(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    original = socket.socket.connect

    def fail(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("dry-run mode opened a socket")

    monkeypatch.setattr(socket.socket, "connect", fail)
    try:
        rc = run_cli(
            [
                "--mode",
                "dry-run",
                "--registry",
                str(_registry()),
                "--manifest",
                str(_manifest()),
                "--results-root",
                str(tmp_path / "results"),
            ],
            env={},
        )
    finally:
        monkeypatch.setattr(socket.socket, "connect", original)
    assert rc == 0


def test_registry_failure_surfaces_systemexit(tmp_path: Path) -> None:
    bogus = tmp_path / "bogus"
    with pytest.raises(SystemExit):
        run_cli(["--mode", "dry-run", "--registry", str(bogus)], env={})
