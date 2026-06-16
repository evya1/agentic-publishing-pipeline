"""CrewAI message normalization helpers."""

from __future__ import annotations

from crewai.utilities.types import LLMMessage

DEFAULT_SYSTEM_PROMPT = "You are a precise publishing-pipeline agent."


def split_messages(messages: str | list[LLMMessage]) -> tuple[str, str]:
    """Collapse CrewAI messages into one system prompt and one user prompt."""
    if isinstance(messages, str):
        return DEFAULT_SYSTEM_PROMPT, messages
    system_parts: list[str] = []
    user_parts: list[str] = []
    for message in messages:
        role = str(message.get("role", "user"))
        content = str(message.get("content", ""))
        if role == "system":
            system_parts.append(content)
        else:
            user_parts.append(content)
    system = "\n".join(system_parts).strip()
    user = "\n".join(user_parts).strip()
    return (
        system or DEFAULT_SYSTEM_PROMPT,
        user or system or "Return the requested structured output.",
    )
