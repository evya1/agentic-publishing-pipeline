"""JSON extraction and bounded repair prompts for structured LLM output."""

from __future__ import annotations

import json

from pydantic import BaseModel


def parse_response_model(text: str, model_type: type[BaseModel]) -> BaseModel:
    """Extract the first JSON value and validate it as ``model_type``."""
    return model_type.model_validate_json(extract_json_value(text))


def extract_json_value(text: str) -> str:
    """Return the first complete JSON object or array from model text."""
    stripped = _strip_fence(text.strip())
    starts = [index for index in (stripped.find("{"), stripped.find("[")) if index >= 0]
    if not starts:
        raise ValueError("model response contains no JSON object or array")
    start = min(starts)
    _, end = json.JSONDecoder().raw_decode(stripped[start:])
    return stripped[start : start + end]


def build_repair_prompt(
    *,
    original_prompt: str,
    invalid_output: str,
    response_model: type[BaseModel],
    error: Exception,
) -> str:
    """Create the single bounded schema-repair request."""
    schema = json.dumps(response_model.model_json_schema(), sort_keys=True)
    return (
        "Repair the previous answer. Return JSON only; no Markdown fences.\n"
        f"Required schema: {schema}\n"
        f"Validation error: {error}\n"
        f"Original task: {original_prompt}\n"
        f"Invalid answer: {invalid_output}"
    )


def _strip_fence(text: str) -> str:
    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    if len(lines) < 3 or not lines[-1].strip().startswith("```"):
        return text
    inner = "\n".join(lines[1:-1]).strip()
    if inner.lower().startswith("json"):
        return inner[4:].lstrip()
    return inner
