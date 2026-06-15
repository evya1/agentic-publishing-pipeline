"""CLI mode tests."""

from __future__ import annotations

import json
import socket
from pathlib import Path

import pytest

from agentic_publishing_pipeline.crews import build_parser, run_cli
from agentic_publishing_pipeline.crews._review_gate import (
    make_review_record,
    write_review_record,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _registry() -> Path:
    return REPO_ROOT / "config" / "prompt_registry"


def _manifest() -> Path:
    return REPO_ROOT / "config" / "article_sources.yaml"


def _run_offline_fixture(tmp_path: Path) -> tuple[int, Path]:
    results = tmp_path / "results"
    rc = run_cli(
        [
            "--mode", "offline-fixture",
            "--registry", str(_registry()),
            "--manifest", str(_manifest()),
            "--results-root", str(results),
            "--topic", "Reasoning",
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
            "--mode", "dry-run",
            "--registry", str(_registry()),
            "--manifest", str(_manifest()),
            "--results-root", str(tmp_path / "results"),
        ],
        env={},
    )
    assert rc == 0
    runs = list((tmp_path / "results").iterdir())
    assert len(runs) == 1
    assert not list((runs[0] / "artifacts").iterdir())


def test_offline_fixture_run_creates_full_workspace(tmp_path: Path) -> None:
    rc, workspace = _run_offline_fixture(tmp_path)
    assert rc == 0
    artifacts = {p.name for p in (workspace / "artifacts").iterdir()}
    expected = {
        "research_notes.v1.json", "outline.v1.json", "chapter_drafts.v1.json",
        "asset_specs.v1.json", "bidi.v1.json", "bibliography.v1.json",
        "latex_project_spec.v1.json", "reviewer_signal.v1.json",
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
        "RESEARCH", "OUTLINE", "WRITE", "ASSET",
        "BIDI", "BIBLIOGRAPHY", "LATEX", "REVIEW",
    }.issubset(task_ids)
    assert all(record["estimated_cost_usd"] == 0.0 for record in usage)
    assert all(record["mode"] == "offline-fixture" for record in usage)


def test_offline_fixture_file_contains_eight_task_responses() -> None:
    fixture = REPO_ROOT / "tests" / "fixtures" / "offline" / "task_responses.json"
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    assert set(payload) == {
        "RESEARCH", "OUTLINE", "WRITE", "ASSET",
        "BIDI", "BIBLIOGRAPHY", "LATEX", "REVIEW",
    }


def test_live_mode_refused_without_credentials() -> None:
    with pytest.raises(SystemExit):
        run_cli(
            ["--mode", "live", "--registry", str(_registry())],
            env={},
        )


def test_live_mode_refused_without_supported_adapter() -> None:
    with pytest.raises(SystemExit, match="no supported live adapter"):
        run_cli(
            ["--mode", "live", "--registry", str(_registry())],
            env={"OPENAI_API_KEY": "present"},
        )


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
            "--mode", "validate-only",
            "--registry", str(_registry()),
            "--results-root", str(tmp_path / "results"),
            "--run-id", workspace.name,
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
                "--mode", "compile-only",
                "--registry", str(_registry()),
                "--results-root", str(tmp_path / "results"),
                "--run-id", workspace.name,
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
            "--mode", "compile-only",
            "--registry", str(_registry()),
            "--results-root", str(tmp_path / "results"),
            "--run-id", workspace.name,
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
            "--mode", "resume",
            "--registry", str(_registry()),
            "--results-root", str(tmp_path / "results"),
            "--run-id", workspace.name,
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
                "--mode", "offline-fixture",
                "--registry", str(_registry()),
                "--manifest", str(_manifest()),
                "--results-root", str(tmp_path / "results"),
            ],
            env={},
        )
    finally:
        monkeypatch.setattr(socket.socket, "connect", original)
    assert rc == 0


def test_dry_run_makes_no_network_calls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = socket.socket.connect

    def fail(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("dry-run mode opened a socket")

    monkeypatch.setattr(socket.socket, "connect", fail)
    try:
        rc = run_cli(
            [
                "--mode", "dry-run",
                "--registry", str(_registry()),
                "--manifest", str(_manifest()),
                "--results-root", str(tmp_path / "results"),
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
