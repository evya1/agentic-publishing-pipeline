"""Prompt/config registry loader and compatibility check.

Per FR-47, the runtime refuses to start if the registry's
``compatibility.contract_versions`` does not cover every contract
version the deterministic code requires. The registry layout lives in
``docs/architecture/prompt_config_registry.md`` and the verbatim text
mirrors ``docs/PROMPTS.md`` (the human evidence ledger).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import yaml


class RegistryError(RuntimeError):
    """Raised on malformed registry or compatibility violations."""


@dataclass(frozen=True)
class PromptConfig:
    """A single agent or task entry from the registry."""

    id: str
    ledger_id: str
    kind: str
    version: str
    prompt: dict[str, str]
    config: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class Registry:
    """In-memory representation of the runtime prompt/config registry."""

    registry_version: str
    generated_at: str
    agents: dict[str, PromptConfig]
    tasks: dict[str, PromptConfig]
    contract_versions: tuple[str, ...]
    fingerprint: str

    def get_agent(self, prompt_id: str) -> PromptConfig:
        try:
            return self.agents[prompt_id]
        except KeyError as exc:
            raise RegistryError(f"unknown agent prompt id: {prompt_id!r}") from exc

    def get_task(self, prompt_id: str) -> PromptConfig:
        try:
            return self.tasks[prompt_id]
        except KeyError as exc:
            raise RegistryError(f"unknown task prompt id: {prompt_id!r}") from exc


def _load_yaml(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise RegistryError(f"registry file missing: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RegistryError(f"registry yaml must be a mapping: {path}")
    return data


def _load_entry(path: Path) -> PromptConfig:
    data = _load_yaml(path)
    try:
        return PromptConfig(
            id=str(data["id"]),
            ledger_id=str(data["ledger_id"]),
            kind=str(data["kind"]),
            version=str(data["version"]),
            prompt={k: str(v) for k, v in dict(data["prompt"]).items()},
            config=dict(data.get("config", {})),
        )
    except (KeyError, TypeError) as exc:
        raise RegistryError(f"malformed registry entry at {path}: {exc}") from exc


def _fingerprint(parts: list[str]) -> str:
    body = "\n".join(sorted(parts))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def load_registry(root: Path) -> Registry:
    """Load and validate the registry rooted at ``root``."""

    assert root.is_dir(), f"registry root not a directory: {root}"
    index = _load_yaml(root / "registry.v1.yaml")
    entries = index.get("entries", {})
    if not isinstance(entries, dict):
        raise RegistryError("registry.entries must be a mapping")
    agents: dict[str, PromptConfig] = {}
    tasks: dict[str, PromptConfig] = {}
    fp_parts: list[str] = []
    for kind, target in (("agents", agents), ("tasks", tasks)):
        raw = entries.get(kind, [])
        for spec in raw:
            entry = _load_entry(root / str(spec["path"]))
            target[entry.id] = entry
            fp_parts.append(f"{entry.id}|{entry.version}|{entry.ledger_id}")
    contract_versions = tuple(
        str(v) for v in (index.get("compatibility", {}) or {}).get("contract_versions", [])
    )
    fp_parts.extend(contract_versions)
    return Registry(
        registry_version=str(index.get("registry_version", "v1")),
        generated_at=str(index.get("generated_at", "")),
        agents=agents,
        tasks=tasks,
        contract_versions=contract_versions,
        fingerprint=_fingerprint(fp_parts),
    )


def verify_compatibility(
    registry: Registry,
    required: tuple[str, ...] | list[str],
) -> None:
    """Raise :class:`RegistryError` if ``required`` is not fully covered."""

    declared = set(registry.contract_versions)
    missing = [name for name in required if name not in declared]
    if missing:
        raise RegistryError(
            "Registry compatibility check failed; missing contract versions: " + ", ".join(missing)
        )
