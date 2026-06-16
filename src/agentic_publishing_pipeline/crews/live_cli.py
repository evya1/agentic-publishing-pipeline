"""CLI helpers for live manuscript generation."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from pathlib import Path

from ..providers import (
    DisabledSearchAdapter,
    OpenAIChatAdapter,
    ProviderConfig,
    ProviderFacade,
    load_provider_config,
)
from ..runtime import PipelineRunContext, Registry
from ..services.source_context import load_source_context
from ..tools.gatekeeper import ApiGatekeeper
from .live_runner import run_live_manuscript

PROJECT_ROOT = Path(__file__).resolve().parents[3]
REVIEW_TEMPLATE = PROJECT_ROOT / "results/run_logs/phase6_review_packet.md"
PREVIOUS_CANONICAL = PROJECT_ROOT / "results/generated_markdown"

LIVE_PROVIDER_CREDENTIALS: Mapping[str, str] = {"openai": "OPENAI_API_KEY"}


class LiveAdapterUnavailable(RuntimeError):
    """Raised when live mode cannot construct a supported provider adapter."""


def run_live_cli(
    *,
    args: argparse.Namespace,
    env: Mapping[str, str],
    registry: Registry,
) -> int:
    """Run the live pre-review manuscript path and write a review packet."""
    config = load_provider_config(env)
    context = PipelineRunContext.create(
        results_root=Path(args.results_root).resolve(),
        mode=args.mode,
        topic=args.topic,
        manifest_path=args.manifest,
        registry_version=registry.fingerprint,
        env=env,
    )
    source_context = load_source_context(Path(args.manifest).resolve())
    gatekeeper = ApiGatekeeper(
        facade=_live_facade(config=config, env=env),
        config=config,
        run_context=context,
    )
    run_live_manuscript(
        context=context,
        registry=registry,
        gatekeeper=gatekeeper,
        topic=args.topic or "Reasoning-Centric Agentic LLM Systems",
        source_context_text=source_context.as_prompt_text(),
        citation_keys=source_context.citation_keys,
        target_pages=_positive_int(env, "APP_LIVE_TARGET_PAGES", 18),
        target_words=_positive_int(env, "APP_LIVE_TARGET_WORDS", 5000),
        min_words_per_chapter=_positive_int(env, "APP_LIVE_MIN_WORDS_PER_CHAPTER", 400),
        min_hebrew_tokens=_positive_int(env, "APP_LIVE_MIN_HEBREW_TOKENS", 40),
        min_embedded_english_terms=_positive_int(env, "APP_LIVE_MIN_ENGLISH_TERMS", 1),
        source_context=source_context,
        review_template_path=REVIEW_TEMPLATE,
        previous_canonical_root=PREVIOUS_CANONICAL.resolve(),
    )
    return 0


def _live_facade(*, config: ProviderConfig, env: Mapping[str, str]) -> ProviderFacade:
    provider = config.llm_provider.lower()
    expected = LIVE_PROVIDER_CREDENTIALS.get(provider)
    if expected is None:
        raise LiveAdapterUnavailable(
            f"live mode has no supported {provider!r} adapter; "
            f"supported providers: {sorted(LIVE_PROVIDER_CREDENTIALS)}"
        )
    api_key = str(env.get(expected, "")).strip()
    if not api_key:
        raise LiveAdapterUnavailable(
            f"live mode requires non-empty {expected} for provider {provider!r}"
        )
    model = OpenAIChatAdapter(
        api_key=api_key,
        model=config.llm_model_id,
        timeout=config.gatekeeper_timeout_seconds,
    )
    return ProviderFacade(model=model, search=DisabledSearchAdapter())


def _positive_int(env: Mapping[str, str], name: str, default: int) -> int:
    raw = env.get(name)
    if raw in (None, ""):
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise SystemExit(f"{name} must be an integer") from exc
    if value <= 0:
        raise SystemExit(f"{name} must be positive")
    return value
