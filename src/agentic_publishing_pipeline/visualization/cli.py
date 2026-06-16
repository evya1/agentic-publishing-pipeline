"""CLI for canonical graph rendering."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .errors import SpecValidationError
from .render_pipeline import generate_graph


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agentic-publishing-pipeline.visualization")
    parser.add_argument("--spec", required=True, help="Path to a graph spec YAML file.")
    parser.add_argument(
        "--output-root",
        default=".",
        help="Root directory that receives latex_project/ and results/ outputs.",
    )
    parser.add_argument(
        "--overwrite-existing",
        action="store_true",
        help="Allow explicit overwrite of existing canonical artifacts.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = generate_graph(
            spec_path=Path(args.spec),
            output_root=Path(args.output_root),
            overwrite_existing=bool(args.overwrite_existing),
        )
    except SpecValidationError as exc:
        print(
            json.dumps(
                {"error": "spec_validation_failed", "issues": _issues_payload(exc)},
                indent=2,
            )
        )
        return 2
    if not result.success:
        print(
            json.dumps(
                {
                    "error": result.error_code,
                    "message": result.message,
                    "asset_id": result.asset_id,
                    "kind": result.kind,
                    "slot": result.slot,
                },
                indent=2,
            )
        )
        return 1
    print(
        json.dumps(
            {
                "asset_id": result.asset_id,
                "path": result.path,
                "provenance_path": result.provenance_path,
                "input_sha256": result.input_sha256,
                "output_sha256": result.output_sha256,
            },
            indent=2,
        )
    )
    return 0


def _issues_payload(exc: SpecValidationError) -> list[dict[str, str]]:
    return [{"path": issue.path, "message": issue.message} for issue in exc.issues]
