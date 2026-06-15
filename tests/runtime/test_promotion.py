"""Promotion preconditions and atomic-copy behaviour tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_publishing_pipeline.runtime import (
    PipelineRunContext,
    PromotionRefused,
    generate_run_id,
    promote,
)


def _setup_passing_run(tmp_path: Path) -> PipelineRunContext:
    ctx = PipelineRunContext(
        run_id=generate_run_id(),
        results_root=tmp_path / "results",
        mode="offline-fixture",
        env={},
    )
    ctx.write_artifact_json("artifacts/latex_project_spec.v1.json", {"k": "v"})
    ctx.register_artifact(
        artifact_id="latex_project_spec",
        contract="LaTeXProjectSpec",
        contract_version="v1",
        relative_path="artifacts/latex_project_spec.v1.json",
        produced_by_task="T7",
    )
    main_tex = ctx.paths.child("latex_project/main.tex")
    main_tex.write_text("\\documentclass{article}\n", encoding="utf-8")
    ctx.register_artifact(
        artifact_id="main_tex",
        contract="LaTeXFile",
        contract_version="v1",
        relative_path="latex_project/main.tex",
        produced_by_task="renderer",
    )
    validation_path = ctx.paths.child("validation/report.v1.json")
    validation_path.write_text(json.dumps({"result": "pass"}), encoding="utf-8")
    return ctx


def test_promotion_succeeds_on_pass(tmp_path: Path) -> None:
    ctx = _setup_passing_run(tmp_path)
    canonical_root = tmp_path / "canonical"
    canonical_root.mkdir()
    result = promote(
        workspace_root=ctx.paths.root,
        canonical_root=canonical_root,
        manifest_path=ctx.paths.child("manifest.v1.json"),
        validation_report_path=ctx.paths.child("validation/report.v1.json"),
        pairs=[("latex_project/main.tex", "latex_project/main.tex")],
    )
    assert (canonical_root / "latex_project" / "main.tex").exists()
    assert result["latex_project/main.tex"]


def test_promotion_refuses_on_fail(tmp_path: Path) -> None:
    ctx = _setup_passing_run(tmp_path)
    ctx.paths.child("validation/report.v1.json").write_text(
        json.dumps({"result": "fail"}), encoding="utf-8"
    )
    canonical_root = tmp_path / "canonical"
    canonical_root.mkdir()
    with pytest.raises(PromotionRefused):
        promote(
            workspace_root=ctx.paths.root,
            canonical_root=canonical_root,
            manifest_path=ctx.paths.child("manifest.v1.json"),
            validation_report_path=ctx.paths.child("validation/report.v1.json"),
            pairs=[("latex_project/main.tex", "latex_project/main.tex")],
        )


def test_promotion_refuses_when_manifest_hash_mismatches(tmp_path: Path) -> None:
    ctx = _setup_passing_run(tmp_path)
    main_tex = ctx.paths.child("latex_project/main.tex")
    main_tex.write_text("\\documentclass{report}\n", encoding="utf-8")
    canonical_root = tmp_path / "canonical"
    canonical_root.mkdir()
    with pytest.raises(PromotionRefused):
        promote(
            workspace_root=ctx.paths.root,
            canonical_root=canonical_root,
            manifest_path=ctx.paths.child("manifest.v1.json"),
            validation_report_path=ctx.paths.child("validation/report.v1.json"),
            pairs=[("latex_project/main.tex", "latex_project/main.tex")],
        )


def test_promotion_refuses_existing_canonical_unless_forced(tmp_path: Path) -> None:
    ctx = _setup_passing_run(tmp_path)
    canonical_root = tmp_path / "canonical"
    target = canonical_root / "latex_project" / "main.tex"
    target.parent.mkdir(parents=True)
    target.write_text("old\n", encoding="utf-8")
    with pytest.raises(PromotionRefused):
        promote(
            workspace_root=ctx.paths.root,
            canonical_root=canonical_root,
            manifest_path=ctx.paths.child("manifest.v1.json"),
            validation_report_path=ctx.paths.child("validation/report.v1.json"),
            pairs=[("latex_project/main.tex", "latex_project/main.tex")],
        )
    result = promote(
        workspace_root=ctx.paths.root,
        canonical_root=canonical_root,
        manifest_path=ctx.paths.child("manifest.v1.json"),
        validation_report_path=ctx.paths.child("validation/report.v1.json"),
        pairs=[("latex_project/main.tex", "latex_project/main.tex")],
        force=True,
        force_reason="operator override",
    )
    assert "latex_project/main.tex" in result


def test_force_without_reason_refused(tmp_path: Path) -> None:
    ctx = _setup_passing_run(tmp_path)
    canonical_root = tmp_path / "canonical"
    canonical_root.mkdir()
    with pytest.raises(PromotionRefused):
        promote(
            workspace_root=ctx.paths.root,
            canonical_root=canonical_root,
            manifest_path=ctx.paths.child("manifest.v1.json"),
            validation_report_path=ctx.paths.child("validation/report.v1.json"),
            pairs=[("latex_project/main.tex", "latex_project/main.tex")],
            force=True,
            force_reason=None,
        )
