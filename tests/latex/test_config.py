from pathlib import Path

import pytest
import yaml

from agentic_publishing_pipeline.latex.config_loader import (
    Phase9ConfigError,
    load_phase9_config,
)


def test_config_rejects_traversal(tmp_path: Path, config) -> None:
    payload = config.model_dump(mode="json")
    payload["source"]["graph_path"] = "../escape.png"
    target = tmp_path / "phase9.yaml"
    target.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    with pytest.raises(Phase9ConfigError):
        load_phase9_config(target)


def test_config_requires_all_phase9_asset_kinds(config) -> None:
    payload = config.model_dump(mode="json")
    payload["assets"] = [item for item in payload["assets"] if item["kind"] != "tikz"]
    with pytest.raises(ValueError, match="asset kinds missing"):
        type(config).model_validate(payload)


def test_config_rejects_missing_equation_reference_target(config) -> None:
    payload = config.model_dump(mode="json")
    reference = next(item for item in payload["assets"] if item["kind"] == "equation_ref")
    reference["payload"]["target"] = "not-defined"
    with pytest.raises(ValueError, match="targets missing equation labels"):
        type(config).model_validate(payload)


def test_config_rejects_citation_requirement_for_unknown_chapter(config) -> None:
    payload = config.model_dump(mode="json")
    payload["chapter_citation_requirements"] = {"missing": ["known"]}
    with pytest.raises(ValueError, match="unknown chapters"):
        type(config).model_validate(payload)
