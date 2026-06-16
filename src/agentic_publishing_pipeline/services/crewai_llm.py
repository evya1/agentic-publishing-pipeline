"""CrewAI LLM adapter routed through the repository API Gatekeeper."""

from __future__ import annotations

import json
from typing import Any

from crewai.llms.base_llm import BaseLLM
from crewai.utilities.types import LLMMessage
from pydantic import BaseModel, ValidationError
from typing_extensions import override

from ..providers import ModelRequest
from ..tools.gatekeeper import ApiGatekeeper, request_identity
from ._crewai_messages import split_messages
from ._json_output import build_repair_prompt, parse_response_model

GATEKEEPER_MODEL = "agentic-publishing-gatekeeper"


class CrewStructuredOutputError(RuntimeError):
    """Raised when a CrewAI task exhausts its bounded repair attempt."""


class ControlledCrewLlm(BaseLLM):
    """Translate CrewAI calls into Gatekeeper-controlled model requests."""

    def __init__(
        self,
        *,
        gatekeeper: ApiGatekeeper,
        agent_id: str,
        task_id: str,
        model_class: str,
        run_id: str,
        prompt_version: str,
        max_attempts: int | None = None,
        max_repairs: int = 1,
        max_tokens: int = 8192,
        temperature: float = 0.2,
    ) -> None:
        assert agent_id and task_id and run_id and prompt_version
        if max_repairs < 0:
            raise ValueError("max_repairs must be >= 0")
        derived_attempts = max_repairs + 1 if max_attempts is None else max_attempts
        if derived_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        super().__init__(model=GATEKEEPER_MODEL, temperature=temperature)
        self._gatekeeper = gatekeeper
        self._agent_id = agent_id
        self._task_id = task_id
        self._model_class = model_class
        self._run_id = run_id
        self._prompt_version = prompt_version
        self._max_attempts = derived_attempts
        self._max_repairs = max_repairs
        self._max_tokens = max_tokens

    @override
    def call(
        self,
        messages: str | list[LLMMessage],
        tools: list[dict[str, Any]] | None = None,
        callbacks: list[Any] | None = None,
        available_functions: dict[str, Any] | None = None,
        from_task: Any | None = None,
        from_agent: Any | None = None,
        response_model: type[BaseModel] | None = None,
    ) -> str | BaseModel:
        del tools, callbacks, available_functions, from_task, from_agent
        system_prompt, prompt = split_messages(messages)
        first = self._complete(
            system_prompt=system_prompt,
            prompt=prompt,
            attempt=1,
            purpose="primary",
        )
        if response_model is None:
            return first
        try:
            return parse_response_model(first, response_model)
        except (ValidationError, ValueError, json.JSONDecodeError) as error:
            invalid_output = first
            last_error: Exception = error
        repairs_used = 0
        for attempt in range(2, self._max_attempts + 1):
            if repairs_used >= self._max_repairs:
                break
            repairs_used += 1
            repair_prompt = build_repair_prompt(
                original_prompt=prompt,
                invalid_output=invalid_output,
                response_model=response_model,
                error=last_error,
            )
            repaired = self._complete(
                system_prompt=system_prompt,
                prompt=repair_prompt,
                attempt=attempt,
                purpose="structured-repair",
            )
            try:
                return parse_response_model(repaired, response_model)
            except (ValidationError, ValueError, json.JSONDecodeError) as error:
                invalid_output = repaired
                last_error = error
        message = (
            f"{self._task_id} failed {response_model.__name__} validation after "
            f"{1 + repairs_used} attempt(s); max_attempts={self._max_attempts}, "
            f"max_repairs={self._max_repairs}"
        )
        raise CrewStructuredOutputError(message) from last_error

    def _complete(
        self,
        *,
        system_prompt: str,
        prompt: str,
        attempt: int,
        purpose: str,
    ) -> str:
        request = ModelRequest(
            model_class=self._model_class,
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=self._max_tokens,
            temperature=float(self.temperature or 0.2),
            metadata={
                "run_id": self._run_id,
                "agent_id": self._agent_id,
                "task_id": self._task_id,
                "prompt_version": self._prompt_version,
                "purpose": purpose,
                "attempt": str(attempt),
            },
        )
        response = self._gatekeeper.call_model(
            request,
            identity=request_identity(self._agent_id, self._task_id, attempt=attempt),
        )
        text = response.text.strip()
        if not text:
            raise CrewStructuredOutputError(
                f"{self._task_id} returned an empty model response"
            )
        return text

    def supports_function_calling(self) -> bool:
        """Use explicit Pydantic JSON rather than tool calling."""
        return False
