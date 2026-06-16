#!/usr/bin/env python3
"""Inspect or render the Phase 9 project without invoking a TeX compiler."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from agentic_publishing_pipeline.latex.approval_loader import load_approved_manuscript
from agentic_publishing_pipeline.latex.config_loader import (
    load_phase9_config,
    resolve_repo_path,
)
from agentic_publishing_pipeline.latex.preflight import run_phase9_preflight
from agentic_publishing_pipeline.latex.project_renderer import build_project_plan
from agentic_publishing_pipeline.latex.standalone import compare_plan, write_plan


def main() -> int:
    args = _parser().parse_args()
    repo_root = args.repo_root.resolve()
    config = load_phase9_config(args.config.resolve())
    source = config.source
    manuscript = load_approved_manuscript(
        generated_md_root=resolve_repo_path(repo_root, source.markdown_root),
        run_log_root=resolve_repo_path(repo_root, source.review_log_root),
        chapter_order=tuple(config.chapter_order),
    )
    bibliography = resolve_repo_path(repo_root, source.bibliography_path)
    graph = resolve_repo_path(repo_root, source.graph_path)
    report = run_phase9_preflight(
        manuscript=manuscript,
        config=config,
        outline_path=resolve_repo_path(repo_root, source.outline_path),
        bibliography_path=bibliography,
        graph_path=graph,
    )
    print(json.dumps(report.to_json(), indent=2, ensure_ascii=False))
    if not report.passed:
        return 2
    if args.check_inputs:
        return 0
    plan = build_project_plan(
        manuscript=manuscript,
        config=config,
        bibliography_path=bibliography,
        graph_path=graph,
    )
    if args.render_to:
        write_plan(plan, args.render_to.resolve())
    if args.check_tree:
        drift = compare_plan(plan, args.check_tree.resolve())
        print(json.dumps(drift.__dict__, indent=2))
        return 0 if drift.clean else 3
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/latex/phase9_project.yaml"),
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check-inputs", action="store_true")
    action.add_argument("--render-to", type=Path)
    action.add_argument("--check-tree", type=Path)
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
