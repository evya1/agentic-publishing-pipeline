"""CLI surface for the agentic-publishing-pipeline runtime.

Modes (per docs/architecture/run_lifecycle.md §3):

- ``dry-run``: bootstrap workspace, verify registry, emit no calls.
- ``offline-fixture``: deterministic full pipeline against fixtures.
- ``live``: real LLM/search; requires API keys (refused without).
- ``compile-only``: re-run renderer + compiler on existing workspace.
- ``validate-only``: re-run validator on existing workspace.
- ``resume``: re-enter at first non-PASS stage of existing workspace.

The CLI never opens a socket. ``offline-fixture`` and ``dry-run``
require no API keys; ``live`` refuses to start when no provider
credential is present.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from ..contracts import REQUIRED_CONTRACT_VERSIONS
from ..providers import load_provider_config
from ..runtime import PipelineRunContext, Registry, load_registry, verify_compatibility
from ._existing_run import handle_existing_mode
from ._phase6_generate import run_phase6_generate
from ._smoke import OFFLINE_MODES, run_offline_smoke
from .live_cli import LIVE_PROVIDER_CREDENTIALS, run_live_cli

PROJECT_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_DEFAULT = PROJECT_ROOT / "config/prompt_registry"
MANIFEST_DEFAULT = PROJECT_ROOT / "config/article_sources.yaml"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentic-publishing-pipeline",
        description="HW3 CrewAI-based article/book generation pipeline.",
    )
    parser.add_argument(
        "--mode",
        choices=[
            "dry-run",
            "offline-fixture",
            "live",
            "compile-only",
            "validate-only",
            "resume",
        ],
        default="offline-fixture",
    )
    parser.add_argument("--topic", default=None)
    parser.add_argument("--manifest", default=str(MANIFEST_DEFAULT))
    parser.add_argument("--registry", default=str(REGISTRY_DEFAULT))
    parser.add_argument("--results-root", default="results")
    parser.add_argument("--run-id", default=None, help="for compile/validate/resume")
    parser.add_argument(
        "--i-understand-this-makes-paid-calls",
        action="store_true",
        help="required for live mode before any provider is constructed",
    )
    return parser


def _check_live_credentials(env: dict[str, str]) -> None:
    provider = load_provider_config(env).llm_provider.lower()
    expected = LIVE_PROVIDER_CREDENTIALS.get(provider)
    if expected is None:
        raise SystemExit(
            f"live mode has no supported {provider!r} adapter; "
            f"set APP_LLM_PROVIDER to one of {sorted(LIVE_PROVIDER_CREDENTIALS)}"
        )
    value = str(env.get(expected, "")).strip()
    if not value:
        raise SystemExit(
            f"live mode requires {expected} for provider {provider!r}; "
            "set the variable to a non-empty key in .env"
        )


def _check_live_ack(args: argparse.Namespace) -> None:
    if not args.i_understand_this_makes_paid_calls:
        raise SystemExit("live mode requires --i-understand-this-makes-paid-calls")


def _load_registry_or_die(path: Path) -> Registry:
    try:
        registry = load_registry(path)
        verify_compatibility(registry, REQUIRED_CONTRACT_VERSIONS)
    except Exception as exc:
        raise SystemExit(f"registry load failed: {exc}") from exc
    return registry


def _new_run_context(
    args: argparse.Namespace,
    env: dict[str, str],
    registry_fingerprint: str,
) -> PipelineRunContext:
    results_root = Path(args.results_root).resolve()
    return PipelineRunContext.create(
        results_root=results_root,
        mode=args.mode,
        topic=args.topic,
        manifest_path=args.manifest,
        registry_version=registry_fingerprint,
        env=env,
    )


def _mark_completed(ctx: PipelineRunContext) -> None:
    ctx.manifest.completed_at = datetime.now(UTC).isoformat()
    ctx.manifest.write(ctx.paths.child("manifest.v1.json"))
    ctx.manifest.write(ctx.paths.child("manifest.json"))


def run_cli(argv: Sequence[str] | None = None, *, env: dict[str, str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    env_map = dict(env if env is not None else os.environ)
    registry_path = _resolve_cli_path(args.registry)
    manifest_path = _resolve_cli_path(args.manifest)
    args.registry = str(registry_path)
    args.manifest = str(manifest_path)
    registry = _load_registry_or_die(registry_path)
    registry_fp = registry.fingerprint
    if args.mode == "live":
        _check_live_ack(args)
        _check_live_credentials(env_map)
        return run_live_cli(args=args, env=env_map, registry=registry)
    if args.mode in {"compile-only", "validate-only", "resume"}:
        if not args.run_id:
            raise SystemExit(f"--run-id is required for mode {args.mode!r}")
        return handle_existing_mode(
            mode=args.mode,
            results_root=Path(args.results_root).resolve(),
            run_id=args.run_id,
        )
    ctx = _new_run_context(args, env_map, registry_fp)
    if args.mode == "dry-run":
        ctx.events.append("run.completed", {"mode": "dry-run"})
        _mark_completed(ctx)
        return 0
    if args.mode in OFFLINE_MODES:
        run_offline_smoke(ctx, manifest_path=manifest_path)
        results_root = Path(args.results_root).resolve()
        run_phase6_generate(results_root, manifest_path)
        ctx.events.append("run.completed", {"mode": ctx.mode})
        _mark_completed(ctx)
        return 0
    raise SystemExit(f"unsupported mode {args.mode!r}")


def _resolve_cli_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    repo_relative = PROJECT_ROOT / path
    if repo_relative.exists():
        return repo_relative.resolve()
    return path.resolve()


def main() -> int:
    return run_cli()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
